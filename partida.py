import re
import random
import sys
import tablero
import flota
import armamento
import radar
import registro
from errores import (
    ErrorOperacionCubo,
    ConfiguracionInvalida,
    JugadaInvalida,
    ArmaNoDisponible,
    SinMunicion,
    PuntoFueraDelCubo,
    CeldaYaAtacada,
    PartidaTerminada
)

TAMANIO = 8
BONIFICACION_MUNICION_ESTACION = 1

PATRON_PUNTO = r"(\d{1,2}),(\d{1,2}),(\d{1,2})"


# ---------------------------------------------------------------
# Logica de la partida (sin print ni input)
# ---------------------------------------------------------------

def _punto_de_jugada(cubo, jugada):
    """Valida y normaliza el objetivo de un disparo con coordenadas."""
    punto = jugada.get("objetivo")
    try:
        valido = tablero.validar_punto(cubo, punto)
    except (TypeError, ValueError, IndexError):
        valido = False
    if not valido:
        raise PuntoFueraDelCubo("El objetivo esta fuera del cubo.")
    return tuple(punto)


def _celdas_torpedo(cubo, flota_objetivo, jugada):
    punto = _punto_de_jugada(cubo, jugada)
    return {"tipo": "ataque", "objetivo": punto,
            "celdas": armamento.celdas_torpedo(punto)}


def _celdas_racimo(cubo, flota_objetivo, jugada):
    punto = _punto_de_jugada(cubo, jugada)
    return {"tipo": "ataque", "objetivo": punto,
            "celdas": armamento.celdas_racimo(cubo, punto)}


def _celdas_carga_profundidad(cubo, flota_objetivo, jugada):
    punto = _punto_de_jugada(cubo, jugada)
    return {"tipo": "ataque", "objetivo": punto,
            "celdas": armamento.celdas_carga_profundidad(cubo, punto)}


def _celdas_barrido_laser(cubo, flota_objetivo, jugada):
    punto = _punto_de_jugada(cubo, jugada)
    eje = jugada.get("eje")
    try:
        celdas = armamento.celdas_barrido_laser(cubo, flota_objetivo, punto, eje)
    except ValueError as error:
        raise JugadaInvalida(str(error))
    return {"tipo": "ataque", "objetivo": punto, "eje": eje, "celdas": celdas}


def _celdas_onda_expansiva(cubo, flota_objetivo, jugada):
    punto = _punto_de_jugada(cubo, jugada)
    return {"tipo": "ataque", "objetivo": punto,
            "celdas": armamento.celdas_onda_expansiva(cubo, punto)}


def _celdas_torpedo_guiado(cubo, flota_objetivo, jugada):
    punto = _punto_de_jugada(cubo, jugada)
    return {"tipo": "ataque", "objetivo": punto,
            "celdas": armamento.celdas_torpedo_guiado(cubo, flota_objetivo, punto)}


def _ejecutar_sonar(cubo, flota_objetivo, jugada):
    eje = jugada.get("eje")
    valor = jugada.get("valor")
    try:
        plano = radar.sonar_plano(cubo, eje, valor)
    except (TypeError, ValueError) as error:
        raise JugadaInvalida(str(error))

    contactos = []
    for punto in plano:
        if tablero.obtener_celda(cubo, punto) == tablero.DETECTADO_SONAR:
            contactos.append(punto)

    return {"tipo": "sonar", "eje": eje, "valor": valor,
            "celdas": plano, "contactos": contactos}


# Cada letra despacha a la funcion que prepara sus celdas afectadas.
DISPAROS = {
    "T": _celdas_torpedo,
    "R": _celdas_racimo,
    "C": _celdas_carga_profundidad,
    "S": _ejecutar_sonar,
    "L": _celdas_barrido_laser,
    "O": _celdas_onda_expansiva,
    "G": _celdas_torpedo_guiado,
}


def _celdas_reimpactables(cubo, flota_objetivo):
    """Devuelve casillas del portaaviones que admiten su segundo impacto."""
    puntos = []
    for nave in flota_objetivo.values():
        if nave["tipo"] != "P":
            continue
        for punto in nave["celdas"]:
            if (tablero.obtener_celda(cubo, punto) == tablero.IMPACTO
                    and flota.puede_recibir_impacto(flota_objetivo, punto)):
                puntos.append(punto)
    return puntos


def elegir_al_azar(cubo, flota_objetivo=None):
    """
    elige al azar una celda del cubo que todavia no recibio disparos.
    recibe el cubo del rival.
    retorna una tupla (z, x, y).
    """
    if flota_objetivo is not None:
        reimpactables = _celdas_reimpactables(cubo, flota_objetivo)
        if reimpactables:
            return random.choice(reimpactables)

    libres = []
    n = len(cubo)

    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                estado_celda = tablero.obtener_celda(cubo, (z, x, y))
                if estado_celda in (tablero.AGUA_SIN_EXPLORAR,
                                    tablero.NAVE_OCULTA,
                                    tablero.DETECTADO_SONAR):
                    libres.append((z, x, y))

    if not libres:
        raise JugadaInvalida("No quedan celdas disponibles para disparar.")
    return random.choice(libres)


def elegir_por_probabilidad(cubo, flota_objetivo=None):
    """Elige al azar entre las celdas con mayor probabilidad estimada."""
    if flota_objetivo is not None:
        reimpactables = _celdas_reimpactables(cubo, flota_objetivo)
        if reimpactables:
            return random.choice(reimpactables)

    probabilidades = radar.mapa_probabilidad(cubo)
    maximos = radar.obtener_maximos_probabilidad(cubo, probabilidades)
    if not maximos:
        raise JugadaInvalida("No quedan celdas disponibles para disparar.")
    return random.choice(maximos)


# Niveles de la maquina: nombre -> funcion que elige el objetivo.
DIFICULTADES = {
    "facil": elegir_al_azar,
    "dificil": elegir_por_probabilidad,
}


def crear_jugador(datos, tipo):
    """
    arma el diccionario de un jugador para el estado de la partida.
    recibe un diccionario con nombre, cubo y flota, y el tipo ("humano" o "maquina").
    retorna el jugador con su propia municion inicial.
    """
    municion = {}
    catalogo = armamento.obtener_catalogo()
    for letra in catalogo:
        municion[letra] = catalogo[letra]["municion"]

    return {
        "nombre": datos["nombre"],
        "tipo": tipo,
        "cubo": datos["cubo"],
        "flota": datos["flota"],
        "municion": municion,
    }


def armar_estado(jugador1, jugador2):
    """
    recibe los dos jugadores ya creados.
    retorna el estado inicial de la partida. Empieza el jugador 1.
    """
    return {
        "jugadores": [jugador1, jugador2],
        "actual": 0,
        "turno": 1,
        "registro": registro.crear_registro(),
        "ultimo_disparo": None,
    }


def validar_configuracion(configuracion):
    """
    recibe la configuracion de una partida.
    retorna la lista de los dos jugadores.
    lanza ConfiguracionInvalida si no hay exactamente dos jugadores.
    """
    jugadores = configuracion.get("jugadores", [])
    if len(jugadores) != 2:
        raise ConfiguracionInvalida("La partida necesita dos jugadores.")
    return jugadores


def nueva_partida_1v1(configuracion):
    """
    recibe la configuracion: {"jugadores": [jugador1, jugador2]},
    donde cada jugador es un diccionario con nombre, cubo y flota ya ubicada.
    retorna el estado inicial de una partida entre dos personas.
    lanza ConfiguracionInvalida si la configuracion no es correcta.
    """
    jugadores = validar_configuracion(configuracion)
    return armar_estado(crear_jugador(jugadores[0], "humano"),
                        crear_jugador(jugadores[1], "humano"))


def nueva_partida_vs_maquina(configuracion, dificultad):
    """
    recibe la configuracion (el segundo jugador es la maquina) y la dificultad.
    retorna el estado inicial de una partida contra la maquina.
    lanza ConfiguracionInvalida si la configuracion o la dificultad no son correctas.
    """
    jugadores = validar_configuracion(configuracion)
    if dificultad not in DIFICULTADES:
        raise ConfiguracionInvalida("Dificultad desconocida: " + str(dificultad))

    maquina = crear_jugador(jugadores[1], "maquina")
    maquina["dificultad"] = dificultad
    return armar_estado(crear_jugador(jugadores[0], "humano"), maquina)


def nueva_partida_maquina_vs_maquina(configuracion, dificultades):
    """Crea un estado inicial con dos maquinas y sus niveles de dificultad.

    Recibe una configuracion con dos jugadores y una lista o tupla con una
    dificultad para cada maquina. Devuelve el estado inicial o lanza
    ConfiguracionInvalida si los datos no son correctos.
    """
    jugadores = validar_configuracion(configuracion)
    if not isinstance(dificultades, (list, tuple)) or len(dificultades) != 2:
        raise ConfiguracionInvalida("Indique una dificultad para cada maquina.")

    maquinas = []
    for indice in range(2):
        dificultad = dificultades[indice]
        if dificultad not in DIFICULTADES:
            raise ConfiguracionInvalida("Dificultad desconocida: " + str(dificultad))
        maquina = crear_jugador(jugadores[indice], "maquina")
        maquina["dificultad"] = dificultad
        maquinas.append(maquina)

    return armar_estado(maquinas[0], maquinas[1])


def jugador_actual(estado):
    """recibe el estado. retorna el jugador que tiene el turno."""
    return estado["jugadores"][estado["actual"]]


def rival_actual(estado):
    """recibe el estado. retorna el rival del jugador que tiene el turno."""
    return estado["jugadores"][1 - estado["actual"]]


def _revelar_celda_del_rival(jugador):
    """Marca una celda oculta de la flota del rival como detectada."""
    puntos = []
    for punto in tablero.recorrido_zxy(jugador["cubo"]):
        if tablero.obtener_celda(jugador["cubo"], punto) == tablero.NAVE_OCULTA:
            puntos.append(punto)

    if not puntos:
        return None

    punto = random.choice(puntos)
    tablero.cambiar_celda(jugador["cubo"], punto, tablero.DETECTADO_SONAR)
    return punto


def _otorgar_municion_extra(jugador):
    """Suma una unidad a cada arma limitada por el hundimiento de la estacion."""
    otorgada = {}
    for letra in jugador["municion"]:
        if jugador["municion"][letra] != "ilimitada":
            jugador["municion"][letra] = (
                jugador["municion"][letra] + BONIFICACION_MUNICION_ESTACION
            )
            otorgada[letra] = BONIFICACION_MUNICION_ESTACION
    return otorgada


def _registrar_celda_afectada(cubo, flota_objetivo, punto, resultado, estado_previo):
    """Registra en la flota un impacto producido sobre una celda."""
    if (resultado == "celda ya atacada" and estado_previo == tablero.IMPACTO
            and flota.puede_recibir_impacto(flota_objetivo, punto)):
        resultado = "impacto"

    detalle = {"punto": punto, "resultado": resultado, "nave": None}
    if resultado != "impacto":
        return detalle

    id_nave = flota.registrar_impacto(cubo, flota_objetivo, punto)
    if id_nave is None:
        return detalle

    nave = flota_objetivo[id_nave]
    detalle["id_nave"] = id_nave
    detalle["nave"] = flota.CATALOGO[nave["tipo"]]["nombre"]
    detalle["tipo_nave"] = nave["tipo"]
    detalle["impactos"] = sum(
        nave.get("danio", {}).get(celda, int(celda in nave["impactos"]))
        for celda in nave["celdas"]
    )
    detalle["celdas"] = len(nave["celdas"])
    detalle["resultado"] = "hundido" if flota.estado_nave(flota_objetivo, id_nave) == "hundida" else "impacto"
    return detalle


def _crear_resumen_disparo(jugador, letra, preparado, detalles):
    """Construye el resultado publico de un arma y sus impactos."""
    impacto = [detalle for detalle in detalles if detalle["resultado"] in ("impacto", "hundido")]
    hundidos = []
    naves_impactadas = []
    for detalle in impacto:
        if detalle["nave"] and detalle["nave"] not in naves_impactadas:
            naves_impactadas.append(detalle["nave"])
        if (detalle["resultado"] == "hundido" and detalle["nave"]
                and detalle["nave"] not in hundidos):
            hundidos.append(detalle["nave"])

    resultado = "agua"
    if preparado["tipo"] == "sonar":
        resultado = "sonar"
    elif hundidos:
        resultado = "hundido"
    elif impacto:
        resultado = "impacto"

    disparo = {
        "jugador": jugador["nombre"],
        "arma": letra,
        "objetivo": preparado.get("objetivo"),
        "resultado": resultado,
        "impactos_totales": len(impacto),
        "naves_impactadas": naves_impactadas,
        "naves_hundidas": hundidos,
        "celdas_afectadas": detalles,
    }
    if preparado["tipo"] == "sonar":
        disparo["eje"] = preparado["eje"]
        disparo["valor"] = preparado["valor"]
        disparo["contactos"] = len(preparado["contactos"])
    if len(impacto) == 1:
        disparo["nave"] = impacto[0]["nave"]
        disparo["impactos"] = impacto[0].get("impactos", 0)
        disparo["celdas"] = impacto[0].get("celdas", 0)
    return disparo


def ejecutar_turno(estado, jugada):
    """
    aplica la jugada del jugador que tiene el turno y pasa al siguiente.
    recibe el estado y una jugada con arma y objetivo; el sonar usa eje y valor.
    retorna el estado actualizado. En "ultimo_disparo" queda el resultado.
    lanza PartidaTerminada, ArmaNoDisponible, SinMunicion,
    PuntoFueraDelCubo o CeldaYaAtacada.
    En esos casos el estado no cambia y el turno no avanza.
    """
    if hay_ganador(estado) is not None:
        raise PartidaTerminada("La partida ya termino.")
    if not isinstance(jugada, dict):
        raise JugadaInvalida("La jugada debe indicar un arma y sus parametros.")

    jugador = jugador_actual(estado)
    rival = rival_actual(estado)
    letra = jugada.get("arma")

    if not isinstance(letra, str) or letra not in DISPAROS:
        raise ArmaNoDisponible("El arma elegida no esta disponible.")
    if jugador["municion"][letra] == 0:
        raise SinMunicion("No queda municion de " + armamento.obtener_arma(letra)["nombre"] + ".")
    preparado = DISPAROS[letra](rival["cubo"], rival["flota"], jugada)
    detalles = []
    revelaciones = []
    bonificaciones = {}

    if preparado["tipo"] == "sonar":
        for punto in preparado["celdas"]:
            detalles.append({"punto": punto, "resultado": "sonar", "nave": None})
    else:
        estados_previos = [tablero.obtener_celda(rival["cubo"], punto)
                           for punto in preparado["celdas"]]
        if all(estado_celda not in (tablero.AGUA_SIN_EXPLORAR,
                                    tablero.NAVE_OCULTA,
                                    tablero.DETECTADO_SONAR,
                                    tablero.IMPACTO)
               or (estado_celda == tablero.IMPACTO
                   and not flota.puede_recibir_impacto(rival["flota"], punto))
               for punto, estado_celda in zip(preparado["celdas"], estados_previos)):
            raise CeldaYaAtacada("Todas las celdas alcanzadas ya fueron atacadas.")
        resultados = armamento.aplicar_arma(rival["cubo"], preparado["celdas"])
        for punto, resultado, previo in zip(preparado["celdas"], resultados, estados_previos):
            detalle = _registrar_celda_afectada(
                rival["cubo"], rival["flota"], punto, resultado, previo
            )
            detalles.append(detalle)

            if detalle["resultado"] in ("impacto", "hundido"):
                if detalle.get("tipo_nave") == "D":
                    revelada = _revelar_celda_del_rival(jugador)
                    if revelada is not None:
                        revelaciones.append(revelada)
                if (detalle.get("tipo_nave") == "E"
                        and detalle["resultado"] == "hundido"):
                    extra = _otorgar_municion_extra(jugador)
                    for arma in extra:
                        bonificaciones[arma] = bonificaciones.get(arma, 0) + extra[arma]

    armamento.usar_municion(jugador["municion"], letra)
    disparo = _crear_resumen_disparo(jugador, letra, preparado, detalles)
    if revelaciones:
        disparo["celdas_reveladas"] = len(revelaciones)
    if bonificaciones:
        disparo["municion_extra"] = bonificaciones

    registro.agregar_evento(estado["registro"], estado["turno"], jugador["nombre"],
                            armamento.obtener_arma(letra)["nombre"], disparo["resultado"])
    estado["ultimo_disparo"] = disparo

    # Si la partida termino, el turno queda en el ganador.
    if hay_ganador(estado) is None:
        estado["actual"] = 1 - estado["actual"]
        estado["turno"] = estado["turno"] + 1

    return estado


def turno_maquina(estado):
    """
    juega el turno de la maquina que tiene el turno.
    recibe el estado de la partida.
    retorna el estado actualizado.
    lanza JugadaInvalida si el jugador que tiene el turno no es una maquina.
    """
    maquina = jugador_actual(estado)
    if maquina["tipo"] != "maquina":
        raise JugadaInvalida("No es el turno de la maquina.")

    rival = rival_actual(estado)
    elegir_objetivo = DIFICULTADES[maquina["dificultad"]]
    objetivo = elegir_objetivo(rival["cubo"], rival["flota"])
    return ejecutar_turno(estado, {"arma": "T", "objetivo": objetivo})


def hay_ganador(estado):
    """
    recibe el estado de la partida.
    retorna el nombre del ganador, o None si la partida sigue.
    """
    jugadores = estado["jugadores"]
    for i in range(2):
        flota_rival = jugadores[1 - i]["flota"]
        if flota_rival and flota.flota_hundida(flota_rival):
            return jugadores[i]["nombre"]
    return None


# ---------------------------------------------------------------
# Entrada y salida
# ---------------------------------------------------------------

def leer_opcion(opciones):
    """
    pide una opcion de menu hasta que sea valida.
    recibe un diccionario cuyas claves son las opciones ("1", "2"...).
    retorna la opcion elegida.
    """
    patron = "^[" + "".join(opciones) + "]$"
    texto = input("Opcion: ").strip()

    while re.match(patron, texto) is None:
        print("Opcion invalida. Intente de nuevo.")
        texto = input("Opcion: ").strip()

    return texto


def leer_letra_nave(pendientes):
    """
    pide la letra de una nave hasta que sea valida y queden naves de ese tipo.
    recibe el diccionario de naves pendientes.
    retorna la letra en mayuscula.
    """
    texto = input("Nave (F/D/S/C/P/E): ").strip().upper()

    while texto not in pendientes or pendientes[texto] == 0:
        print("Nave invalida. Intente de nuevo.")
        texto = input("Nave (F/D/S/C/P/E): ").strip().upper()

    return texto


def leer_tramo():
    """
    pide un tramo con el formato z,x,y-z,x,y hasta que el formato sea valido.
    retorna dos tuplas: el punto desde y el punto hasta.
    """
    patron = "^" + PATRON_PUNTO + "-" + PATRON_PUNTO + "$"
    texto = input("Desde-hasta: ").strip()
    coincidencia = re.match(patron, texto)

    while coincidencia is None:
        print("Formato invalido. Ejemplo: 3,5,4-3,5,5")
        texto = input("Desde-hasta: ").strip()
        coincidencia = re.match(patron, texto)

    desde = (int(coincidencia.group(1)), int(coincidencia.group(2)), int(coincidencia.group(3)))
    hasta = (int(coincidencia.group(4)), int(coincidencia.group(5)), int(coincidencia.group(6)))

    return desde, hasta


def leer_punto(mensaje):
    """
    pide un punto con el formato z,x,y hasta que el formato sea valido.
    recibe el mensaje que se muestra al pedirlo.
    retorna una tupla (z, x, y).
    """
    patron = "^" + PATRON_PUNTO + "$"
    texto = input(mensaje).strip()
    coincidencia = re.match(patron, texto)

    while coincidencia is None:
        print("Formato invalido. Ejemplo: 4,2,7")
        texto = input(mensaje).strip()
        coincidencia = re.match(patron, texto)

    return (int(coincidencia.group(1)), int(coincidencia.group(2)), int(coincidencia.group(3)))


def leer_arma():
    """
    pide la letra de un arma del catalogo hasta que sea valida.
    retorna la letra en mayuscula.
    """
    letras = "".join(armamento.obtener_catalogo())
    patron = "^[" + letras + "]$"
    mensaje = "Arma (" + "/".join(letras) + "): "
    texto = input(mensaje).strip().upper()

    while re.match(patron, texto) is None:
        print("Arma invalida. Intente de nuevo.")
        texto = input(mensaje).strip().upper()

    return texto


def leer_eje(mensaje, ejes):
    """Pide un eje permitido y devuelve su letra en minuscula."""
    permitidos = tuple(ejes)
    texto = input(mensaje).strip().lower()
    while texto not in permitidos:
        print("Eje invalido. Opciones: " + "/".join(permitidos) + ".")
        texto = input(mensaje).strip().lower()
    return texto


def leer_valor_plano(mensaje):
    """Pide un numero de plano entre 1 y el tamanio del cubo."""
    texto = input(mensaje).strip()
    while re.match(r"^\d+$", texto) is None or not 1 <= int(texto) <= TAMANIO:
        print("Plano invalido. Ingrese un numero entre 1 y " + str(TAMANIO) + ".")
        texto = input(mensaje).strip()
    return int(texto)


def leer_dificultad(nombre="maquina"):
    """Pide uno de los niveles de dificultad disponibles."""
    opciones = {"1": "facil", "2": "dificil"}
    print("Dificultad de " + nombre + ":")
    print("1 - Facil")
    print("2 - Dificil")
    return opciones[leer_opcion(opciones)]


def confirmar(pregunta):
    """
    hace una pregunta de si o no hasta que la respuesta sea valida.
    recibe el texto de la pregunta.
    retorna True si la respuesta es s.
    """
    texto = input(pregunta + " (s/n): ").strip().lower()

    while re.match("^[sn]$", texto) is None:
        print("Responda s o n.")
        texto = input(pregunta + " (s/n): ").strip().lower()

    return texto == "s"


def texto_punto(punto):
    """recibe una tupla (z, x, y). retorna el texto z,x,y."""
    return str(punto[0]) + "," + str(punto[1]) + "," + str(punto[2])


# Mensaje que se muestra segun el resultado del disparo.
MENSAJES = {
    "agua": "Agua.",
    "impacto": "Impacto. Nave averiada: {nave} ({impactos} de {celdas}).",
    "hundido": "Impacto. Nave hundida: {nave}.",
}


def describir_disparo(disparo):
    """
    recibe el diccionario del ultimo disparo.
    retorna el texto que describe el resultado.
    """
    if disparo["resultado"] == "sonar":
        cantidad = disparo["contactos"]
        nombre = "celda detectada" if cantidad == 1 else "celdas detectadas"
        mensaje = ("Sonar en el plano " + disparo["eje"] + "="
                   + str(disparo["valor"]) + ": " + str(cantidad) + " "
                   + nombre + ".")
    elif disparo.get("impactos_totales", 0) > 1:
        mensaje = "Impactos en " + str(disparo["impactos_totales"]) + " celdas."
        hundidas = disparo.get("naves_hundidas", [])
        if hundidas:
            mensaje += " Naves hundidas: " + ", ".join(hundidas) + "."
    else:
        mensaje = MENSAJES[disparo["resultado"]].format(**disparo)

    if disparo.get("celdas_reveladas", 0):
        mensaje += " El destructor rival revelo una celda de tu flota."
    if disparo.get("municion_extra"):
        extra = []
        for arma, cantidad in disparo["municion_extra"].items():
            extra.append(arma + ": +" + str(cantidad))
        mensaje += " Estacion orbital hundida; municion extra (" + ", ".join(extra) + ")."
    return mensaje


def dibujar_estado(nombre, cubo, mostrar_naves=True):
    """
    muestra el cubo de un jugador por capas de z, con encabezados de x y de y.
    recibe el nombre del jugador, su cubo y si se muestran las naves ocultas.
    """
    tamanio = len(cubo)
    print("\nCubo de " + nombre)

    for z in range(1, tamanio + 1):
        print("========= CAPA z = " + str(z) + " =========")
        print(tablero.crear_plano_z(cubo, z, mostrar_naves=mostrar_naves), end="")

    print("Referencias: ~ agua   N nave   o agua marcada   X impacto   # hundido   ? sonar")


def mostrar_pendientes(pendientes):
    """
    muestra las naves que faltan ubicar, en el orden de la consigna.
    recibe el diccionario de naves pendientes.
    retorna la cantidad total de naves que faltan.
    """
    texto = "Pendientes:"
    total = 0
    for letra in "FDSCPE":
        if pendientes[letra] > 0:
            texto = texto + " " + letra + " x" + str(pendientes[letra])
            total = total + pendientes[letra]

    if total > 0:
        print(texto)
    else:
        print("Flota completa.")
    return total


def ubicacion_manual(cubo, mi_flota):
    """
    pide nave por nave hasta ubicar la flota completa.
    recibe el cubo y la flota del jugador, y los modifica.
    retorna la flota completa.
    """
    pendientes = flota.naves_pendientes(mi_flota)

    while mostrar_pendientes(pendientes) > 0:
        letra = leer_letra_nave(pendientes)
        desde, hasta = leer_tramo()

        if flota.ubicar_nave(cubo, mi_flota, letra, desde, hasta):
            print("Ubicada.")
        else:
            print("No se puede ubicar ahi. Intente de nuevo.")

        pendientes = flota.naves_pendientes(mi_flota)

    return mi_flota


def ubicacion_al_azar(cubo, mi_flota):
    """
    ubica la flota completa en forma automatica.
    recibe el cubo (lo modifica) y la flota del jugador.
    retorna la flota completa.
    """
    semilla = random.randint(1, 1000000)
    print("Flota ubicada automaticamente.")
    return flota.ubicacion_automatica(cubo, flota.CATALOGO, semilla)


# Opciones del submenu de ubicacion: numero -> (texto, funcion).
MENU_UBICACION = {
    "1": ("Ubicacion manual", ubicacion_manual),
    "2": ("Ubicacion automatica", ubicacion_al_azar),
}


def submenu_ubicacion(nombre):
    """
    muestra el submenu de ubicacion de la flota de un jugador.
    recibe el nombre del jugador.
    retorna el cubo y la flota del jugador ya ubicada.
    """
    cubo = tablero.crear_cubo(TAMANIO)
    mi_flota = {}

    print("\n--- Flota de " + nombre + " ---")
    for opcion in MENU_UBICACION:
        print(opcion + " - " + MENU_UBICACION[opcion][0])
    opcion = leer_opcion(MENU_UBICACION)
    mi_flota = MENU_UBICACION[opcion][1](cubo, mi_flota)

    return cubo, mi_flota


def flota_maquina(nombre):
    """
    crea el cubo de la maquina y ubica su flota en forma automatica.
    recibe el nombre de la maquina.
    retorna el cubo y la flota.
    """
    cubo = tablero.crear_cubo(TAMANIO)
    print("\n--- Flota de " + nombre + " ---")
    mi_flota = ubicacion_al_azar(cubo, {})
    return cubo, mi_flota


def opcion_disparar(estado):
    """
    pide arma y objetivo hasta que el disparo sea valido y muestra el resultado.
    recibe el estado de la partida.
    retorna True porque el turno termina.
    """
    disparo_hecho = False

    while not disparo_hecho:
        letra = leer_arma()
        if letra == "S":
            eje = leer_eje("Eje del plano (z/x/y): ", ("z", "x", "y"))
            jugada = {"arma": letra, "eje": eje,
                      "valor": leer_valor_plano("Numero del plano: ")}
        else:
            jugada = {"arma": letra, "objetivo": leer_punto("Objetivo (z,x,y): ")}
            if letra == "L":
                jugada["eje"] = leer_eje("Eje del barrido (x/y): ", ("x", "y"))
        try:
            ejecutar_turno(estado, jugada)
        except JugadaInvalida as error:
            print(str(error) + " Intente de nuevo.")
        else:
            disparo_hecho = True

    print(describir_disparo(estado["ultimo_disparo"]))
    return True


def opcion_ver_cubo(estado):
    """
    muestra el cubo propio con las naves y el del rival con los disparos hechos.
    recibe el estado de la partida.
    retorna False porque el turno sigue.
    """
    jugador = jugador_actual(estado)
    rival = rival_actual(estado)
    dibujar_estado(jugador["nombre"] + " (tu flota)", jugador["cubo"])
    dibujar_estado(rival["nombre"] + " (tus disparos)", rival["cubo"], mostrar_naves=False)
    return False


MENU_RECORRIDOS = {
    "1": ("Iterativo z, x, y", tablero.recorrido_zxy),
    "2": ("Recursivo y, x, z", tablero.recorrido_recursivo_yxz),
    "3": ("Recursivo x, y, z", tablero.recorrido_recursivo_xyz),
}


def opcion_recorrer_cubo(estado):
    """Permite elegir y muestra una de las tres formas de recorrer el cubo."""
    print("Recorridos del cubo:")
    for opcion, (nombre, _) in MENU_RECORRIDOS.items():
        print(opcion + " - " + nombre)
    seleccion = leer_opcion(MENU_RECORRIDOS)
    puntos = MENU_RECORRIDOS[seleccion][1](jugador_actual(estado)["cubo"])
    for indice, punto in enumerate(puntos, 1):
        print(texto_punto(punto), end="\n" if indice % 8 == 0 else " | ")
    if len(puntos) % 8:
        print()
    return False


def _pedir_nombre_y_guardar(estado, mensaje):
    """Pide un nombre válido y reintenta si ya existe o no cumple el patrón."""
    while True:
        nombre = input(mensaje).strip()
        try:
            return registro.guardar_partida(estado, nombre)
        except (ValueError, FileExistsError) as error:
            print(str(error) + " Intente con otro nombre.")


def opcion_guardar_y_salir(estado):
    """Guarda el estado actual y vuelve al menu principal sin disparar."""
    ruta = _pedir_nombre_y_guardar(estado, "Nombre para guardar la partida: ")
    estado["_guardar_y_salir"] = True
    print("Partida guardada en " + str(ruta) + ".")
    return True


# Menu del turno: numero -> (texto, funcion). La funcion retorna True si el turno termino.
MENU_TURNO = {
    "1": ("Disparar", opcion_disparar),
    "2": ("Ver el cubo", opcion_ver_cubo),
    "3": ("Guardar y salir", opcion_guardar_y_salir),
    "4": ("Recorrer el cubo", opcion_recorrer_cubo),
}


def jugar_turno_humano(estado):
    """
    muestra el menu del turno hasta que el jugador dispara.
    recibe el estado de la partida.
    """
    turno_terminado = False
    while not turno_terminado:
        for opcion in MENU_TURNO:
            print(opcion + " - " + MENU_TURNO[opcion][0])
        opcion = leer_opcion(MENU_TURNO)
        turno_terminado = MENU_TURNO[opcion][1](estado)


def jugar_turno_maquina(estado):
    """
    juega el turno de la maquina y muestra a donde disparo.
    recibe el estado de la partida.
    """
    turno_maquina(estado)
    disparo = estado["ultimo_disparo"]
    print("Dispara a " + texto_punto(disparo["objetivo"]) + ". " + describir_disparo(disparo))


# Como se juega el turno segun el tipo de jugador.
TURNOS = {
    "humano": jugar_turno_humano,
    "maquina": jugar_turno_maquina,
}


def mostrar_resumen(estado, ganador):
    """
    muestra el resultado final y las estadisticas de la partida.
    recibe el estado y el nombre del ganador (None si la partida no termino).
    """
    resumen = registro.crear_resumen(estado["registro"], ganador)

    print("\n===== FIN DE LA PARTIDA =====")
    if ganador is None:
        print("La partida quedo sin terminar.")
    else:
        print("Gano " + ganador + "!")
    print("Disparos: " + str(resumen["total_eventos"])
          + " | Impactos: " + str(resumen["impactos"])
          + " | Agua: " + str(resumen["agua"])
          + " | Hundidos: " + str(resumen["hundidos"]))


def jugar(estado, confirmar_inicio=True):
    """
    pide confirmacion y alterna turnos hasta que alguien hunde la flota rival.
    recibe el estado inicial de la partida.
    """
    if confirmar_inicio and not confirmar("Flotas listas. Iniciar la partida?"):
        print("Partida cancelada.")
        return

    ganador = None
    estado.pop("_guardar_y_salir", None)
    try:
        while ganador is None and not estado.get("_guardar_y_salir", False):
            jugador = jugador_actual(estado)
            print("\n--- Turno de " + jugador["nombre"] + " ---")
            TURNOS[jugador["tipo"]](estado)
            ganador = hay_ganador(estado)
    finally:
        if not estado.get("_guardar_y_salir", False):
            # Se muestra el resumen aunque la partida se corte (por ejemplo con Ctrl+C).
            mostrar_resumen(estado, ganador)

    if (ganador is not None and sys.stdin.isatty()
            and confirmar("Guardar el resultado de la partida?")):
        ruta = _pedir_nombre_y_guardar(estado, "Nombre para el registro: ")
        print("Resultado guardado en " + str(ruta) + ".")


def partida_1v1():
    """Ubica las flotas de los dos jugadores y juega la partida."""
    cubo1, flota1 = submenu_ubicacion("Jugador 1")
    cubo2, flota2 = submenu_ubicacion("Jugador 2")

    configuracion = {"jugadores": [
        {"nombre": "Jugador 1", "cubo": cubo1, "flota": flota1},
        {"nombre": "Jugador 2", "cubo": cubo2, "flota": flota2},
    ]}
    jugar(nueva_partida_1v1(configuracion))
    return True


def partida_vs_maquina():
    """Ubica la flota del jugador y la de la maquina, y juega la partida."""
    cubo1, flota1 = submenu_ubicacion("Jugador 1")
    cubo2, flota2 = flota_maquina("Maquina")

    configuracion = {"jugadores": [
        {"nombre": "Jugador 1", "cubo": cubo1, "flota": flota1},
        {"nombre": "Maquina", "cubo": cubo2, "flota": flota2},
    ]}
    dificultad = leer_dificultad("la maquina")
    jugar(nueva_partida_vs_maquina(configuracion, dificultad))
    return True


def partida_maquina_vs_maquina():
    """Ubica las flotas de las dos maquinas y ejecuta la partida completa."""
    cubo1, flota1 = flota_maquina("Maquina 1")
    cubo2, flota2 = flota_maquina("Maquina 2")
    configuracion = {"jugadores": [
        {"nombre": "Maquina 1", "cubo": cubo1, "flota": flota1},
        {"nombre": "Maquina 2", "cubo": cubo2, "flota": flota2},
    ]}
    dificultades = [
        leer_dificultad("Maquina 1"),
        leer_dificultad("Maquina 2"),
    ]
    jugar(nueva_partida_maquina_vs_maquina(configuracion, dificultades),
          confirmar_inicio=False)
    return True


def continuar_partida():
    """Lista las partidas guardadas y permite continuar una de ellas."""
    partidas = [p for p in registro.obtener_detalle_partidas() if p["ganador"] is None]
    if not partidas:
        print("No hay partidas guardadas.")
        return True

    opciones = {}
    print("\n--- Partidas guardadas ---")
    for indice, partida in enumerate(partidas, 1):
        clave = str(indice)
        opciones[clave] = partida
        print(clave + " - " + partida["nombre"] + " | turno "
              + str(partida["turno"]) + " | " + str(partida["fecha"]))
    print("0 - Volver")
    opciones["0"] = None
    seleccion = input("Opcion: ").strip()
    while seleccion not in opciones:
        print("Opcion invalida. Intente de nuevo.")
        seleccion = input("Opcion: ").strip()
    if seleccion == "0":
        return True

    estado = registro.cargar_partida(opciones[seleccion]["nombre"])
    print("Partida cargada.")
    jugar(estado, confirmar_inicio=False)
    return True


def listar_partidas_guardadas():
    """Muestra los resúmenes de las partidas almacenadas."""
    partidas = registro.obtener_detalle_partidas()
    if not partidas:
        print("No hay partidas guardadas.")
        return True
    for partida in partidas:
        ganador = partida["ganador"] or "En curso"
        jugadores = " vs. ".join(j for j in partida["jugadores"] if j)
        print(partida["nombre"] + " | " + jugadores + " | " + ganador
              + " | turno " + str(partida["turno"]) + " | " + str(partida["fecha"]))
    return True


def exportar_partidas_guardadas():
    """Exporta los resúmenes guardados a un archivo CSV."""
    destino = input("Archivo CSV (Enter para partidas_exportadas.csv): ").strip()
    if not destino:
        destino = "partidas_exportadas.csv"
    ruta = registro.exportar_partidas(destino)
    print("Partidas exportadas a " + str(ruta) + ".")
    return True


def mostrar_ranking():
    """Muestra el ranking de victorias de las partidas guardadas."""
    ranking = registro.obtener_ranking()
    if not ranking:
        print("Todavia no hay resultados para mostrar.")
        return True
    print("\n--- Ranking ---")
    for posicion, datos in enumerate(ranking, 1):
        print(str(posicion) + ". " + datos["jugador"] + " | "
              + str(datos["victorias"]) + " victorias | "
              + str(datos["partidas"]) + " partidas")
    return True


def submenu_registros():
    """Ofrece el listado, la exportación y el ranking de partidas guardadas."""
    opciones = {
        "1": ("Listar partidas guardadas", listar_partidas_guardadas),
        "2": ("Exportar partidas a CSV", exportar_partidas_guardadas),
        "3": ("Ver ranking", mostrar_ranking),
        "4": ("Volver", None),
    }
    volver = False
    while not volver:
        print("\n--- Registro de partidas ---")
        for opcion, (texto, _) in opciones.items():
            print(opcion + " - " + texto)
        seleccion = leer_opcion(opciones)
        if seleccion == "4":
            volver = True
        else:
            opciones[seleccion][1]()
    return True


def salir():
    """Termina el programa."""
    print("Hasta luego.")
    return False


MENU_PRINCIPAL = {
    "1": ("Partida uno contra uno", partida_1v1),
    "2": ("Partida uno contra la maquina", partida_vs_maquina),
    "3": ("Partida maquina contra maquina", partida_maquina_vs_maquina),
    "4": ("Continuar una partida guardada", continuar_partida),
    "5": ("Salir", salir),
    "6": ("Registro, exportacion y ranking", submenu_registros),
}


def menu_principal():
    """
    muestra el menu principal hasta que se elija salir.
    ningun error corta el programa: se avisa y se vuelve al menu.
    """
    seguir = True
    while seguir:
        print("\n===== OPERACION CUBO =====")
        for opcion in MENU_PRINCIPAL:
            print(opcion + " - " + MENU_PRINCIPAL[opcion][0])
        opcion = leer_opcion(MENU_PRINCIPAL)

        try:
            seguir = MENU_PRINCIPAL[opcion][1]()
        except ErrorOperacionCubo as error:
            print("Error: " + str(error))
        except EOFError:
            # Se cerro la entrada (por ejemplo con Ctrl+D): no hay forma de seguir pidiendo datos.
            seguir = False
        except Exception as error:
            print("Ocurrio un error inesperado: " + str(error))


if __name__ == "__main__":
    menu_principal()

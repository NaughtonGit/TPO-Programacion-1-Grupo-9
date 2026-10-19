import re
import random
import tablero
import flota
import armamento
import registro
from errores import (
    ErrorOperacionCubo,
    ConfiguracionInvalida,
    JugadaInvalida,
    ArmaNoDisponible,
    SinMunicion,
    PuntoFueraDelCubo,
    CeldaYaAtacada
)

TAMANIO = 8

PATRON_PUNTO = r"(\d{1,2}),(\d{1,2}),(\d{1,2})"


# ---------------------------------------------------------------
# Logica de la partida (sin print ni input)
# ---------------------------------------------------------------

# Armas que ya se pueden disparar: letra -> funcion que aplica el disparo.
# Cuando armamento sume armas nuevas, se agregan aca.
DISPAROS = {
    "T": armamento.aplicar_torpedo,
}


def elegir_al_azar(cubo):
    """
    elige al azar una celda del cubo que todavia no recibio disparos.
    recibe el cubo del rival.
    retorna una tupla (z, x, y).
    """
    libres = []
    n = len(cubo)

    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                estado_celda = tablero.obtener_celda(cubo, (z, x, y))
                if estado_celda == tablero.AGUA_SIN_EXPLORAR or estado_celda == tablero.NAVE_OCULTA:
                    libres.append((z, x, y))

    return random.choice(libres)


# Niveles de la maquina: nombre -> funcion que elige el objetivo.
# El segundo nivel corresponde a la entrega 3.
DIFICULTADES = {
    "facil": elegir_al_azar,
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


def jugador_actual(estado):
    """recibe el estado. retorna el jugador que tiene el turno."""
    return estado["jugadores"][estado["actual"]]


def rival_actual(estado):
    """recibe el estado. retorna el rival del jugador que tiene el turno."""
    return estado["jugadores"][1 - estado["actual"]]


def ejecutar_turno(estado, jugada):
    """
    aplica la jugada del jugador que tiene el turno y pasa al siguiente.
    recibe el estado y la jugada: {"arma": letra, "objetivo": (z, x, y)}.
    retorna el estado actualizado. En "ultimo_disparo" queda el resultado.
    lanza ArmaNoDisponible, SinMunicion, PuntoFueraDelCubo o CeldaYaAtacada.
    En esos casos el estado no cambia y el turno no avanza.
    """
    jugador = jugador_actual(estado)
    rival = rival_actual(estado)
    letra = jugada["arma"]
    punto = jugada["objetivo"]

    if letra not in DISPAROS:
        raise ArmaNoDisponible("El arma " + letra + " todavia no esta disponible.")
    if jugador["municion"][letra] == 0:
        raise SinMunicion("No queda municion de " + armamento.obtener_arma(letra)["nombre"] + ".")
    if not tablero.validar_punto(rival["cubo"], punto):
        raise PuntoFueraDelCubo("El objetivo esta fuera del cubo.")

    resultado = DISPAROS[letra](rival["cubo"], punto)
    if resultado == "celda ya atacada":
        raise CeldaYaAtacada("Esa celda ya fue atacada.")

    disparo = {
        "jugador": jugador["nombre"],
        "arma": letra,
        "objetivo": punto,
        "resultado": resultado,
        "nave": None,
    }

    if resultado == "impacto":
        id_nave = flota.registrar_impacto(rival["cubo"], rival["flota"], punto)
        nave = rival["flota"][id_nave]
        disparo["nave"] = flota.CATALOGO[nave["tipo"]]["nombre"]
        disparo["impactos"] = len(nave["impactos"])
        disparo["celdas"] = len(nave["celdas"])

        if flota.estado_nave(rival["flota"], id_nave) == "hundida":
            disparo["resultado"] = "hundido"

    if jugador["municion"][letra] != "ilimitada":
        jugador["municion"][letra] = jugador["municion"][letra] - 1

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

    elegir_objetivo = DIFICULTADES[maquina["dificultad"]]
    objetivo = elegir_objetivo(rival_actual(estado)["cubo"])
    return ejecutar_turno(estado, {"arma": "T", "objetivo": objetivo})


def hay_ganador(estado):
    """
    recibe el estado de la partida.
    retorna el nombre del ganador, o None si la partida sigue.
    """
    jugadores = estado["jugadores"]
    for i in range(2):
        if flota.flota_hundida(jugadores[1 - i]["flota"]):
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
    return MENSAJES[disparo["resultado"]].format(**disparo)


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
        jugada = {"arma": leer_arma(), "objetivo": leer_punto("Objetivo: ")}
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


def opcion_guardar_y_salir(estado):
    """Todavia no disponible. Retorna False porque el turno sigue."""
    print("Opcion disponible en una proxima entrega.")
    return False


# Menu del turno: numero -> (texto, funcion). La funcion retorna True si el turno termino.
MENU_TURNO = {
    "1": ("Disparar", opcion_disparar),
    "2": ("Ver el cubo", opcion_ver_cubo),
    "3": ("Guardar y salir", opcion_guardar_y_salir),
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


def jugar(estado):
    """
    pide confirmacion y alterna turnos hasta que alguien hunde la flota rival.
    recibe el estado inicial de la partida.
    """
    if not confirmar("Flotas listas. Iniciar la partida?"):
        print("Partida cancelada.")
        return

    ganador = None
    try:
        while ganador is None:
            jugador = jugador_actual(estado)
            print("\n--- Turno de " + jugador["nombre"] + " ---")
            TURNOS[jugador["tipo"]](estado)
            ganador = hay_ganador(estado)
    finally:
        # Se muestra el resumen aunque la partida se corte (por ejemplo con Ctrl+C).
        mostrar_resumen(estado, ganador)


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
    jugar(nueva_partida_vs_maquina(configuracion, "facil"))
    return True


def partida_maquina_vs_maquina():
    """Ubica las flotas de las dos maquinas y dibuja el estado."""
    cubo1, flota1 = flota_maquina("Maquina 1")
    cubo2, flota2 = flota_maquina("Maquina 2")
    dibujar_estado("Maquina 1", cubo1)
    dibujar_estado("Maquina 2", cubo2)
    return True


def continuar_partida():
    """Todavia no disponible."""
    print("Opcion disponible en una proxima entrega.")
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
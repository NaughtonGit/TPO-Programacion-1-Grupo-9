from tablero import (
    obtener_celda,
    cambiar_celda,
    validar_punto,
    obtener_vecinos,
    AGUA_SIN_EXPLORAR,
    NAVE_OCULTA,
    AGUA_MARCADA,
    IMPACTO,
    DETECTADO_SONAR
)
from flota import estado_nave

# Radio con el que se propaga la onda expansiva si no se indica otro.
RADIO_ONDA = 1

# Catalogo de armas disponibles.
# Cada arma tiene una letra, un nombre y su cantidad inicial de municion.
ARMAS = {
    "T": {
        "nombre": "Torpedo",
        "municion": "ilimitada"
    },
    "R": {
        "nombre": "Misil de racimo",
        "municion": 3
    },
    "C": {
        "nombre": "Carga de profundidad",
        "municion": 2
    },
    "S": {
        "nombre": "Sonar",
        "municion": 4
    },
    "L": {
        "nombre": "Barrido laser",
        "municion": 2
    },
    "O": {
        "nombre": "Onda expansiva",
        "municion": 1
    },
    "G": {
        "nombre": "Torpedo guiado",
        "municion": 1
    }
}


def obtener_arma(letra):
    """
    Recibe la letra de un arma.
    Devuelve los datos del arma correspondiente.
    Lanza ValueError si el arma no existe.
    """
    # Verifica que la letra ingresada exista en el catalogo.
    if letra not in ARMAS:
        raise ValueError("Arma invalida")

    return ARMAS[letra]


def obtener_catalogo():
    """
    No recibe parametros.
    Devuelve el catalogo completo de armas.
    """
    return ARMAS


def celdas_torpedo(punto):
    """
    Recibe un punto [z, x, y].
    Devuelve una lista con la unica celda afectada por el torpedo.
    """
    return [punto]


def aplicar_torpedo(cubo, punto):
    """
    Recibe un cubo y un punto [z, x, y].
    Aplica un torpedo sobre la celda indicada.
    Devuelve "impacto" si encuentra una nave,
    "agua" si no encuentra una nave o
    "celda ya atacada" si la celda ya fue utilizada.
    """
    # Obtiene el estado actual de la celda antes de disparar.
    estado = obtener_celda(cubo, punto)

    # Si hay una nave oculta o detectada por el sonar, la celda pasa a ser un impacto.
    if estado == NAVE_OCULTA or estado == DETECTADO_SONAR:
        cambiar_celda(cubo, punto, IMPACTO)
        return "impacto"

    # Si hay agua sin explorar, la celda queda marcada como agua.
    if estado == AGUA_SIN_EXPLORAR:
        cambiar_celda(cubo, punto, AGUA_MARCADA)
        return "agua"
    
    # Si no era agua sin explorar ni una nave oculta,
    return "celda ya atacada"

def celdas_racimo(cubo, punto):
    """
    Recibe un cubo y un punto [z, x, y].
    Devuelve una lista con la celda apuntada y sus vecinas ortogonales
    (las que quedan fuera del cubo no se incluyen).
    Lanza ValueError si el punto es invalido.
    """
    # obtener_vecinos ya valida el punto.
    return [tuple(punto)] + obtener_vecinos(cubo, punto)


def celdas_carga_profundidad(cubo, punto):
    """
    Recibe un cubo y un punto [z, x, y].
    Devuelve una lista con toda la recta sobre el eje z que pasa por el punto.
    Lanza ValueError si el punto es invalido.
    """
    if not validar_punto(cubo, punto):
        raise ValueError("Punto invalido")

    celdas = []

    for z in range(1, len(cubo) + 1):
        celdas.append((z, punto[1], punto[2]))

    return celdas


def celdas_barrido_laser(cubo, flota, punto, eje):
    """
    Recibe un cubo, la flota atacada, un punto [z, x, y] y el eje ("x" o "y").
    Devuelve una lista con la recta completa sobre ese eje que pasa por el punto.
    Las celdas de los submarinos no se incluyen: el laser no los alcanza.
    Lanza ValueError si el punto es invalido o el eje no es "x" ni "y".
    """
    if not validar_punto(cubo, punto):
        raise ValueError("Punto invalido")

    if eje != "x" and eje != "y":
        raise ValueError("El barrido laser va sobre el eje x o el eje y")

    # Junta las celdas de todos los submarinos.
    submarinos = set()
    for id_nave in flota:
        if flota[id_nave]["tipo"] == "S":
            submarinos = submarinos | flota[id_nave]["celdas"]

    celdas = []

    for valor in range(1, len(cubo) + 1):
        if eje == "x":
            celda = (punto[0], valor, punto[2])
        else:
            celda = (punto[0], punto[1], valor)

        if celda not in submarinos:
            celdas.append(celda)

    return celdas


def _propagar_onda(cubo, punto, radio, alcanzadas):
    """
    Recibe un cubo, un punto, el radio que le queda a la onda y el diccionario
    de celdas alcanzadas (celda -> mayor radio con el que se llego a ella).
    Agrega el punto y se llama a si misma sobre cada vecina ortogonal con un
    radio menor en 1. Corta cuando el radio se agota o cuando la celda ya fue
    alcanzada con un radio igual o mayor.
    No devuelve nada: modifica alcanzadas.
    """
    # Si ya se llego aca con igual o mas radio, no hay nada nuevo que propagar.
    if punto in alcanzadas and alcanzadas[punto] >= radio:
        return

    alcanzadas[punto] = radio

    # Caso base: sin radio, la onda no sigue avanzando.
    if radio == 0:
        return

    for vecino in obtener_vecinos(cubo, punto):
        _propagar_onda(cubo, vecino, radio - 1, alcanzadas)


def celdas_onda_expansiva(cubo, punto, radio=RADIO_ONDA):
    """
    Recibe un cubo, un punto [z, x, y] y el radio de la onda (por defecto RADIO_ONDA).
    Devuelve una lista con las celdas que alcanza la onda: la apuntada primero y
    luego las que la onda va tocando al propagarse, en forma recursiva, por las
    vecinas ortogonales con radio decreciente. No hay celdas repetidas y las que
    quedan fuera del cubo no se incluyen.
    Lanza ValueError si el punto es invalido o el radio no es un entero mayor o igual a 0.
    """
    if not validar_punto(cubo, punto):
        raise ValueError("Punto invalido")

    if type(radio) != int or radio < 0:
        raise ValueError("Radio invalido")

    alcanzadas = {}
    _propagar_onda(cubo, tuple(punto), radio, alcanzadas)

    return list(alcanzadas)


def _buscar_celda_contigua(cubo, celdas_nave, actual, visitadas):
    """
    Recibe un cubo, el conjunto de celdas de una nave, la celda desde la que se
    busca y el conjunto de celdas ya visitadas.
    Recorre en forma recursiva las celdas contiguas de la misma nave hasta
    encontrar una que todavia no recibio un disparo (nave oculta o detectada
    por el sonar).
    Devuelve esa celda como tupla, o None si no queda ninguna en la nave.
    """
    for vecino in obtener_vecinos(cubo, actual):
        if vecino in celdas_nave and vecino not in visitadas:
            visitadas.add(vecino)

            estado = obtener_celda(cubo, vecino)
            if estado == NAVE_OCULTA or estado == DETECTADO_SONAR:
                return vecino

            # Esta celda ya fue impactada: se sigue la busqueda desde ella.
            encontrada = _buscar_celda_contigua(cubo, celdas_nave, vecino, visitadas)
            if encontrada is not None:
                return encontrada

    return None


def celdas_torpedo_guiado(cubo, flota, punto):
    """
    Recibe un cubo, la flota atacada y un punto [z, x, y].
    Si hay un impacto previo sobre una nave no hundida, busca en forma
    recursiva una celda contigua de esa nave que todavia no fue atacada y
    devuelve una lista con esa unica celda.
    Si no hay impacto previo sobre una nave no hundida (o no queda ninguna
    celda por atacar en ellas), actua como un torpedo comun y devuelve
    una lista con el punto apuntado.
    Lanza ValueError si el punto es invalido.
    """
    if not validar_punto(cubo, punto):
        raise ValueError("Punto invalido")

    for id_nave in flota:
        nave = flota[id_nave]

        # Solo sirven las naves ya impactadas que todavia no se hundieron.
        if len(nave["impactos"]) == 0 or estado_nave(flota, id_nave) == "hundida":
            continue

        # Se ordena para que el resultado no dependa del orden del conjunto.
        for impacto in sorted(nave["impactos"]):
            encontrada = _buscar_celda_contigua(cubo, nave["celdas"], impacto, {impacto})
            if encontrada is not None:
                return [encontrada]

    return [tuple(punto)]


def aplicar_arma(cubo, celdas):
    """
    Recibe un cubo y la lista de celdas que afecta un arma.
    Aplica un disparo sobre cada celda, igual que el torpedo.
    Devuelve una lista con el resultado de cada celda ("impacto", "agua"
    o "celda ya atacada"), en el mismo orden que las celdas.
    """
    resultados = []

    for celda in celdas:
        resultados.append(aplicar_torpedo(cubo, celda))

    return resultados


def crear_municion():
    """
    No recibe parametros.
    Devuelve un diccionario con la municion inicial de cada arma, por su letra.
    Cada jugador tiene el suyo.
    """
    municion = {}

    for letra in ARMAS:
        municion[letra] = ARMAS[letra]["municion"]

    return municion


def usar_municion(municion, letra):
    """
    Recibe la municion del jugador y la letra del arma.
    Descuenta un disparo de esa arma. El torpedo es ilimitado y no se descuenta.
    Lanza ValueError si el arma no existe o no le queda municion.
    """
    if letra not in municion:
        raise ValueError("Arma invalida")

    if municion[letra] == "ilimitada":
        return

    if municion[letra] <= 0:
        raise ValueError("No queda municion de " + ARMAS[letra]["nombre"])

    municion[letra] = municion[letra] - 1
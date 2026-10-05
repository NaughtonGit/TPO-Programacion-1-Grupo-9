from tablero import (
    obtener_celda,
    cambiar_celda,
    AGUA_SIN_EXPLORAR,
    NAVE_OCULTA,
    AGUA_MARCADA,
    IMPACTO
)

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

    # Si hay una nave oculta, la celda pasa a ser un impacto.
    if estado == NAVE_OCULTA:
        cambiar_celda(cubo, punto, IMPACTO)
        return "impacto"

    # Si hay agua sin explorar, la celda queda marcada como agua.
    if estado == AGUA_SIN_EXPLORAR:
        cambiar_celda(cubo, punto, AGUA_MARCADA)
        return "agua"
    
    # Si no era agua sin explorar ni una nave oculta,
    return "celda ya atacada"
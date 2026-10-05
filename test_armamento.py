import pytest

from armamento import (
    ARMAS,
    obtener_arma,
    obtener_catalogo,
    celdas_torpedo,
    aplicar_torpedo
)

from tablero import (
    crear_cubo,
    cambiar_celda,
    obtener_celda,
    NAVE_OCULTA,
    IMPACTO,
    AGUA_MARCADA
)


def test_obtener_arma():
    arma = obtener_arma("T")

    assert arma["nombre"] == "Torpedo"
    assert arma["municion"] == "ilimitada"


def test_arma_invalida():
    with pytest.raises(ValueError):
        obtener_arma("Z")


def test_obtener_catalogo():
    catalogo = obtener_catalogo()

    assert "T" in catalogo
    assert "R" in catalogo
    assert "C" in catalogo
    assert "S" in catalogo
    assert "L" in catalogo
    assert "O" in catalogo
    assert "G" in catalogo


def test_celdas_torpedo():
    punto = [2, 3, 4]

    celdas = celdas_torpedo(punto)

    assert celdas == [[2, 3, 4]]


def test_torpedo_impacto():
    cubo = crear_cubo(2)

    cambiar_celda(cubo, [1, 1, 1], NAVE_OCULTA)

    resultado = aplicar_torpedo(cubo, [1, 1, 1])

    assert resultado == "impacto"
    assert obtener_celda(cubo, [1, 1, 1]) == IMPACTO


def test_torpedo_agua():
    cubo = crear_cubo(2)

    resultado = aplicar_torpedo(cubo, [1, 1, 1])

    assert resultado == "agua"
    assert obtener_celda(cubo, [1, 1, 1]) == AGUA_MARCADA


def test_torpedo_celda_ya_atacada():
    cubo = crear_cubo(2)

    cambiar_celda(cubo, [1, 1, 1], IMPACTO)

    resultado = aplicar_torpedo(cubo, [1, 1, 1])

    assert resultado == "celda ya atacada"
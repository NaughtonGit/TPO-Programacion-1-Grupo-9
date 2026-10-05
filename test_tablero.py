import pytest

from tablero import (
    AGUA_SIN_EXPLORAR,
    NAVE_OCULTA,
    IMPACTO,
    crear_cubo,
    validar_punto,
    obtener_celda,
    cambiar_celda,
    obtener_plano_z,
    crear_plano_z,
    crear_matriz,
    obtener_valor_matriz,
    cambiar_valor_matriz
)


def test_crear_cubo():
    cubo = crear_cubo(2)

    assert len(cubo) == 2
    assert len(cubo[0]) == 2
    assert len(cubo[0][0]) == 2
    assert cubo[0][0][0] == AGUA_SIN_EXPLORAR


def test_validar_punto():
    cubo = crear_cubo(2)

    assert validar_punto(cubo, [1, 1, 1]) == True
    assert validar_punto(cubo, [2, 2, 2]) == True
    assert validar_punto(cubo, [2, 2, 3]) == False


def test_obtener_celda():
    cubo = crear_cubo(2)

    assert obtener_celda(cubo, [1, 1, 1]) == AGUA_SIN_EXPLORAR


def test_cambiar_celda():
    cubo = crear_cubo(2)

    cambiar_celda(cubo, [1, 1, 1], NAVE_OCULTA)

    assert obtener_celda(cubo, [1, 1, 1]) == NAVE_OCULTA


def test_obtener_plano_z():
    cubo = crear_cubo(2)

    plano = obtener_plano_z(cubo, 1)

    assert len(plano) == 2
    assert len(plano[0]) == 2


def test_crear_plano_z():
    cubo = crear_cubo(2)

    dibujo = crear_plano_z(cubo, 1)

    assert "x1" in dibujo
    assert "x2" in dibujo
    assert "y1" in dibujo
    assert "y2" in dibujo


@pytest.mark.parametrize("mostrar_naves, simbolo", [(False, "~"), (True, "N")])
def test_crear_plano_z_mostrar_naves(mostrar_naves, simbolo):
    cubo = crear_cubo(2)
    cambiar_celda(cubo, [1, 1, 1], NAVE_OCULTA)
    cambiar_celda(cubo, [1, 2, 1], IMPACTO)

    dibujo = crear_plano_z(cubo, 1, mostrar_naves=mostrar_naves)

    assert dibujo.splitlines()[1].split() == ["y1", simbolo, "X"]
    assert obtener_celda(cubo, [1, 1, 1]) == NAVE_OCULTA


def test_crear_matriz():
    matriz = crear_matriz(2, 3)

    assert matriz == [
        [0, 0, 0],
        [0, 0, 0]
    ]


def test_obtener_valor_matriz():
    matriz = crear_matriz(2, 2)

    assert obtener_valor_matriz(matriz, 0, 0) == 0


def test_cambiar_valor_matriz():
    matriz = crear_matriz(2, 2)

    cambiar_valor_matriz(matriz, 0, 1, 5)

    assert matriz[0][1] == 5

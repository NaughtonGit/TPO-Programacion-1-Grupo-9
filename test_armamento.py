import pytest

from armamento import (
    ARMAS,
    obtener_arma,
    obtener_catalogo,
    celdas_torpedo,
    aplicar_torpedo,
    celdas_racimo,
    celdas_carga_profundidad,
    celdas_barrido_laser,
    aplicar_arma,
    crear_municion,
    usar_municion
)

from tablero import (
    crear_cubo,
    cambiar_celda,
    obtener_celda,
    NAVE_OCULTA,
    IMPACTO,
    AGUA_MARCADA,
    DETECTADO_SONAR
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


def test_torpedo_sobre_celda_detectada_por_sonar():
    cubo = crear_cubo(2)

    cambiar_celda(cubo, [1, 1, 1], DETECTADO_SONAR)

    resultado = aplicar_torpedo(cubo, [1, 1, 1])

    assert resultado == "impacto"
    assert obtener_celda(cubo, [1, 1, 1]) == IMPACTO


def test_celdas_racimo():
    cubo = crear_cubo(8)

    celdas = celdas_racimo(cubo, [4, 4, 4])

    assert len(celdas) == 7
    assert celdas[0] == (4, 4, 4)
    assert (5, 4, 4) in celdas


def test_celdas_racimo_en_esquina():
    cubo = crear_cubo(8)

    assert len(celdas_racimo(cubo, [1, 1, 1])) == 4


def test_celdas_carga_profundidad():
    cubo = crear_cubo(8)

    celdas = celdas_carga_profundidad(cubo, [3, 5, 4])

    assert len(celdas) == 8
    assert celdas[0] == (1, 5, 4)
    assert celdas[7] == (8, 5, 4)


def test_celdas_barrido_laser():
    cubo = crear_cubo(8)

    sobre_x = celdas_barrido_laser(cubo, {}, [3, 5, 4], "x")
    sobre_y = celdas_barrido_laser(cubo, {}, [3, 5, 4], "y")

    assert len(sobre_x) == 8
    assert sobre_x[0] == (3, 1, 4)
    assert sobre_y[0] == (3, 5, 1)


def test_barrido_laser_no_alcanza_submarinos():
    cubo = crear_cubo(8)
    flota = {
        "S1": {"tipo": "S", "celdas": {(3, 2, 4), (3, 3, 4), (3, 4, 4)}, "impactos": set()}
    }

    celdas = celdas_barrido_laser(cubo, flota, [3, 5, 4], "x")

    assert len(celdas) == 5
    assert (3, 2, 4) not in celdas


def test_armas_punto_o_eje_invalido():
    cubo = crear_cubo(2)

    with pytest.raises(ValueError):
        celdas_racimo(cubo, [3, 1, 1])

    with pytest.raises(ValueError):
        celdas_carga_profundidad(cubo, [3, 1, 1])

    with pytest.raises(ValueError):
        celdas_barrido_laser(cubo, {}, [1, 1, 1], "z")


def test_aplicar_arma():
    cubo = crear_cubo(8)
    cambiar_celda(cubo, [2, 5, 4], NAVE_OCULTA)

    resultados = aplicar_arma(cubo, celdas_carga_profundidad(cubo, [3, 5, 4]))

    assert len(resultados) == 8
    assert resultados[1] == "impacto"
    assert resultados.count("agua") == 7


def test_crear_municion():
    municion = crear_municion()

    assert municion["T"] == "ilimitada"
    assert municion["R"] == 3
    assert municion["C"] == 2
    assert municion["L"] == 2


def test_usar_municion():
    municion = crear_municion()

    usar_municion(municion, "R")
    assert municion["R"] == 2

    usar_municion(municion, "T")
    assert municion["T"] == "ilimitada"


def test_sin_municion():
    municion = crear_municion()

    usar_municion(municion, "C")
    usar_municion(municion, "C")

    with pytest.raises(ValueError):
        usar_municion(municion, "C")


def test_cada_jugador_tiene_su_municion():
    municion_1 = crear_municion()
    municion_2 = crear_municion()

    usar_municion(municion_1, "R")

    assert municion_2["R"] == 3
    assert ARMAS["R"]["municion"] == 3
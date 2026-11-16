import pytest

from armamento import (
    ARMAS,
    RADIO_ONDA,
    obtener_arma,
    obtener_catalogo,
    celdas_torpedo,
    aplicar_torpedo,
    celdas_racimo,
    celdas_carga_profundidad,
    celdas_barrido_laser,
    celdas_onda_expansiva,
    celdas_torpedo_guiado,
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


def test_onda_expansiva_radio_cero():
    cubo = crear_cubo(8)

    assert celdas_onda_expansiva(cubo, [4, 4, 4], 0) == [(4, 4, 4)]


def test_onda_expansiva_radio_por_defecto():
    cubo = crear_cubo(8)

    celdas = celdas_onda_expansiva(cubo, [4, 4, 4])

    assert RADIO_ONDA == 1
    assert celdas[0] == (4, 4, 4)
    assert sorted(celdas) == sorted(celdas_racimo(cubo, [4, 4, 4]))


def test_onda_expansiva_radio_decreciente():
    cubo = crear_cubo(8)

    celdas = celdas_onda_expansiva(cubo, [4, 4, 4], 2)

    assert len(celdas) == 25
    assert len(set(celdas)) == 25
    assert (6, 4, 4) in celdas
    assert (5, 5, 4) in celdas
    assert (7, 4, 4) not in celdas


def test_onda_expansiva_en_esquina_no_sale_del_cubo():
    cubo = crear_cubo(8)

    celdas = celdas_onda_expansiva(cubo, [1, 1, 1], 2)

    assert len(celdas) == 10
    assert (0, 1, 1) not in celdas


def test_onda_expansiva_invalida():
    cubo = crear_cubo(2)

    with pytest.raises(ValueError):
        celdas_onda_expansiva(cubo, [3, 1, 1])

    with pytest.raises(ValueError):
        celdas_onda_expansiva(cubo, [1, 1, 1], -1)

    with pytest.raises(ValueError):
        celdas_onda_expansiva(cubo, [1, 1, 1], "2")


def test_onda_expansiva_aplicada():
    cubo = crear_cubo(8)
    cambiar_celda(cubo, [5, 4, 4], NAVE_OCULTA)

    resultados = aplicar_arma(cubo, celdas_onda_expansiva(cubo, [4, 4, 4]))

    assert len(resultados) == 7
    assert resultados.count("impacto") == 1
    assert resultados.count("agua") == 6


def armar_flota_guiado(cubo, celdas, impactos):
    """Arma una flota de un destructor y deja el cubo en el estado que corresponde."""
    for celda in celdas:
        cambiar_celda(cubo, celda, IMPACTO if celda in impactos else NAVE_OCULTA)

    return {"D1": {"tipo": "D", "celdas": set(celdas), "impactos": set(impactos)}}


def test_torpedo_guiado_sin_impacto_previo_es_un_torpedo():
    cubo = crear_cubo(4)
    flota = armar_flota_guiado(cubo, [(1, 1, 1), (1, 1, 2), (1, 1, 3)], [])

    assert celdas_torpedo_guiado(cubo, flota, [3, 3, 3]) == [(3, 3, 3)]
    assert celdas_torpedo_guiado(cubo, {}, [3, 3, 3]) == [(3, 3, 3)]


def test_torpedo_guiado_busca_celda_contigua():
    cubo = crear_cubo(4)
    flota = armar_flota_guiado(cubo, [(1, 1, 1), (1, 1, 2), (1, 1, 3)], [(1, 1, 2)])

    assert celdas_torpedo_guiado(cubo, flota, [4, 4, 4]) == [(1, 1, 1)]


def test_torpedo_guiado_recorre_la_nave_en_forma_recursiva():
    cubo = crear_cubo(4)
    celdas = [(1, 1, 1), (1, 1, 2), (1, 1, 3), (1, 1, 4)]
    flota = armar_flota_guiado(cubo, celdas, [(1, 1, 1), (1, 1, 2), (1, 1, 3)])

    assert celdas_torpedo_guiado(cubo, flota, [4, 4, 4]) == [(1, 1, 4)]


def test_torpedo_guiado_ignora_naves_hundidas():
    cubo = crear_cubo(4)
    celdas = [(1, 1, 1), (1, 1, 2)]
    flota = armar_flota_guiado(cubo, celdas, celdas)

    assert celdas_torpedo_guiado(cubo, flota, [3, 3, 3]) == [(3, 3, 3)]


def test_torpedo_guiado_aplicado():
    cubo = crear_cubo(4)
    flota = armar_flota_guiado(cubo, [(1, 1, 1), (1, 1, 2), (1, 1, 3)], [(1, 1, 2)])

    resultados = aplicar_arma(cubo, celdas_torpedo_guiado(cubo, flota, [4, 4, 4]))

    assert resultados == ["impacto"]
    assert obtener_celda(cubo, [1, 1, 1]) == IMPACTO


def test_torpedo_guiado_punto_invalido():
    cubo = crear_cubo(2)

    with pytest.raises(ValueError):
        celdas_torpedo_guiado(cubo, {}, [3, 1, 1])


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
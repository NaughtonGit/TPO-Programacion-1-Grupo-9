import pytest

import radar
import tablero


@pytest.fixture
def flota_ejemplo():
    return {
        "F1": {
            "tipo": "F",
            "celdas": {(3, 5, 4), (3, 5, 5)},
            "impactos": set(),
        },
        "D1": {
            "tipo": "D",
            "celdas": {(6, 2, 2), (6, 2, 3), (6, 2, 4)},
            "impactos": set(),
        },
    }


def test_busqueda_lineal_devuelve_formato_de_metricas_comun(flota_ejemplo):
    id_nave, metricas = radar.busqueda_lineal(flota_ejemplo, (3, 5, 4))

    assert id_nave == "F1"
    assert set(metricas) == {"comparaciones", "tiempo_ms", "profundidad_max"}
    assert 1 <= metricas["comparaciones"] <= 2
    assert metricas["tiempo_ms"] >= 0
    assert metricas["profundidad_max"] == 0


def test_busqueda_lineal_sin_nave(flota_ejemplo):
    id_nave, metricas = radar.busqueda_lineal(flota_ejemplo, (8, 8, 8))

    assert id_nave is None
    assert metricas["comparaciones"] == 5


def test_busqueda_optimizada_y_lineal_comparten_formato(flota_ejemplo):
    mapa = radar.construir_mapa(flota_ejemplo)

    _, lineales = radar.busqueda_lineal(flota_ejemplo, (8, 8, 8))
    _, optimizadas = radar.busqueda_optimizada(flota_ejemplo, (8, 8, 8), mapa)

    assert set(lineales) == set(optimizadas)


def test_busqueda_recursiva_devuelve_nave_y_metricas(flota_ejemplo):
    id_nave, metricas = radar.busqueda_recursiva(flota_ejemplo, (8, 8, 8))

    assert id_nave is None
    assert metricas["comparaciones"] == 5
    assert metricas["profundidad_max"] == 3
    assert metricas["tiempo_ms"] >= 0


def test_detectar_reutiliza_el_indice(flota_ejemplo, monkeypatch):
    cubo = tablero.crear_cubo(8)
    mapa = radar.construir_mapa(flota_ejemplo)

    def no_reconstruir(_):
        raise AssertionError("No se debe reconstruir el mapa en cada consulta")

    monkeypatch.setattr(radar, "construir_mapa", no_reconstruir)
    for punto, esperado in [((3, 5, 4), "F1"), ((8, 8, 8), None)]:
        id_nave, metricas = radar.detectar(cubo, flota_ejemplo, punto, mapa)
        assert id_nave == esperado
        assert metricas["comparaciones"] == 1


def test_detectar_invalido_devuelve_metricas_comunes(flota_ejemplo):
    cubo = tablero.crear_cubo(8)

    id_nave, metricas = radar.detectar(cubo, flota_ejemplo, (9, 2, 3))

    assert id_nave is None
    assert metricas == {
        "comparaciones": 0,
        "tiempo_ms": 0.0,
        "profundidad_max": 0,
    }


def test_sonar_plano_usa_coordenadas_1_based():
    cubo = tablero.crear_cubo(2)

    assert radar.sonar_plano(cubo, "z", 1) == [
        (1, 1, 1), (1, 1, 2), (1, 2, 1), (1, 2, 2)
    ]
    assert radar.sonar_plano(cubo, "x", 2) == [
        (1, 2, 1), (1, 2, 2), (2, 2, 1), (2, 2, 2)
    ]


def test_sonar_marca_naves_del_plano_como_detectadas():
    cubo = tablero.crear_cubo(8)
    tablero.cambiar_celda(cubo, (3, 5, 4), tablero.NAVE_OCULTA)
    tablero.cambiar_celda(cubo, (3, 5, 5), tablero.NAVE_OCULTA)
    tablero.cambiar_celda(cubo, (6, 2, 2), tablero.NAVE_OCULTA)

    plano = radar.sonar_plano(cubo, "z", 3)

    assert (3, 5, 4) in plano
    assert tablero.obtener_celda(cubo, (3, 5, 4)) == tablero.DETECTADO_SONAR
    assert tablero.obtener_celda(cubo, (3, 5, 5)) == tablero.DETECTADO_SONAR
    assert tablero.obtener_celda(cubo, (6, 2, 2)) == tablero.NAVE_OCULTA


@pytest.mark.parametrize("eje,valor", [("q", 1), ("z", 0), ("x", 3)])
def test_sonar_rechaza_ejes_y_planos_invalidos(eje, valor):
    with pytest.raises(ValueError):
        radar.sonar_plano(tablero.crear_cubo(2), eje, valor)


def test_mapa_probabilidad_respeta_agua_descartada():
    cubo = tablero.crear_cubo(4)
    tablero.cambiar_celda(cubo, (1, 1, 1), tablero.AGUA_MARCADA)

    probabilidades = radar.mapa_probabilidad(cubo)

    assert len(probabilidades) == 4
    assert probabilidades[0][0][0] == 0
    assert probabilidades[1][1][1] > probabilidades[0][0][0]

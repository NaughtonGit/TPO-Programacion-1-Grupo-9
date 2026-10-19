import pytest

import radar
import tablero


@pytest.fixture
def flota_ejemplo():
    return {
        "F1": {
            "tipo": "F",
            "celdas": {(3, 5, 4), (3, 5, 5)},
            "impactos": set()
        },
        "D1": {
            "tipo": "D",
            "celdas": {(6, 2, 2), (6, 2, 3), (6, 2, 4)},
            "impactos": set()
        }
    }


def test_radar_con_nave(flota_ejemplo, capsys):
    cubo = tablero.crear_cubo(8)

    id_nave, comparaciones = radar.detectar(cubo, flota_ejemplo, (3, 5, 4))
    assert id_nave == "F1"
    # Las celdas son conjuntos: su orden de recorrido puede variar.
    assert 1 <= comparaciones <= 2

    assert radar.mostrar_resultado(cubo, flota_ejemplo, (3, 5, 4)) is True
    assert capsys.readouterr().out == (
        "Radar: nave detectada\n"
        "Nave: F1\n"
        f"Comparaciones: {comparaciones}\n"
    )


def test_radar_sin_nave(flota_ejemplo, capsys):
    cubo = tablero.crear_cubo(8)

    assert radar.detectar(cubo, flota_ejemplo, (8, 8, 8)) == (None, 5)
    assert radar.mostrar_resultado(cubo, flota_ejemplo, (8, 8, 8)) is False
    assert capsys.readouterr().out == (
        "Radar: no se detecto ninguna nave\n"
        "Comparaciones: 5\n"
    )


def test_radar_punto_invalido(flota_ejemplo, capsys):
    cubo = tablero.crear_cubo(8)

    assert radar.detectar(cubo, flota_ejemplo, (9, 2, 3)) == (None, 0)
    assert radar.mostrar_resultado(cubo, flota_ejemplo, (9, 2, 3)) is False
    assert capsys.readouterr().out == "Punto invalido\n"


def test_sonar_plano_usa_coordenadas_1_based():
    cubo = tablero.crear_cubo(2)

    assert radar.sonar_plano(cubo, "z", 1) == [(1, 1, 1), (1, 1, 2), (1, 2, 1), (1, 2, 2)]
    assert radar.sonar_plano(cubo, "x", 2) == [(1, 2, 1), (1, 2, 2), (2, 2, 1), (2, 2, 2)]


def test_busqueda_optimizada_con_mapa_reutilizable(flota_ejemplo):
    mapa = radar.construir_mapa(flota_ejemplo)

    id_nave, metricas = radar.busqueda_optimizada(flota_ejemplo, (3, 5, 4), mapa)
    assert id_nave == "F1"
    assert metricas["comparaciones"] == 1
    assert metricas["tiempo_ms"] >= 0
    assert metricas["profundidad_max"] == 0

    id_nave, metricas = radar.busqueda_optimizada(flota_ejemplo, (8, 8, 8), mapa)
    assert id_nave is None
    assert metricas["comparaciones"] == 1


def test_sonar_marca_naves_del_plano_como_detectadas(flota_ejemplo):
    cubo = tablero.crear_cubo(8)
    tablero.cambiar_celda(cubo, (3, 5, 4), tablero.NAVE_OCULTA)
    tablero.cambiar_celda(cubo, (3, 5, 5), tablero.NAVE_OCULTA)
    tablero.cambiar_celda(cubo, (6, 2, 2), tablero.NAVE_OCULTA)

    plano = radar.sonar_plano(cubo, "z", 3)

    assert (3, 5, 4) in plano
    assert tablero.obtener_celda(cubo, (3, 5, 4)) == tablero.DETECTADO_SONAR
    assert tablero.obtener_celda(cubo, (3, 5, 5)) == tablero.DETECTADO_SONAR
    assert tablero.obtener_celda(cubo, (6, 2, 2)) == tablero.NAVE_OCULTA

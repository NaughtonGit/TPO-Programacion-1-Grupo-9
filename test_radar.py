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

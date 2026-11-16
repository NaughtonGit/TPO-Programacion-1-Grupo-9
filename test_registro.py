import csv

import pytest

import registro
from registro import (
    crear_registro,
    agregar_evento,
    obtener_historial,
    contar_eventos,
    contar_eventos_jugador,
    contar_resultado,
    obtener_estadisticas,
    crear_resumen
)


def test_crear_registro():
    registro = crear_registro()

    assert registro == []


def test_agregar_evento():
    registro = crear_registro()

    agregar_evento(
        registro,
        1,
        "Jugador 1",
        "Torpedo",
        "impacto"
    )

    assert len(registro) == 1
    assert registro[0]["jugador"] == "Jugador 1"
    assert registro[0]["resultado"] == "impacto"


def test_obtener_historial():
    registro = crear_registro()

    agregar_evento(
        registro,
        1,
        "Jugador 1",
        "Torpedo",
        "agua"
    )

    historial = obtener_historial(registro)

    assert len(historial) == 1


def test_contar_eventos():
    registro = crear_registro()

    agregar_evento(registro, 1, "Jugador 1", "Torpedo", "agua")
    agregar_evento(registro, 2, "Jugador 2", "Torpedo", "impacto")

    assert contar_eventos(registro) == 2


def test_contar_eventos_jugador():
    registro = crear_registro()

    agregar_evento(registro, 1, "Jugador 1", "Torpedo", "agua")
    agregar_evento(registro, 2, "Jugador 2", "Torpedo", "impacto")
    agregar_evento(registro, 3, "Jugador 1", "Torpedo", "impacto")

    assert contar_eventos_jugador(registro, "Jugador 1") == 2


def test_contar_resultado():
    registro = crear_registro()

    agregar_evento(registro, 1, "Jugador 1", "Torpedo", "impacto")
    agregar_evento(registro, 2, "Jugador 2", "Torpedo", "agua")
    agregar_evento(registro, 3, "Jugador 1", "Torpedo", "impacto")

    assert contar_resultado(registro, "impacto") == 2


def test_obtener_estadisticas():
    registro = crear_registro()

    agregar_evento(registro, 1, "Jugador 1", "Torpedo", "impacto")
    agregar_evento(registro, 2, "Jugador 2", "Torpedo", "agua")
    agregar_evento(registro, 3, "Jugador 1", "Torpedo", "hundido")

    estadisticas = obtener_estadisticas(registro)

    assert estadisticas["total_eventos"] == 3
    assert estadisticas["impactos"] == 1
    assert estadisticas["agua"] == 1
    assert estadisticas["hundidos"] == 1


def test_crear_resumen():
    registro = crear_registro()

    agregar_evento(registro, 1, "Jugador 1", "Torpedo", "impacto")
    agregar_evento(registro, 2, "Jugador 2", "Torpedo", "agua")

    resumen = crear_resumen(registro, "Jugador 1")

    assert resumen["ganador"] == "Jugador 1"
    assert resumen["total_eventos"] == 2
    assert resumen["impactos"] == 1
    assert resumen["agua"] == 1


def _estado_guardable(partida_terminada=False):
    punto = (1, 1, 1)
    flota_ana = {
        "F1": {"tipo": "F", "celdas": {punto}, "impactos": set(), "danio": {punto: 0}}
    }
    impactos_beto = {punto} if partida_terminada else set()
    flota_beto = {
        "F1": {
            "tipo": "F",
            "celdas": {punto},
            "impactos": impactos_beto,
            "danio": {punto: int(partida_terminada)},
        }
    }
    return {
        "jugadores": [
            {"nombre": "Ana", "flota": flota_ana},
            {"nombre": "Beto", "flota": flota_beto},
        ],
        "actual": 0,
        "turno": 4,
        "coordenada": punto,
    }


def test_guardar_cargar_y_listar_partida(monkeypatch, tmp_path):
    monkeypatch.setattr(registro, "DIRECTORIO_PARTIDAS", tmp_path / "datos" / "partidas")
    estado = _estado_guardable()

    ruta = registro.guardar_partida(estado, "Partida Uno")

    assert ruta.is_relative_to(tmp_path)
    assert registro.listar_partidas() == ["Partida Uno"]
    assert registro.cargar_partida("Partida Uno") == estado


def test_guardar_partida_valida_el_nombre(monkeypatch, tmp_path):
    monkeypatch.setattr(registro, "DIRECTORIO_PARTIDAS", tmp_path / "partidas")

    with pytest.raises(ValueError):
        registro.guardar_partida(_estado_guardable(), "../fuera")


def test_exportar_partidas_a_csv(monkeypatch, tmp_path):
    monkeypatch.setattr(registro, "DIRECTORIO_PARTIDAS", tmp_path / "datos" / "partidas")
    monkeypatch.chdir(tmp_path)
    registro.guardar_partida(_estado_guardable(partida_terminada=True), "Final")

    ruta = registro.exportar_partidas()

    with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
        filas = list(csv.DictReader(archivo))
    assert filas[0]["nombre"] == "Final"
    assert filas[0]["ganador"] == "Ana"


def test_ranking_usa_partidas_guardadas(monkeypatch, tmp_path):
    monkeypatch.setattr(registro, "DIRECTORIO_PARTIDAS", tmp_path / "partidas")
    registro.guardar_partida(_estado_guardable(partida_terminada=True), "Final")

    assert registro.obtener_ranking() == [
        {"jugador": "Ana", "partidas": 1, "victorias": 1},
        {"jugador": "Beto", "partidas": 1, "victorias": 0},
    ]

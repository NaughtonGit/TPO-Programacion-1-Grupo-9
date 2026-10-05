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
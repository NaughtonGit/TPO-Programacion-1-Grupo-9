from copy import deepcopy

import pytest

import tablero
import flota
import partida
from errores import (
    ConfiguracionInvalida,
    JugadaInvalida,
    ArmaNoDisponible,
    PuntoFueraDelCubo,
    CeldaYaAtacada,
    PartidaTerminada
)


def simular_teclado(monkeypatch, respuestas):
    """
    hace que cada input() devuelva la siguiente respuesta de la lista.
    recibe el monkeypatch de pytest y la lista de respuestas.
    """
    
    monkeypatch.setattr("builtins.input", lambda mensaje: respuestas.pop(0))


def test_leer_opcion_valida(monkeypatch):
    simular_teclado(monkeypatch, ["3"])
    assert partida.leer_opcion(partida.MENU_PRINCIPAL) == "3"


def test_leer_opcion_reintenta_si_es_invalida(monkeypatch):
    simular_teclado(monkeypatch, ["9", "hola", "", "2"])
    assert partida.leer_opcion(partida.MENU_PRINCIPAL) == "2"


def test_leer_tramo(monkeypatch):
    simular_teclado(monkeypatch, ["3,5,4-3,5,5"])
    assert partida.leer_tramo() == ((3, 5, 4), (3, 5, 5))


def test_leer_tramo_reintenta_si_es_invalido(monkeypatch):
    simular_teclado(monkeypatch, ["3,5,4", "a,b,c-1,2,3", "3,5,4-3,5,5x", "1,1,1-1,1,2"])
    assert partida.leer_tramo() == ((1, 1, 1), (1, 1, 2))


def test_leer_letra_nave(monkeypatch):
    pendientes = flota.naves_pendientes({})
    simular_teclado(monkeypatch, ["x", "", "s"])
    assert partida.leer_letra_nave(pendientes) == "S"


def test_leer_letra_nave_sin_pendientes(monkeypatch):
    pendientes = flota.naves_pendientes({})
    pendientes["E"] = 0
    simular_teclado(monkeypatch, ["E", "F"])
    assert partida.leer_letra_nave(pendientes) == "F"


def test_mostrar_pendientes(capsys):
    assert partida.mostrar_pendientes(flota.naves_pendientes({})) == 10
    assert "Pendientes: F x3 D x2 S x2 C x1 P x1 E x1" in capsys.readouterr().out


def test_mostrar_pendientes_flota_completa(capsys):
    completa = {"F": 0, "D": 0, "S": 0, "C": 0, "P": 0, "E": 0}
    assert partida.mostrar_pendientes(completa) == 0
    assert "Flota completa." in capsys.readouterr().out


def test_ubicacion_manual_con_errores(monkeypatch):
    cubo = tablero.crear_cubo(partida.TAMANIO)
    simular_teclado(monkeypatch, [
        "E", "5,2,2-6,3,3",
        "P", "7,6,1-7,6,5",
        "C", "3,1,5-3,1,8",
        "S", "1,8,1-1,8,3",
        "S", "1,8,6-1,8,8",
        "D", "8,8,1-8,8,3",
        "D", "8,8,6-8,8,8",
        "F", "3,5,4-3,5,5",
        "F", "3,5,6-3,5,7",   
        "F", "1,1,1-1,1,2",
        "F", "8,1,7-8,1,8",
    ])
    mi_flota = partida.ubicacion_manual(cubo, {})
    assert len(mi_flota) == 10


def test_submenu_ubicacion_automatica(monkeypatch):
    simular_teclado(monkeypatch, ["2"])
    cubo, mi_flota = partida.submenu_ubicacion("Jugador 1")
    assert len(mi_flota) == 10


def test_flota_maquina():
    cubo, mi_flota = partida.flota_maquina("Maquina")
    assert len(mi_flota) == 10


def test_dibujar_estado(capsys):
    cubo = tablero.crear_cubo(partida.TAMANIO)
    partida.dibujar_estado("Jugador 1", cubo)
    salida = capsys.readouterr().out
    assert "Cubo de Jugador 1" in salida
    assert "CAPA z = 1" in salida
    assert "CAPA z = 8" in salida
    assert "N" not in salida.replace("Referencias: ~ agua   N nave", "")


def test_continuar_y_salir():
    assert partida.continuar_partida() == True
    assert partida.salir() == False


def test_menu_principal_termina_al_salir(monkeypatch):
    simular_teclado(monkeypatch, ["7", "4", "5"])
    partida.menu_principal()
    

def armar_jugador(nombre, desde, hasta):
    """crea un jugador con una sola fragata, para partidas cortas."""
    cubo = tablero.crear_cubo(partida.TAMANIO)
    mi_flota = {}
    flota.ubicar_nave(cubo, mi_flota, "F", desde, hasta)
    return {"nombre": nombre, "cubo": cubo, "flota": mi_flota}


def estado_de_prueba():
    configuracion = {"jugadores": [
        armar_jugador("Ana", (1, 1, 1), (1, 1, 2)),
        armar_jugador("Beto", (3, 5, 4), (3, 5, 5)),
    ]}
    return partida.nueva_partida_1v1(configuracion)


def test_nueva_partida_1v1():
    estado = estado_de_prueba()
    assert estado["actual"] == 0
    assert estado["turno"] == 1
    assert estado["jugadores"][1]["municion"]["T"] == "ilimitada"


def test_configuracion_invalida():
    with pytest.raises(ConfiguracionInvalida):
        partida.nueva_partida_1v1({"jugadores": []})
    with pytest.raises(ConfiguracionInvalida):
        partida.nueva_partida_vs_maquina({"jugadores": [{}, {}]}, "imposible")


def test_disparo_al_agua_pasa_el_turno():
    estado = estado_de_prueba()
    partida.ejecutar_turno(estado, {"arma": "T", "objetivo": (8, 8, 8)})
    assert estado["ultimo_disparo"]["resultado"] == "agua"
    assert estado["actual"] == 1
    assert estado["turno"] == 2


def test_impacto_hundido_y_ganador():
    estado = estado_de_prueba()
    partida.ejecutar_turno(estado, {"arma": "T", "objetivo": (3, 5, 4)})   # Ana
    assert estado["ultimo_disparo"]["resultado"] == "impacto"
    assert estado["ultimo_disparo"]["impactos"] == 1

    partida.ejecutar_turno(estado, {"arma": "T", "objetivo": (8, 8, 8)})   # Beto
    partida.ejecutar_turno(estado, {"arma": "T", "objetivo": (3, 5, 5)})   # Ana
    assert estado["ultimo_disparo"]["resultado"] == "hundido"
    assert partida.hay_ganador(estado) == "Ana"
    assert estado["actual"] == 0
    assert tablero.obtener_celda(estado["jugadores"][1]["cubo"], (3, 5, 4)) == tablero.HUNDIDO


@pytest.mark.parametrize("jugada, error", [
    ({"arma": "T", "objetivo": (9, 1, 1)}, PuntoFueraDelCubo),
    ({"arma": "G", "objetivo": (1, 1, 1)}, ArmaNoDisponible),
])
def test_jugada_invalida_no_cambia_el_turno(jugada, error):
    estado = estado_de_prueba()
    with pytest.raises(error):
        partida.ejecutar_turno(estado, jugada)
    assert estado["actual"] == 0
    assert estado["registro"] == []


def test_celda_ya_atacada():
    estado = estado_de_prueba()
    partida.ejecutar_turno(estado, {"arma": "T", "objetivo": (8, 8, 8)})   # Ana, cubo de Beto
    partida.ejecutar_turno(estado, {"arma": "T", "objetivo": (8, 8, 8)})   # Beto, cubo de Ana
    with pytest.raises(CeldaYaAtacada):
        partida.ejecutar_turno(estado, {"arma": "T", "objetivo": (8, 8, 8)})


def test_turno_maquina():
    configuracion = {"jugadores": [
        armar_jugador("Ana", (1, 1, 1), (1, 1, 2)),
        armar_jugador("Robot", (3, 5, 4), (3, 5, 5)),
    ]}
    estado = partida.nueva_partida_vs_maquina(configuracion, "facil")

    with pytest.raises(JugadaInvalida):
        partida.turno_maquina(estado)

    partida.ejecutar_turno(estado, {"arma": "T", "objetivo": (8, 8, 8)})
    partida.turno_maquina(estado)
    assert estado["ultimo_disparo"]["jugador"] == "Robot"
    assert estado["actual"] == 0
    assert len(estado["registro"]) == 2


def test_jugar_partida_completa(monkeypatch, capsys):
    estado = estado_de_prueba()
    simular_teclado(monkeypatch, [
        "s",
        "1", "Z", "G", "3,5,4", "T", "3,5,4",   # Ana: letra invalida, arma no disponible, impacto
        "1", "T", "8,8,8",                      # Beto: agua
        "1", "T", "3,5,5",                      # Ana: hunde y gana
    ])
    partida.jugar(estado)
    salida = capsys.readouterr().out
    assert "todavia no esta disponible" in salida
    assert "Nave hundida: Fragata" in salida
    assert "Gano Ana!" in salida


@pytest.mark.parametrize("ganador, objetivos", [
    ("Ana", [(3, 5, 4), (8, 8, 8), (3, 5, 5)]),
    ("Beto", [(8, 8, 8), (1, 1, 1), (7, 7, 7), (1, 1, 2)]),
])
def test_victoria_impide_seguir_disparando(ganador, objetivos):
    estado = estado_de_prueba()
    for objetivo in objetivos:
        partida.ejecutar_turno(estado, {"arma": "T", "objetivo": objetivo})

    assert partida.hay_ganador(estado) == ganador
    assert partida.jugador_actual(estado)["nombre"] == ganador
    anterior = deepcopy(estado)

    with pytest.raises(PartidaTerminada):
        partida.ejecutar_turno(estado, {"arma": "T", "objetivo": (6, 6, 6)})
    assert estado == anterior


def test_flota_vacia_no_da_una_victoria():
    estado = estado_de_prueba()
    estado["jugadores"][1]["flota"] = {}
    assert partida.hay_ganador(estado) is None


def test_hundir_una_nave_no_alcanza_para_ganar():
    estado = estado_de_prueba()
    rival = estado["jugadores"][1]
    assert flota.ubicar_nave(rival["cubo"], rival["flota"], "F", (8, 1, 1), (8, 1, 2))

    partida.ejecutar_turno(estado, {"arma": "T", "objetivo": (3, 5, 4)})
    partida.ejecutar_turno(estado, {"arma": "T", "objetivo": (8, 8, 8)})
    partida.ejecutar_turno(estado, {"arma": "T", "objetivo": (3, 5, 5)})

    assert estado["ultimo_disparo"]["resultado"] == "hundido"
    assert partida.hay_ganador(estado) is None
    assert estado["actual"] == 1
    assert estado["turno"] == 4

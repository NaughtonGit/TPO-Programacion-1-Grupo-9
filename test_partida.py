import tablero
import flota
import partida


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

import pytest
import tablero
import flota
 
 
def test_pendientes_flota_vacia():
    assert flota.naves_pendientes({}) == {"E": 1, "P": 1, "C": 1, "S": 2, "D": 2, "F": 3}
 
 
def test_restricciones_de_zona():
    assert flota.cumple_restriccion("S", {(2, 1, 1), (3, 1, 1), (4, 1, 1)}, 8) == True
    assert flota.cumple_restriccion("S", {(4, 1, 1), (5, 1, 1), (6, 1, 1)}, 8) == False   
    assert flota.cumple_restriccion("P", {(1, 1, 1), (1, 1, 2), (1, 1, 3), (1, 1, 4), (1, 1, 5)}, 8) == False
    assert flota.cumple_restriccion("C", {(1, 2, 2), (1, 2, 3), (1, 2, 4), (1, 2, 5)}, 8) == False
    assert flota.cumple_restriccion("E", {(1, 4, 4), (2, 5, 5)}, 8) == False            
 
 
def test_formas_validas():
    cubo = tablero.crear_cubo(8)
    assert flota.calcular_ubicacion(cubo, {}, "D", (2, 1, 7), (2, 1, 5)) == {(2, 1, 5), (2, 1, 6), (2, 1, 7)}
    assert len(flota.calcular_ubicacion(cubo, {}, "E", (4, 4, 4), (5, 5, 5))) == 8
 
 
def test_formas_invalidas():
    cubo = tablero.crear_cubo(8)
    assert flota.calcular_ubicacion(cubo, {}, "F", (1, 1, 1), (1, 2, 2)) == set()   
    assert flota.calcular_ubicacion(cubo, {}, "F", (1, 1, 1), (1, 1, 3)) == set() 
    assert flota.calcular_ubicacion(cubo, {}, "F", (8, 8, 8), (8, 8, 9)) == set() 
    assert flota.calcular_ubicacion(cubo, {}, "C", (3, 2, 2), (3, 3, 3)) == set()   
    assert flota.calcular_ubicacion(cubo, {}, "E", (4, 4, 2), (5, 5, 5)) == set()   
 
 
def test_separacion_entre_naves():
    cubo = tablero.crear_cubo(8)
    mi_flota = {}
    flota.ubicar_nave(cubo, mi_flota, "F", (3, 5, 4), (3, 5, 5))
    assert flota.ubicar_nave(cubo, mi_flota, "D", (3, 5, 6), (3, 5, 8)) == False
    assert flota.ubicar_nave(cubo, mi_flota, "F", (4, 6, 6), (4, 6, 7)) == False
 
 
def test_ubicar_fragata_del_ejemplo():
    cubo = tablero.crear_cubo(8)
    mi_flota = {}
    assert flota.ubicar_nave(cubo, mi_flota, "F", (3, 5, 4), (3, 5, 5)) == True
    assert mi_flota["F1"]["celdas"] == {(3, 5, 4), (3, 5, 5)}
    assert tablero.obtener_celda(cubo, (3, 5, 4)) == tablero.NAVE_OCULTA
 
 
def test_ubicar_rechazos():
    cubo = tablero.crear_cubo(8)
    mi_flota = {}
    assert flota.ubicar_nave(cubo, mi_flota, "X", (1, 1, 1), (1, 1, 2)) == False   
    flota.ubicar_nave(cubo, mi_flota, "C", (2, 1, 1), (2, 1, 4))
    assert flota.ubicar_nave(cubo, mi_flota, "C", (2, 5, 1), (2, 5, 4)) == False   
 
 
def test_error_no_modifica_nada():
    cubo = tablero.crear_cubo(8)
    mi_flota = {}
    assert flota.ubicar_nave(cubo, mi_flota, "F", (1, 1, 1), (1, 2, 2)) == False
    assert mi_flota == {}
    assert tablero.obtener_celda(cubo, (1, 1, 1)) == tablero.AGUA_SIN_EXPLORAR
 
 
def test_automatica_completa():
    for semilla in range(20):
        mi_flota = flota.ubicacion_automatica(tablero.crear_cubo(8), flota.CATALOGO, semilla)
        assert len(mi_flota) == 10
 
 
def test_automatica_misma_semilla_misma_flota():
    flota1 = flota.ubicacion_automatica(tablero.crear_cubo(8), flota.CATALOGO, 42)
    flota2 = flota.ubicacion_automatica(tablero.crear_cubo(8), flota.CATALOGO, 42)
    assert flota1 == flota2


def test_registrar_impacto():
    cubo = tablero.crear_cubo(8)
    mi_flota = {}
    flota.ubicar_nave(cubo, mi_flota, "F", (3, 5, 4), (3, 5, 5))

    assert flota.registrar_impacto(cubo, mi_flota, [3, 5, 4]) == "F1"
    assert (3, 5, 4) in mi_flota["F1"]["impactos"]
    assert tablero.obtener_celda(cubo, [3, 5, 4]) == tablero.IMPACTO


def test_registrar_impacto_en_agua():
    cubo = tablero.crear_cubo(8)
    mi_flota = {}
    flota.ubicar_nave(cubo, mi_flota, "F", (3, 5, 4), (3, 5, 5))

    assert flota.registrar_impacto(cubo, mi_flota, [1, 1, 1]) == None
    assert mi_flota["F1"]["impactos"] == set()


def test_nave_averiada_y_hundida():
    cubo = tablero.crear_cubo(8)
    mi_flota = {}
    flota.ubicar_nave(cubo, mi_flota, "D", (2, 1, 5), (2, 1, 7))

    assert flota.estado_nave(mi_flota, "D1") == "intacta"

    flota.registrar_impacto(cubo, mi_flota, [2, 1, 5])
    assert flota.estado_nave(mi_flota, "D1") == "averiada"

    flota.registrar_impacto(cubo, mi_flota, [2, 1, 6])
    flota.registrar_impacto(cubo, mi_flota, [2, 1, 7])
    assert flota.estado_nave(mi_flota, "D1") == "hundida"
    assert tablero.obtener_celda(cubo, [2, 1, 5]) == tablero.HUNDIDO
    assert tablero.obtener_celda(cubo, [2, 1, 7]) == tablero.HUNDIDO


def test_mismo_impacto_dos_veces_no_suma():
    cubo = tablero.crear_cubo(8)
    mi_flota = {}
    flota.ubicar_nave(cubo, mi_flota, "F", (3, 5, 4), (3, 5, 5))

    flota.registrar_impacto(cubo, mi_flota, [3, 5, 4])
    flota.registrar_impacto(cubo, mi_flota, [3, 5, 4])
    assert flota.estado_nave(mi_flota, "F1") == "averiada"


def test_flota_hundida():
    cubo = tablero.crear_cubo(8)
    mi_flota = {}
    flota.ubicar_nave(cubo, mi_flota, "F", (3, 5, 4), (3, 5, 5))
    assert flota.flota_hundida(mi_flota) == False

    flota.registrar_impacto(cubo, mi_flota, [3, 5, 4])
    assert flota.flota_hundida(mi_flota) == False

    flota.registrar_impacto(cubo, mi_flota, [3, 5, 5])
    assert flota.flota_hundida(mi_flota) == True
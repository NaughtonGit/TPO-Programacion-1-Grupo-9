import re
import random
import tablero
import flota
 
TAMANIO = 8
 

def leer_opcion(opciones):
    """
    pide una opcion de menu hasta que sea valida.
    recibe un diccionario cuyas claves son las opciones ("1", "2"...).
    retorna la opcion elegida.
    """

    patron = "^[" + "".join(opciones) + "]$"
    texto = input("Opcion: ").strip()
 
    while re.match(patron, texto) is None:
        print("Opcion invalida. Intente de nuevo.")
        texto = input("Opcion: ").strip()
 
    return texto
 
 
def leer_letra_nave(pendientes):
    """
    pide la letra de una nave hasta que sea valida y queden naves de ese tipo.
    recibe el diccionario de naves pendientes.
    retorna la letra en mayuscula.
    """

    texto = input("Nave (F/D/S/C/P/E): ").strip().upper()
 
    while texto not in pendientes or pendientes[texto] == 0:
        print("Nave invalida. Intente de nuevo.")
        texto = input("Nave (F/D/S/C/P/E): ").strip().upper()
 
    return texto
 
 
def leer_tramo():
    """
    pide un tramo con el formato z,x,y-z,x,y hasta que el formato sea valido.
    retorna dos tuplas: el punto desde y el punto hasta.
    """

    patron = r"^(\d{1,2}),(\d{1,2}),(\d{1,2})-(\d{1,2}),(\d{1,2}),(\d{1,2})$"
    texto = input("Desde-hasta: ").strip()
    coincidencia = re.match(patron, texto)
 
    while coincidencia is None:
        print("Formato invalido. Ejemplo: 3,5,4-3,5,5")
        texto = input("Desde-hasta: ").strip()
        coincidencia = re.match(patron, texto)
 
    desde = (int(coincidencia.group(1)), int(coincidencia.group(2)), int(coincidencia.group(3)))
    hasta = (int(coincidencia.group(4)), int(coincidencia.group(5)), int(coincidencia.group(6)))
    
    return desde, hasta
 
 

def dibujar_estado(nombre, cubo):
    """
    muestra el cubo de un jugador por capas de z, con encabezados de x y de y.
    recibe el nombre del jugador y su cubo.
    """

    tamanio = len(cubo)
    print("\nCubo de " + nombre)
 
    for z in range(1, tamanio + 1):
        print("========= CAPA z = " + str(z) + " =========")
 
        encabezado = "    "
        for x in range(1, tamanio + 1):
            encabezado = encabezado + "x" + str(x) + "  "
        print(encabezado)
 
        for y in range(1, tamanio + 1):
            fila = "y" + str(y) + "  "
            for x in range(1, tamanio + 1):
                if tablero.obtener_celda(cubo, (z, x, y)) == tablero.AGUA_SIN_EXPLORAR:
                    fila = fila + "~   "
                else:
                    fila = fila + "N   "
            print(fila)
 
    print("Referencias: ~ agua   N nave")
 
 

def mostrar_pendientes(pendientes):
    """
    muestra las naves que faltan ubicar, en el orden de la consigna.
    recibe el diccionario de naves pendientes.
    retorna la cantidad total de naves que faltan.
    """

    texto = "Pendientes:"
    total = 0
    for letra in "FDSCPE":
        if pendientes[letra] > 0:
            texto = texto + " " + letra + " x" + str(pendientes[letra])
            total = total + pendientes[letra]
 
    if total > 0:
        print(texto)
    else:
        print("Flota completa.")
    return total
 
 
def ubicacion_manual(cubo, mi_flota):
    """
    pide nave por nave hasta ubicar la flota completa.
    recibe el cubo y la flota del jugador, y los modifica.
    retorna la flota completa.
    """
    pendientes = flota.naves_pendientes(mi_flota)
 
    while mostrar_pendientes(pendientes) > 0:
        letra = leer_letra_nave(pendientes)
        desde, hasta = leer_tramo()
 
        if flota.ubicar_nave(cubo, mi_flota, letra, desde, hasta):
            print("Ubicada.")
        else:
            print("No se puede ubicar ahi. Intente de nuevo.")
 
        pendientes = flota.naves_pendientes(mi_flota)
 
    return mi_flota
 
 
def ubicacion_al_azar(cubo, mi_flota):
    """
    ubica la flota completa en forma automatica.
    recibe el cubo (lo modifica) y la flota del jugador.
    retorna la flota completa.
    """

    semilla = random.randint(1, 1000000)
    print("Flota ubicada automaticamente.")
    return flota.ubicacion_automatica(cubo, flota.CATALOGO, semilla)
 
 
# Opciones del submenu de ubicacion: numero -> (texto, funcion).
MENU_UBICACION = {
    "1": ("Ubicacion manual", ubicacion_manual),
    "2": ("Ubicacion automatica", ubicacion_al_azar),
}
 
 
def submenu_ubicacion(nombre):
    """
    muestra el submenu de ubicacion de la flota de un jugador.
    recibe el nombre del jugador.
    retorna el cubo y la flota del jugador ya ubicada.
    """

    cubo = tablero.crear_cubo(TAMANIO)
    mi_flota = {}
 
    print("\n--- Flota de " + nombre + " ---")
    for opcion in MENU_UBICACION:
        print(opcion + " - " + MENU_UBICACION[opcion][0])
    opcion = leer_opcion(MENU_UBICACION)
    mi_flota = MENU_UBICACION[opcion][1](cubo, mi_flota)
 
    return cubo, mi_flota
 
 
def flota_maquina(nombre):
    """
    crea el cubo de la maquina y ubica su flota en forma automatica.
    recibe el nombre de la maquina.
    retorna el cubo y la flota.
    """

    cubo = tablero.crear_cubo(TAMANIO)
    print("\n--- Flota de " + nombre + " ---")
    mi_flota = ubicacion_al_azar(cubo, {})
    return cubo, mi_flota
 

def partida_1v1():
    """Ubica las flotas de dos jugadores y dibuja el estado."""

    cubo1, flota1 = submenu_ubicacion("Jugador 1")
    cubo2, flota2 = submenu_ubicacion("Jugador 2")
    dibujar_estado("Jugador 1", cubo1)
    dibujar_estado("Jugador 2", cubo2)
    return True
 
 
def partida_vs_maquina():
    """Ubica la flota del jugador y la de la maquina, y dibuja el estado."""

    cubo1, flota1 = submenu_ubicacion("Jugador 1")
    cubo2, flota2 = flota_maquina("Maquina")
    dibujar_estado("Jugador 1", cubo1)
    return True
 
 
def partida_maquina_vs_maquina():
    """Ubica las flotas de las dos maquinas y dibuja el estado."""

    cubo1, flota1 = flota_maquina("Maquina 1")
    cubo2, flota2 = flota_maquina("Maquina 2")
    dibujar_estado("Maquina 1", cubo1)
    dibujar_estado("Maquina 2", cubo2)
    return True
 
 
def continuar_partida():
    """Todavia no disponible."""

    print("Opcion disponible en una proxima entrega.")
    return True
 
 
def salir():

    """Termina el programa."""
    print("Hasta luego.")
    return False
 
 
MENU_PRINCIPAL = {

    "1": ("Partida uno contra uno", partida_1v1),
    "2": ("Partida uno contra la maquina", partida_vs_maquina),
    "3": ("Partida maquina contra maquina", partida_maquina_vs_maquina),
    "4": ("Continuar una partida guardada", continuar_partida),
    "5": ("Salir", salir),
}
 
 
def menu_principal():
    """
    muestra el menu principal hasta que se elija salir.
    """

    seguir = True
    while seguir:
        print("\n===== OPERACION CUBO =====")
        for opcion in MENU_PRINCIPAL:
            print(opcion + " - " + MENU_PRINCIPAL[opcion][0])
        opcion = leer_opcion(MENU_PRINCIPAL)
        seguir = MENU_PRINCIPAL[opcion][1]()
 
 
menu_principal()
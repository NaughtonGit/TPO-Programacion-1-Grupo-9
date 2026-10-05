import random
import tablero

CATALOGO = {
    "E": {"nombre": "Estacion orbital", "celdas": 8, "cantidad": 1, "ejes": 3, "zona": "interior"},
    "P": {"nombre": "Portaaviones", "celdas": 5, "cantidad": 1, "ejes": 1, "zona": "superior"},
    "C": {"nombre": "Crucero", "celdas": 4, "cantidad": 1, "ejes": 1, "zona": "sin_extremos"},
    "S": {"nombre": "Submarino", "celdas": 3, "cantidad": 2, "ejes": 1, "zona": "inferior"},
    "D": {"nombre": "Destructor", "celdas": 3, "cantidad": 2, "ejes": 1, "zona": "libre"},
    "F": {"nombre": "Fragata", "celdas": 2, "cantidad": 3, "ejes": 1, "zona": "libre"},
}


def naves_pendientes(flota, catalogo=CATALOGO):
    """
    calcula cuantas naves de cada tipo faltan ubicar.
    recibe la flota del jugador y el catalogo de naves.
    retorna un diccionario con la cantidad de naves pendientes de ubicar por tipo.
    """
    pendientes = {}

    for letra in catalogo:
        pendientes[letra] = catalogo[letra]["cantidad"]

    for id_nave in flota:
        letra = flota[id_nave]["tipo"]
        pendientes[letra] = pendientes[letra] - 1

    return pendientes


def cumple_restriccion(nave, celdas, n):
    """
    verificar la regla de ubicacion propia de cada tipo de nave.
    recibe la letra del tipo de nave, un conjunto de celdas y el tamaño del tablero.
    retorna True si todas las celdas respetan la zona de esa nave.
    """
    zona = CATALOGO[nave]["zona"]
 
    for z, x, y in celdas:
        if zona == "inferior" and z > n // 2:
            return False
        if zona == "superior" and z <= n // 2:
            return False
        if zona == "sin_extremos" and (z == 1 or z == n):
            return False
        if zona == "interior" and (1 in (z, x, y) or n in (z, x, y)):
            return False
    return True

def calcular_ubicacion(cubo, flota, nave, desde, hasta):
    """
    aplicar todas las reglas de ubicacion a una nave y calcular las celdas que ocuparia.
    recibe un cubo, la flota del jugador, la letra del tipo de nave y dos tuplas con las coordenadas de los extremos.
    retorna las celdas que ocuparia la nave, o un conjunto vacio si rompe alguna regla.
    """
    n = len(cubo)
 
    if not tablero.validar_punto(cubo, desde) or not tablero.validar_punto(cubo, hasta):
        return set()
 
    ejes_distintos = 0
    for i in range(3):
        if desde[i] != hasta[i]:
            ejes_distintos = ejes_distintos + 1
    if ejes_distintos != CATALOGO[nave]["ejes"]:
        return set()
 
    celdas = set()
    for z in range(min(desde[0], hasta[0]), max(desde[0], hasta[0]) + 1):
        for x in range(min(desde[1], hasta[1]), max(desde[1], hasta[1]) + 1):
            for y in range(min(desde[2], hasta[2]), max(desde[2], hasta[2]) + 1):
                celdas.add((z, x, y))
    if len(celdas) != CATALOGO[nave]["celdas"]:
        return set()
 
    if not cumple_restriccion(nave, celdas, n):
        return set()
 
    for id_nave in flota:
        for z, x, y in celdas:
            for dz in range(-1, 2):
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if (z + dz, x + dx, y + dy) in flota[id_nave]["celdas"]:
                            return set()
 
    return celdas

def nuevo_id(flota, letra):
    """
    generar el identificador de la proxima nave de un tipo.
    recibe la flota del jugador y la letra del tipo de nave.
    retorna un string con el identificador de la proxima nave de ese tipo.
    """
    numero = 1
    while letra + str(numero) in flota:
        numero = numero + 1

    return letra + str(numero)
 
 
def ubicar_nave(cubo, flota, nave, desde, hasta):
    """
    ubicar una nave en el cubo, entre dos extremos.
    recibe el cubo, la flota del jugador, la letra del tipo de nave y dos tuplas con las coordenadas de los extremos.
    retorna true si la nave se ubico (el cubo y la flota quedan actualizados). 
    False si la nave no existe, ya no quedan de ese tipo, sale del cubo, no tiene la forma correcta, no cumple su regla propia o queda pegada a otra nave
    """
    if nave not in CATALOGO:
        return False
 
    if naves_pendientes(flota)[nave] <= 0:
        return False
 
    celdas = calcular_ubicacion(cubo, flota, nave, desde, hasta)
    if len(celdas) == 0:
        return False
 
    for punto in celdas:
        tablero.escribir_celda(cubo, punto, tablero.NAVE_OCULTA)
 
    flota[nuevo_id(flota, nave)] = {"tipo": nave, "celdas": celdas, "impactos": set()}
    return True

 
 
def ubicacion_automatica(cubo, catalogo, semilla):
    """
    ubicar la flota completa al azar, respetando las reglas. 
    prueba posiciones al azar para cada navehasta que una sea valida.
    recibe el cubo, el catalogo de naves y una semilla para el azar.
    retorna la flota completa .
    """
    random.seed(semilla)
    n = len(cubo)
    flota = {}
 
    for letra in catalogo:
        for numero in range(catalogo[letra]["cantidad"]):
            ubicada = False

            while not ubicada:
                desde = (random.randint(1, n), random.randint(1, n), random.randint(1, n))

                if letra == "E":
                    hasta = (desde[0] + 1, desde[1] + 1, desde[2] + 1)

                else:
                    eje = random.randint(0, 2)
                    hasta = list(desde)
                    hasta[eje] = hasta[eje] + catalogo[letra]["celdas"] - 1
                    hasta = tuple(hasta)


                ubicada = ubicar_nave(cubo, flota, letra, desde, hasta)
 
    return flota


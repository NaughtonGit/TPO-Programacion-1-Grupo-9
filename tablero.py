AGUA_SIN_EXPLORAR = 0

def crear_cubo(tamanio=8):
    """
    Recibe el tamaño del cubo 3D NxNxN.
    Ataja error por si ponen cualquier cosa ValueError si el tamaño es inválido.
    """
    if type(tamanio) != int or tamanio < 1:
        raise ValueError("Tamaño inválido")

    cubo = []

    for z in range(tamanio):
        capa = []

        for x in range(tamanio):
            fila = []

            for y in range(tamanio):
                fila.append(AGUA_SIN_EXPLORAR)

            capa.append(fila)

        cubo.append(capa)

    return cubo

def validar_punto(cubo, punto):
    """
    Recibe un cubo y un punto [z, x, y].
    Devuelve True si el punto está dentro del cubo.
    """

    if len(punto) != 3:
        return False

    tamanio = len(cubo)

    for coordenada in punto:
        if coordenada < 1 or coordenada > tamanio:
            return False

    return True


def obtener_celda(cubo, punto):
    """
    Recibe un cubo y un punto [z, x, y].
    Devuelve el contenido de esa celda.
    Lanza ValueError si el punto es inválido.
    """

    if not validar_punto(cubo, punto):
        raise ValueError("Punto inválido")

    z = punto[0]
    x = punto[1]
    y = punto[2]

    return cubo[z - 1][x - 1][y - 1]

# PRUEBAS
#Crea el cubo correctamente
print("\nPRUEBA crear_cubo")
cubo = crear_cubo(2)
print(cubo)
#valida la primera posicion del cubo recordar que empieza de 1
print("\nPRUEBA validar_punto")
print(validar_punto(cubo, [1, 1, 1]))
#Muestra que la columna 3 no existe porque se le pasa un cubo de 2x2x2
print(validar_punto(cubo, [2, 2, 3]))
#Se obtienen los valores de la primera locacion del cubo
print("\nPRUEBA obtener_celda")
print(obtener_celda(cubo, [1, 1, 1]))

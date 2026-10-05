AGUA_SIN_EXPLORAR = 0
NAVE_OCULTA = 1
AGUA_MARCADA = 2
IMPACTO = 3
HUNDIDO = 4
DETECTADO_SONAR = 5


# Relaciona cada estado de una celda con el simbolo que se muestra en el tablero.
# La nave oculta se muestra como agua para no revelar su posicion.
SIMBOLOS = {
    AGUA_SIN_EXPLORAR: "~",
    NAVE_OCULTA: "~",
    AGUA_MARCADA: "o",
    IMPACTO: "X",
    HUNDIDO: "#",
    DETECTADO_SONAR: "?"
}


def crear_cubo(tamanio=8):
    """
    Recibe el tamaño del cubo 3D NxNxN.
    Devuelve un cubo con todas sus celdas como agua sin explorar.
    Lanza ValueError si el tamaño es invalido.
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
    Devuelve True si el punto esta dentro del cubo.
    Devuelve False si el punto esta fuera del cubo.
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
    Lanza ValueError si el punto es invalido.
    """

    if not validar_punto(cubo, punto):
        raise ValueError("Punto inválido")

    z = punto[0]
    x = punto[1]
    y = punto[2]

    return cubo[z - 1][x - 1][y - 1]


def cambiar_celda(cubo, punto, valor):
    """
    Recibe un cubo, un punto [z, x, y] y un valor.
    Cambia el contenido de esa celda.
    Lanza ValueError si el punto es invalido.
    """

    if not validar_punto(cubo, punto):
        raise ValueError("Punto inválido")

    z = punto[0]
    x = punto[1]
    y = punto[2]

    cubo[z - 1][x - 1][y - 1] = valor


def obtener_plano_z(cubo, z):
    """
    Recibe un cubo y un valor z.
    Devuelve el plano que corresponde a ese valor z.
    Lanza ValueError si el plano indicado no existe.
    """

    tamanio = len(cubo)

    if z < 1 or z > tamanio:
        raise ValueError("Plano z inválido")

    return cubo[z - 1]


def crear_plano_z(cubo, z, mostrar_naves=False):
    """
    Recibe un cubo y un valor z.
    Devuelve un plano z graficado con x como columnas e y como filas.
    Si mostrar_naves es True, muestra las naves propias como N.
    """

    plano = obtener_plano_z(cubo, z)
    dibujo = "    "

    # Crea los encabezados de las columnas.
    for x in range(1, len(plano) + 1):
        dibujo = dibujo + "x" + str(x) + " "

    dibujo = dibujo + "\n"

    # Recorre primero las filas y, dentro de cada fila, las columnas.
    for y in range(1, len(plano) + 1):
        dibujo = dibujo + "y" + str(y) + "  "

        for x in range(1, len(plano) + 1):
            celda = plano[x - 1][y - 1]
            if mostrar_naves and celda == NAVE_OCULTA:
                simbolo = "N"
            else:
                simbolo = SIMBOLOS[celda]
            dibujo = dibujo + simbolo + " "

        dibujo = dibujo + "\n"

    return dibujo


def crear_matriz(filas, columnas, valor=0):
    """
    Recibe la cantidad de filas, columnas y un valor.
    Devuelve una matriz con todas sus posiciones cargadas con ese valor.
    """

    matriz = []

    for fila in range(filas):
        nueva_fila = []

        for columna in range(columnas):
            nueva_fila.append(valor)

        matriz.append(nueva_fila)

    return matriz


def obtener_valor_matriz(matriz, fila, columna):
    """
    Recibe una matriz, una fila y una columna.
    Devuelve el valor que se encuentra en esa posicion.
    """

    return matriz[fila][columna]


def cambiar_valor_matriz(matriz, fila, columna, valor):
    """
    Recibe una matriz, una fila, una columna y un valor.
    Cambia el valor que se encuentra en esa posicion.
    """

    matriz[fila][columna] = valor

import tablero


def busqueda_lineal(flota, punto):
    """
    buscar una coordenada dentro de todas las celdas de la flota.
    recibe la flota del jugador y una tupla con el punto (z, x, y).
    retorna el id de la nave encontrada y la cantidad de comparaciones.
    si no encuentra una nave retorna None y la cantidad de comparaciones.
    """

    comparaciones = 0

    for id_nave in flota:
        for celda in flota[id_nave]["celdas"]:
            comparaciones = comparaciones + 1

            if celda == punto:
                return id_nave, comparaciones

    return None, comparaciones


def detectar(cubo, flota, punto):
    """
    usar el radar para buscar una nave en un punto del cubo.
    recibe el cubo, la flota y una tupla con las coordenadas.
    retorna el id de la nave encontrada y la cantidad de comparaciones.
    si el punto no es valido retorna None y 0 comparaciones.
    """

    if not tablero.validar_punto(cubo, punto):
        return None, 0

    id_nave, comparaciones = busqueda_lineal(flota, punto)

    return id_nave, comparaciones


def mostrar_resultado(cubo, flota, punto):
    """
    mostrar el resultado de una busqueda del radar.
    recibe el cubo, la flota y el punto a buscar.
    retorna True si encontro una nave y False si no encontro.
    """

    if not tablero.validar_punto(cubo, punto):
        print("Punto invalido")
        return False

    id_nave, comparaciones = detectar(cubo, flota, punto)

    if id_nave != None:
        print("Radar: nave detectada")
        print("Nave:", id_nave)
        print("Comparaciones:", comparaciones)
        return True

    print("Radar: no se detecto ninguna nave")
    print("Comparaciones:", comparaciones)
    return False


# PRUEBAS

if __name__ == "__main__":

    cubo = tablero.crear_cubo(8)

    flota = {
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

    print("\nPRUEBA radar con nave")
    mostrar_resultado(cubo, flota, (3, 5, 4))

    print("\nPRUEBA radar sin nave")
    mostrar_resultado(cubo, flota, (8, 8, 8))

    print("\nPRUEBA radar punto invalido")
    mostrar_resultado(cubo, flota, (9, 2, 3))

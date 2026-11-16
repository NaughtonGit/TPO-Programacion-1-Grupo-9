import time

import tablero


def _crear_metricas(comparaciones, tiempo_ms, profundidad_max=0):
    """Devuelve las métricas en un formato común para las búsquedas."""
    return {
        "comparaciones": comparaciones,
        "tiempo_ms": tiempo_ms,
        "profundidad_max": profundidad_max,
    }


def busqueda_lineal(flota, punto):
    """Busca una coordenada recorriendo las celdas de cada nave.

    Devuelve ``(id_nave, metricas)``. Si no encuentra una nave, id_nave es
    None. Las métricas tienen el mismo formato que las de busqueda_optimizada.
    """
    punto = tuple(punto)
    comparaciones = 0
    inicio = time.perf_counter()

    for id_nave, datos in flota.items():
        for celda in datos["celdas"]:
            comparaciones += 1
            if tuple(celda) == punto:
                tiempo_ms = (time.perf_counter() - inicio) * 1000
                return id_nave, _crear_metricas(comparaciones, tiempo_ms)

    tiempo_ms = (time.perf_counter() - inicio) * 1000
    return None, _crear_metricas(comparaciones, tiempo_ms)


def busqueda_optimizada(flota, punto, mapa=None):
    """Busca una coordenada en un índice hash.

    Para varias consultas se debe construir el mapa una sola vez con
    construir_mapa y pasarlo en cada llamada. Si no se recibe, se crea uno
    para facilitar consultas aisladas.
    """
    if mapa is None:
        mapa = construir_mapa(flota)

    inicio = time.perf_counter()
    resultado = mapa.get(tuple(punto))
    tiempo_ms = (time.perf_counter() - inicio) * 1000

    return resultado, _crear_metricas(1, tiempo_ms)


def busqueda_recursiva(flota, punto):
    """Busca una coordenada en la flota mediante llamadas recursivas."""
    punto = tuple(punto)
    celdas = []
    for id_nave, datos in flota.items():
        for celda in datos["celdas"]:
            celdas.append((id_nave, tuple(celda)))

    inicio = time.perf_counter()
    metricas = {"comparaciones": 0, "profundidad_max": 0}

    def buscar(inicio_busqueda, fin_busqueda, profundidad):
        if inicio_busqueda >= fin_busqueda:
            return None

        metricas["profundidad_max"] = max(metricas["profundidad_max"], profundidad)
        mitad = (inicio_busqueda + fin_busqueda) // 2
        metricas["comparaciones"] += 1
        id_nave, celda = celdas[mitad]
        if celda == punto:
            return id_nave

        encontrada = buscar(inicio_busqueda, mitad, profundidad + 1)
        if encontrada is not None:
            return encontrada
        return buscar(mitad + 1, fin_busqueda, profundidad + 1)

    resultado = buscar(0, len(celdas), 1)
    tiempo_ms = (time.perf_counter() - inicio) * 1000
    return resultado, _crear_metricas(
        metricas["comparaciones"], tiempo_ms, metricas["profundidad_max"]
    )


def construir_mapa(flota):
    """Construye una vez el índice de coordenada a identificador de nave."""
    mapa = {}
    for id_nave, datos in flota.items():
        for celda in datos["celdas"]:
            mapa[tuple(celda)] = id_nave
    return mapa


def mapa_probabilidad(cubo):
    """Cuenta cuántas ubicaciones posibles de naves contienen cada celda.

    El resultado es una matriz NxNxN. No usa la flota real: solo descarta
    celdas que ya se sabe que son agua o pertenecen a una nave hundida.
    """
    tamanio = len(cubo)
    probabilidades = tablero.crear_cubo(tamanio)
    estados_posibles = (
        tablero.AGUA_SIN_EXPLORAR,
        tablero.NAVE_OCULTA,
        tablero.DETECTADO_SONAR,
        tablero.IMPACTO,
    )

    def ubicacion_posible(celdas, tipo):
        for punto in celdas:
            if tablero.obtener_celda(cubo, punto) not in estados_posibles:
                return False
            z = punto[0]
            if tipo == "P" and z <= tamanio // 2:
                return False
            if tipo == "S" and z > tamanio // 2:
                return False
            if tipo == "C" and z in (1, tamanio):
                return False
            if tipo == "E" and any(coordenada in (1, tamanio) for coordenada in punto):
                return False
        return True

    def sumar_ubicacion(celdas):
        for z, x, y in celdas:
            probabilidades[z - 1][x - 1][y - 1] += 1

    # Cada longitud aparece tantas veces como naves de ese tamaño hay.
    for longitud, cantidad, tipo in (
        (2, 3, "F"), (3, 2, "D"), (3, 2, "S"), (4, 1, "C"), (5, 1, "P")
    ):
        for repeticion in range(cantidad):
            for eje in range(3):
                for z in range(1, tamanio + 1):
                    for x in range(1, tamanio + 1):
                        for y in range(1, tamanio + 1):
                            inicio = [z, x, y]
                            fin = inicio[eje] + longitud - 1
                            if fin > tamanio:
                                continue

                            celdas = []
                            for desplazamiento in range(longitud):
                                punto = list(inicio)
                                punto[eje] += desplazamiento
                                celdas.append(tuple(punto))

                            if ubicacion_posible(celdas, tipo):
                                sumar_ubicacion(celdas)

    # La estación ocupa un bloque 2x2x2.
    for z in range(1, tamanio):
        for x in range(1, tamanio):
            for y in range(1, tamanio):
                celdas = []
                for dz in range(2):
                    for dx in range(2):
                        for dy in range(2):
                            celdas.append((z + dz, x + dx, y + dy))
                if ubicacion_posible(celdas, "E"):
                    sumar_ubicacion(celdas)

    # Los impactos previos orientan a la máquina hacia celdas contiguas.
    for z in range(1, tamanio + 1):
        for x in range(1, tamanio + 1):
            for y in range(1, tamanio + 1):
                punto = (z, x, y)
                if tablero.obtener_celda(cubo, punto) != tablero.IMPACTO:
                    continue
                for vecino in tablero.obtener_vecinos(cubo, punto):
                    vz, vx, vy = vecino
                    if tablero.obtener_celda(cubo, vecino) in estados_posibles:
                        probabilidades[vz - 1][vx - 1][vy - 1] += 20

    return probabilidades


def obtener_maximos_probabilidad(cubo, probabilidades):
    """Devuelve las celdas disponibles con la puntuación más alta."""
    maximo = -1
    puntos = []
    tamanio = len(cubo)
    estados_disponibles = (
        tablero.AGUA_SIN_EXPLORAR,
        tablero.NAVE_OCULTA,
        tablero.DETECTADO_SONAR,
    )

    for z in range(1, tamanio + 1):
        for x in range(1, tamanio + 1):
            for y in range(1, tamanio + 1):
                punto = (z, x, y)
                if tablero.obtener_celda(cubo, punto) not in estados_disponibles:
                    continue
                puntuacion = probabilidades[z - 1][x - 1][y - 1]
                if puntuacion > maximo:
                    maximo = puntuacion
                    puntos = [punto]
                elif puntuacion == maximo:
                    puntos.append(punto)

    return puntos


def detectar(cubo, flota, punto, mapa=None):
    """Valida el punto y devuelve la nave encontrada junto con sus métricas.

    Si se pasa un mapa reutilizable, usa la búsqueda optimizada. Sin mapa,
    usa la búsqueda lineal y no reconstruye un índice para esa consulta.
    """
    try:
        punto_valido = tablero.validar_punto(cubo, punto)
    except (TypeError, ValueError):
        punto_valido = False
    if not punto_valido:
        return None, _crear_metricas(0, 0.0)

    if mapa is None:
        return busqueda_lineal(flota, punto)
    return busqueda_optimizada(flota, punto, mapa)


def sonar_plano(cubo, eje, valor):
    """Devuelve las coordenadas de un plano y marca las naves detectadas.

    Las coordenadas usan índices 1-based. Las celdas con naves ocultas quedan
    marcadas como DETECTADO_SONAR. Esta función no presenta mensajes.
    """
    if eje not in ("z", "x", "y"):
        raise ValueError("Eje inválido. Use 'z', 'x' o 'y'.")

    n = len(cubo)
    if type(valor) is not int or valor < 1 or valor > n:
        raise ValueError("Plano inválido")

    if eje == "z":
        plano = [(valor, x, y) for x in range(1, n + 1) for y in range(1, n + 1)]
    elif eje == "x":
        plano = [(z, valor, y) for z in range(1, n + 1) for y in range(1, n + 1)]
    else:
        plano = [(z, x, valor) for z in range(1, n + 1) for x in range(1, n + 1)]

    for punto in plano:
        if tablero.obtener_celda(cubo, punto) == tablero.NAVE_OCULTA:
            tablero.cambiar_celda(cubo, punto, tablero.DETECTADO_SONAR)

    return plano

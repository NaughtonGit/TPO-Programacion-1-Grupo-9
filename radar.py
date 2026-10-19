import time
import tablero


def busqueda_lineal(flota, punto):
    """
    Buscar una coordenada dentro de todas las celdas de la flota.
    Recibe: flota (dict), punto (tupla z,x,y).
    Devuelve: id de la nave encontrada y cantidad de comparaciones.
    Si no encuentra una nave, retorna None y la cantidad de comparaciones.
    """
    comparaciones = 0

    for id_nave in flota:
        for celda in flota[id_nave]["celdas"]:
            comparaciones += 1
            if celda == punto:
                return id_nave, comparaciones

    return None, comparaciones


def busqueda_optimizada(flota, punto, mapa=None):
    """
    Búsqueda optimizada usando un diccionario hash para acceso directo.
    Recibe: flota (dict), punto (tupla z,x,y) y, opcionalmente, un índice
    creado con construir_mapa.
    Devuelve: id de la nave encontrada o None, más métricas.
    """
    # Para varias consultas, se construye el índice una vez y se reutiliza.
    # Si no se recibe, se prepara aquí por comodidad.
    if mapa is None:
        mapa = construir_mapa(flota)

    # La métrica mide la consulta al índice, no su preparación.
    inicio = time.perf_counter()
    resultado = mapa.get(tuple(punto))
    tiempo_ms = (time.perf_counter() - inicio) * 1000

    return resultado, {
        "comparaciones": 1,
        "tiempo_ms": tiempo_ms,
        "profundidad_max": 0
    }


def construir_mapa(flota):
    """Construye un índice coordenada -> nave a partir de una flota.

    Recibe una flota (diccionario) y devuelve un diccionario hash que permite
    consultar en tiempo promedio constante qué nave ocupa cada coordenada.
    """
    mapa = {}
    for id_nave, datos in flota.items():
        for celda in datos["celdas"]:
            mapa[tuple(celda)] = id_nave
    return mapa


def detectar(cubo, flota, punto):
    """
    Usar el radar para buscar una nave en un punto del cubo.
    Recibe: cubo, flota y una tupla con las coordenadas.
    Devuelve: id de la nave encontrada y cantidad de comparaciones.
    Si el punto no es válido, retorna None y 0 comparaciones.
    """
    if not tablero.validar_punto(cubo, punto):
        return None, 0

    return busqueda_lineal(flota, punto)


def mostrar_resultado(cubo, flota, punto):
    """
    Muestra el resultado de una búsqueda del radar.
    Recibe: cubo, flota y el punto a buscar.
    Devuelve: True si hubo una nave, False si no.
    """
    if not tablero.validar_punto(cubo, punto):
        print("Punto invalido")
        return False

    id_nave, comparaciones = detectar(cubo, flota, punto)

    if id_nave is not None:
        print("Radar: nave detectada")
        print("Nave:", id_nave)
        print("Comparaciones:", comparaciones)
        return True

    print("Radar: no se detecto ninguna nave")
    print("Comparaciones:", comparaciones)
    return False


def sonar_plano(cubo, eje, valor):
    """
    Sonar por planos: revela todas las coordenadas de un plano del cubo.
    Recibe: cubo (lista 3D), eje ('z','x','y') y valor (int).
    Devuelve la lista de coordenadas del plano con índices 1-based.
    Las celdas con naves ocultas quedan marcadas como detectadas por sonar.
    """
    if eje not in ("z", "x", "y"):
        raise ValueError("Eje inválido. Use 'z', 'x' o 'y'.")

    n = len(cubo)
    if type(valor) is not int or valor < 1 or valor > n:
        raise ValueError("Plano inválido")

    plano = []

    if eje == "z":
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                plano.append((valor, x, y))
    elif eje == "x":
        for z in range(1, n + 1):
            for y in range(1, n + 1):
                plano.append((z, valor, y))
    else:
        for z in range(1, n + 1):
            for x in range(1, n + 1):
                plano.append((z, x, valor))

    # El cubo del rival conserva las posiciones de las naves como estados.
    # Marcar esos contactos permite que otras partes del juego los muestren.
    for punto in plano:
        if tablero.obtener_celda(cubo, punto) == tablero.NAVE_OCULTA:
            tablero.cambiar_celda(cubo, punto, tablero.DETECTADO_SONAR)

    return plano

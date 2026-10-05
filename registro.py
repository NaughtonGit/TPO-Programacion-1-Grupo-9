def crear_registro():
    """
    Recibe nada.
    Crea y devuelve una lista vacia.
    """
    return []


def agregar_evento(registro, turno, jugador, accion, resultado):
    """
    Recibe el registro y los datos para crear el evento.
    Agrega el evento al historial de la partida.
    Devuelve el evento agregado.
    """
    evento = {
        "turno": turno,
        "jugador": jugador,
        "accion": accion,
        "resultado": resultado
    }

    registro.append(evento)

    return evento


def obtener_historial(registro):
    """
    Recibe el registro de una partida.
    Devuelve el historial completo.
    """
    return registro


def contar_eventos(registro):
    """
    Recibe el registro de una partida.
    Devuelve la cantidad total de eventos registrados.
    """
    return len(registro)


def contar_eventos_jugador(registro, jugador):
    """
    Recibe el registro y el nombre de un jugador.
    Devuelve la cantidad de eventos realizados por ese jugador.
    """
    cantidad = 0

    for evento in registro:
        if evento["jugador"] == jugador:
            cantidad = cantidad + 1

    return cantidad


def contar_resultado(registro, resultado):
    """
    Recibe el registro y un resultado.
    Devuelve cuantas veces aparece ese resultado.
    """
    cantidad = 0

    for evento in registro:
        if evento["resultado"] == resultado:
            cantidad = cantidad + 1

    return cantidad


def obtener_estadisticas(registro):
    """
    Recibe el registro de una partida.
    Devuelve un diccionario con estadisticas generales.
    """
    estadisticas = {
        "total_eventos": len(registro),
        "impactos": 0,
        "agua": 0,
        "hundidos": 0
    }

    for evento in registro:

        if evento["resultado"] == "impacto":
            estadisticas["impactos"] = estadisticas["impactos"] + 1

        if evento["resultado"] == "agua":
            estadisticas["agua"] = estadisticas["agua"] + 1

        if evento["resultado"] == "hundido":
            estadisticas["hundidos"] = estadisticas["hundidos"] + 1

    return estadisticas


def crear_resumen(registro, ganador):
    """
    Recibe el registro de una partida y el ganador.
    Devuelve un diccionario con el resumen final de la partida.
    """
    estadisticas = obtener_estadisticas(registro)

    resumen = {
        "ganador": ganador,
        "total_eventos": estadisticas["total_eventos"],
        "impactos": estadisticas["impactos"],
        "agua": estadisticas["agua"],
        "hundidos": estadisticas["hundidos"]
    }

    return resumen
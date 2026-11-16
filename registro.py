import csv
import json
import re
from datetime import datetime
from pathlib import Path

DIRECTORIO_PARTIDAS = Path("datos") / "partidas"
PATRON_NOMBRE_PARTIDA = r"[\w][\w -]{0,39}"


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


def _preparar_json(valor):
    """Convierte tuplas y conjuntos del estado de juego a valores JSON."""
    if isinstance(valor, tuple):
        return {"__tipo_python__": "tupla", "elementos": [_preparar_json(x) for x in valor]}
    if isinstance(valor, set):
        return {"__tipo_python__": "conjunto", "elementos": [_preparar_json(x) for x in sorted(valor)]}
    if isinstance(valor, dict):
        return {
            "__tipo_python__": "diccionario",
            "elementos": [[_preparar_json(clave), _preparar_json(elemento)]
                          for clave, elemento in valor.items()],
        }
    if isinstance(valor, list):
        return [_preparar_json(elemento) for elemento in valor]
    return valor


def _restaurar_json(valor):
    """Restaura tuplas y conjuntos guardados con _preparar_json."""
    if isinstance(valor, dict):
        tipo = valor.get("__tipo_python__")
        if tipo == "tupla":
            return tuple(_restaurar_json(x) for x in valor["elementos"])
        if tipo == "conjunto":
            return set(_restaurar_json(x) for x in valor["elementos"])
        if tipo == "diccionario":
            return {_restaurar_json(clave): _restaurar_json(elemento)
                    for clave, elemento in valor["elementos"]}
        return {clave: _restaurar_json(elemento) for clave, elemento in valor.items()}
    if isinstance(valor, list):
        return [_restaurar_json(elemento) for elemento in valor]
    return valor


def _nombre_archivo(nombre):
    """Convierte un nombre validado en un identificador relativo seguro."""
    return re.sub(r"\s+", "_", nombre.strip())


def guardar_partida(estado, nombre):
    """Recibe estado y nombre; guarda el JSON y devuelve su ruta relativa.

    Lanza ValueError si el nombre no cumple el patrón y FileExistsError si
    ya existe una partida con ese nombre.
    """
    if not isinstance(nombre, str) or re.fullmatch(PATRON_NOMBRE_PARTIDA, nombre.strip()) is None:
        raise ValueError("Nombre inválido. Use hasta 40 letras, números, espacios, guiones o guiones bajos.")

    nombre = nombre.strip()
    carpeta = DIRECTORIO_PARTIDAS
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / (_nombre_archivo(nombre) + ".json")
    if ruta.exists():
        raise FileExistsError("Ya existe una partida guardada con ese nombre.")

    datos = {
        "nombre": nombre,
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "ganador": _determinar_ganador(estado),
        "estado": _preparar_json(estado),
    }
    with ruta.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
    return ruta


def cargar_partida(nombre):
    """Recibe el nombre guardado y devuelve el estado restaurado desde JSON.

    Lanza ValueError si el nombre es inválido y FileNotFoundError si no existe.
    """
    if not isinstance(nombre, str) or re.fullmatch(PATRON_NOMBRE_PARTIDA, nombre.strip()) is None:
        raise ValueError("Nombre de partida inválido.")
    ruta = DIRECTORIO_PARTIDAS / (_nombre_archivo(nombre) + ".json")
    with ruta.open("r", encoding="utf-8") as archivo_json:
        datos = json.load(archivo_json)
    return _restaurar_json(datos["estado"])


def obtener_detalle_partidas():
    """Devuelve metadatos de las partidas para mostrarlos en el integrador."""
    carpeta = DIRECTORIO_PARTIDAS
    if not carpeta.exists():
        return []

    partidas = []
    for ruta in sorted(carpeta.glob("*.json")):
        with ruta.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        estado = _restaurar_json(datos["estado"])
        partidas.append({
            "nombre": datos.get("nombre", ruta.stem),
            "identificador": ruta.stem,
            "fecha": datos.get("fecha"),
            "archivo": str(ruta),
            "turno": estado.get("turno"),
            "jugadores": [j.get("nombre") for j in estado.get("jugadores", [])],
            "ganador": datos.get("ganador"),
        })
    return partidas


def listar_partidas():
    """Devuelve los nombres de las partidas guardadas."""
    return [partida["nombre"] for partida in obtener_detalle_partidas()]


def _determinar_ganador(estado):
    """Calcula el ganador a partir de las flotas, si la partida terminó."""
    import flota as modulo_flota

    jugadores = estado.get("jugadores", [])
    for indice, jugador in enumerate(jugadores):
        rival = jugadores[1 - indice] if len(jugadores) == 2 else None
        if rival and rival.get("flota") and modulo_flota.flota_hundida(rival["flota"]):
            return jugador.get("nombre")
    return None


def exportar_partidas(archivo_destino="partidas_exportadas.csv"):
    """Exporta a CSV el resumen de todas las partidas guardadas.

    Devuelve la ruta del archivo CSV generado.
    """
    partidas = obtener_detalle_partidas()
    ruta = Path(archivo_destino)
    if ruta.is_absolute() or ".." in ruta.parts:
        raise ValueError("La ruta de exportación debe ser relativa al proyecto.")
    if ruta.suffix.lower() != ".csv":
        ruta = ruta.with_suffix(".csv")
    if ruta.parent != Path(""):
        ruta.parent.mkdir(parents=True, exist_ok=True)

    columnas = ("nombre", "fecha", "jugadores", "ganador", "turno", "archivo")
    with ruta.open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        for partida in partidas:
            fila = {columna: partida[columna] for columna in columnas}
            fila["jugadores"] = ", ".join(j for j in partida["jugadores"] if j)
            escritor.writerow(fila)
    return ruta


def obtener_ranking():
    """Devuelve jugadores ordenados por victorias y luego por partidas jugadas."""
    ranking = {}
    for partida in obtener_detalle_partidas():
        for jugador in partida["jugadores"]:
            if not jugador:
                continue
            datos = ranking.setdefault(jugador, {"jugador": jugador, "partidas": 0, "victorias": 0})
            datos["partidas"] += 1
            if partida["ganador"] == jugador:
                datos["victorias"] += 1
    return sorted(ranking.values(), key=lambda datos: (-datos["victorias"], -datos["partidas"], datos["jugador"].lower()))

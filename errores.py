class ErrorOperacionCubo(Exception):
    """Clase base de todos los errores propios del juego."""


class ConfiguracionInvalida(ErrorOperacionCubo):
    """Los datos para crear una partida no son correctos."""


class JugadaInvalida(ErrorOperacionCubo):
    """La jugada no se puede realizar. El turno no avanza."""


class ArmaNoDisponible(JugadaInvalida):
    """El arma elegida todavia no esta implementada."""


class SinMunicion(JugadaInvalida):
    """No queda municion del arma elegida."""


class PuntoFueraDelCubo(JugadaInvalida):
    """El objetivo esta fuera del cubo."""


class CeldaYaAtacada(JugadaInvalida):
    """La celda ya habia recibido un disparo."""


class PartidaTerminada(JugadaInvalida):
    """Ya hay un ganador y no se pueden realizar mas jugadas."""

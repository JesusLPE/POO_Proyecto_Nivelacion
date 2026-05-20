from .persona import Persona

class Coordinador(Persona):
    """Clase que representa al coordinador del sistema."""

    def obtener_rol(self):
        return "coordinador"
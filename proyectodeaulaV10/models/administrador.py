from .persona import Persona

class Administrador(Persona):
    """Clase que representa al administrador del sistema."""

    def obtener_rol(self):
        return "administrador"
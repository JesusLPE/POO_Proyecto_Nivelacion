from .persona import Persona

class Administrador(Persona):
    def obtener_rol(self):
        return "administrador"
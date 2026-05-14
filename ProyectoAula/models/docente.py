from .persona import Persona

class Docente(Persona):
    def __init__(self, nombre, apellido, email, password, especialidad):
        super().__init__(nombre, apellido, email, password)
        self.especialidad = especialidad

    def obtener_rol(self):
        return "docente"
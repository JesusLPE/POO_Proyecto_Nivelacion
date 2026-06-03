from .persona import Persona

class Docente(Persona):
    """Clase que representa a un docente del sistema."""

    def __init__(self, nombre, apellido, email, password, especialidad):
        super().__init__(nombre, apellido, email, password)
        self.especialidad = especialidad

    def obtener_rol(self):
        return "docente"

    def registrar_nota(self, estudiante, asignatura, nota):
        # Simulación de registro de nota en fase 1.
        print(f"[SIMULACIÓN] Docente {self.nombre} registra nota {nota} a {estudiante.nombre} en {asignatura}")
        # En la fase 2 se podría crear un objeto Calificacion y asociarlo al estudiante.

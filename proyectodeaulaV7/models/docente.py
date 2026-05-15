from .persona import Persona

class Docente(Persona):
    def __init__(self, nombre, apellido, email, password, especialidad):
        super().__init__(nombre, apellido, email, password)
        self.especialidad = especialidad

    def obtener_rol(self):
        return "docente"

    def registrar_nota(self, estudiante, asignatura, nota):
        # Simulación de interacción con Estudiante
        print(f"[SIMULACIÓN] Docente {self.nombre} registra nota {nota} a {estudiante.nombre} en {asignatura}")
        # En fase 2 aquí se crearía una Calificacion y se añadiría al estudiante
from .persona import Persona

class Estudiante(Persona):
    def __init__(self, nombre, apellido, email, password, matricula, carrera):
        super().__init__(nombre, apellido, email, password)
        self.matricula = matricula
        self.carrera = carrera
        self.tareas_subidas = []   # lista de diccionarios con tareas

    def obtener_rol(self):
        return "estudiante"

    def subir_tarea(self, titulo, archivo, fecha_entrega):
        self.tareas_subidas.append({
            "titulo": titulo,
            "archivo": archivo,
            "fecha": fecha_entrega,
            "calificacion": None
        })
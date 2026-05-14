from .persona import Persona

class Estudiante(Persona):
    def __init__(self, nombre, apellido, email, password, matricula, carrera):
        super().__init__(nombre, apellido, email, password)
        self.matricula = matricula
        self.carrera = carrera
        # En fase 2 aquí se guardarán las tareas reales
        self.tareas_subidas = []   # lista simulada

    def obtener_rol(self):
        return "estudiante"

    def subir_tarea(self, titulo, archivo, fecha_entrega):
        # SOLO SIMULACIÓN – No guarda realmente
        print(f"[SIMULACIÓN] El estudiante {self.nombre} subió la tarea '{titulo}'")
        # En fase 2 se agregaría a self.tareas_subidas

    def calcular_promedio(self):
        # Simulación: retorna un valor fijo
        return 0.0
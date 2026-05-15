from models.persona import Persona
from models.matricula import Matricula  # Importación corregida

class Estudiante(Persona):
    """Clase concreta que representa a un Estudiante."""

    def __init__(self, nombre, apellido, email, password, matricula, carrera):
        super().__init__(nombre, apellido, email, password)  # Herencia
        self.__matricula = matricula
        self.carrera = carrera
        self.__tareas_subidas = []  # Lista simulada
        self.__matriculas = []      # Nueva lista para relación con Matricula
    
    def obtener_rol(self):
        return "estudiante"
    
    def agregar_matricula(self, matricula: Matricula):
        """Agrega una matrícula a la lista del estudiante."""
        self.__matriculas.append(matricula)
        print(f"[SIMULACIÓN] Matrícula agregada a {self.nombre}")

    def subir_tarea(self, titulo, archivo, fecha_entrega):
        # Solo simulación
        print(f"[SIMULACIÓN] El estudiante {self.nombre} subió la tarea '{titulo}'")

    def calcular_promedio(self):
        # Simulación: retorna un valor fijo
        return 0.0
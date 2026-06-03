from models.persona import Persona
from models.matricula import Matricula

class Estudiante(Persona):
    def __init__(self, nombre, apellido, email, password, matricula, carrera):
        super().__init__(nombre, apellido, email, password)
        self.__matricula = matricula
        self.carrera = carrera
        self.__tareas_subidas = []
        self.__matriculas = []

    @property
    def matricula(self):
        return self.__matricula

    def obtener_rol(self):
        return "estudiante"

    def agregar_matricula(self, matricula: Matricula):
        self.__matriculas.append(matricula)
        print(f"[SIMULACIÓN] Matrícula agregada a {self.nombre}")

    def subir_tarea(self, titulo, archivo, fecha_entrega):
        print(f"[SIMULACIÓN] El estudiante {self.nombre} subió la tarea '{titulo}'")

    def calcular_promedio(self):
        return 0.0
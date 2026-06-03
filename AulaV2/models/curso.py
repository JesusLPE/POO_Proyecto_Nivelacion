from typing import Optional
from .horario import Horario
from .modalidad import Modalidad

class Curso:
    def __init__(self, id: int, nombre: str, duracion_semanas: int, total_horas: int):
        self._id = id
        self._nombre = nombre
        self._duracion_semanas = duracion_semanas
        self._total_horas = total_horas
        self._horario: Optional[Horario] = None
        self._modalidad: Optional[Modalidad] = None
        self.docente_email = None

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def horario(self):
        return self._horario

    @property
    def modalidad(self):
        return self._modalidad

    def asignar_horario(self, horario: Horario):
        self._horario = horario
        print(f"[SIMULACIÓN] Horario asignado a {self._nombre}")

    def asignar_modalidad(self, modalidad: Modalidad):
        self._modalidad = modalidad
        print(f"[SIMULACIÓN] Modalidad asignada a {self._nombre}")

    def info(self):
        return f"{self._nombre} ({self._duracion_semanas} semanas, {self._total_horas}h)"
    
    def asignar_docente(self, email):
        self.docente_email = email
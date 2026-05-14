# curso.py
from typing import Optional

class Horario:
    def __init__(self, id: int, dia: str, hora_inicio: str, hora_fin: str):
        self._id = id
        self._dia = dia
        self._hora_inicio = hora_inicio
        self._hora_fin = hora_fin

class Modalidad:
    def __init__(self, id: int, nombre: str, descripcion: str, estado: bool, plataforma: str = ""):
        self._id = id
        self._nombre = nombre
        self._descripcion = descripcion
        self._estado = estado
        self._plataforma = plataforma

class Curso:
    def __init__(self, id: int, nombre: str, duracion_semanas: int, total_horas: int):
        self._id = id
        self._nombre = nombre
        self._duracion_semanas = duracion_semanas
        self._total_horas = total_horas
        self._horario: Optional[Horario] = None
        self._modalidad: Optional[Modalidad] = None

    def asignar_horario(self, horario: Horario):
        self._horario = horario
        print(f"[SIMULACIÓN] Horario asignado a {self._nombre}")

    def asignar_modalidad(self, modalidad: Modalidad):
        self._modalidad = modalidad
        print(f"[SIMULACIÓN] Modalidad asignada a {self._nombre}")

    def info(self):
        return f"{self._nombre} ({self._duracion_semanas} semanas, {self._total_horas}h)"
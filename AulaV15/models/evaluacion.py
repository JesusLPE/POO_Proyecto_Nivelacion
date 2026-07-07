from abc import ABC, abstractmethod
from datetime import date


class Evaluacion(ABC):
    """OCP – nueva modalidad de evaluación = nueva subclase, sin tocar las existentes."""

    def __init__(self, id: int, tipo: str, fecha: date, ponderacion: float):
        self._id = id
        self._tipo = tipo
        self._fecha = fecha
        self._ponderacion = ponderacion

    @abstractmethod
    def calcular_promedio(self, notas: list) -> float: pass

    @property
    def tipo(self):
        return self._tipo

    @property
    def ponderacion(self):
        return self._ponderacion


class Examen(Evaluacion):
    def __init__(self, id: int, fecha: date, ponderacion: float = 0.6):
        super().__init__(id, "Examen", fecha, ponderacion)

    def calcular_promedio(self, notas: list) -> float:
        return round(sum(notas) / len(notas) * self._ponderacion, 2) if notas else 0.0


class TrabajoPractico(Evaluacion):
    def __init__(self, id: int, fecha: date, ponderacion: float = 0.4):
        super().__init__(id, "Trabajo Práctico", fecha, ponderacion)

    def calcular_promedio(self, notas):
        return round(sum(notas) / len(notas) * self._ponderacion, 2) if notas else 0.0

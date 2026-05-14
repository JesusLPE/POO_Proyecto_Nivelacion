from abc import ABC, abstractmethod
from datetime import date

class Evaluacion(ABC):
    def __init__(self, id: int, tipo: str, fecha: date):
        self._id = id
        self._tipo = tipo
        self._fecha = fecha

    @abstractmethod
    def calcular_promedio(self, notas: list) -> float:
        """Método abstracto para calcular promedio según tipo de evaluación"""
        pass

    def __str__(self):
        return f"Evaluación {self._tipo} - {self._fecha}"

class Examen(Evaluacion):
    def __init__(self, id: int, fecha: date, ponderacion: float = 0.6):
        super().__init__(id, "Examen", fecha)
        self._ponderacion = ponderacion

    def calcular_promedio(self, notas: list) -> float:
        # El examen tiene una sola nota, devuelve esa nota * ponderación
        if not notas:
            return 0.0
        return notas[0] * self._ponderacion

class TrabajoPractico(Evaluacion):
    def __init__(self, id: int, fecha: date, cantidad_entregas: int):
        super().__init__(id, "Trabajo Práctico", fecha)
        self._cantidad_entregas = cantidad_entregas

    def calcular_promedio(self, notas: list) -> float:
        # Promedio simple de todas las entregas
        if not notas:
            return 0.0
        return sum(notas) / len(notas)
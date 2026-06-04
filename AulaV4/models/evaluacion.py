from abc import ABC, abstractmethod
from datetime import date

class Evaluacion(ABC):
    def __init__(self, id: int, tipo: str, fecha: date):
        self._id = id
        self._tipo = tipo
        self._fecha = fecha

    @abstractmethod
    def calcular_promedio(self, notas: list) -> float:
        pass

class Examen(Evaluacion):
    def __init__(self, id: int, fecha: date, ponderacion: float = 0.6):
        super().__init__(id, "Examen", fecha)
        self._ponderacion = ponderacion

    def calcular_promedio(self, notas: list) -> float:
        # Simulación: retorna un valor fijo para demostrar polimorfismo
        return 7.5

class TrabajoPractico(Evaluacion):
    def __init__(self, id: int, fecha: date, cantidad_entregas: int):
        super().__init__(id, "Trabajo Práctico", fecha)
        self._cantidad_entregas = cantidad_entregas

    def calcular_promedio(self, notas: list) -> float:
        return 8.0
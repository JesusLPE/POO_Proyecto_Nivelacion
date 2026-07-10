from abc import ABC, abstractmethod
from datetime import date


# POO: Clase abstracta (ABC) -> no se puede instanciar directamente
# POO: Polimorfismo con clases abstractas -> base para Examen/TrabajoPractico
# SOLID -> OCP (Open/Closed): se pueden agregar nuevos tipos de evaluación
# (ej. Quiz) sin modificar esta clase ni las ya existentes
class Evaluacion(ABC):
    """Base para tipos de evaluacion intercambiables."""

    # POO: Constructor | POO: Propiedades
    def __init__(self, id: int, tipo: str, fecha: date, ponderacion: float):
        self.id = id
        self.tipo = tipo
        self.fecha = fecha
        self.ponderacion = ponderacion

    # POO: Método abstracto -> cada subclase debe definir su propio cálculo
    @abstractmethod
    def calcular_promedio(self, notas: list) -> float:
        pass


# POO: Clase | Herencia: Examen hereda de Evaluacion
class Examen(Evaluacion):
    # POO: Constructor -> usa super() para reutilizar el constructor del padre
    def __init__(self, id: int, fecha: date, ponderacion: float = 0.6):
        super().__init__(id, "Examen", fecha, ponderacion)

    # POO: Polimorfismo -> misma firma que TrabajoPractico, cálculo distinto
    def calcular_promedio(self, notas: list) -> float:
        return round(sum(notas) / len(notas) * self.ponderacion, 2) if notas else 0.0


# POO: Clase | Herencia: TrabajoPractico hereda de Evaluacion
class TrabajoPractico(Evaluacion):
    def __init__(self, id: int, fecha: date, ponderacion: float = 0.4):
        super().__init__(id, "Trabajo Practico", fecha, ponderacion)

    # POO: Polimorfismo -> ambas subclases responden distinto a la misma
    # llamada calcular_promedio(notas), aunque la ponderación cambie
    def calcular_promedio(self, notas):
        return round(sum(notas) / len(notas) * self.ponderacion, 2) if notas else 0.0

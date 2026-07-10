from abc import ABC, abstractmethod


# POO: Clase (interfaz) | Interfaces -> contrato para los "productos" del Factory Method
class IImportador(ABC):
    """Contrato pequeño: cada importador solo lee un archivo y devuelve filas."""

    @abstractmethod
    def leer(self, ruta_archivo: str) -> list[dict]:
        pass


# POO: Clase (interfaz) | Interfaces -> contrato del patrón Strategy
# (cada estrategia concreta implementa "importar" a su manera)
class IEstrategiaImportacion(ABC):
    """Contrato de estrategia: procesa filas sin saber si vienen de CSV o Excel."""

    @abstractmethod
    def importar(self, filas: list[dict]) -> object:
        pass

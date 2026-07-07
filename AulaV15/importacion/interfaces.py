from abc import ABC, abstractmethod


class IImportador(ABC):
    """Contrato pequeño: cada importador solo lee un archivo y devuelve filas."""

    @abstractmethod
    def leer(self, ruta_archivo: str) -> list[dict]:
        pass


class IEstrategiaImportacion(ABC):
    """Contrato de estrategia: procesa filas sin saber si vienen de CSV o Excel."""

    @abstractmethod
    def importar(self, filas: list[dict]) -> object:
        pass

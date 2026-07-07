from pathlib import Path
from .interfaces import IImportador
from .importadores import CSVImportador, ExcelImportador


class ImportadorFactory:
    """Factory Method/Simple Factory para seleccionar el importador por extensión."""

    _importadores: dict[str, type[IImportador]] = {
        ".csv": CSVImportador,
        ".xlsx": ExcelImportador,
    }

    @classmethod
    def crear(cls, ruta_archivo: str) -> IImportador:
        extension = Path(ruta_archivo).suffix.lower()
        importador_cls = cls._importadores.get(extension)
        if importador_cls is None:
            raise ValueError(f"Formato no soportado: {extension}. Use .csv o .xlsx")
        return importador_cls()

    @classmethod
    def registrar(cls, extension: str, importador_cls: type[IImportador]) -> None:
        """Permite agregar JSON/XML sin modificar la lógica existente."""
        if not extension.startswith("."):
            extension = f".{extension}"
        cls._importadores[extension.lower()] = importador_cls

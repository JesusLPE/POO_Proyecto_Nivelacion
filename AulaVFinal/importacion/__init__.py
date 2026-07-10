"""Subsistema de importación masiva CSV/Excel.

Aquí se combinan tres patrones de diseño:
- Factory Method (factory.py) -> elige el lector según la extensión
- Strategy (estrategias.py)   -> valida y crea los estudiantes
- Facade (facade.py)          -> punto único de entrada para la UI
"""
from .facade import ImportacionEstudiantesFacade
from .factory import ImportadorFactory
from .interfaces import IImportador, IEstrategiaImportacion
from .resultado import ResultadoImportacion, ErrorImportacion

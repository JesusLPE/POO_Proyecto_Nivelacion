from .factory import ImportadorFactory
from .interfaces import IEstrategiaImportacion
from .estrategias import EstrategiaImportacionEstudiantes
from .resultado import ResultadoImportacion


# POO: Clase | Patrón de diseño ESTRUCTURAL: Facade
# Oculta a la UI la complejidad de: Factory (elegir lector) + Strategy (validar/crear)
class ImportacionEstudiantesFacade:
    """Facade para importar estudiantes desde la UI.

    Centraliza el flujo completo de importacion masiva para que la interfaz
    no tenga que conocer la Factory, los lectores de archivos ni la Strategy
    que valida y registra estudiantes.
    """

    # POO: Constructor
    # POO: Inyección de dependencias -> "estrategia" se recibe de afuera
    # (o se crea una por defecto), en vez de estar fija/hardcodeada
    def __init__(self, repo, estrategia: IEstrategiaImportacion | None = None):
        self._repo = repo
        self._estrategia = estrategia or EstrategiaImportacionEstudiantes(repo)

    # POO: Método -> orquesta Factory + Strategy detrás de una sola llamada
    def importar_estudiantes_desde_archivo(self, ruta_archivo: str) -> ResultadoImportacion:
        """Ejecuta el caso de uso completo de importacion masiva."""
        importador = ImportadorFactory.crear(ruta_archivo)
        filas = importador.leer(ruta_archivo)
        return self._estrategia.importar(filas)

    def importar(self, ruta_archivo: str) -> ResultadoImportacion:
        """Alias compatible con llamadas existentes."""
        return self.importar_estudiantes_desde_archivo(ruta_archivo)

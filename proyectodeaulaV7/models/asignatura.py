class Asignatura:
    """Clase que representa una asignatura o materia."""

    def __init__(self, id: int, nombre: str, horas: int, creditos: int, estado: str):
        # Atributos privados
        self.__id = id
        self.__nombre = nombre
        self.__horas = horas
        self.__creditos = creditos
        self.__estado = estado

    # Propiedades
    @property
    def id(self) -> int:
        return self.__id

    @property
    def nombre(self) -> str:
        return self.__nombre

    # Métodos (solo estructura)
    def crearAsignatura(self) -> None:
        print("[SIMULACIÓN] Creando asignatura...")

    def editarAsignatura(self) -> None:
        print("[SIMULACIÓN] Editando asignatura...")

    def eliminarAsignatura(self) -> None:
        print("[SIMULACIÓN] Eliminando asignatura...")

    def asignarDocente(self, docente) -> None:
        """Relación con Docente (simulada)."""
        print(f"[SIMULACIÓN] Asignando docente a {self.__nombre}")
class Asignatura:
    """Clase que representa una asignatura o materia."""

    def __init__(self, id: int, nombre: str, horas: int, creditos: int, estado: str):
        self.__id = id
        self.__nombre = nombre
        self.__horas = horas
        self.__creditos = creditos
        self.__estado = estado

    @property
    def id(self) -> int:
        return self.__id

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def horas(self) -> int:
        return self.__horas

    @property
    def creditos(self) -> int:
        return self.__creditos

    @property
    def estado(self) -> str:
        return self.__estado

    def crearAsignatura(self) -> None:
        print("[SIMULACIÓN] Creando asignatura...")

    def editarAsignatura(self) -> None:
        print("[SIMULACIÓN] Editando asignatura...")

    def eliminarAsignatura(self) -> None:
        print("[SIMULACIÓN] Eliminando asignatura...")

    def asignarDocente(self, docente) -> None:
        print(f"[SIMULACIÓN] Asignando docente a {self.__nombre}")
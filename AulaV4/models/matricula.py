class Matricula:
    def __init__(self, id: int, fecha: str, tipo: str, estado: str,
                 esSegundaMatricula: bool, estudiante=None, asignatura=None):
        self.__id = id
        self.__fecha = fecha
        self.__tipo = tipo
        self.__estado = estado
        self.__esSegundaMatricula = esSegundaMatricula
        self.estudiante = estudiante
        self.asignatura = asignatura

    @property
    def id(self) -> int: return self.__id
    @property
    def tipo(self) -> str: return self.__tipo
    @property
    def estado(self) -> str: return self.__estado
    @estado.setter
    def estado(self, v: str): self.__estado = v
    @property
    def fecha(self): return self.__fecha
    @property
    def esSegundaMatricula(self): return self.__esSegundaMatricula

    def registrarMatricula(self) -> None: pass
    def anularMatricula(self) -> None: self.__estado = "Anulada"
    def verificarGratuidad(self) -> bool: return not self.__esSegundaMatricula
    def _cambiarEstado(self, nuevo: str) -> None: self.__estado = nuevo

class Matricula:
    """Clase que representa una matrícula de un estudiante."""

    def __init__(self, id: int, fecha: str, tipo: str, estado: str,
                 esSegundaMatricula: bool, estudiante=None):
        self.__id = id
        self.__fecha = fecha
        self.__tipo = tipo
        self.__estado = estado
        self.__esSegundaMatricula = esSegundaMatricula
        self.estudiante = estudiante  # Atributo público para referencia al estudiante

    @property
    def id(self) -> int:
        return self.__id

    @property
    def tipo(self) -> str:
        return self.__tipo

    @property
    def estado(self) -> str:
        return self.__estado

    @estado.setter
    def estado(self, nuevo_estado: str):
        self.__estado = nuevo_estado

    @property
    def fecha(self):
        return self.__fecha

    @property
    def esSegundaMatricula(self):
        return self.__esSegundaMatricula

    def registrarMatricula(self) -> None:
        print("[SIMULACIÓN] Matrícula registrada")

    def anularMatricula(self) -> None:
        print("[SIMULACIÓN] Matrícula anulada")

    def verificarGratuidad(self) -> None:
        print("[SIMULACIÓN] Verificando gratuidad...")

    def _cambiarEstado(self) -> None:
        print("[SIMULACIÓN] Cambiando estado de matrícula...")
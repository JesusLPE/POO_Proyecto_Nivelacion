from typing import Optional
from .asignatura import Asignatura


class Matricula:
    """SRP – vincula un estudiante a una asignatura en un estado dado."""

    def __init__(self, id: int, fecha: str, tipo: str, estado: str,
                 es_segunda: bool, estudiante=None, asignatura: Optional[Asignatura] = None):
        self.__id = id
        self.__fecha = fecha
        self.__tipo = tipo
        self.__estado = estado
        self.__es_segunda = es_segunda
        self.estudiante = estudiante
        self.asignatura = asignatura

    @property
    def id(self):
        return self.__id

    @property
    def fecha(self):
        return self.__fecha

    @property
    def tipo(self):
        return self.__tipo

    @property
    def estado(self):
        return self.__estado

    @estado.setter
    def estado(self, v):
        self.__estado = v

    @property
    def esSegundaMatricula(self):
        return self.__es_segunda

    def anular(self):
        self.__estado = "Anulada"

    def activar(self):
        self.__estado = "Activa"

    def verificarGratuidad(self):
        return not self.__es_segunda

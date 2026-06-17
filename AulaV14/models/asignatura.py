class Asignatura:
    """SRP – solo describe una asignatura del plan de estudios."""

    def __init__(self, id: int, nombre: str, horas: int, creditos: int, estado: str):
        self.__id = id
        self.__nombre = nombre
        self.__horas = horas
        self.__creditos = creditos
        self.__estado = estado

    @property
    def id(self):
        return self.__id

    @property
    def nombre(self):
        return self.__nombre

    @property
    def horas(self):
        return self.__horas

    @property
    def creditos(self):
        return self.__creditos

    @property
    def estado(self):
        return self.__estado

    @estado.setter
    def estado(self, v):
        self.__estado = v

    def __repr__(self):
        return f"Asignatura({self.__nombre})"

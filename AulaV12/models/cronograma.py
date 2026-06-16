"""models/cronograma.py

SRP – Cronograma representa el calendario académico de un curso o
grupo de nivelación: fecha de inicio, fecha de fin y carga horaria
total. Es un modelo de dominio puro (sin persistencia ni lógica de UI).
"""


class Cronograma:
    """Encapsula las fechas y la carga horaria total de un curso."""

    def __init__(self, id: int, curso_id: int, fecha_inicio: str,
                 fecha_fin: str, total_horas: int, descripcion: str = ""):
        self.__id = id
        self.__curso_id = curso_id
        self.__fecha_inicio = fecha_inicio
        self.__fecha_fin = fecha_fin
        self.__total_horas = total_horas
        self.__descripcion = descripcion

    @property
    def id(self) -> int:
        return self.__id

    @property
    def curso_id(self) -> int:
        return self.__curso_id

    @property
    def fecha_inicio(self) -> str:
        return self.__fecha_inicio

    @fecha_inicio.setter
    def fecha_inicio(self, valor: str):
        self.__fecha_inicio = valor

    @property
    def fecha_fin(self) -> str:
        return self.__fecha_fin

    @fecha_fin.setter
    def fecha_fin(self, valor: str):
        self.__fecha_fin = valor

    @property
    def total_horas(self) -> int:
        return self.__total_horas

    @total_horas.setter
    def total_horas(self, valor: int):
        self.__total_horas = valor

    @property
    def descripcion(self) -> str:
        return self.__descripcion

    @descripcion.setter
    def descripcion(self, valor: str):
        self.__descripcion = valor

    def __str__(self) -> str:
        return f"{self.__fecha_inicio} – {self.__fecha_fin} ({self.__total_horas} h)"

    def __repr__(self) -> str:
        return f"Cronograma(curso_id={self.__curso_id}, {self.__fecha_inicio}–{self.__fecha_fin})"

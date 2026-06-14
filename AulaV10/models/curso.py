from typing import Optional
from .horario import Horario
from .modalidad import Modalidad


class Curso:
    """SRP – representa un curso con su horario, modalidad y docente."""

    def __init__(self, id: int, nombre: str, duracion_semanas: int,
                 total_horas: int, carrera: str = ""):
        self._id = id
        self._nombre = nombre
        self._duracion_semanas = duracion_semanas
        self._total_horas = total_horas
        self._horario: Optional[Horario] = None
        self._modalidad: Optional[Modalidad] = None
        self.docente_email: Optional[str] = None
        self.carrera: str = carrera

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def horario(self) -> Optional[Horario]:
        return self._horario

    @property
    def modalidad(self) -> Optional[Modalidad]:
        return self._modalidad

    def asignar_horario(self, horario: Horario):
        self._horario = horario

    def asignar_modalidad(self, modalidad: Modalidad):
        self._modalidad = modalidad

    def asignar_docente(self, email: str):
        self.docente_email = email

    def __repr__(self):
        return f"Curso({self._nombre})"

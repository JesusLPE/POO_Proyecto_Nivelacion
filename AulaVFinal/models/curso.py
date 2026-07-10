from typing import Optional
from .horario import Horario
from .modalidad import Modalidad


# POO: Clase
# POO: Relación entre clases -> Agregación/Composición: un Curso "tiene" un
# Horario y una Modalidad (atributos que son objetos de otras clases)
class Curso:
    """Representa un curso con horario, modalidad y docente."""

    # POO: Constructor | POO: Propiedades (atributos de instancia)
    def __init__(self, id: int, nombre: str, duracion_semanas: int,
                 total_horas: int, carrera: str = ""):
        self.id = id
        self.nombre = nombre
        self.duracion_semanas = duracion_semanas
        self.total_horas = total_horas
        self.horario: Optional[Horario] = None
        self.modalidad: Optional[Modalidad] = None
        self.docente_email: Optional[str] = None
        self.carrera: str = carrera

    # POO: Métodos -> establecen las relaciones (asociaciones) con Horario/Modalidad
    def asignar_horario(self, horario: Horario):
        self.horario = horario

    def asignar_modalidad(self, modalidad: Modalidad):
        self.modalidad = modalidad

    # POO: Relación entre clases -> Asociación simple con Docente (solo guarda
    # el email como referencia, no el objeto completo)
    def asignar_docente(self, email: str):
        self.docente_email = email

    def __repr__(self):
        return f"Curso({self.nombre})"

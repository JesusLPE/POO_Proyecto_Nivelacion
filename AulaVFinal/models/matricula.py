from typing import Optional
from .asignatura import Asignatura


# POO: Clase
# POO: Relación entre clases -> Asociación: vincula un Estudiante con una Asignatura
class Matricula:
    """Vincula un estudiante a una asignatura."""

    # POO: Constructor | POO: Propiedades (atributos de instancia)
    def __init__(self, id: int, fecha: str, tipo: str, estado: str,
                 es_segunda: bool, estudiante=None, asignatura: Optional[Asignatura] = None):
        self.id = id
        self.fecha = fecha
        self.tipo = tipo
        self.estado = estado
        self.es_segunda = es_segunda
        self.estudiante = estudiante
        self.asignatura = asignatura

    # POO: Propiedad (@property) -> expone es_segunda como atributo de solo
    # lectura con otro nombre (esSegundaMatricula), sin métodos get_/set_ explícitos
    @property
    def esSegundaMatricula(self):
        return self.es_segunda

    # POO: Métodos
    def anular(self):
        self.estado = "Anulada"

    def activar(self):
        self.estado = "Activa"

    def verificarGratuidad(self):
        return not self.es_segunda

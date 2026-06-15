from .interfaces import ICalificable


class Calificacion(ICalificable):
    """SRP+LSP – extiende ICalificable con lógica real."""

    def __init__(self, estudiante, asignatura_nombre: str,
                 nota: float, observacion: str = ""):
        self.estudiante = estudiante
        self.asignatura = asignatura_nombre
        self.nota = nota
        self.observacion = observacion

    def calcularPromedio(self, notas: list) -> float:
        return sum(notas) / len(notas) if notas else 0.0

    def esta_aprobado(self) -> bool:
        return self.nota is not None and self.nota >= 7.0

    def modificar_nota(self, nueva: float) -> None:
        self.nota = nueva

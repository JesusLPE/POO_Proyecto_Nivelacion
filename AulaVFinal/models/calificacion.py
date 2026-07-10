from .interfaces import ICalificable


# POO: Clase | Herencia: Calificacion hereda de (implementa) ICalificable
# POO: Polimorfismo con interfaces -> puede tratarse como un ICalificable genérico
# SOLID -> LSP (Liskov): puede sustituir a ICalificable donde se lo requiera
# SOLID -> SRP: esta clase solo se ocupa de la nota/calificación de un estudiante
class Calificacion(ICalificable):
    """SRP+LSP – extiende ICalificable con lógica real."""

    # POO: Constructor | POO: Propiedades
    # POO: Relación entre clases -> Asociación con el objeto Estudiante (persona)
    def __init__(self, estudiante, asignatura_nombre: str,
                 nota: float, observacion: str = ""):
        self.estudiante = estudiante
        self.asignatura = asignatura_nombre
        self.nota = nota
        self.observacion = observacion

    # POO: Polimorfismo -> implementación concreta del método abstracto de la interfaz
    def calcularPromedio(self, notas: list) -> float:
        return sum(notas) / len(notas) if notas else 0.0

    def esta_aprobado(self) -> bool:
        return self.nota is not None and self.nota >= 7.0

    # POO: Método
    def modificar_nota(self, nueva: float) -> None:
        self.nota = nueva

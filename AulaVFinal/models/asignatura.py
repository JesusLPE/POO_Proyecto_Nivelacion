# POO: Clase
class Asignatura:
    """Describe una asignatura del plan de estudios."""

    # POO: Constructor | POO: Propiedades (atributos de instancia)
    def __init__(self, id: int, nombre: str, horas: int, creditos: int, estado: str):
        self.id = id
        self.nombre = nombre
        self.horas = horas
        self.creditos = creditos
        self.estado = estado

    # POO: Método (dunder / especial) -> representación legible del objeto
    def __repr__(self):
        return f"Asignatura({self.nombre})"

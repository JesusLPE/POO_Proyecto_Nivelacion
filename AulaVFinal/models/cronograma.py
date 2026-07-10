# POO: Clase
class Cronograma:
    """Calendario academico de un curso."""

    # POO: Constructor | POO: Propiedades
    # POO: Relación entre clases -> Asociación con Curso (guarda curso_id, no el objeto)
    def __init__(self, id: int, curso_id: int, fecha_inicio: str,
                 fecha_fin: str, total_horas: int, descripcion: str = ""):
        self.id = id
        self.curso_id = curso_id
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.total_horas = total_horas
        self.descripcion = descripcion

    # POO: Métodos especiales -> str() para mostrar, repr() para depurar
    def __str__(self) -> str:
        return f"{self.fecha_inicio} - {self.fecha_fin} ({self.total_horas} h)"

    def __repr__(self) -> str:
        return f"Cronograma(curso_id={self.curso_id}, {self.fecha_inicio}-{self.fecha_fin})"

# POO: Clase
class Horario:
    """Bloque horario de clase."""

    # POO: Constructor | POO: Propiedades
    def __init__(self, id: int, dia: str, hora_inicio: str, hora_fin: str, aula: str = ""):
        self.id = id
        self.dia = dia
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.aula = aula

    # POO: Método especial -> permite usar str(horario) / print(horario)
    def __str__(self) -> str:
        return f"{self.dia} {self.hora_inicio}-{self.hora_fin}"

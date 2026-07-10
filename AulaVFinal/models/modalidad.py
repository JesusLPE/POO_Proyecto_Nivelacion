# POO: Clase
class Modalidad:
    """Modalidad de un curso."""

    # POO: Constructor | POO: Propiedades
    def __init__(self, id: int, nombre: str, descripcion: str, estado: bool, plataforma: str = ""):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = estado
        self.plataforma = plataforma

    # POO: Método especial (str)
    def __str__(self):
        return self.nombre

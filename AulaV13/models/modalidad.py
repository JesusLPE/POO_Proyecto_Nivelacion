class Modalidad:
    """SRP – solo encapsula la modalidad de un curso."""

    def __init__(self, id: int, nombre: str, descripcion: str, estado: bool, plataforma: str = ""):
        self._id = id
        self._nombre = nombre
        self._descripcion = descripcion
        self._estado = estado
        self._plataforma = plataforma

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def plataforma(self):
        return self._plataforma

    def __str__(self):
        return self._nombre

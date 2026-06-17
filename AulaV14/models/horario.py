class Horario:
    """SRP – solo encapsula un bloque horario."""

    def __init__(self, id: int, dia: str, hora_inicio: str, hora_fin: str, aula: str = ""):
        self._id = id
        self._dia = dia
        self._hora_inicio = hora_inicio
        self._hora_fin = hora_fin
        self._aula = aula

    @property
    def id(self) -> int:
        return self._id

    @property
    def dia(self) -> str:
        return self._dia

    @property
    def hora_inicio(self) -> str:
        return self._hora_inicio

    @property
    def hora_fin(self) -> str:
        return self._hora_fin

    @property
    def aula(self) -> str:
        return self._aula

    def __str__(self) -> str:
        return f"{self._dia} {self._hora_inicio}–{self._hora_fin}"

class Horario:
    def __init__(self, id: int, dia: str, hora_inicio: str, hora_fin: str):
        self._id = id
        self._dia = dia
        self._hora_inicio = hora_inicio
        self._hora_fin = hora_fin

    @property
    def id(self):
        return self._id

    @property
    def dia(self):
        return self._dia

    @property
    def hora_inicio(self):
        return self._hora_inicio

    @property
    def hora_fin(self):
        return self._hora_fin

    def __str__(self):
        return f"{self._dia} de {self._hora_inicio} a {self._hora_fin}"
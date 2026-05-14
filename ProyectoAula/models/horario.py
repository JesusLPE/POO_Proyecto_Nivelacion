# horario.py
class Horario:
    def __init__(self, id: int, dia: str, hora_inicio: str, hora_fin: str):
        self._id = id
        self._dia = dia
        self._hora_inicio = hora_inicio
        self._hora_fin = hora_fin
class Asistencia:
    def __init__(self, fecha: str, porcentaje: float, estadoAsistencia: str):
        self.__fecha = fecha
        self.__porcentaje = porcentaje
        self.__estadoAsistencia = estadoAsistencia

    @property
    def fecha(self): return self.__fecha

    def registrar(self) -> None:
        print("[SIMULACIÓN] Asistencia registrada")

    def justificarFalta(self) -> None:
        print("[SIMULACIÓN] Falta justificada")
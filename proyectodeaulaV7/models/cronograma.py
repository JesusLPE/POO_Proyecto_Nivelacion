class Cronograma:
    def __init__(self, id: int, fechaInicio: str, fechaFin: str, totalHoras: int):
        self.__id = id
        self.__fechaInicio = fechaInicio
        self.__fechaFin = fechaFin
        self.__totalHoras = totalHoras

    def crearCronograma(self) -> None:
        print("[SIMULACIÓN] Cronograma creado")
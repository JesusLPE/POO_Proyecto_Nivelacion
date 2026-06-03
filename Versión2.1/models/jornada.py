class Jornada:
    def __init__(self, id: int, tipo: str, estado: str, cupoMaximo: int):
        self.__id = id
        self.__tipo = tipo
        self.__estado = estado
        self.__cupoMaximo = cupoMaximo

    @property
    def id(self): return self.__id
    @property
    def tipo(self): return self.__tipo

    def asignarJornada(self) -> None:
        print("[SIMULACIÓN] Jornada asignada")
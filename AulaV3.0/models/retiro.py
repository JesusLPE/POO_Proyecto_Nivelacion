class Retiro:
    def __init__(self, id: int, tipo: str, fecha: str, motivo: str):
        self.__id = id
        self.__tipo = tipo
        self.__fecha = fecha
        self.__motivo = motivo

    def registrarRetiro(self) -> None:
        print("[SIMULACIÓN] Retiro registrado")
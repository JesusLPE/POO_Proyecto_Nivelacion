class Notas:
    """Clase que representa las notas de un estudiante."""

    def __init__(self, promedioFinal: float, estadoAprobacion: str):
        # Atributos privados
        self.__promedioFinal = promedioFinal
        self.__estadoAprobacion = estadoAprobacion

    # Propiedades
    @property
    def promedioFinal(self) -> float:
        return self.__promedioFinal

    @property
    def estadoAprobacion(self) -> str:
        return self.__estadoAprobacion

    # Métodos (sin lógica real)
    def generar(self) -> None:
        print("[SIMULACIÓN] Generando notas...")

    def calcularPromedio(self, nota1: float, nota2: float, nota3: float = 0) -> float:
        """Sobrecarga simulada: calcula promedio de 2 o 3 notas."""
        if nota3 == 0:
            return (nota1 + nota2) / 2  # Promedio de 2 notas
        else:
            return (nota1 + nota2 + nota3) / 3  # Promedio de 3 notas

    def habilitarRecuperacion(self) -> None:
        print("[SIMULACIÓN] Habilitando recuperación...")
class Notas:
    """Demuestra sobrecarga de método con parámetro opcional."""

    @staticmethod
    def calcularPromedio(nota1: float, nota2: float, nota3: float = 0.0) -> float:
        if nota3 == 0.0:
            return round((nota1 + nota2) / 2, 2)
        return round((nota1 + nota2 + nota3) / 3, 2)

    @staticmethod
    def estado(promedio: float) -> str:
        if promedio >= 9.0:  return "Sobresaliente"
        if promedio >= 7.0:  return "Aprobado"
        if promedio >= 5.0:  return "En recuperación"
        return "Reprobado"

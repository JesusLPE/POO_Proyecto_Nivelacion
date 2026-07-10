# POO: Clase (utilitaria, solo con @staticmethod)
class Notas:
    """Demuestra sobrecarga de método con parámetro opcional."""

    # POO: Sobrecarga de método -> Python no soporta overload real (mismo
    # nombre, distintas firmas), así que se simula con un parámetro opcional
    # (nota3=0.0): la misma llamada calcularPromedio() se comporta distinto
    # según reciba 2 o 3 notas.
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

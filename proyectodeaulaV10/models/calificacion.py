class Calificacion:
    def __init__(self, estudiante, asignatura: str, nota: float, observacion: str = ""):
        self.estudiante = estudiante
        self.asignatura = asignatura
        self.nota = nota
        self.observacion = observacion

    # Los métodos son solo placeholders
    def asignar_nota(self, docente):
        print(f"[SIMULACIÓN] Asignando nota {self.nota} a {self.estudiante.nombre}")

    def modificar_nota(self, nueva_nota: float):
        self.nota = nueva_nota

    def eliminar_nota(self):
        self.nota = None
class Calificacion:
    def __init__(self, estudiante, asignatura: str, nota: float, observacion: str = ""):
        self.estudiante = estudiante
        self.asignatura = asignatura
        self.nota = nota
        self.observacion = observacion

    def asignar_nota(self, docente):
        docente.registrar_nota(self.estudiante, self.asignatura, self.nota)

    def modificar_nota(self, nueva_nota: float):
        self.nota = nueva_nota

    def eliminar_nota(self):
        self.nota = None
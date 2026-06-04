class Calificacion:
    def __init__(self, estudiante, asignatura: str, nota: float, observacion: str = ""):
        self.estudiante = estudiante
        self.asignatura = asignatura
        self.nota = nota
        self.observacion = observacion

    def asignar_nota(self, docente):
        # nota real ya está asignada en constructor
        pass

    def modificar_nota(self, nueva_nota: float):
        self.nota = nueva_nota

    def eliminar_nota(self):
        self.nota = None

    def esta_aprobado(self) -> bool:
        return self.nota is not None and self.nota >= 7.0

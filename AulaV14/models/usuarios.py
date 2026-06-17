from .persona import Persona


class Estudiante(Persona):
    """OCP – agrega matrícula, carrera, curso y horario sin tocar Persona."""

    def __init__(self, nombre, apellido, email, password, cedula: str, matricula: str, carrera: str,
                 curso_id=None, horario_id=None):
        super().__init__(nombre, apellido, email, password)
        self.__cedula = cedula
        self.__matricula = matricula
        self.carrera = carrera
        self.curso_id = curso_id      # id del Curso asignado (obligatorio en alta)
        self.horario_id = horario_id  # id del Horario asignado (obligatorio en alta)

    @property
    def cedula(self) -> str: return self.__cedula

    @cedula.setter
    def cedula(self, valor: str): self.__cedula = valor

    @property
    def matricula(self) -> str: return self.__matricula

    def obtener_rol(self) -> str: return "estudiante"


class Docente(Persona):
    """OCP – agrega especialidad sin tocar Persona."""

    def __init__(self, nombre, apellido, email, password, especialidad: str):
        super().__init__(nombre, apellido, email, password)
        self.especialidad = especialidad

    def obtener_rol(self) -> str: return "docente"


class Coordinador(Persona):
    def obtener_rol(self) -> str: return "coordinador"


class Administrador(Persona):
    def obtener_rol(self) -> str: return "administrador"

from models.persona import Persona


class Estudiante(Persona):
    """OCP – agrega matrícula y carrera sin tocar Persona."""

    def __init__(self, nombre, apellido, email, password, matricula: str, carrera: str):
        super().__init__(nombre, apellido, email, password)
        self.__matricula = matricula
        self.carrera = carrera

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

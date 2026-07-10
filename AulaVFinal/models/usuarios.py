from .persona import Persona


# POO: Clase | Herencia: Estudiante hereda de Persona (extiende sus atributos y métodos)
class Estudiante(Persona):
    """Usuario estudiante con datos academicos propios."""

    # POO: Constructor -> agrega parámetros propios y llama al constructor
    # del padre con super() (reutiliza la lógica de Persona)
    def __init__(self, nombre, apellido, email, password, cedula: str, matricula: str, carrera: str,
                 curso_id=None, horario_id=None):
        super().__init__(nombre, apellido, email, password)
        self.cedula = cedula
        self.matricula = matricula
        self.carrera = carrera
        self.curso_id = curso_id
        self.horario_id = horario_id

    # POO: Polimorfismo -> sobrescribe (override) el método abstracto de Persona;
    # cada subclase responde distinto a la misma llamada obtener_rol()
    def obtener_rol(self) -> str:
        return "estudiante"


# POO: Clase | Herencia: Docente hereda de Persona
class Docente(Persona):
    """Usuario docente."""

    def __init__(self, nombre, apellido, email, password, especialidad: str):
        super().__init__(nombre, apellido, email, password)
        self.especialidad = especialidad

    # POO: Polimorfismo -> misma firma que en Estudiante, comportamiento distinto
    def obtener_rol(self) -> str:
        return "docente"


# POO: Clase | Herencia: Coordinador hereda de Persona (no agrega atributos
# nuevos, reutiliza el constructor de Persona tal cual)
class Coordinador(Persona):
    # POO: Polimorfismo
    def obtener_rol(self) -> str:
        return "coordinador"


# POO: Clase | Herencia: Administrador hereda de Persona
class Administrador(Persona):
    # POO: Polimorfismo
    def obtener_rol(self) -> str:
        return "administrador"

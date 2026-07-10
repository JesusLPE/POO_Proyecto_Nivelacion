"""Factory Method para crear usuarios del sistema académico.

Este módulo centraliza la creación de objetos Estudiante, Docente,
Coordinador y Administrador. Así evitamos repetir constructores en
servicios y repositorios, y si mañana aparece un nuevo rol solo se agrega
su regla de creación aquí.

"""

from abc import ABC, abstractmethod

from models.usuarios import Estudiante, Docente, Coordinador, Administrador

# Patrón de diseño CREACIONAL: Factory Method
# POO: Clase abstracta (ABC) -> define el "Creator" del patrón
class CreadorUsuario(ABC):
    """Creator del patrón Factory Method.

    Define la interfaz para crear un usuario y puede contener lógica
    compartida (ej. logging, validación) alrededor del factory_method.
    Las subclases concretas solo deben implementar factory_method().
    """

    # POO: Método abstracto -> "factory method" que cada subclase implementa
    # POO: Polimorfismo con clases abstractas -> cada Creator concreto crea
    # un tipo de usuario distinto respondiendo al mismo mensaje factory_method()
    @abstractmethod
    def factory_method(self, nombre: str, apellido: str, email: str,
                       password: str, **kwargs):
        """Crea y devuelve la instancia de usuario correspondiente.

        Cada Creator concreto sobrescribe este método para instanciar
        su propia clase de usuario sin que el caller conozca el tipo real.
        """

    # POO: Método (concreto, compartido por todas las subclases)
    def crear(self, nombre: str, apellido: str, email: str,
              password: str, **kwargs):
        """Orquesta la creación; llama a factory_method internamente.

        Agrega el punto de extensión para pre/post-procesamiento
        (validaciones, auditoría, etc.) sin alterar las subclases.
        """
        usuario = self.factory_method(nombre, apellido, email, password, **kwargs)
        return usuario


# POO: Clase | Herencia: hereda de CreadorUsuario (Concrete Creator del Factory Method)
class CreadorEstudiante(CreadorUsuario):
    """Concrete Creator: produce instancias de Estudiante."""

    # POO: Polimorfismo -> sobrescribe factory_method para devolver un Estudiante
    def factory_method(self, nombre: str, apellido: str, email: str,
                       password: str, **kwargs):
        return Estudiante(
            nombre, apellido, email, password,
            kwargs.get("cedula", ""),
            kwargs.get("matricula", ""),
            kwargs.get("carrera", ""),
            curso_id=kwargs.get("curso_id"),
            horario_id=kwargs.get("horario_id"),
        )


# POO: Clase | Herencia: Concrete Creator
class CreadorDocente(CreadorUsuario):
    """Concrete Creator: produce instancias de Docente."""

    def factory_method(self, nombre: str, apellido: str, email: str,
                       password: str, **kwargs):
        return Docente(
            nombre, apellido, email, password,
            kwargs.get("especialidad", "")
        )


# POO: Clase | Herencia: Concrete Creator
class CreadorCoordinador(CreadorUsuario):
    """Concrete Creator: produce instancias de Coordinador."""

    def factory_method(self, nombre: str, apellido: str, email: str,
                       password: str, **kwargs):
        return Coordinador(nombre, apellido, email, password)


# POO: Clase | Herencia: Concrete Creator
class CreadorAdministrador(CreadorUsuario):
    """Concrete Creator: produce instancias de Administrador."""

    def factory_method(self, nombre: str, apellido: str, email: str,
                       password: str, **kwargs):
        return Administrador(nombre, apellido, email, password)


_CREATORS: dict[str, CreadorUsuario] = {
    "estudiante":    CreadorEstudiante(),
    "docente":       CreadorDocente(),
    "coordinador":   CreadorCoordinador(),
    "administrador": CreadorAdministrador(),
}

# POO: Clase | Patrón: fachada simple sobre el Factory Method (punto único de creación)
class UsuarioFactory:
    """Fachada Simple-Factory que delega en los Concrete Creators.

    Mantiene la API original (crear_usuario) intacta para no romper
    servicios y repositorios existentes, mientras internamente aplica
    el patrón Factory Method completo.
    """

    # POO: Método estático
    # SOLID -> OCP: agregar un rol nuevo no modifica este método, solo se
    # registra un nuevo Creator (ver registrar_creator más abajo)
    @staticmethod
    def crear_usuario(rol: str, nombre: str, apellido: str, email: str,
                      password: str, **kwargs):
        """Punto de entrada unificado; selecciona el Creator apropiado."""
        clave = (rol or "").strip().lower()
        creator = _CREATORS.get(clave)
        if creator is None:
            raise ValueError(f"Rol de usuario no soportado: '{rol}'")
        return creator.crear(nombre, apellido, email, password, **kwargs)

    @staticmethod
    def registrar_creator(rol: str, creator: CreadorUsuario) -> None:
        """Permite extender el sistema con nuevos roles en tiempo de ejecución.

        Ejemplo:
            UsuarioFactory.registrar_creator("tutor", CreadorTutor())
        """
        if not isinstance(creator, CreadorUsuario):
            raise TypeError("creator debe ser instancia de CreadorUsuario")
        _CREATORS[rol.strip().lower()] = creator

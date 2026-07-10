from abc import abstractmethod
from .interfaces import IAutenticable


# POO: Clase base | Herencia: Persona hereda de (implementa) IAutenticable
# POO: Polimorfismo con interfaces -> Persona cumple el contrato IAutenticable
# POO: Polimorfismo con clases abstractas -> Persona es la superclase abstracta
# de Estudiante/Docente/Coordinador/Administrador (ver usuarios.py)
class Persona(IAutenticable):
    """Entidad base para usuarios del sistema.

    Los datos normales del dominio son atributos públicos. La contrasena
    queda marcada como atributo interno porque no debe editarse
    accidentalmente desde la UI ni desde listados.
    """

    # POO: Constructor (__init__)
    # POO: Propiedades/atributos -> nombre, apellido, email públicos;
    # POO: Encapsulamiento -> _password con guion bajo = atributo protegido,
    # no se debe acceder directamente desde fuera de la clase
    def __init__(self, nombre: str, apellido: str, email: str, password: str):
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self._password = password

    # POO: Método (getter manual, parte del encapsulamiento de _password)
    def get_password(self) -> str:
        return self._password

    # POO: Método abstracto -> obliga a cada subclase a implementar su propio
    # rol; base de la Polimorfismo con clases abstractas
    @abstractmethod
    def obtener_rol(self) -> str:
        pass

    # POO: Método (implementación concreta requerida por la interfaz IAutenticable)
    def iniciarSesion(self, usuario: str, contrasenia: str) -> bool:
        return self.email == usuario and self._password == contrasenia

    def cerrarSesion(self) -> None:
        pass

    def verificar_cuenta(self) -> bool:
        return bool(self.email)

    # POO: Encapsulamiento -> método interno (prefijo _) que solo reexpone
    # verificar_cuenta() para uso interno de la clase/subclases
    def _verificarCuenta(self) -> bool:
        return self.verificar_cuenta()

    def get_id(self) -> str:
        return self.email

    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

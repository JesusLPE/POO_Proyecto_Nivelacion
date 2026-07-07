from abc import abstractmethod
from .interfaces import IAutenticable


class Persona(IAutenticable):
    """SRP – solo gestiona datos e identidad de una persona."""

    def __init__(self, nombre: str, apellido: str, email: str, password: str):
        self.__nombre = nombre
        self.__apellido = apellido
        self.__email = email
        self.__password = password

    @property
    def nombre(self) -> str: return self.__nombre
    @nombre.setter
    def nombre(self, valor: str): self.__nombre = valor

    @property
    def apellido(self) -> str: return self.__apellido
    @apellido.setter
    def apellido(self, valor: str): self.__apellido = valor

    @property
    def email(self) -> str: return self.__email

    def get_password(self) -> str: return self.__password

    @abstractmethod
    def obtener_rol(self) -> str: pass

    # IAutenticable
    def iniciarSesion(self, usuario: str, contrasenia: str) -> bool:
        return self.__email == usuario and self.__password == contrasenia

    def cerrarSesion(self) -> None: pass

    def _verificarCuenta(self) -> bool: return bool(self.__email)

    def get_id(self) -> str: return self.__email

    def nombre_completo(self) -> str:
        return f"{self.__nombre} {self.__apellido}"

from abc import ABC, abstractmethod
from models.interfaz import IniciarSesion

class Persona(IniciarSesion, ABC):  # Ya no hereda de UserMixin
    def __init__(self, nombre, apellido, email, password):
        self.__nombre = nombre
        self.__apellido = apellido
        self.__email = email
        self.__password = password

    @property
    def nombre(self):
        return self.__nombre

    @property
    def apellido(self):
        return self.__apellido

    @property
    def email(self):
        return self.__email

    @abstractmethod
    def obtener_rol(self):
        pass

    def get_password(self):
        return self.__password

    # Implementación de la interfaz IniciarSesion
    def iniciarSesion(self, usuario: str, contrasenia: str) -> bool:
        # Aquí iría la lógica real; por ahora simulamos
        return self.email == usuario and self.__password == contrasenia

    def cerrarSesion(self) -> None:
        print("[SIMULACIÓN] Cerrando sesión")

    def _verificarCuenta(self) -> bool:
        return True

    # Método necesario para identificador (antes era get_id de Flask)
    def get_id(self):
        return self.__email
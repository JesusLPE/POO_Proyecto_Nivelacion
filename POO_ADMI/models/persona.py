from abc import ABC, abstractmethod
from flask_login import UserMixin
from models.interfaz import IniciarSesion  # Importa la interfaz

class Persona(UserMixin, IniciarSesion, ABC):
    """Clase abstracta base para todos los usuarios del sistema."""

    def __init__(self, nombre, apellido, email, password):
        # Atributos privados (encapsulamiento)
        self.__nombre = nombre
        self.__apellido = apellido
        self.__email = email
        self.__password = password

    # Propiedades (Getters)
    @property
    def nombre(self):
        return self.__nombre

    @property
    def apellido(self):
        return self.__apellido

    @property
    def email(self):
        return self.__email

    # Método requerido por Flask-Login
    def get_id(self):
        return self.__email

    # Método abstracto que deben implementar las hijas
    @abstractmethod
    def obtener_rol(self):
        pass

    def get_password(self):
        return self.__password

    # Implementación de la interfaz IniciarSesion (puede ser sobreescrita)
    def iniciarSesion(self, usuario: str, contrasenia: str) -> bool:
        print(f"[SIMULACIÓN] Iniciando sesión para {usuario}")
        return True

    def cerrarSesion(self) -> None:
        print("[SIMULACIÓN] Cerrando sesión")

    def _verificarCuenta(self) -> bool:
        print("[SIMULACIÓN] Verificando cuenta...")
        return True
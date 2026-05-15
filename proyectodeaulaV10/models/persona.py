from abc import ABC, abstractmethod
from flask_login import UserMixin
from models.interfaz import IniciarSesion  # Importa la interfaz

class Persona(UserMixin, IniciarSesion, ABC):
    """Clase abstracta base para todos los usuarios del sistema.

    Esta clase define los datos comunes a todos los roles y obliga a que
    las clases hijas implementen el método obtener_rol.
    """

    def __init__(self, nombre, apellido, email, password):
        # Atributos privados para proteger el acceso directo desde fuera.
        self.__nombre = nombre
        self.__apellido = apellido
        self.__email = email
        self.__password = password

    # Propiedades para acceder de forma segura a los datos del usuario.
    @property
    def nombre(self):
        return self.__nombre

    @property
    def apellido(self):
        return self.__apellido

    @property
    def email(self):
        return self.__email

    # Flask-Login necesita este método para identificar al usuario en la sesión.
    def get_id(self):
        return self.__email

    # Método abstracto que obliga a cada rol a devolver su nombre.
    @abstractmethod
    def obtener_rol(self):
        pass

    def get_password(self):
        return self.__password

    # Implementación genérica de la interfaz de inicio/cierre de sesión.
    # En esta fase solo imprimimos mensajes de simulación.
    def iniciarSesion(self, usuario: str, contrasenia: str) -> bool:
        print(f"[SIMULACIÓN] Iniciando sesión para {usuario}")
        return True

    def cerrarSesion(self) -> None:
        print("[SIMULACIÓN] Cerrando sesión")

    def _verificarCuenta(self) -> bool:
        print("[SIMULACIÓN] Verificando cuenta...")
        return True
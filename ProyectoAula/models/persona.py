from abc import ABC, abstractmethod
from flask_login import UserMixin

class Persona(UserMixin, ABC):
    def __init__(self, nombre, apellido, email, password):
        self._nombre = nombre
        self._apellido = apellido
        self._email = email
        self._password = password   # en producción usar hash

    @property
    def nombre(self):
        return self._nombre

    @property
    def apellido(self):
        return self._apellido

    @property
    def email(self):
        return self._email

    def get_id(self):
        return self._email

    @abstractmethod
    def obtener_rol(self):
        pass
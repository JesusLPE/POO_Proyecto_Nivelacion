# POO: Interfaces -> en Python se implementan con ABC + @abstractmethod.
# Cada clase de abajo es una interfaz (no tiene atributos ni lógica propia).
# SOLID -> ISP (Interface Segregation): en vez de una sola interfaz gigante,
# hay varias interfaces pequeñas y específicas (una por responsabilidad).
from abc import ABC, abstractmethod


# POO: Clase (interfaz) | Herencia: hereda de ABC (Abstract Base Class)
class IAutenticable(ABC):
    """Contrato pequeno y publico para objetos que pueden autenticarse."""

    # POO: Métodos -> firmas abstractas, sin implementación (el "qué", no el "cómo")
    @abstractmethod
    def iniciarSesion(self, usuario: str, contrasenia: str) -> bool:
        pass

    @abstractmethod
    def cerrarSesion(self) -> None:
        pass

    @abstractmethod
    def verificar_cuenta(self) -> bool:
        pass


# POO: Clase (interfaz) | Polimorfismo con interfaces: cualquier clase que
# implemente ICalificable puede usarse donde se espere "algo calificable"
class ICalificable(ABC):
    """Contrato especifico para objetos que calculan calificaciones."""

    @abstractmethod
    def calcularPromedio(self, notas: list) -> float:
        pass

    @abstractmethod
    def esta_aprobado(self) -> bool:
        pass


# POO: Clase (interfaz) | SOLID -> DIP (Dependency Inversion): las capas
# superiores (services/repositories) dependen de esta abstracción, no de
# una implementación concreta como JSON, BD, etc.
class IRepositorio(ABC):
    """Abstraccion de persistencia usada por las capas superiores."""

    @abstractmethod
    def cargar(self, ruta: str) -> list:
        pass

    @abstractmethod
    def guardar(self, ruta: str, datos: list) -> None:
        pass


# POO: Clase (interfaz) -> no tiene implementación concreta en el proyecto
# todavía, pero existe como contrato preparado para extender (OCP)
class INotificable(ABC):
    """Contrato especifico para clases que envian notificaciones."""

    @abstractmethod
    def notificar(self, mensaje: str, destinatario) -> None:
        pass

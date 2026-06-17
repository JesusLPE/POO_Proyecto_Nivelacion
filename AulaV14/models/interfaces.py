from abc import ABC, abstractmethod


# ISP – interfaces específicas, no un único dios-contrato
class IAutenticable(ABC):
    @abstractmethod
    def iniciarSesion(self, usuario: str, contrasenia: str) -> bool: pass
    @abstractmethod
    def cerrarSesion(self) -> None: pass
    @abstractmethod
    def _verificarCuenta(self) -> bool: pass


class ICalificable(ABC):
    @abstractmethod
    def calcularPromedio(self, notas: list) -> float: pass
    @abstractmethod
    def esta_aprobado(self) -> bool: pass


class IRepositorio(ABC):
    """DIP – las capas superiores dependen de esta abstracción, no de JsonManager."""
    @abstractmethod
    def cargar(self, ruta: str) -> list: pass
    @abstractmethod
    def guardar(self, ruta: str, datos: list) -> None: pass


class INotificable(ABC):
    @abstractmethod
    def notificar(self, mensaje: str, destinatario) -> None: pass

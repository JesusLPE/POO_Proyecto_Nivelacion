
from abc import ABC, abstractmethod

class IniciarSesion(ABC):
    """Interfaz (contrato) para inicio y cierre de sesión."""

    @abstractmethod
    def iniciarSesion(self, usuario: str, contrasenia: str) -> bool:
        """Método abstracto para iniciar sesión."""
        pass

    @abstractmethod
    def cerrarSesion(self) -> None:
        """Método abstracto para cerrar sesión."""
        pass

    @abstractmethod
    def _verificarCuenta(self) -> bool:
        """Método protegido abstracto para verificar cuenta."""
        pass
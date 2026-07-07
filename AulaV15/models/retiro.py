"""models/retiro.py

SRP – SolicitudRetiro representa la solicitud de un estudiante para
retirarse de una materia/asignatura. Es un modelo de dominio puro:
solo datos y encapsulamiento, sin lógica de persistencia ni de UI.
"""


class SolicitudRetiro:
    """Encapsula una solicitud de retiro de materia."""

    ESTADOS_VALIDOS = ("Pendiente", "Aprobada", "Rechazada")

    def __init__(self, id: int, estudiante_id: str, materia_id: int,
                 motivo: str, estado: str = "Pendiente",
                 fecha: str = "", respuesta_coordinador: str = ""):
        self.__id = id
        self.__estudiante_id = estudiante_id   # email del estudiante
        self.__materia_id = materia_id         # id de la Asignatura
        self.__motivo = motivo
        self.__estado = estado if estado in self.ESTADOS_VALIDOS else "Pendiente"
        self.__fecha = fecha
        self.__respuesta_coordinador = respuesta_coordinador

    @property
    def id(self) -> int:
        return self.__id

    @property
    def estudiante_id(self) -> str:
        return self.__estudiante_id

    @property
    def materia_id(self) -> int:
        return self.__materia_id

    @property
    def motivo(self) -> str:
        return self.__motivo

    @property
    def estado(self) -> str:
        return self.__estado

    @estado.setter
    def estado(self, valor: str):
        if valor not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido: {valor}. Use uno de {self.ESTADOS_VALIDOS}")
        self.__estado = valor

    @property
    def fecha(self) -> str:
        return self.__fecha

    @property
    def respuesta_coordinador(self) -> str:
        return self.__respuesta_coordinador

    @respuesta_coordinador.setter
    def respuesta_coordinador(self, valor: str):
        self.__respuesta_coordinador = valor

    def aprobar(self, respuesta: str = "") -> None:
        self.estado = "Aprobada"
        if respuesta:
            self.respuesta_coordinador = respuesta

    def rechazar(self, respuesta: str = "") -> None:
        self.estado = "Rechazada"
        if respuesta:
            self.respuesta_coordinador = respuesta

    def esta_pendiente(self) -> bool:
        return self.__estado == "Pendiente"

    def __repr__(self) -> str:
        return f"SolicitudRetiro(id={self.__id}, estado={self.__estado})"

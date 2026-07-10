# POO: Clase
class SolicitudRetiro:
    """Solicitud de retiro de materia.

    Mantiene una propiedad para estado porque ahi si existe una regla de
    negocio: solo se aceptan estados conocidos.
    """

    ESTADOS_VALIDOS = ("Pendiente", "Aprobada", "Rechazada")

    # POO: Constructor | POO: Propiedades (atributos de instancia)
    def __init__(self, id: int, estudiante_id: str, materia_id: int,
                 motivo: str, estado: str = "Pendiente",
                 fecha: str = "", respuesta_coordinador: str = ""):
        self.id = id
        self.estudiante_id = estudiante_id
        self.materia_id = materia_id
        self.motivo = motivo
        # POO: Encapsulamiento -> _estado es el atributo real "protegido"
        self._estado = "Pendiente"
        self.estado = estado if estado in self.ESTADOS_VALIDOS else "Pendiente"
        self.fecha = fecha
        self.respuesta_coordinador = respuesta_coordinador

    # POO: Propiedad (@property) -> getter de estado
    @property
    def estado(self) -> str:
        return self._estado

    # POO: Propiedad (setter) -> valida antes de asignar; ejemplo real de
    # Encapsulamiento (controla cómo se modifica el atributo interno _estado)
    @estado.setter
    def estado(self, valor: str):
        if valor not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado invalido: {valor}. Use uno de {self.ESTADOS_VALIDOS}")
        self._estado = valor

    # POO: Métodos
    def aprobar(self, respuesta: str = "") -> None:
        self.estado = "Aprobada"
        if respuesta:
            self.respuesta_coordinador = respuesta

    def rechazar(self, respuesta: str = "") -> None:
        self.estado = "Rechazada"
        if respuesta:
            self.respuesta_coordinador = respuesta

    def esta_pendiente(self) -> bool:
        return self.estado == "Pendiente"

    def __repr__(self) -> str:
        return f"SolicitudRetiro(id={self.id}, estado={self.estado})"

from dataclasses import dataclass, field
from typing import Any


# POO: Clase (dataclass)
@dataclass
class ErrorImportacion:
    fila: int
    campo: str
    mensaje: str
    datos: dict[str, Any] = field(default_factory=dict)


# POO: Clase (dataclass)
# POO: Relación entre clases -> Composición: contiene una lista de ErrorImportacion
@dataclass
class ResultadoImportacion:
    total: int = 0
    validos: int = 0
    invalidos: int = 0
    creados: int = 0
    errores: list[ErrorImportacion] = field(default_factory=list)

    # POO: Propiedad (@property) -> valor derivado, no se guarda directamente
    @property
    def exitoso(self) -> bool:
        return self.invalidos == 0 and self.creados > 0

    # POO: Método
    def agregar_error(self, fila: int, campo: str, mensaje: str, datos: dict | None = None) -> None:
        self.invalidos += 1
        self.errores.append(ErrorImportacion(fila, campo, mensaje, datos or {}))

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ErrorImportacion:
    fila: int
    campo: str
    mensaje: str
    datos: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultadoImportacion:
    total: int = 0
    validos: int = 0
    invalidos: int = 0
    creados: int = 0
    errores: list[ErrorImportacion] = field(default_factory=list)

    @property
    def exitoso(self) -> bool:
        return self.invalidos == 0 and self.creados > 0

    def agregar_error(self, fila: int, campo: str, mensaje: str, datos: dict | None = None) -> None:
        self.invalidos += 1
        self.errores.append(ErrorImportacion(fila, campo, mensaje, datos or {}))

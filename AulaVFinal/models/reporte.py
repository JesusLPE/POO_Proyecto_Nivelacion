"""models/reporte.py

Modelo de datos puro para el subsistema de reportes.

- `SeccionReporte`  : un bloque tabular dentro de un reporte.
- `Reporte`         : el PRODUCTO final construido por los módulos de
                      `services/reporte_service/` (uno por tipo de
                      reporte). No contiene lógica de negocio, solo
                      datos listos para que la UI los renderice.
- `RegistroReporte` : entrada de historial que se persiste cuando un
                      reporte es generado (por ejemplo, por el
                      Coordinador), para que otros roles (el
                      Administrador) puedan consultar qué reportes se
                      generaron, cuándo y por quién.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


# POO: Clase (con @dataclass -> genera constructor y __repr__ automáticamente)
@dataclass
class SeccionReporte:
    """Una sección del reporte: título, columnas y filas tabulares."""
    # POO: Propiedades (atributos de instancia declarados como dataclass)
    titulo: str
    columnas: List[str]
    filas: List[tuple]
    nota: Optional[str] = None  # observación o texto explicativo opcional


# POO: Clase (dataclass) | Patrón: "Producto" resultado de Facade/Director
# POO: Relación entre clases -> Composición: un Reporte contiene una lista
# de SeccionReporte (si se destruye el Reporte, sus secciones dejan de tener sentido)
@dataclass
class Reporte:
    """Producto final construido por `services/reporte_service/`.

    Es deliberadamente "tonto": no contiene lógica, solo datos ya
    procesados y listos para que la capa UI los renderice (tablas,
    tarjetas, etc.) sin volver a consultar el repositorio.
    """
    titulo: str
    subtitulo: str = ""
    generado_en: str = field(default_factory=lambda: datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    secciones: List[SeccionReporte] = field(default_factory=list)
    totales: List[tuple] = field(default_factory=list)   # [(etiqueta, valor), ...]
    pie: str = ""

    # POO: Métodos
    def agregar_seccion(self, seccion: SeccionReporte) -> None:
        self.secciones.append(seccion)

    def agregar_total(self, etiqueta: str, valor) -> None:
        self.totales.append((etiqueta, valor))


# POO: Clase (dataclass)
@dataclass
class RegistroReporte:
    """Metadatos persistidos de un reporte generado.

    Se guarda en `data/reportes_generados.json` cada vez que un rol
    (típicamente el Coordinador) genera un reporte, para que el
    Administrador pueda revisar el historial desde su propia interfaz.
    """
    id: int
    tipo: str               # "docente" | "coordinador" | "estudiante" | "administrador"
    titulo: str
    subtitulo: str
    generado_por: str       # email del usuario que generó el reporte
    rol_generador: str      # rol del usuario que generó el reporte
    fecha: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    totales: List[tuple] = field(default_factory=list)
    num_secciones: int = 0

    # POO: Propiedad (@property) -> valor calculado a partir de otros atributos,
    # se usa como si fuera un atributo normal (registro.resumen_totales)
    @property
    def resumen_totales(self) -> str:
        """Representación corta de los totales para listados."""
        if not self.totales:
            return "-"
        return "  ·  ".join(f"{etq}: {val}" for etq, val in self.totales[:3])

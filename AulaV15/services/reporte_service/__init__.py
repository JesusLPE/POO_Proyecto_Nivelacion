"""services/reporte_service/ (paquete)

Subsistema de reportes, dividido en un módulo por tipo de reporte para
que ningún archivo concentre la lógica de todos los roles a la vez
(el archivo único anterior mezclaba Docente/Coordinador/Estudiante/
Administrador/métricas y superaba las 600 líneas).

API pública (igual que antes de dividir el archivo, para no romper la
capa UI):

    from services.reporte_service import DirectorReportes, ReporteService

- `DirectorReportes` (`director.py`): Facade con un método por reporte.
- `ReporteService`   (`historial.py`): persistencia del historial de
  reportes generados.

Cada `reporte_<rol>.py` / `reporte_<metrica>.py` expone una única
función `construir(repo, ...)` y es responsable únicamente de ESE
reporte (SRP a nivel de archivo, igual que ya se aplicó en `models/`).
"""

from .director import DirectorReportes
from .historial import ReporteService

__all__ = ["DirectorReportes", "ReporteService"]

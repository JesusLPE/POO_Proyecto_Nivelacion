"""services/reporte_service/soporte.py

Utilidades pequeñas compartidas por varios reportes. Vive aparte para
que ningún módulo de reporte necesite importar a otro solo para
reutilizar dos líneas de cálculo.
"""

from __future__ import annotations

from repositories.repositorio_academico import RepositorioAcademico

PIE_POR_DEFECTO = (
    "Sistema de Admisión – Proceso de Nivelación  ·  "
    "Reporte generado automáticamente."
)


def promedio_estudiante(repo: RepositorioAcademico, email: str) -> float:
    """Promedio de notas de un estudiante (0.0 si no tiene calificaciones)."""
    notas = [c.nota for c in repo.calificaciones if c.estudiante.email == email]
    return round(sum(notas) / len(notas), 2) if notas else 0.0

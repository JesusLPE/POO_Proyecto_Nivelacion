"""services/reporte_service/reporte_promedios.py

Reporte de promedios académicos por estudiante.
"""

from __future__ import annotations

from models import Reporte, SeccionReporte
from repositories.repositorio_academico import RepositorioAcademico


def construir(repo: RepositorioAcademico) -> Reporte:
    reporte = Reporte(
        titulo="Reporte de Promedios por Estudiante",
        subtitulo="Promedio académico de estudiantes con calificaciones registradas",
    )
    calificaciones = repo.calificaciones
    if not calificaciones:
        reporte.agregar_seccion(SeccionReporte(
            "Promedios", ["Estudiante", "Carrera", "Promedio"], [],
            nota="No hay calificaciones registradas para generar este reporte."))
        return reporte

    por_estudiante = {}
    for cal in calificaciones:
        key = cal.estudiante.email
        datos = por_estudiante.setdefault(key, {
            "cedula": getattr(cal.estudiante, "cedula", ""),
            "nombre": cal.estudiante.nombre_completo(),
            "carrera": getattr(cal.estudiante, "carrera", "-"),
            "suma": 0.0, "cantidad": 0
        })
        datos["suma"] += float(cal.nota or 0.0)
        datos["cantidad"] += 1

    filas = []
    totales = 0.0
    for datos in sorted(por_estudiante.values(), key=lambda x: x["suma"] / x["cantidad"], reverse=True):
        promedio = datos["suma"] / datos["cantidad"]
        filas.append((datos["cedula"], datos["nombre"], datos["carrera"], f"{promedio:.2f}"))
        totales += promedio

    promedio_general = totales / len(filas) if filas else 0.0
    reporte.agregar_total("Estudiantes con notas", len(filas))
    reporte.agregar_total("Promedio general", f"{promedio_general:.2f}")
    reporte.agregar_seccion(SeccionReporte(
        "Promedios por estudiante", ["Cédula", "Estudiante", "Carrera", "Promedio"], filas[:10],
        nota="Se muestran los 10 estudiantes con mejor promedio."))
    return reporte

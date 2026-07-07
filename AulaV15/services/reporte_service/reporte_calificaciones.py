"""services/reporte_service/reporte_calificaciones.py

Reporte de calificaciones agrupadas por asignatura.
"""

from __future__ import annotations

from models import Reporte, SeccionReporte
from repositories.repositorio_academico import RepositorioAcademico


def construir(repo: RepositorioAcademico) -> Reporte:
    reporte = Reporte(
        titulo="Reporte de Calificaciones por Asignatura",
        subtitulo="Resumen de notas y aprobaciones por asignatura",
    )
    calificaciones = repo.calificaciones
    if not calificaciones:
        reporte.agregar_seccion(SeccionReporte(
            "Resumen de calificaciones", ["Asignatura", "Cantidad"], [],
            nota="No hay calificaciones registradas para generar este reporte."))
        return reporte

    por_asig = {}
    aprobados = 0
    reprobados = 0
    total_nota = 0.0
    total_count = 0
    for cal in calificaciones:
        info = por_asig.setdefault(cal.asignatura, {
            "cantidad": 0, "suma": 0.0, "aprobados": 0, "reprobados": 0
        })
        info["cantidad"] += 1
        info["suma"] += float(cal.nota or 0.0)
        if cal.esta_aprobado():
            info["aprobados"] += 1
            aprobados += 1
        else:
            info["reprobados"] += 1
            reprobados += 1
        total_nota += float(cal.nota or 0.0)
        total_count += 1

    filas = [
        (asig, datos["cantidad"], f"{datos['suma'] / datos['cantidad']:.2f}",
         datos["aprobados"], datos["reprobados"])
        for asig, datos in sorted(por_asig.items(), key=lambda x: (-x[1]["cantidad"], x[0]))
    ]
    reporte.agregar_total("Calificaciones totales", total_count)
    reporte.agregar_total("Aprobados", aprobados)
    reporte.agregar_total("Reprobados", reprobados)
    reporte.agregar_total("Promedio general", f"{(total_nota / total_count):.2f}" if total_count else "0.00")
    reporte.agregar_seccion(SeccionReporte(
        "Calificaciones por asignatura",
        ["Asignatura", "Cantidad", "Promedio", "Aprobados", "Reprobados"],
        filas,
    ))

    mejores = sorted(calificaciones, key=lambda c: float(c.nota or 0.0), reverse=True)[:10]
    reporte.agregar_seccion(SeccionReporte(
        "Mejores calificaciones recientes",
        ["Estudiante", "Asignatura", "Nota"],
        [(c.estudiante.nombre_completo(), c.asignatura, f"{c.nota:.2f}") for c in mejores],
    ))
    return reporte

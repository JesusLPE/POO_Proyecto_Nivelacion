"""services/reporte_service/reporte_carga.py

Reporte de carga de asignaturas: matriculados, horas y créditos.
"""

from __future__ import annotations

from models import Reporte, SeccionReporte
from repositories.repositorio_academico import RepositorioAcademico


def construir(repo: RepositorioAcademico) -> Reporte:
    reporte = Reporte(
        titulo="Reporte de Carga de Asignaturas",
        subtitulo="Alumnos matriculados por asignatura y créditos asociados",
    )
    matriculas = [m for m in repo.matriculas if m.asignatura]
    if not matriculas:
        reporte.agregar_seccion(SeccionReporte(
            "Carga de asignaturas", ["Asignatura", "Matriculados", "Horas", "Créditos"], [],
            nota="No hay matrículas activas para generar este reporte."))
        return reporte

    por_asig = {}
    for m in matriculas:
        nombre = m.asignatura.nombre
        datos = por_asig.setdefault(nombre, {
            "matriculados": 0,
            "horas": m.asignatura.horas,
            "creditos": m.asignatura.creditos,
        })
        datos["matriculados"] += 1

    filas = [
        (asig, datos["matriculados"], datos["horas"], datos["creditos"])
        for asig, datos in sorted(por_asig.items(), key=lambda x: (-x[1]["matriculados"], x[0]))
    ]
    reporte.agregar_total("Asignaturas con matrícula", len(filas))
    reporte.agregar_total("Estudiantes matriculados", sum(d["matriculados"] for d in por_asig.values()))
    reporte.agregar_seccion(SeccionReporte(
        "Carga por asignatura", ["Asignatura", "Matriculados", "Horas", "Créditos"], filas))
    return reporte

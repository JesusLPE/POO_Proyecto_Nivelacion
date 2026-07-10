"""services/reporte_service/reporte_matriculas.py

Reporte de estado de matrículas (activas, pendientes, anuladas).
"""

from __future__ import annotations

from models import Reporte, SeccionReporte
from repositories.repositorio_academico import RepositorioAcademico


def construir(repo: RepositorioAcademico) -> Reporte:
    reporte = Reporte(
        titulo="Reporte de Estado de Matrículas",
        subtitulo="Cantidad de matrículas activas, pendientes y anuladas",
    )
    matriculas = repo.matriculas
    if not matriculas:
        reporte.agregar_seccion(SeccionReporte(
            "Estado de matrículas", ["Asignatura", "Activas", "Pendientes", "Anuladas"], [],
            nota="No hay matrículas registradas para generar este reporte."))
        return reporte

    por_asig = {}
    totales = {"Activa": 0, "Pendiente": 0, "Anulada": 0, "Otra": 0}
    for m in matriculas:
        nombre = m.asignatura.nombre if m.asignatura else "Sin asignatura"
        info = por_asig.setdefault(nombre, {"Activa": 0, "Pendiente": 0, "Anulada": 0, "Otra": 0})
        estado = m.estado if m.estado in info else "Otra"
        info[estado] += 1
        totales[estado] += 1

    filas = [
        (asignatura, info["Activa"], info["Pendiente"], info["Anulada"])
        for asignatura, info in sorted(por_asig.items(), key=lambda x: (-sum(x[1].values()), x[0]))
    ]
    reporte.agregar_total("Matrículas totales", len(matriculas))
    reporte.agregar_total("Activas", totales["Activa"])
    reporte.agregar_total("Pendientes", totales["Pendiente"])
    reporte.agregar_total("Anuladas", totales["Anulada"])
    reporte.agregar_seccion(SeccionReporte(
        "Matrículas por asignatura",
        ["Asignatura", "Activas", "Pendientes", "Anuladas"],
        filas,
    ))
    return reporte

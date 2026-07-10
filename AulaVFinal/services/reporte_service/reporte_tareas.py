"""services/reporte_service/reporte_tareas.py

Reporte de tareas creadas y su estado de entrega.
"""

from __future__ import annotations

from models import Reporte, SeccionReporte
from repositories.repositorio_academico import RepositorioAcademico


def construir(repo: RepositorioAcademico) -> Reporte:
    reporte = Reporte(
        titulo="Reporte de Tareas",
        subtitulo="Visión rápida de tareas creadas y su estado",
    )
    tareas = repo.tareas
    if not tareas:
        reporte.agregar_seccion(SeccionReporte(
            "Tareas", ["Título", "Asignatura", "Creador", "Entregas", "Estado"], [],
            nota="No hay tareas registradas para generar este reporte."))
        return reporte

    entregadas = sum(1 for t in tareas if t.entregas)
    pendientes = sum(1 for t in tareas if not t.entregas)
    reporte.agregar_total("Tareas totales", len(tareas))
    reporte.agregar_total("Con entregas", entregadas)
    reporte.agregar_total("Pendientes", pendientes)

    filas = []
    for tarea in sorted(tareas, key=lambda t: (-len(t.entregas), t.titulo)):
        asignatura = next((a.nombre for a in repo.asignaturas if a.id == tarea.asignatura_id), "General")
        creador = repo.usuarios.get(tarea.creador_email)
        filas.append((
            tarea.titulo,
            asignatura,
            creador.nombre_completo() if creador else tarea.creador_email,
            len(tarea.entregas),
            "Entregada" if tarea.entregas else "Pendiente",
        ))
    reporte.agregar_seccion(SeccionReporte(
        "Tareas y entregas", ["Título", "Asignatura", "Creador", "Entregas", "Estado"], filas))
    return reporte

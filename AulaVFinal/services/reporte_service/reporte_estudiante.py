"""services/reporte_service/reporte_estudiante.py

Construcción del reporte de progreso individual de un Estudiante.
"""

from __future__ import annotations

from models import Notas, Reporte, SeccionReporte
from repositories.repositorio_academico import RepositorioAcademico

from .soporte import PIE_POR_DEFECTO, promedio_estudiante


def construir(repo: RepositorioAcademico, estudiante_email: str) -> Reporte:
    estudiante = repo.usuarios.get(estudiante_email)
    reporte = Reporte(titulo="Reporte de progreso individual")

    # Sección 1: calificaciones
    califs = [c for c in repo.calificaciones if c.estudiante.email == estudiante_email]
    filas_notas = [
        (c.asignatura, f"{c.nota:.1f}", Notas.estado(c.nota), c.observacion or "-")
        for c in califs
    ]
    reporte.agregar_seccion(SeccionReporte(
        titulo="Calificaciones por asignatura",
        columnas=["Asignatura", "Nota", "Estado", "Observaciones"],
        filas=filas_notas,
    ))

    # Sección 2: tareas y entregas
    ids_matriculadas = repo.ids_asignaturas_matriculadas(estudiante_email)
    tareas_visibles = repo.tareas_visibles(estudiante_email)
    filas_tareas = []
    for t in tareas_visibles:
        asignatura = next((a.nombre for a in repo.asignaturas if a.id == t.asignatura_id), "General")
        estado = "Entregada" if t.entregada_por(estudiante_email) else "Pendiente"
        filas_tareas.append((t.titulo, asignatura, t.fecha_limite or "-", estado))
    reporte.agregar_seccion(SeccionReporte(
        titulo="Tareas y entregas",
        columnas=["Actividad", "Asignatura", "Fecha límite", "Estado"],
        filas=filas_tareas,
    ))

    # Sección 3: matrículas
    filas_matriculas = []
    for m in repo.matriculas:
        if m.estudiante and m.estudiante.email == estudiante_email:
            gratuita = "Sí" if m.verificarGratuidad() else "No"
            filas_matriculas.append((
                m.asignatura.nombre if m.asignatura else "-",
                m.fecha, m.tipo, m.estado, gratuita,
            ))
    reporte.agregar_seccion(SeccionReporte(
        titulo="Historial de matrículas",
        columnas=["Asignatura", "Fecha", "Tipo", "Estado", "Gratuita"],
        filas=filas_matriculas,
    ))

    # Totales
    promedio = promedio_estudiante(repo, estudiante_email)
    entregadas = len([t for t in tareas_visibles if t.entregada_por(estudiante_email)])
    pendientes = len(tareas_visibles) - entregadas

    reporte.agregar_total("Promedio general", f"{promedio:.2f}")
    reporte.agregar_total("Estado académico", Notas.estado(promedio))
    reporte.agregar_total("Tareas entregadas", entregadas)
    reporte.agregar_total("Tareas pendientes", pendientes)
    reporte.agregar_total("Asignaturas matriculadas activas", len(ids_matriculadas))

    if estudiante is not None:
        reporte.subtitulo = (
            f"{estudiante.nombre_completo()}  ·  "
            f"{getattr(estudiante, 'carrera', '')}  ·  "
            f"Cédula: {getattr(estudiante, 'cedula', '-')}  ·  Matrícula: {getattr(estudiante, 'matricula', '-')}"
        )
    reporte.pie = PIE_POR_DEFECTO
    return reporte

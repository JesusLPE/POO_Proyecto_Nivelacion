"""services/reporte_service/reporte_docente.py

Construcción del reporte de progreso de alumnos para un Docente.
Único responsable de este reporte (SRP) — no conoce a los demás.
"""

from __future__ import annotations

from models import Notas, Reporte, SeccionReporte
from repositories.repositorio_academico import RepositorioAcademico

from .soporte import PIE_POR_DEFECTO


def construir(repo: RepositorioAcademico, docente_email: str) -> Reporte:
    docente = repo.usuarios.get(docente_email)
    reporte = Reporte(
        titulo="Reporte de progreso de alumnos",
        subtitulo=docente.nombre_completo() if docente else docente_email,
    )

    asignaturas_ids = {
        t.asignatura_id
        for t in repo.tareas_docente(docente_email)
        if t.asignatura_id
    }
    nombres_asignaturas = {a.nombre for a in repo.asignaturas if a.id in asignaturas_ids}

    if not nombres_asignaturas:
        carreras = {c.carrera for c in repo.cursos
                    if c.docente_email == docente_email and c.carrera}
        nombres_asignaturas = {
            m.asignatura.nombre for m in repo.matriculas
            if m.asignatura and m.estudiante
            and getattr(m.estudiante, "carrera", "") in carreras
        }

    calificaciones = [c for c in repo.calificaciones if c.asignatura in nombres_asignaturas]

    emails_estudiantes = {
        m.estudiante.email for m in repo.matriculas
        if m.estado == "Activa" and m.estudiante and m.asignatura
        and m.asignatura.nombre in nombres_asignaturas
    }
    estudiantes = [e for e in repo.estudiantes if e.email in emails_estudiantes]

    # Sección 1: acta de calificaciones
    filas_acta = []
    for c in calificaciones:
        estado = "Aprobado" if c.esta_aprobado() else "Reprobado"
        filas_acta.append((getattr(c.estudiante, "cedula", ""), c.estudiante.nombre_completo(), c.asignatura,
                            f"{c.nota:.1f}", estado, c.observacion or "-"))
    reporte.agregar_seccion(SeccionReporte(
        titulo="Acta de calificaciones",
        columnas=["Cédula", "Estudiante", "Asignatura", "Nota", "Estado", "Observaciones"],
        filas=filas_acta,
    ))

    # Sección 2: progreso de entregas por tarea
    filas_progreso = []
    for tarea in repo.tareas_docente(docente_email):
        asignatura = next((a.nombre for a in repo.asignaturas
                            if a.id == tarea.asignatura_id), "General")
        entregadas = len([e for e in tarea.entregas if e.get("estado") == "Realizada"])
        pendientes = max(len(estudiantes) - entregadas, 0)
        resultado = "Completa" if pendientes == 0 and estudiantes else "Con pendientes"
        filas_progreso.append((tarea.titulo, asignatura, entregadas, pendientes, resultado))
    reporte.agregar_seccion(SeccionReporte(
        titulo="Progreso de actividades evaluativas",
        columnas=["Actividad", "Asignatura", "Entregadas", "Pendientes", "Resultado"],
        filas=filas_progreso,
    ))

    # Sección 3: progreso individual por estudiante
    filas_estudiantes = []
    for est in estudiantes:
        notas = [c.nota for c in calificaciones if c.estudiante.email == est.email]
        promedio = round(sum(notas) / len(notas), 2) if notas else 0.0
        entregadas = sum(1 for tarea in repo.tareas_docente(docente_email)
                          if tarea.entregada_por(est.email))
        filas_estudiantes.append((
            getattr(est, "cedula", ""), est.nombre_completo(), getattr(est, "carrera", "-"),
            f"{entregadas} entrega(s)", f"{promedio:.2f}",
            Notas.estado(promedio),
        ))
    reporte.agregar_seccion(SeccionReporte(
        titulo="Progreso individual de estudiantes",
        columnas=["Cédula", "Estudiante", "Carrera", "Entregas", "Promedio", "Estado"],
        filas=filas_estudiantes,
    ))

    # Totales
    reporte.agregar_total("Estudiantes evaluados", len(estudiantes))
    reporte.agregar_total("Calificaciones registradas", len(calificaciones))
    aprobados = len([c for c in calificaciones if c.esta_aprobado()])
    reporte.agregar_total("Aprobados", aprobados)
    reporte.agregar_total("Reprobados", len(calificaciones) - aprobados)
    reporte.pie = PIE_POR_DEFECTO
    return reporte

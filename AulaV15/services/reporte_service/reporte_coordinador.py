"""services/reporte_service/reporte_coordinador.py

Construcción del reporte de métricas globales y rendimiento académico
para el Coordinador.
"""

from __future__ import annotations

from models import Reporte, SeccionReporte
from repositories.repositorio_academico import RepositorioAcademico

from .soporte import PIE_POR_DEFECTO, promedio_estudiante


def construir(repo: RepositorioAcademico) -> Reporte:
    reporte = Reporte(
        titulo="Reporte de métricas globales y rendimiento",
        subtitulo="Proceso de Nivelación – Coordinación Académica",
    )

    # Sección 1: carga docente
    filas_docentes = []
    for d in repo.docentes:
        cursos = [c for c in repo.cursos if c.docente_email == d.email]
        asignadas = ", ".join(c.nombre for c in cursos) if cursos else "Sin asignar"
        horarios = "; ".join(str(c.horario) for c in cursos if c.horario) or "Sin horario"
        horas = sum(c._total_horas for c in cursos)
        filas_docentes.append((d.nombre_completo(), asignadas, horarios, f"{horas} h"))
    reporte.agregar_seccion(SeccionReporte(
        titulo="Carga docente",
        columnas=["Docente", "Asignaturas asignadas", "Horarios de clase", "Carga horaria"],
        filas=filas_docentes,
    ))

    # Sección 2: rendimiento por asignatura
    filas_asignaturas = []
    for a in repo.asignaturas:
        notas = [c for c in repo.calificaciones if c.asignatura == a.nombre]
        prom = round(sum(c.nota for c in notas) / len(notas), 2) if notas else 0.0
        filas_asignaturas.append((
            a.nombre, f"{prom:.2f}",
            len([c for c in notas if c.nota >= 7]),
            len([c for c in notas if c.nota < 7]),
        ))
    reporte.agregar_seccion(SeccionReporte(
        titulo="Rendimiento por asignatura",
        columnas=["Asignatura", "Promedio", "Aprobados", "Reprobados"],
        filas=filas_asignaturas,
    ))

    # Sección 3: rendimiento por grupo/carrera
    filas_grupos = []
    for c in repo.cursos:
        ests = [e for e in repo.estudiantes if getattr(e, "carrera", "") == c.carrera]
        promedios = [promedio_estudiante(repo, e.email) for e in ests]
        promedios = [p for p in promedios if p > 0]
        prom = round(sum(promedios) / len(promedios), 2) if promedios else 0.0
        filas_grupos.append((c.nombre, c.carrera or "General", f"{prom:.2f}", len(ests)))
    reporte.agregar_seccion(SeccionReporte(
        titulo="Rendimiento por grupo",
        columnas=["Grupo", "Carrera", "Promedio", "Estudiantes"],
        filas=filas_grupos,
    ))

    # Sección 4: estado de matrículas
    estados = {"Activa": 0, "Pendiente": 0, "Anulada": 0}
    for m in repo.matriculas:
        estados[m.estado] = estados.get(m.estado, 0) + 1
    filas_matriculas = [(estado, total) for estado, total in estados.items()]
    reporte.agregar_seccion(SeccionReporte(
        titulo="Estado de matrículas",
        columnas=["Estado", "Total"],
        filas=filas_matriculas,
    ))

    # Totales / indicadores globales
    total_estudiantes = len(repo.estudiantes)
    aprobados = [e for e in repo.estudiantes if promedio_estudiante(repo, e.email) >= 7]
    evaluados = [e for e in repo.estudiantes if promedio_estudiante(repo, e.email) > 0]
    anuladas = estados.get("Anulada", 0)
    total_matriculas = len(repo.matriculas)
    tasa_aprobacion = round(len(aprobados) * 100 / total_estudiantes, 2) if total_estudiantes else 0
    tasa_desercion = round(anuladas * 100 / total_matriculas, 2) if total_matriculas else 0

    reporte.agregar_total("Tasa de aprobación", f"{tasa_aprobacion}%")
    reporte.agregar_total("Tasa de deserción", f"{tasa_desercion}%")
    reporte.agregar_total("Estudiantes evaluados", len(evaluados))
    reporte.agregar_total("Estudiantes que pasan de nivel", len(aprobados))
    reporte.pie = PIE_POR_DEFECTO
    return reporte

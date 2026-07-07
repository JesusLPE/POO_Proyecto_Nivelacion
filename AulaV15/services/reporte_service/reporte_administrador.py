"""services/reporte_service/reporte_administrador.py

Construcción del reporte de auditoría del sistema para el Administrador.
"""

from __future__ import annotations

from models import Reporte, SeccionReporte
from repositories.repositorio_academico import RepositorioAcademico

from .soporte import PIE_POR_DEFECTO


def construir(repo: RepositorioAcademico) -> Reporte:
    reporte = Reporte(
        titulo="Reporte de auditoría del sistema",
        subtitulo="Usuarios activos e inconsistencias de datos",
    )

    # Sección 1: usuarios por rol
    conteo_roles = {}
    for u in repo.usuarios.values():
        rol = u.obtener_rol()
        conteo_roles[rol] = conteo_roles.get(rol, 0) + 1
    filas_roles = [(rol.capitalize(), total) for rol, total in conteo_roles.items()]
    reporte.agregar_seccion(SeccionReporte(
        titulo="Usuarios activos por rol",
        columnas=["Rol", "Total"],
        filas=filas_roles,
    ))

    # Sección 2: inconsistencias de datos
    inconsistencias = _detectar_inconsistencias(repo)
    reporte.agregar_seccion(SeccionReporte(
        titulo="Inconsistencias detectadas",
        columnas=["Tipo", "Referencia", "Detalle"],
        filas=inconsistencias,
    ))

    # Sección 3: resumen académico global
    filas_resumen = [
        ("Estudiantes", len(repo.estudiantes)),
        ("Docentes", len(repo.docentes)),
        ("Grupos de nivelación", len(repo.cursos)),
        ("Asignaturas", len(repo.asignaturas)),
        ("Matrículas registradas", len(repo.matriculas)),
        ("Tareas publicadas", len(repo.tareas)),
        ("Calificaciones registradas", len(repo.calificaciones)),
        ("Horarios programados", len(repo.horarios)),
    ]
    reporte.agregar_seccion(SeccionReporte(
        titulo="Resumen académico global",
        columnas=["Entidad", "Total"],
        filas=filas_resumen,
    ))

    # Totales
    problemas_reales = [i for i in inconsistencias if i[0] != "Sin inconsistencias"]
    reporte.agregar_total("Usuarios totales", len(repo.usuarios))
    reporte.agregar_total("Inconsistencias detectadas", len(problemas_reales))
    reporte.agregar_total(
        "Estado de integridad",
        "Correcto" if not problemas_reales else "Requiere revisión",
    )
    reporte.pie = PIE_POR_DEFECTO
    return reporte


def _detectar_inconsistencias(repo: RepositorioAcademico) -> list[tuple]:
    """Reglas de integridad de datos, aisladas para no inflar `construir`."""
    inconsistencias = []

    for c in repo.cursos:
        if not c.docente_email:
            inconsistencias.append(("Grupo sin docente", c.nombre,
                                    "Asignar un docente desde Coordinación"))
        elif c.docente_email not in repo.usuarios:
            inconsistencias.append(("Docente inexistente", c.nombre,
                                    f"El correo {c.docente_email} no está registrado"))
        if not c.horario:
            inconsistencias.append(("Grupo sin horario", c.nombre,
                                    "Programar horario desde Coordinación"))

    for m in repo.matriculas:
        if m.estudiante is None:
            inconsistencias.append(("Matrícula sin estudiante", f"ID {m.id}",
                                    "Revisar referencia de estudiante"))
        if m.asignatura is None:
            inconsistencias.append(("Matrícula sin asignatura", f"ID {m.id}",
                                    "Revisar referencia de asignatura"))

    for c in repo.calificaciones:
        if not (0 <= c.nota <= 10):
            inconsistencias.append(("Calificación fuera de rango",
                                    f"{c.estudiante.nombre_completo()} – {c.asignatura}",
                                    f"Nota registrada: {c.nota}"))

    if not inconsistencias:
        inconsistencias.append(("Sin inconsistencias", "-",
                                "No se detectaron problemas de integridad de datos"))
    return inconsistencias

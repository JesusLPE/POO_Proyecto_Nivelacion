"""services/reporte_service.py

Lógica de negocio del subsistema de reportes (patrón Builder + persistencia).

- El PRODUCTO (`Reporte`, `SeccionReporte`) y el modelo de historial
  (`RegistroReporte`) viven en `models/reporte.py` — este módulo solo
  contiene COMPORTAMIENTO, no datos.
- `ReporteBuilder` es la interfaz/clase base del Builder: define los
  pasos comunes (encabezado, secciones, totales, pie) y la interfaz
  fluida (cada paso retorna `self`).
- `ReporteDocenteBuilder`, `ReporteCoordinadorBuilder`,
  `ReporteEstudianteBuilder` y `ReporteAdministradorBuilder` son los
  builders concretos: cada uno sabe construir las secciones propias
  de su rol a partir del `RepositorioAcademico`.
- `DirectorReportes` orquesta la construcción completa para no dejar
  esa responsabilidad en la capa de UI.
- `ReporteService` persiste un `RegistroReporte` cada vez que se genera
  un reporte (por ejemplo, desde el panel del Coordinador), para que
  el Administrador pueda consultar el historial desde su propia UI.

La capa UI solo debe:
    director = DirectorReportes(repo)
    reporte  = director.construir_reporte_coordinador()
    # ... renderizar reporte ...
    ReporteService(repo).registrar_generacion(reporte, "coordinador", usuario.email, "coordinador")
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from models import Notas, Reporte, SeccionReporte, RegistroReporte
from repositories.repositorio_academico import RepositorioAcademico


# ── BUILDER BASE ──────────────────────────────────────────────────────────────
class ReporteBuilder(ABC):
    """Interfaz/clase base del Builder.

    Cada paso retorna `self` para permitir una interfaz fluida:
        builder.iniciar_reporte(...).agregar_secciones(...).finalizar()

    Las subclases concretas implementan `agregar_secciones`, que es el
    único paso que varía verdaderamente entre roles.
    """

    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo
        self._reporte: Optional[Reporte] = None

    # Paso 1 – encabezado del reporte
    def iniciar_reporte(self, titulo: str, subtitulo: str = "") -> "ReporteBuilder":
        self._reporte = Reporte(titulo=titulo, subtitulo=subtitulo)
        return self

    # Paso 2 – secciones específicas de cada rol (varía por builder concreto)
    @abstractmethod
    def agregar_secciones(self, **contexto) -> "ReporteBuilder":
        ...

    # Paso 3 – pie de página común a todos los reportes
    def agregar_pie(self, texto: Optional[str] = None) -> "ReporteBuilder":
        self._reporte.pie = texto or (
            "Sistema de Admisión – Proceso de Nivelación  ·  "
            "Reporte generado automáticamente."
        )
        return self

    # Paso 4 – producto final
    def construir(self) -> Reporte:
        if self._reporte is None:
            raise ValueError("Debe llamar a iniciar_reporte() antes de construir().")
        return self._reporte

    # Utilidad compartida para builders concretos
    def _promedio_estudiante(self, email: str) -> float:
        notas = [c.nota for c in self._repo.calificaciones if c.estudiante.email == email]
        return round(sum(notas) / len(notas), 2) if notas else 0.0


# ── BUILDER: DOCENTE ──────────────────────────────────────────────────────────
class ReporteDocenteBuilder(ReporteBuilder):
    """Construye el reporte de progreso de alumnos para un docente."""

    def agregar_secciones(self, **contexto) -> "ReporteDocenteBuilder":
        docente_email: str = contexto["docente_email"]
        repo = self._repo

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
        self._reporte.agregar_seccion(SeccionReporte(
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
        self._reporte.agregar_seccion(SeccionReporte(
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
        self._reporte.agregar_seccion(SeccionReporte(
            titulo="Progreso individual de estudiantes",
            columnas=["Cédula", "Estudiante", "Carrera", "Entregas", "Promedio", "Estado"],
            filas=filas_estudiantes,
        ))

        # Totales
        self._reporte.agregar_total("Estudiantes evaluados", len(estudiantes))
        self._reporte.agregar_total("Calificaciones registradas", len(calificaciones))
        aprobados = len([c for c in calificaciones if c.esta_aprobado()])
        self._reporte.agregar_total("Aprobados", aprobados)
        self._reporte.agregar_total("Reprobados", len(calificaciones) - aprobados)
        return self


# ── BUILDER: COORDINADOR ──────────────────────────────────────────────────────
class ReporteCoordinadorBuilder(ReporteBuilder):
    """Construye el reporte de métricas globales y rendimiento académico."""

    def agregar_secciones(self, **contexto) -> "ReporteCoordinadorBuilder":
        repo = self._repo

        # Sección 1: carga docente
        filas_docentes = []
        for d in repo.docentes:
            cursos = [c for c in repo.cursos if c.docente_email == d.email]
            asignadas = ", ".join(c.nombre for c in cursos) if cursos else "Sin asignar"
            horarios = "; ".join(str(c.horario) for c in cursos if c.horario) or "Sin horario"
            horas = sum(c._total_horas for c in cursos)
            filas_docentes.append((d.nombre_completo(), asignadas, horarios, f"{horas} h"))
        self._reporte.agregar_seccion(SeccionReporte(
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
        self._reporte.agregar_seccion(SeccionReporte(
            titulo="Rendimiento por asignatura",
            columnas=["Asignatura", "Promedio", "Aprobados", "Reprobados"],
            filas=filas_asignaturas,
        ))

        # Sección 3: rendimiento por grupo/carrera
        filas_grupos = []
        for c in repo.cursos:
            ests = [e for e in repo.estudiantes if getattr(e, "carrera", "") == c.carrera]
            promedios = [self._promedio_estudiante(e.email) for e in ests]
            promedios = [p for p in promedios if p > 0]
            prom = round(sum(promedios) / len(promedios), 2) if promedios else 0.0
            filas_grupos.append((c.nombre, c.carrera or "General", f"{prom:.2f}", len(ests)))
        self._reporte.agregar_seccion(SeccionReporte(
            titulo="Rendimiento por grupo",
            columnas=["Grupo", "Carrera", "Promedio", "Estudiantes"],
            filas=filas_grupos,
        ))

        # Sección 4: estado de matrículas
        estados = {"Activa": 0, "Pendiente": 0, "Anulada": 0}
        for m in repo.matriculas:
            estados[m.estado] = estados.get(m.estado, 0) + 1
        filas_matriculas = [(estado, total) for estado, total in estados.items()]
        self._reporte.agregar_seccion(SeccionReporte(
            titulo="Estado de matrículas",
            columnas=["Estado", "Total"],
            filas=filas_matriculas,
        ))

        # Totales / indicadores globales
        total_estudiantes = len(repo.estudiantes)
        aprobados = [e for e in repo.estudiantes if self._promedio_estudiante(e.email) >= 7]
        evaluados = [e for e in repo.estudiantes if self._promedio_estudiante(e.email) > 0]
        anuladas = estados.get("Anulada", 0)
        total_matriculas = len(repo.matriculas)
        tasa_aprobacion = round(len(aprobados) * 100 / total_estudiantes, 2) if total_estudiantes else 0
        tasa_desercion = round(anuladas * 100 / total_matriculas, 2) if total_matriculas else 0

        self._reporte.agregar_total("Tasa de aprobación", f"{tasa_aprobacion}%")
        self._reporte.agregar_total("Tasa de deserción", f"{tasa_desercion}%")
        self._reporte.agregar_total("Estudiantes evaluados", len(evaluados))
        self._reporte.agregar_total("Estudiantes que pasan de nivel", len(aprobados))
        return self


# ── BUILDER: ESTUDIANTE ───────────────────────────────────────────────────────
class ReporteEstudianteBuilder(ReporteBuilder):
    """Construye el reporte de progreso individual de un estudiante."""

    def agregar_secciones(self, **contexto) -> "ReporteEstudianteBuilder":
        estudiante_email: str = contexto["estudiante_email"]
        repo = self._repo

        estudiante = repo.usuarios.get(estudiante_email)

        # Sección 1: calificaciones
        califs = [c for c in repo.calificaciones if c.estudiante.email == estudiante_email]
        filas_notas = []
        for c in califs:
            filas_notas.append((c.asignatura, f"{c.nota:.1f}", Notas.estado(c.nota), c.observacion or "-"))
        self._reporte.agregar_seccion(SeccionReporte(
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
        self._reporte.agregar_seccion(SeccionReporte(
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
        self._reporte.agregar_seccion(SeccionReporte(
            titulo="Historial de matrículas",
            columnas=["Asignatura", "Fecha", "Tipo", "Estado", "Gratuita"],
            filas=filas_matriculas,
        ))

        # Totales
        promedio = self._promedio_estudiante(estudiante_email)
        entregadas = len([t for t in tareas_visibles if t.entregada_por(estudiante_email)])
        pendientes = len(tareas_visibles) - entregadas

        self._reporte.agregar_total("Promedio general", f"{promedio:.2f}")
        self._reporte.agregar_total("Estado académico", Notas.estado(promedio))
        self._reporte.agregar_total("Tareas entregadas", entregadas)
        self._reporte.agregar_total("Tareas pendientes", pendientes)
        self._reporte.agregar_total("Asignaturas matriculadas activas", len(ids_matriculadas))

        if estudiante is not None:
            self._reporte.subtitulo = (
                f"{estudiante.nombre_completo()}  ·  "
                f"{getattr(estudiante, 'carrera', '')}  ·  "
                f"Cédula: {getattr(estudiante, 'cedula', '-')}  ·  Matrícula: {getattr(estudiante, 'matricula', '-')}"
            )
        return self


# ── BUILDER: ADMINISTRADOR ────────────────────────────────────────────────────
class ReporteAdministradorBuilder(ReporteBuilder):
    """Construye el reporte de auditoría del sistema."""

    def agregar_secciones(self, **contexto) -> "ReporteAdministradorBuilder":
        repo = self._repo

        # Sección 1: usuarios por rol
        conteo_roles = {}
        for u in repo.usuarios.values():
            rol = u.obtener_rol()
            conteo_roles[rol] = conteo_roles.get(rol, 0) + 1
        filas_roles = [(rol.capitalize(), total) for rol, total in conteo_roles.items()]
        self._reporte.agregar_seccion(SeccionReporte(
            titulo="Usuarios activos por rol",
            columnas=["Rol", "Total"],
            filas=filas_roles,
        ))

        # Sección 2: inconsistencias de datos
        inconsistencias = []

        # Grupos sin docente asignado
        for c in repo.cursos:
            if not c.docente_email:
                inconsistencias.append(("Grupo sin docente", c.nombre,
                                        "Asignar un docente desde Coordinación"))
            elif c.docente_email not in repo.usuarios:
                inconsistencias.append(("Docente inexistente", c.nombre,
                                        f"El correo {c.docente_email} no está registrado"))

        # Grupos sin horario
        for c in repo.cursos:
            if not c.horario:
                inconsistencias.append(("Grupo sin horario", c.nombre,
                                        "Programar horario desde Coordinación"))

        # Matrículas con estudiante o asignatura inexistente
        for m in repo.matriculas:
            if m.estudiante is None:
                inconsistencias.append(("Matrícula sin estudiante", f"ID {m.id}",
                                        "Revisar referencia de estudiante"))
            if m.asignatura is None:
                inconsistencias.append(("Matrícula sin asignatura", f"ID {m.id}",
                                        "Revisar referencia de asignatura"))

        # Calificaciones fuera de rango
        for c in repo.calificaciones:
            if not (0 <= c.nota <= 10):
                inconsistencias.append(("Calificación fuera de rango",
                                        f"{c.estudiante.nombre_completo()} – {c.asignatura}",
                                        f"Nota registrada: {c.nota}"))

        if not inconsistencias:
            inconsistencias.append(("Sin inconsistencias", "-",
                                    "No se detectaron problemas de integridad de datos"))

        self._reporte.agregar_seccion(SeccionReporte(
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
        self._reporte.agregar_seccion(SeccionReporte(
            titulo="Resumen académico global",
            columnas=["Entidad", "Total"],
            filas=filas_resumen,
        ))

        # Totales
        problemas_reales = [i for i in inconsistencias if i[0] != "Sin inconsistencias"]
        self._reporte.agregar_total("Usuarios totales", len(repo.usuarios))
        self._reporte.agregar_total("Inconsistencias detectadas", len(problemas_reales))
        self._reporte.agregar_total(
            "Estado de integridad",
            "Correcto" if not problemas_reales else "Requiere revisión",
        )
        return self


# ── DIRECTOR ──────────────────────────────────────────────────────────────────
class DirectorReportes:
    """Orquesta la construcción completa de cada tipo de reporte.

    La UI solo debe instanciar el Director y llamar al método
    correspondiente; el Director decide qué builder usar, qué pasos
    ejecutar y en qué orden — la UI nunca llama a los builders
    directamente.
    """

    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def _ejecutar(self, builder: ReporteBuilder, titulo: str,
                   subtitulo: str = "", **contexto) -> Reporte:
        return (
            builder
            .iniciar_reporte(titulo, subtitulo)
            .agregar_secciones(**contexto)
            .agregar_pie()
            .construir()
        )

    def construir_reporte_docente(self, docente_email: str) -> Reporte:
        docente = self._repo.usuarios.get(docente_email)
        subtitulo = docente.nombre_completo() if docente else docente_email
        builder = ReporteDocenteBuilder(self._repo)
        return self._ejecutar(
            builder,
            titulo="Reporte de progreso de alumnos",
            subtitulo=subtitulo,
            docente_email=docente_email,
        )

    def construir_reporte_coordinador(self) -> Reporte:
        builder = ReporteCoordinadorBuilder(self._repo)
        return self._ejecutar(
            builder,
            titulo="Reporte de métricas globales y rendimiento",
            subtitulo="Proceso de Nivelación – Coordinación Académica",
        )

    def construir_reporte_calificaciones_por_asignatura(self) -> Reporte:
        reporte = Reporte(
            titulo="Reporte de Calificaciones por Asignatura",
            subtitulo="Resumen de notas y aprobaciones por asignatura",
        )
        calificaciones = self._repo.calificaciones
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

    def construir_reporte_estado_matriculas(self) -> Reporte:
        reporte = Reporte(
            titulo="Reporte de Estado de Matrículas",
            subtitulo="Cantidad de matrículas activas, pendientes y anuladas",
        )
        matriculas = self._repo.matriculas
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

    def construir_reporte_tareas(self) -> Reporte:
        reporte = Reporte(
            titulo="Reporte de Tareas",
            subtitulo="Visión rápida de tareas creadas y su estado",
        )
        tareas = self._repo.tareas
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
            asignatura = next((a.nombre for a in self._repo.asignaturas if a.id == tarea.asignatura_id), "General")
            creador = self._repo.usuarios.get(tarea.creador_email)
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

    def construir_reporte_promedios_estudiantes(self) -> Reporte:
        reporte = Reporte(
            titulo="Reporte de Promedios por Estudiante",
            subtitulo="Promedio académico de estudiantes con calificaciones registradas",
        )
        calificaciones = self._repo.calificaciones
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

    def construir_reporte_carga_asignaturas(self) -> Reporte:
        reporte = Reporte(
            titulo="Reporte de Carga de Asignaturas",
            subtitulo="Alumnos matriculados por asignatura y créditos asociados",
        )
        matriculas = [m for m in self._repo.matriculas if m.asignatura]
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

    def construir_reporte_estudiante(self, estudiante_email: str) -> Reporte:
        builder = ReporteEstudianteBuilder(self._repo)
        return self._ejecutar(
            builder,
            titulo="Reporte de progreso individual",
            estudiante_email=estudiante_email,
        )

    def construir_reporte_administrador(self) -> Reporte:
        builder = ReporteAdministradorBuilder(self._repo)
        return self._ejecutar(
            builder,
            titulo="Reporte de auditoría del sistema",
            subtitulo="Usuarios activos e inconsistencias de datos",
        )


# ── PERSISTENCIA DEL HISTORIAL DE REPORTES ────────────────────────────────────
class ReporteService:
    """SRP – persiste un `RegistroReporte` cada vez que se genera un reporte
    mediante el patrón Builder, para que otros roles (Administrador) puedan
    consultar el historial.

    No reemplaza al Builder: lo complementa. El flujo típico en la UI es:

        director = DirectorReportes(repo)
        reporte  = director.construir_reporte_coordinador()
        render_reporte(contenido, reporte, ...)
        ReporteService(repo).registrar_generacion(
            reporte, tipo="coordinador",
            generado_por=usuario.email, rol_generador=usuario.obtener_rol(),
        )
    """

    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def registrar_generacion(self, reporte: Reporte, tipo: str,
                             generado_por: str, rol_generador: str) -> RegistroReporte:
        nid = self._repo.siguiente_id(self._repo.reportes_generados)
        registro = RegistroReporte(
            id=nid, tipo=tipo, titulo=reporte.titulo, subtitulo=reporte.subtitulo,
            generado_por=generado_por, rol_generador=rol_generador,
            totales=list(reporte.totales), num_secciones=len(reporte.secciones),
        )
        self._repo.reportes_generados.append(registro)
        self._repo.guardar_reportes_generados()
        return registro

    def historial(self) -> List[RegistroReporte]:
        """Lista de reportes generados, más recientes primero."""
        return sorted(self._repo.reportes_generados, key=lambda r: r.fecha, reverse=True)

    def historial_de(self, rol: str) -> List[RegistroReporte]:
        return [r for r in self.historial() if r.rol_generador == rol]

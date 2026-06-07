"""services/academico.py
SRP - cada Service gestiona una sola área de negocio.
OCP - agregar lógica nueva = nueva clase Service, no modificar las existentes.
DIP - Services dependen del repositorio abstracto (IRepositorio), no de JSON directamente.
"""
from datetime import datetime
from typing import Optional, Tuple

from models.usuarios import Estudiante, Docente, Coordinador, Administrador
from models.domain import (Asignatura, Curso, Horario, Modalidad,
                            Matricula, Tarea, Calificacion, Notas)
from repositories.repositorio_academico import RepositorioAcademico


# ── AuthService ───────────────────────────────────────────────────────────────
class AuthService:
    """SRP - solo autenticación."""
    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def login(self, email: str, password: str):
        user = self._repo.usuarios.get(email.strip())
        if user and user.iniciarSesion(email.strip(), password):
            return user
        return None

    def email_disponible(self, email: str) -> bool:
        return email not in self._repo.usuarios

    def validar_email(self, email: str) -> bool:
        return "@" in email and "." in email and len(email) > 5


# ── UsuarioService ────────────────────────────────────────────────────────────
class UsuarioService:
    """SRP – solo CRUD de usuarios."""
    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def crear_estudiante(self, nombre, apellido, email, pwd, matricula, carrera) -> Tuple[bool, str]:
        if not AuthService(self._repo).email_disponible(email):
            return False, "El email ya está registrado"
        obj = Estudiante(nombre, apellido, email, pwd, matricula, carrera)
        self._repo.estudiantes.append(obj)
        self._repo.usuarios[obj.email] = obj
        self._repo.guardar_estudiantes()
        return True, "Estudiante creado"

    def crear_docente(self, nombre, apellido, email, pwd, especialidad) -> Tuple[bool, str]:
        if not AuthService(self._repo).email_disponible(email):
            return False, "El email ya está registrado"
        obj = Docente(nombre, apellido, email, pwd, especialidad)
        self._repo.docentes.append(obj)
        self._repo.usuarios[obj.email] = obj
        self._repo.guardar_docentes()
        return True, "Docente creado"

    def crear_coordinador(self, nombre, apellido, email, pwd) -> Tuple[bool, str]:
        if not AuthService(self._repo).email_disponible(email):
            return False, "El email ya está registrado"
        obj = Coordinador(nombre, apellido, email, pwd)
        self._repo.usuarios[obj.email] = obj
        self._repo.guardar_coordinadores()
        return True, "Coordinador creado"

    def crear_administrador(self, nombre, apellido, email, pwd) -> Tuple[bool, str]:
        if not AuthService(self._repo).email_disponible(email):
            return False, "El email ya está registrado"
        obj = Administrador(nombre, apellido, email, pwd)
        self._repo.usuarios[obj.email] = obj
        self._repo.guardar_administradores()
        return True, "Administrador creado"

    def eliminar_usuario(self, email: str, usuario_actual) -> Tuple[bool, str]:
        if email == usuario_actual.email:
            return False, "No puede eliminarse a sí mismo"
        if email not in self._repo.usuarios:
            return False, "Usuario no encontrado"
        del self._repo.usuarios[email]
        self._repo.estudiantes[:] = [e for e in self._repo.estudiantes if e.email != email]
        self._repo.docentes[:] = [d for d in self._repo.docentes if d.email != email]
        self._repo.guardar_estudiantes()
        self._repo.guardar_docentes()
        self._repo.guardar_administradores()
        self._repo.guardar_coordinadores()
        return True, f"Usuario {email} eliminado"

    def todos(self) -> list:
        return list(self._repo.usuarios.values())


# ── CursoService ──────────────────────────────────────────────────────────────
class CursoService:
    """SRP – solo CRUD de cursos."""
    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def crear(self, nombre: str, carrera: str, duracion: int,
              horas: int, modalidad_str: str, docente_email: str = "") -> Tuple[bool, str, Optional[Curso]]:
        if not nombre.strip():
            return False, "El nombre es obligatorio", None
        if duracion <= 0 or horas <= 0:
            return False, "Duración y horas deben ser positivas", None
        nid = self._repo.siguiente_id(self._repo.cursos)
        curso = Curso(nid, nombre.strip(), duracion, horas, carrera.strip())
        if modalidad_str:
            curso.asignar_modalidad(Modalidad(nid, modalidad_str, "", True))
        if docente_email and docente_email in self._repo.usuarios:
            curso.docente_email = docente_email
        self._repo.cursos.append(curso)
        self._repo.guardar_cursos()
        return True, "Curso creado", curso

    def asignar_docente(self, curso_id: int, docente_email: str) -> Tuple[bool, str]:
        curso = self._buscar(curso_id)
        if not curso: return False, "Curso no encontrado"
        if docente_email not in self._repo.usuarios:
            return False, "Docente no encontrado"
        curso.docente_email = docente_email
        self._repo.guardar_cursos()
        return True, "Docente asignado"

    def eliminar(self, curso_id: int) -> Tuple[bool, str]:
        if not self._buscar(curso_id):
            return False, "Curso no encontrado"
        self._repo.cursos[:] = [c for c in self._repo.cursos if c.id != curso_id]
        self._repo.guardar_cursos()
        return True, "Curso eliminado"

    def _buscar(self, curso_id: int) -> Optional[Curso]:
        return next((c for c in self._repo.cursos if c.id == curso_id), None)

    def por_carrera(self, carrera: str) -> list:
        return self._repo.cursos_por_carrera(carrera)

    def del_docente(self, email: str) -> list:
        return [c for c in self._repo.cursos if c.docente_email == email]


# ── HorarioService ────────────────────────────────────────────────────────────
class HorarioService:
    """SRP – solo CRUD de horarios independientes y update de cursos."""
    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def crear(self, curso_id: int, dia: str, inicio: str,
              fin: str, modalidad: str, aula: str) -> Tuple[bool, str]:
        curso = next((c for c in self._repo.cursos if c.id == curso_id), None)
        if not curso: return False, "Curso no encontrado"
        if not dia or not inicio or not fin:
            return False, "Día, hora inicio y fin son obligatorios"
        nid = self._repo.siguiente_id_dict(self._repo.horarios)
        h_obj = {"id": nid, "curso_id": curso_id, "curso": curso.nombre,
                  "dia": dia, "inicio": inicio, "fin": fin,
                  "modalidad": modalidad, "aula": aula}
        curso.asignar_horario(Horario(curso_id, dia, inicio, fin, aula))
        if modalidad:
            curso.asignar_modalidad(Modalidad(curso_id, modalidad, "", True))
        self._repo.horarios.append(h_obj)
        self._repo.guardar_horarios()
        self._repo.guardar_cursos()
        return True, f"Horario {dia} {inicio}–{fin} creado"

    def editar(self, horario_id: int, dia: str, inicio: str,
               fin: str, modalidad: str, aula: str) -> Tuple[bool, str]:
        h = next((x for x in self._repo.horarios if x.get("id") == horario_id), None)
        if not h: return False, "Horario no encontrado"
        h.update({"dia": dia, "inicio": inicio, "fin": fin,
                   "modalidad": modalidad, "aula": aula})
        curso = next((c for c in self._repo.cursos if c.id == h.get("curso_id")), None)
        if curso:
            curso.asignar_horario(Horario(h["curso_id"], dia, inicio, fin, aula))
            if modalidad:
                curso.asignar_modalidad(Modalidad(h["curso_id"], modalidad, "", True))
        self._repo.guardar_horarios()
        self._repo.guardar_cursos()
        return True, "Horario actualizado"

    def eliminar(self, horario_id: int) -> Tuple[bool, str]:
        if not any(x.get("id") == horario_id for x in self._repo.horarios):
            return False, "Horario no encontrado"
        self._repo.horarios[:] = [x for x in self._repo.horarios if x.get("id") != horario_id]
        self._repo.guardar_horarios()
        return True, "Horario eliminado"

    def todos(self) -> list:
        return self._repo.horarios


# ── AsignaturaService ─────────────────────────────────────────────────────────
class AsignaturaService:
    """SRP – solo CRUD de asignaturas."""
    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def crear(self, nombre: str, horas: int, creditos: int) -> Tuple[bool, str]:
        if not nombre.strip(): return False, "El nombre es obligatorio"
        if horas <= 0 or creditos <= 0: return False, "Horas y créditos deben ser positivos"
        nid = self._repo.siguiente_id(self._repo.asignaturas)
        self._repo.asignaturas.append(Asignatura(nid, nombre.strip(), horas, creditos, "Activa"))
        self._repo.guardar_asignaturas()
        return True, "Asignatura creada"

    def eliminar(self, asig_id: int) -> Tuple[bool, str]:
        en_uso = any(m.asignatura and m.asignatura.id == asig_id
                     for m in self._repo.matriculas if m.estado == "Activa")
        if en_uso: return False, "La asignatura tiene matrículas activas"
        self._repo.asignaturas[:] = [a for a in self._repo.asignaturas if a.id != asig_id]
        self._repo.guardar_asignaturas()
        return True, "Asignatura eliminada"

    def todas(self) -> list:
        return self._repo.asignaturas


# ── MatriculaService ──────────────────────────────────────────────────────────
class MatriculaService:
    """SRP – solo gestión de matrículas."""
    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def matricular(self, est_email: str, asig_id: int, tipo: str) -> Tuple[bool, str]:
        est = self._repo.usuarios.get(est_email)
        if not est or est.obtener_rol() != "estudiante":
            return False, "Estudiante no encontrado"
        asig = next((a for a in self._repo.asignaturas if a.id == asig_id), None)
        if not asig: return False, "Asignatura no encontrada"
        ya = any(m.estudiante and m.estudiante.email == est_email
                 and m.asignatura and m.asignatura.id == asig_id
                 and m.estado == "Activa" for m in self._repo.matriculas)
        if ya: return False, f"{est.nombre} ya está matriculado en {asig.nombre}"
        nid = self._repo.siguiente_id(self._repo.matriculas)
        m = Matricula(nid, datetime.now().strftime("%Y-%m-%d"),
                      tipo, "Activa", tipo == "Segunda", est, asig)
        self._repo.matriculas.append(m)
        self._repo.guardar_matriculas()
        return True, f"Matrícula registrada: {est.nombre} → {asig.nombre}"

    def cambiar_estado(self, mat_id: int, nuevo_estado: str) -> Tuple[bool, str]:
        m = next((x for x in self._repo.matriculas if x.id == mat_id), None)
        if not m: return False, "Matrícula no encontrada"
        m.estado = nuevo_estado
        self._repo.guardar_matriculas()
        return True, f"Estado actualizado a {nuevo_estado}"

    def todas(self) -> list:
        return self._repo.matriculas


# ── TareaService ──────────────────────────────────────────────────────────────
class TareaService:
    """SRP – solo gestión de tareas y entregas."""
    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def crear(self, titulo: str, descripcion: str, fecha_limite: str,
              creador_email: str, asignatura_id: Optional[int] = None) -> Tuple[bool, str]:
        if not titulo.strip(): return False, "El título es obligatorio"
        if fecha_limite:
            try: datetime.strptime(fecha_limite, "%Y-%m-%d")
            except ValueError: return False, "Formato de fecha inválido (YYYY-MM-DD)"
        nid = self._repo.siguiente_id(self._repo.tareas)
        self._repo.tareas.append(
            Tarea(nid, titulo.strip(), descripcion, fecha_limite, creador_email, asignatura_id))
        self._repo.guardar_tareas()
        return True, "Tarea creada"

    def entregar(self, tarea_id: int, estudiante_email: str,
                 descripcion: str, archivo: str) -> Tuple[bool, str]:
        tarea = next((t for t in self._repo.tareas if t.id == tarea_id), None)
        if not tarea: return False, "Tarea no encontrada"
        # Verificar que el estudiante puede ver esta tarea
        if tarea not in self.visibles(estudiante_email):
            return False, "No tienes acceso a esta tarea"
        if tarea.entregada_por(estudiante_email):
            return False, "Ya entregaste esta tarea"
        tarea.agregar_entrega(estudiante_email, descripcion, archivo,
                              datetime.now().strftime("%Y-%m-%d %H:%M"))
        self._repo.guardar_tareas()
        return True, "Tarea entregada exitosamente"

    def visibles(self, email: str) -> list:
        return self._repo.tareas_visibles(email)

    def del_docente(self, email: str) -> list:
        return self._repo.tareas_docente(email)

    def eliminar(self, tarea_id: int, docente_email: str) -> Tuple[bool, str]:
        tarea = next((t for t in self._repo.tareas if t.id == tarea_id), None)
        if not tarea: return False, "Tarea no encontrada"
        if tarea.creador_email != docente_email:
            return False, "Solo el creador puede eliminar esta tarea"
        self._repo.tareas[:] = [t for t in self._repo.tareas if t.id != tarea_id]
        self._repo.guardar_tareas()
        return True, "Tarea eliminada"


# ── CalificacionService ───────────────────────────────────────────────────────
class CalificacionService:
    """SRP – solo gestión de calificaciones."""
    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def registrar(self, est_email: str, asignatura: str,
                  nota: float, observacion: str = "") -> Tuple[bool, str]:
        est = self._repo.usuarios.get(est_email)
        if not est: return False, "Estudiante no encontrado"
        if not 0 <= nota <= 10: return False, "La nota debe estar entre 0 y 10"
        # Actualizar si ya existe
        existente = next((c for c in self._repo.calificaciones
                          if c.estudiante.email == est_email
                          and c.asignatura == asignatura), None)
        if existente:
            existente.modificar_nota(nota)
            existente.observacion = observacion
        else:
            self._repo.calificaciones.append(
                Calificacion(est, asignatura, nota, observacion))
        self._repo.guardar_calificaciones()
        return True, f"Nota {nota} registrada para {est.nombre}"

    def del_estudiante(self, email: str) -> list:
        return self._repo.calificaciones_estudiante(email)

    def promedio_estudiante(self, email: str) -> float:
        califs = self.del_estudiante(email)
        return round(sum(c.nota for c in califs) / len(califs), 2) if califs else 0.0

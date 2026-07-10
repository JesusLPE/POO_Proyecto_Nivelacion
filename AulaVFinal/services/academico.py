"""services/academico.py
SRP - cada Service gestiona una sola área de negocio.
OCP - agregar lógica nueva = nueva clase Service, no modificar las existentes.
DIP - Services dependen del repositorio abstracto (IRepositorio), no de JSON directamente.

POO: todas las clases de este archivo siguen el mismo patrón:
Constructor -> recibe "repo" por Inyección de dependencias (no lo crean ellas).
"""
from datetime import datetime
from typing import Optional, Tuple

from factories.usuario_factory import UsuarioFactory
from models import (Asignatura, Curso, Horario, Modalidad,
                    Matricula, Tarea, Calificacion, Notas, SolicitudRetiro, Cronograma)
from repositories.repositorio_academico import RepositorioAcademico


def validar_cedula_ecuatoriana(cedula: str) -> bool:
    """Valida cédula ecuatoriana de persona natural (10 dígitos)."""
    cedula = (cedula or "").strip()
    if not cedula.isdigit() or len(cedula) != 10:
        return False

    provincia = int(cedula[:2])
    tercer_digito = int(cedula[2])
    if provincia < 1 or provincia > 24 or tercer_digito >= 6:
        return False

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0
    for digito, coef in zip(cedula[:9], coeficientes):
        valor = int(digito) * coef
        if valor >= 10:
            valor -= 9
        suma += valor

    verificador = (10 - (suma % 10)) % 10
    return verificador == int(cedula[9])


# ── AuthService ───────────────────────────────────────────────────────────────
# POO: Clase
class AuthService:
    """SRP - solo autenticación."""
    # POO: Constructor | POO: Encapsulamiento -> _repo es un atributo protegido
    # POO: Inyección de dependencias -> "repo" se pasa desde afuera
    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    # POO: Método
    def login(self, email: str, password: str):
        # Intento rápido por clave exacta (optimización)
        key = email.strip()
        user = self._repo.usuarios.get(key)
        if user and user.iniciarSesion(key, password):
            return user

        # Si no hay coincidencia exacta, buscar de forma tolerante a mayúsculas
        # y diacríticos para evitar problemas con "ñ" u otras variaciones.
        try:
            import unicodedata
        except Exception:
            unicodedata = None

        def _norm(s: str) -> str:
            if s is None:
                return ""
            s2 = s.strip()
            if unicodedata:
                s2 = unicodedata.normalize("NFKD", s2)
                # eliminar marcas diacríticas
                s2 = "".join(ch for ch in s2 if not unicodedata.combining(ch))
            return s2.casefold()

        target = _norm(email)
        for u in self._repo.usuarios.values():
            if _norm(u.email) == target:
                # llamar con el email real del usuario para que Persona.iniciarSesion
                # compare contra su valor interno; así solo la contraseña importa.
                if u.iniciarSesion(u.email, password):
                    return u
                return None
        return None

    def email_disponible(self, email: str) -> bool:
        return email not in self._repo.usuarios

    def validar_email(self, email: str) -> bool:
        return "@" in email and "." in email and len(email) > 5


# ── UsuarioService ────────────────────────────────────────────────────────────
# POO: Clase
class UsuarioService:
    """SRP – solo CRUD de usuarios."""
    # POO: Constructor | POO: Inyección de dependencias
    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    # POO: Método | Patrón: Factory Method -> usa UsuarioFactory en vez de
    # instanciar Estudiante() directamente
    def crear_estudiante(self, nombre, apellido, email, pwd, cedula, matricula, carrera,
                         curso_id=None, horario_id=None) -> Tuple[bool, str]:
        if not AuthService(self._repo).email_disponible(email):
            return False, "El email ya está registrado"
        cedula = (cedula or "").strip()
        if not validar_cedula_ecuatoriana(cedula):
            return False, "Ingrese una cédula ecuatoriana válida"
        if any(getattr(e, "cedula", "") == cedula for e in self._repo.estudiantes):
            return False, "Ya existe un estudiante con esa cédula"
        if curso_id is None or horario_id is None:
            return False, "Debe seleccionar curso y horario para el estudiante"

        obj = UsuarioFactory.crear_usuario("estudiante", nombre, apellido, email, pwd,
                                           cedula=cedula, matricula=matricula, carrera=carrera,
                                           curso_id=curso_id, horario_id=horario_id)
        self._repo.estudiantes.append(obj)
        self._repo.usuarios[obj.email] = obj
        self._repo.guardar_estudiantes()

        # ── Auto-matrícula: heredar las asignaturas activas del mismo grupo ──
        # Busca qué asignaturas tienen los demás estudiantes activos del mismo
        # curso_id, y crea las mismas matrículas para el nuevo estudiante.
        # Esto garantiza que sus tareas sean visibles de inmediato.
        ids_asig_del_grupo: set = set()
        for m in self._repo.matriculas:
            comparte_curso = (
                m.estudiante
                and m.estudiante.email != email
                and getattr(m.estudiante, "curso_id", None) == curso_id
                and m.estado == "Activa"
                and m.asignatura
            )
            if comparte_curso:
                ids_asig_del_grupo.add(m.asignatura.id)

        if ids_asig_del_grupo:
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            for asig_id in sorted(ids_asig_del_grupo):
                asig = next((a for a in self._repo.asignaturas if a.id == asig_id), None)
                if asig:
                    nid = self._repo.siguiente_id(self._repo.matriculas)
                    nueva = Matricula(nid, fecha_hoy, "Regular", "Activa", False, obj, asig)
                    self._repo.matriculas.append(nueva)
            self._repo.guardar_matriculas()
            return True, (f"Estudiante creado y matriculado en "
                          f"{len(ids_asig_del_grupo)} asignatura(s) del grupo")

        return True, "Estudiante creado (sin asignaturas previas en el grupo para heredar)"

    def editar_estudiante(self, email, nombre=None, apellido=None, cedula=None, carrera=None,
                          curso_id=None, horario_id=None) -> Tuple[bool, str]:
        est = self._repo.usuarios.get(email)
        if not est or est.obtener_rol() != "estudiante":
            return False, "Estudiante no encontrado"
        if nombre is not None:   est.nombre = nombre
        if apellido is not None: est.apellido = apellido
        if cedula is not None:
            cedula = cedula.strip()
            if not validar_cedula_ecuatoriana(cedula):
                return False, "Ingrese una cédula ecuatoriana válida"
            if any(getattr(e, "cedula", "") == cedula and e.email != email for e in self._repo.estudiantes):
                return False, "Ya existe otro estudiante con esa cédula"
            est.cedula = cedula
        if carrera is not None:  est.carrera = carrera
        if curso_id is not None:   est.curso_id = curso_id
        if horario_id is not None: est.horario_id = horario_id
        self._repo.guardar_estudiantes()
        return True, "Estudiante actualizado"

    def dar_de_baja(self, email: str) -> Tuple[bool, str]:
        """Marca al estudiante como retirado: limpia curso/horario y anula sus matrículas."""
        est = self._repo.usuarios.get(email)
        if not est or est.obtener_rol() != "estudiante":
            return False, "Estudiante no encontrado"
        est.curso_id = None
        est.horario_id = None
        for m in self._repo.matriculas:
            if m.estudiante and m.estudiante.email == email and m.estado == "Activa":
                m.anular()
        self._repo.guardar_estudiantes()
        self._repo.guardar_matriculas()
        return True, f"{est.nombre} fue dado de baja: curso, horario y matrículas activas anuladas"

    def crear_docente(self, nombre, apellido, email, pwd, especialidad) -> Tuple[bool, str]:
        if not AuthService(self._repo).email_disponible(email):
            return False, "El email ya está registrado"
        obj = UsuarioFactory.crear_usuario("docente", nombre, apellido, email, pwd, especialidad=especialidad)
        self._repo.docentes.append(obj)
        self._repo.usuarios[obj.email] = obj
        self._repo.guardar_docentes()
        return True, "Docente creado"

    def crear_coordinador(self, nombre, apellido, email, pwd) -> Tuple[bool, str]:
        if not AuthService(self._repo).email_disponible(email):
            return False, "El email ya está registrado"
        obj = UsuarioFactory.crear_usuario("coordinador", nombre, apellido, email, pwd)
        self._repo.usuarios[obj.email] = obj
        self._repo.guardar_coordinadores()
        return True, "Coordinador creado"

    def crear_administrador(self, nombre, apellido, email, pwd) -> Tuple[bool, str]:
        if not AuthService(self._repo).email_disponible(email):
            return False, "El email ya está registrado"
        obj = UsuarioFactory.crear_usuario("administrador", nombre, apellido, email, pwd)
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
# POO: Clase
class CursoService:
    """SRP – solo CRUD de cursos."""
    # POO: Constructor | POO: Inyección de dependencias
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
        self._repo.horarios[:] = [h for h in self._repo.horarios if h.get("curso_id") != curso_id]
        self._repo.guardar_cursos()
        self._repo.guardar_horarios()
        return True, "Curso y sus horarios fueron eliminados"

    def _buscar(self, curso_id: int) -> Optional[Curso]:
        return next((c for c in self._repo.cursos if c.id == curso_id), None)

    def por_carrera(self, carrera: str) -> list:
        return self._repo.cursos_por_carrera(carrera)

    def del_docente(self, email: str) -> list:
        return [c for c in self._repo.cursos if c.docente_email == email]


# ── HorarioService ────────────────────────────────────────────────────────────
# POO: Clase
class HorarioService:
    """SRP – solo CRUD de horarios independientes y update de cursos."""
    # POO: Constructor | POO: Inyección de dependencias
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
# POO: Clase
class AsignaturaService:
    """SRP – solo CRUD de asignaturas."""
    # POO: Constructor | POO: Inyección de dependencias
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
# POO: Clase
class MatriculaService:
    """SRP – solo gestión de matrículas."""
    # POO: Constructor | POO: Inyección de dependencias
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
# POO: Clase
class TareaService:
    """SRP – solo gestión de tareas y entregas."""
    # POO: Constructor | POO: Inyección de dependencias
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
# POO: Clase
class CalificacionService:
    """SRP – solo gestión de calificaciones."""
    # POO: Constructor | POO: Inyección de dependencias
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


# ── FacultadService ──────────────────────────────────────────────────────────
# POO: Clase
class FacultadService:
    """SRP – solo consulta el catálogo de facultades y carreras."""
    # POO: Constructor | POO: Inyección de dependencias
    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def todas(self) -> list:
        return self._repo.facultades

    def carreras(self) -> list:
        return self._repo.carreras_catalogo()

    def facultad_de_carrera(self, carrera: str) -> str:
        return self._repo.facultad_de_carrera(carrera)


# ── RetiroService ─────────────────────────────────────────────────────────────
# POO: Clase
class RetiroService:
    """SRP – solo gestiona solicitudes de retiro de materia."""
    # POO: Constructor | POO: Inyección de dependencias
    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def solicitar(self, estudiante_email: str, materia_id: int, motivo: str) -> Tuple[bool, str]:
        est = self._repo.usuarios.get(estudiante_email)
        if not est or est.obtener_rol() != "estudiante":
            return False, "Estudiante no encontrado"
        asig = next((a for a in self._repo.asignaturas if a.id == materia_id), None)
        if not asig: return False, "Asignatura no encontrada"
        if not motivo.strip(): return False, "Debe indicar un motivo"

        matriculado = any(m.estudiante and m.estudiante.email == estudiante_email
                          and m.asignatura and m.asignatura.id == materia_id
                          and m.estado == "Activa" for m in self._repo.matriculas)
        if not matriculado:
            return False, f"No está matriculado activamente en {asig.nombre}"

        ya_pendiente = any(s.estudiante_id == estudiante_email and s.materia_id == materia_id
                           and s.esta_pendiente() for s in self._repo.solicitudes_retiro)
        if ya_pendiente:
            return False, f"Ya existe una solicitud pendiente para {asig.nombre}"

        nid = self._repo.siguiente_id(self._repo.solicitudes_retiro)
        solicitud = SolicitudRetiro(
            id=nid, estudiante_id=estudiante_email, materia_id=materia_id,
            motivo=motivo.strip(), estado="Pendiente",
            fecha=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self._repo.solicitudes_retiro.append(solicitud)
        self._repo.guardar_solicitudes_retiro()
        return True, f"Solicitud de retiro de {asig.nombre} enviada al coordinador"

    def resolver(self, solicitud_id: int, aprobar: bool, respuesta: str = "") -> Tuple[bool, str]:
        solicitud = next((s for s in self._repo.solicitudes_retiro if s.id == solicitud_id), None)
        if not solicitud: return False, "Solicitud no encontrada"
        if not solicitud.esta_pendiente():
            return False, "Esta solicitud ya fue resuelta"

        if aprobar:
            solicitud.aprobar(respuesta)
            # Anular la matrícula correspondiente
            for m in self._repo.matriculas:
                if (m.estudiante and m.estudiante.email == solicitud.estudiante_id
                        and m.asignatura and m.asignatura.id == solicitud.materia_id
                        and m.estado == "Activa"):
                    m.anular()
            self._repo.guardar_matriculas()
            mensaje = "Solicitud aprobada. La matrícula fue anulada."
        else:
            solicitud.rechazar(respuesta)
            mensaje = "Solicitud rechazada."

        self._repo.guardar_solicitudes_retiro()
        return True, mensaje

    def del_estudiante(self, estudiante_email: str) -> list:
        return self._repo.solicitudes_retiro_de(estudiante_email)

    def pendientes(self) -> list:
        return self._repo.solicitudes_retiro_pendientes()

    def todas(self) -> list:
        return self._repo.solicitudes_retiro


# ── CronogramaService ─────────────────────────────────────────────────────────
# POO: Clase
class CronogramaService:
    """SRP – solo gestiona el cronograma (fechas y carga horaria) de un curso."""
    # POO: Constructor | POO: Inyección de dependencias
    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def crear(self, curso_id: int, fecha_inicio: str, fecha_fin: str,
              total_horas: int, descripcion: str = "") -> Tuple[bool, str]:
        curso = next((c for c in self._repo.cursos if c.id == curso_id), None)
        if not curso: return False, "Curso no encontrado"
        if not fecha_inicio or not fecha_fin:
            return False, "Debe indicar fecha de inicio y fin"
        if total_horas <= 0:
            return False, "El total de horas debe ser positivo"
        nid = self._repo.siguiente_id(self._repo.cronogramas)
        crono = Cronograma(nid, curso_id, fecha_inicio, fecha_fin, total_horas, descripcion)
        self._repo.cronogramas.append(crono)
        self._repo.guardar_cronogramas()
        return True, f"Cronograma creado para {curso.nombre}"

    def editar(self, cronograma_id: int, fecha_inicio=None, fecha_fin=None,
              total_horas=None, descripcion=None) -> Tuple[bool, str]:
        crono = next((c for c in self._repo.cronogramas if c.id == cronograma_id), None)
        if not crono: return False, "Cronograma no encontrado"
        if fecha_inicio is not None: crono.fecha_inicio = fecha_inicio
        if fecha_fin is not None:    crono.fecha_fin = fecha_fin
        if total_horas is not None:  crono.total_horas = total_horas
        if descripcion is not None:  crono.descripcion = descripcion
        self._repo.guardar_cronogramas()
        return True, "Cronograma actualizado"

    def eliminar(self, cronograma_id: int) -> Tuple[bool, str]:
        if not any(c.id == cronograma_id for c in self._repo.cronogramas):
            return False, "Cronograma no encontrado"
        self._repo.cronogramas[:] = [c for c in self._repo.cronogramas if c.id != cronograma_id]
        self._repo.guardar_cronogramas()
        return True, "Cronograma eliminado"

    def de_curso(self, curso_id: int) -> list:
        return [c for c in self._repo.cronogramas if c.curso_id == curso_id]

    def todos(self) -> list:
        return self._repo.cronogramas

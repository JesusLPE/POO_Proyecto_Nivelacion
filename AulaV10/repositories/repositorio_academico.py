from models.interfaces import IRepositorio
from factories.usuario_factory import UsuarioFactory
from models import (Asignatura, Curso, Horario, Modalidad,
                    Matricula, Tarea, Calificacion)


class RepositorioAcademico:
    """SRP – solo carga y persiste datos.
       DIP – depende de IRepositorio, no de JsonManager directamente."""

    # Rutas de datos centralizadas
    RUTAS = {
        "estudiantes":     "data/estudiantes.json",
        "docentes":        "data/docentes.json",
        "administradores": "data/administradores.json",
        "coordinadores":   "data/coordinadores.json",
        "cursos":          "data/cursos.json",
        "asignaturas":     "data/asignaturas.json",
        "matriculas":      "data/matriculas.json",
        "tareas":          "data/tareas.json",
        "calificaciones":  "data/calificaciones.json",
        "horarios":        "data/horarios.json",
        "facultades":      "data/facultades.json",
    }

    def __init__(self, storage: IRepositorio):
        self._storage = storage
        self.usuarios: dict = {}
        self.estudiantes: list = []
        self.docentes: list = []
        self.asignaturas: list = []
        self.cursos: list = []
        self.matriculas: list = []
        self.tareas: list = []
        self.calificaciones: list = []
        self.horarios: list = []
        self.facultades: list = []
        self._cargar_todo()

    def _r(self, clave: str) -> list:
        return self._storage.cargar(self.RUTAS[clave])

    def _w(self, clave: str, datos: list) -> None:
        self._storage.guardar(self.RUTAS[clave], datos)

    def _cargar_todo(self):
        self._cargar_usuarios()
        self._cargar_cursos()
        self._cargar_asignaturas()
        self._cargar_matriculas()
        self._cargar_tareas()
        self._cargar_calificaciones()
        self.horarios = self._r("horarios")
        self.facultades = self._r("facultades")

    # ── Carga ─────────────────────────────────────────────────────────────────
    def _cargar_usuarios(self):
        for e in self._r("estudiantes"):
            obj = UsuarioFactory.crear_usuario(
                "estudiante", e["nombre"], e["apellido"], e["email"], e["password"],
                matricula=e.get("matricula", ""), carrera=e.get("carrera", "")
            )
            self.estudiantes.append(obj)
            self.usuarios[obj.email] = obj

        for d in self._r("docentes"):
            obj = UsuarioFactory.crear_usuario(
                "docente", d["nombre"], d["apellido"], d["email"], d["password"],
                especialidad=d.get("especialidad", "")
            )
            self.docentes.append(obj)
            self.usuarios[obj.email] = obj

        for a in self._r("administradores"):
            obj = UsuarioFactory.crear_usuario(
                "administrador", a["nombre"], a["apellido"], a["email"], a["password"]
            )
            self.usuarios[obj.email] = obj

        for c in self._r("coordinadores"):
            obj = UsuarioFactory.crear_usuario(
                "coordinador", c["nombre"], c["apellido"], c["email"], c["password"]
            )
            self.usuarios[obj.email] = obj

    def _cargar_cursos(self):
        for c in self._r("cursos"):
            curso = Curso(c["id"], c["nombre"], c["duracion"],
                          c["horas"], c.get("carrera", ""))
            curso.docente_email = c.get("docente_email") or None
            h = c.get("horario", "")
            if h:
                partes = h.split()
                dia = partes[0]
                rango = partes[1] if len(partes) > 1 else ""
                ini, fin = (rango.split("-") + [""])[:2]
                curso.asignar_horario(Horario(c["id"], dia, ini, fin, c.get("aula", "")))
            m = c.get("modalidad", "")
            if m:
                curso.asignar_modalidad(Modalidad(c["id"], m, "", True, c.get("plataforma", "")))
            self.cursos.append(curso)

    def _cargar_asignaturas(self):
        for a in self._r("asignaturas"):
            self.asignaturas.append(
                Asignatura(a["id"], a["nombre"], a["horas"], a["creditos"], a["estado"]))

    def _cargar_matriculas(self):
        for m in self._r("matriculas"):
            est = self.usuarios.get(m.get("estudiante_email", ""))
            asig = next((a for a in self.asignaturas if a.id == m.get("asignatura_id")), None)
            self.matriculas.append(
                Matricula(m["id"], m["fecha"], m["tipo"], m["estado"],
                          m.get("segunda", False), est, asig))

    def _cargar_tareas(self):
        for t in self._r("tareas"):
            self.tareas.append(
                Tarea(t["id"], t["titulo"], t.get("descripcion", ""),
                      t.get("fecha_limite", ""), t.get("creador_email", ""),
                      t.get("asignatura_id"), t.get("entregas", [])))

    def _cargar_calificaciones(self):
        for c in self._r("calificaciones"):
            est = self.usuarios.get(c.get("estudiante_email", ""))
            if est:
                self.calificaciones.append(
                    Calificacion(est, c["asignatura"], c["nota"], c.get("observacion", "")))

    # ── Guardar ───────────────────────────────────────────────────────────────
    def guardar_estudiantes(self):
        self._w("estudiantes", [
            {"nombre": e.nombre, "apellido": e.apellido, "email": e.email,
             "password": e.get_password(), "matricula": e.matricula, "carrera": e.carrera}
            for e in self.estudiantes])

    def guardar_docentes(self):
        self._w("docentes", [
            {"nombre": d.nombre, "apellido": d.apellido, "email": d.email,
             "password": d.get_password(), "especialidad": d.especialidad}
            for d in self.docentes])

    def guardar_administradores(self):
        self._w("administradores", [
            {"nombre": u.nombre, "apellido": u.apellido,
             "email": u.email, "password": u.get_password()}
            for u in self.usuarios.values() if u.obtener_rol() == "administrador"])

    def guardar_coordinadores(self):
        self._w("coordinadores", [
            {"nombre": u.nombre, "apellido": u.apellido,
             "email": u.email, "password": u.get_password()}
            for u in self.usuarios.values() if u.obtener_rol() == "coordinador"])

    def guardar_cursos(self):
        datos = []
        for c in self.cursos:
            h = c.horario
            m = c.modalidad
            datos.append({
                "id": c.id, "nombre": c.nombre,
                "duracion": c._duracion_semanas, "horas": c._total_horas,
                "carrera": c.carrera or "",
                "docente_email": c.docente_email or "",
                "horario": f"{h.dia} {h.hora_inicio}-{h.hora_fin}" if h else "",
                "aula": h.aula if h else "",
                "modalidad": m.nombre if m else "",
                "plataforma": m.plataforma if m else "",
            })
        self._w("cursos", datos)

    def guardar_asignaturas(self):
        self._w("asignaturas", [
            {"id": a.id, "nombre": a.nombre, "horas": a.horas,
             "creditos": a.creditos, "estado": a.estado}
            for a in self.asignaturas])

    def guardar_matriculas(self):
        self._w("matriculas", [
            {"id": m.id, "fecha": m.fecha, "tipo": m.tipo, "estado": m.estado,
             "segunda": m.esSegundaMatricula,
             "estudiante_email": m.estudiante.email if m.estudiante else "",
             "asignatura_id": m.asignatura.id if m.asignatura else None}
            for m in self.matriculas])

    def guardar_tareas(self):
        self._w("tareas", [
            {"id": t.id, "titulo": t.titulo, "descripcion": t.descripcion,
             "fecha_limite": t.fecha_limite, "creador_email": t.creador_email,
             "asignatura_id": t.asignatura_id, "entregas": t.entregas}
            for t in self.tareas])

    def guardar_calificaciones(self):
        self._w("calificaciones", [
            {"estudiante_email": c.estudiante.email, "asignatura": c.asignatura,
             "nota": c.nota, "observacion": c.observacion}
            for c in self.calificaciones])

    def guardar_horarios(self):
        self._w("horarios", self.horarios)

    # ── Queries ───────────────────────────────────────────────────────────────
    def cursos_por_carrera(self, carrera: str) -> list:
        return [c for c in self.cursos if not c.carrera or c.carrera == carrera]

    def matriculas_activas_estudiante(self, email: str) -> list:
        return [m for m in self.matriculas
                if m.estudiante and m.estudiante.email == email
                and m.estado == "Activa" and m.asignatura]

    def ids_asignaturas_matriculadas(self, email: str) -> set:
        return {m.asignatura.id for m in self.matriculas_activas_estudiante(email)}

    def tareas_visibles(self, email: str) -> list:
        ids = self.ids_asignaturas_matriculadas(email)
        return [t for t in self.tareas
                if t.asignatura_id is None or t.asignatura_id in ids]

    def calificaciones_estudiante(self, email: str) -> list:
        return [c for c in self.calificaciones if c.estudiante.email == email]

    def tareas_docente(self, email: str) -> list:
        return [t for t in self.tareas if t.creador_email == email]

    def siguiente_id(self, coleccion: list) -> int:
        return max((getattr(x, "id", 0) or 0 for x in coleccion), default=0) + 1

    def siguiente_id_dict(self, coleccion: list, clave: str = "id") -> int:
        return max((x.get(clave, 0) for x in coleccion), default=0) + 1


    # ── Catálogo de facultades/carreras ───────────────────────────────────────
    def carreras_catalogo(self) -> list:
        """Devuelve todas las carreras del catálogo de facultades."""
        carreras = []
        for f in self.facultades:
            carreras.extend(f.get("carreras", []))
        return sorted(set(carreras))

    def facultad_de_carrera(self, carrera: str) -> str:
        """Busca a qué facultad pertenece una carrera."""
        for f in self.facultades:
            if carrera in f.get("carreras", []):
                return f.get("facultad", "")
        return ""

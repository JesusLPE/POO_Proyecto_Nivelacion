from repositories.json_manager import JsonManager
from models.estudiante import Estudiante
from models.docente import Docente
from models.administrador import Administrador
from models.coordinador import Coordinador
from models.curso import Curso, Horario, Modalidad
from models.asignatura import Asignatura
from models.matricula import Matricula
from models.tarea import Tarea
from models.calificacion import Calificacion


class RepositorioAcademico:

    def __init__(self):
        self.usuarios = {}
        self.estudiantes = []
        self.docentes = []
        self.cursos = []
        self.asignaturas = []
        self.matriculas = []
        self.tareas = []
        self.calificaciones = []
        self.horarios = []  # horarios independientes del coordinador
        self.cargar()

    def cargar(self):
        for e in JsonManager.cargar("data/estudiantes.json"):
            obj = Estudiante(e["nombre"], e["apellido"], e["email"], e["password"], e["matricula"], e["carrera"])
            self.estudiantes.append(obj)
            self.usuarios[obj.email] = obj

        for d in JsonManager.cargar("data/docentes.json"):
            obj = Docente(d["nombre"], d["apellido"], d["email"], d["password"], d["especialidad"])
            self.docentes.append(obj)
            self.usuarios[obj.email] = obj

        for a in JsonManager.cargar("data/administradores.json"):
            obj = Administrador(a["nombre"], a["apellido"], a["email"], a["password"])
            self.usuarios[obj.email] = obj

        for c in JsonManager.cargar("data/coordinadores.json"):
            obj = Coordinador(c["nombre"], c["apellido"], c["email"], c["password"])
            self.usuarios[obj.email] = obj

        for c in JsonManager.cargar("data/cursos.json"):
            curso = Curso(c["id"], c["nombre"], c["duracion"], c["horas"], c.get("carrera", ""))
            curso.docente_email = c.get("docente_email") or None
            h = c.get("horario", "")
            if h:
                p = h.split()
                dia = p[0] if p else ""
                rango = p[1] if len(p) > 1 else ""
                ini, fin = (rango.split("-") + [""])[:2]
                curso.asignar_horario(Horario(c["id"], dia, ini, fin))
            m = c.get("modalidad", "")
            if m:
                curso.asignar_modalidad(Modalidad(c["id"], m, "", True))
            self.cursos.append(curso)

        for a in JsonManager.cargar("data/asignaturas.json"):
            obj = Asignatura(a["id"], a["nombre"], a["horas"], a["creditos"], a["estado"])
            self.asignaturas.append(obj)

        for m in JsonManager.cargar("data/matriculas.json"):
            estudiante = self.usuarios.get(m.get("estudiante_email"))
            asignatura = next((a for a in self.asignaturas if a.id == m.get("asignatura_id")), None)
            obj = Matricula(m["id"], m["fecha"], m["tipo"], m["estado"],
                            m.get("segunda", False), estudiante, asignatura)
            self.matriculas.append(obj)

        for t in JsonManager.cargar("data/tareas.json"):
            obj = Tarea(t.get("titulo", ""), t.get("descripcion", ""), t.get("fecha_limite", ""),
                        t.get("creador_email", ""), t.get("id"), t.get("entregas", []),
                        t.get("asignatura_id"))
            self.tareas.append(obj)

        for c in JsonManager.cargar("data/calificaciones.json"):
            est = self.usuarios.get(c.get("estudiante_email"))
            if est:
                obj = Calificacion(est, c.get("asignatura", ""), c.get("nota", 0), c.get("observacion", ""))
                self.calificaciones.append(obj)

        for h in JsonManager.cargar("data/horarios.json"):
            self.horarios.append(h)

    # ── Guardar ──────────────────────────────────────────────────────────────
    def guardar_estudiantes(self):
        JsonManager.guardar("data/estudiantes.json", [
            {"nombre": e.nombre, "apellido": e.apellido, "email": e.email,
             "password": e.get_password(), "matricula": e.matricula, "carrera": e.carrera}
            for e in self.estudiantes
        ])

    def guardar_docentes(self):
        JsonManager.guardar("data/docentes.json", [
            {"nombre": d.nombre, "apellido": d.apellido, "email": d.email,
             "password": d.get_password(), "especialidad": d.especialidad}
            for d in self.docentes
        ])

    def guardar_administradores(self):
        JsonManager.guardar("data/administradores.json", [
            {"nombre": a.nombre, "apellido": a.apellido, "email": a.email, "password": a.get_password()}
            for a in self.usuarios.values() if a.obtener_rol() == "administrador"
        ])

    def guardar_coordinadores(self):
        JsonManager.guardar("data/coordinadores.json", [
            {"nombre": c.nombre, "apellido": c.apellido, "email": c.email, "password": c.get_password()}
            for c in self.usuarios.values() if c.obtener_rol() == "coordinador"
        ])

    def guardar_cursos(self):
        datos = []
        for c in self.cursos:
            h = c.horario
            m = c.modalidad
            datos.append({
                "id": c.id, "nombre": c.nombre,
                "duracion": c._duracion_semanas, "horas": c._total_horas,
                "docente_email": c.docente_email or "",
                "horario": f"{h.dia} {h.hora_inicio}-{h.hora_fin}" if h else "",
                "modalidad": m.nombre if m else "",
                "carrera": c.carrera or ""
            })
        JsonManager.guardar("data/cursos.json", datos)

    def guardar_asignaturas(self):
        JsonManager.guardar("data/asignaturas.json", [
            {"id": a.id, "nombre": a.nombre, "horas": a.horas, "creditos": a.creditos, "estado": a.estado}
            for a in self.asignaturas
        ])

    def guardar_matriculas(self):
        JsonManager.guardar("data/matriculas.json", [
            {"id": m.id, "fecha": m.fecha, "tipo": m.tipo, "estado": m.estado,
             "segunda": m.esSegundaMatricula,
             "estudiante_email": m.estudiante.email if m.estudiante else "",
             "asignatura_id": m.asignatura.id if m.asignatura else None}
            for m in self.matriculas
        ])

    def guardar_tareas(self):
        JsonManager.guardar("data/tareas.json", [
            {"id": t.id, "titulo": t.titulo, "descripcion": t.descripcion,
             "fecha_limite": t.fecha_limite, "creador_email": t.creador_email,
             "entregas": t.entregas, "asignatura_id": t.asignatura_id}
            for t in self.tareas
        ])

    def guardar_calificaciones(self):
        JsonManager.guardar("data/calificaciones.json", [
            {"estudiante_email": c.estudiante.email, "asignatura": c.asignatura,
             "nota": c.nota, "observacion": c.observacion}
            for c in self.calificaciones
        ])

    def guardar_horarios(self):
        JsonManager.guardar("data/horarios.json", self.horarios)

    # ── Queries ───────────────────────────────────────────────────────────────
    def obtener_materias_estudiante(self, email):
        # Solo asignaturas donde está matriculado activo
        return [m.asignatura for m in self.matriculas
                if m.estudiante and m.estudiante.email == email
                and m.asignatura and m.estado == "Activa"]

    def obtener_cursos_por_carrera(self, carrera):
        return [c for c in self.cursos if c.carrera == carrera or c.carrera == ""]

    def obtener_tareas_por_asignatura(self, asignatura_id):
        return [t for t in self.tareas if t.asignatura_id == asignatura_id]

    def obtener_calificaciones_estudiante(self, email):
        return [c for c in self.calificaciones if c.estudiante.email == email]

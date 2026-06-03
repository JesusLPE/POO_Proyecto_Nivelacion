from repositories.json_manager import JsonManager
from models.estudiante import Estudiante
from models.docente import Docente
from models.administrador import Administrador
from models.coordinador import Coordinador
from models.curso import Curso, Horario, Modalidad
from models.asignatura import Asignatura
from models.matricula import Matricula
from models.tarea import Tarea


class RepositorioAcademico:

    def __init__(self):
        self.usuarios = {}
        self.estudiantes = []
        self.docentes = []
        self.cursos = []
        self.asignaturas = []
        self.matriculas = []
        self.tareas = []
        self.cargar()

    def cargar(self):
        # Estudiantes
        for e in JsonManager.cargar("data/estudiantes.json"):
            obj = Estudiante(e["nombre"], e["apellido"], e["email"], e["password"], e["matricula"], e["carrera"])
            self.estudiantes.append(obj)
            self.usuarios[obj.email] = obj

        # Docentes
        for d in JsonManager.cargar("data/docentes.json"):
            obj = Docente(d["nombre"], d["apellido"], d["email"], d["password"], d["especialidad"])
            self.docentes.append(obj)
            self.usuarios[obj.email] = obj

        # Administradores
        for a in JsonManager.cargar("data/administradores.json"):
            obj = Administrador(a["nombre"], a["apellido"], a["email"], a["password"])
            self.usuarios[obj.email] = obj

        # Coordinadores
        for c in JsonManager.cargar("data/coordinadores.json"):
            obj = Coordinador(c["nombre"], c["apellido"], c["email"], c["password"])
            self.usuarios[obj.email] = obj

        # Cursos
        for c in JsonManager.cargar("data/cursos.json"):
            curso = Curso(c["id"], c["nombre"], c["duracion"], c["horas"])
            curso.docente_email = c.get("docente_email")
            horario_str = c.get("horario", "")
            if horario_str:
                partes = horario_str.split()
                dia = partes[0] if partes else ""
                horas = partes[1] if len(partes) > 1 else ""
                inicio, fin = (horas.split("-") + [""])[:2]
                curso.asignar_horario(Horario(c["id"], dia, inicio, fin or ""))
            modalidad_str = c.get("modalidad", "")
            if modalidad_str:
                curso.asignar_modalidad(Modalidad(c["id"], modalidad_str, "", True))
            self.cursos.append(curso)

        # Asignaturas
        for a in JsonManager.cargar("data/asignaturas.json"):
            obj = Asignatura(a["id"], a["nombre"], a["horas"], a["creditos"], a["estado"])
            self.asignaturas.append(obj)

        # Matrículas
        for m in JsonManager.cargar("data/matriculas.json"):
            estudiante = self.usuarios.get(m.get("estudiante_email"))
            asignatura = next((a for a in self.asignaturas if a.id == m.get("asignatura_id")), None)
            obj = Matricula(
                m["id"],
                m["fecha"],
                m["tipo"],
                m["estado"],
                m.get("segunda", False),
                estudiante,
                asignatura,
            )
            self.matriculas.append(obj)

        for t in JsonManager.cargar("data/tareas.json"):
            obj = Tarea(
                t.get("titulo", ""),
                t.get("descripcion", ""),
                t.get("fecha_limite", ""),
                t.get("creador_email", ""),
                t.get("id"),
                t.get("entregas", []),
            )
            self.tareas.append(obj)

    # ─── Guardar usuarios (todos los tipos) ───────────────────────────────────
    def guardar_estudiantes(self):
        datos = [
            {"nombre": e.nombre, "apellido": e.apellido, "email": e.email,
             "password": e.get_password(), "matricula": e.matricula, "carrera": e.carrera}
            for e in self.estudiantes
        ]
        JsonManager.guardar("data/estudiantes.json", datos)

    def guardar_docentes(self):
        datos = [
            {"nombre": d.nombre, "apellido": d.apellido, "email": d.email,
             "password": d.get_password(), "especialidad": d.especialidad}
            for d in self.docentes
        ]
        JsonManager.guardar("data/docentes.json", datos)

    def guardar_administradores(self):
        admins = [u for u in self.usuarios.values() if u.obtener_rol() == "administrador"]
        datos = [
            {"nombre": a.nombre, "apellido": a.apellido, "email": a.email, "password": a.get_password()}
            for a in admins
        ]
        JsonManager.guardar("data/administradores.json", datos)

    def guardar_coordinadores(self):
        coords = [u for u in self.usuarios.values() if u.obtener_rol() == "coordinador"]
        datos = [
            {"nombre": c.nombre, "apellido": c.apellido, "email": c.email, "password": c.get_password()}
            for c in coords
        ]
        JsonManager.guardar("data/coordinadores.json", datos)

    def guardar_cursos(self):
        datos = []
        for c in self.cursos:
            h = c.horario
            horario_str = f"{h.dia} {h.hora_inicio}-{h.hora_fin}" if h else ""
            m = c.modalidad
            modalidad_str = m.nombre if m else ""
            datos.append({
                "id": c.id, "nombre": c.nombre,
                "duracion": c._duracion_semanas, "horas": c._total_horas,
                "docente_email": c.docente_email or "",
                "horario": horario_str, "modalidad": modalidad_str
            })
        JsonManager.guardar("data/cursos.json", datos)

    def guardar_asignaturas(self):
        datos = [
            {"id": a.id, "nombre": a.nombre, "horas": a.horas, "creditos": a.creditos, "estado": a.estado}
            for a in self.asignaturas
        ]
        JsonManager.guardar("data/asignaturas.json", datos)

    def guardar_matriculas(self):
        datos = [
            {"id": m.id, "fecha": m.fecha, "tipo": m.tipo, "estado": m.estado,
             "segunda": m.esSegundaMatricula,
             "estudiante_email": m.estudiante.email if m.estudiante else "",
             "asignatura_id": m.asignatura.id if m.asignatura else None}
            for m in self.matriculas
        ]
        JsonManager.guardar("data/matriculas.json", datos)

    def guardar_tareas(self):
        datos = [
            {
                "id": t.id,
                "titulo": t.titulo,
                "descripcion": t.descripcion,
                "fecha_limite": t.fecha_limite,
                "creador_email": t.creador_email,
                "entregas": t.entregas,
            }
            for t in self.tareas
        ]
        JsonManager.guardar("data/tareas.json", datos)

    def obtener_materias_estudiante(self, estudiante_email):
        return [
            m.asignatura
            for m in self.matriculas
            if m.estudiante
            and m.estudiante.email == estudiante_email
            and m.asignatura
            and m.estado == "Activa"
        ]

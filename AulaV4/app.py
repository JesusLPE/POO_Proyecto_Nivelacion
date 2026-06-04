import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
from models.estudiante import Estudiante
from models.docente import Docente
from models.administrador import Administrador
from models.coordinador import Coordinador
from models.tarea import Tarea
from models.curso import Curso, Horario, Modalidad
from models.calificacion import Calificacion
from models.asignatura import Asignatura
from models.matricula import Matricula
from repositories.repositorio_academico import RepositorioAcademico

C = {
    "bg": "#F0F4F8", "sidebar": "#1A237E", "sidebar2": "#283593",
    "accent": "#3949AB", "accent2": "#5C6BC0", "success": "#2E7D32",
    "danger": "#C62828", "warning": "#E65100", "white": "#FFFFFF",
    "card": "#FFFFFF", "text": "#212121", "text_sec": "#546E7A",
    "border": "#CFD8DC", "header_bg": "#E8EAF6",
}
ROL_COLORES = {
    "estudiante": "#1565C0", "docente": "#2E7D32",
    "coordinador": "#6A1B9A", "administrador": "#BF360C",
}
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
MODALIDADES = ["Presencial", "Virtual", "Híbrida"]


def aplicar_estilo():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("TFrame", background=C["bg"])
    s.configure("TLabel", background=C["bg"], foreground=C["text"])
    s.configure("TNotebook", background=C["bg"])
    s.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=[12, 6])
    s.configure("Treeview", background=C["white"], fieldbackground=C["white"],
                foreground=C["text"], rowheight=26, font=("Segoe UI", 9))
    s.configure("Treeview.Heading", background=C["header_bg"],
                foreground=C["text"], font=("Segoe UI", 9, "bold"))
    s.map("Treeview", background=[("selected", C["accent2"])])
    s.configure("TEntry", fieldbackground=C["white"], foreground=C["text"],
                padding=6, font=("Segoe UI", 10))
    s.configure("TCombobox", fieldbackground=C["white"], foreground=C["text"],
                font=("Segoe UI", 10))
    s.configure("TSpinbox", fieldbackground=C["white"], foreground=C["text"],
                font=("Segoe UI", 10))


class SistemaAcademicoApp:

    def __init__(self, repositorio: RepositorioAcademico):
        self.root = tk.Tk()
        self.root.title("Sistema de Admisión – Proceso de Nivelación")
        self.root.state("zoomed")
        self.root.configure(bg=C["bg"])
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        aplicar_estilo()

        # Inyección de dependencia
        self.repo = repositorio
        self.usuarios          = repositorio.usuarios
        self.estudiantes_lista = repositorio.estudiantes
        self.docentes_lista    = repositorio.docentes
        self.asignaturas_lista = repositorio.asignaturas
        self.cursos_lista      = repositorio.cursos
        self.matriculas_lista  = repositorio.matriculas
        self.tareas            = repositorio.tareas
        self.calificaciones    = repositorio.calificaciones
        self.current_user      = None

        self.show_login()

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _crear_ventana_secundaria(self, titulo, ancho=540, alto=440):
        v = tk.Toplevel(self.root)
        v.title(titulo)
        v.geometry(f"{ancho}x{alto}")
        v.configure(bg=C["bg"])
        v.transient(self.root)
        v.grab_set()
        v.resizable(True, True)
        h = tk.Frame(v, bg=C["sidebar"], height=40)
        h.pack(fill="x")
        tk.Label(h, text=titulo, bg=C["sidebar"], fg=C["white"],
                 font=("Segoe UI", 11, "bold")).pack(side="left", padx=14, pady=8)
        return v

    def _validar_email(self, e): return "@" in e and "." in e and len(e) > 5

    def _validar_fecha(self, f):
        try: datetime.strptime(f, "%Y-%m-%d"); return True
        except ValueError: return False

    def _mostrar_error(self, m): messagebox.showerror("Error", m, parent=self.root)
    def _mostrar_info(self, m): messagebox.showinfo("Información", m, parent=self.root)

    def _btn(self, parent, txt, color, cmd, **kw):
        return tk.Button(parent, text=txt, bg=color, fg=C["white"],
                         font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                         command=cmd, **kw)

    # Tareas que el estudiante actual puede ver (filtradas por sus asignaturas matriculadas)
    def _tareas_visibles_estudiante(self):
        asigs_ids = {m.asignatura.id for m in self.matriculas_lista
                     if m.estudiante and m.estudiante.email == self.current_user.email
                     and m.asignatura and m.estado == "Activa"}
        return [t for t in self.tareas
                if t.asignatura_id is None or t.asignatura_id in asigs_ids]

    def _tarea_entregada(self, tarea):
        return any(e.get("estudiante_email") == self.current_user.email
                   and e.get("estado") == "Realizada" for e in tarea.entregas)

    def _tareas_pendientes(self):
        return [t for t in self._tareas_visibles_estudiante() if not self._tarea_entregada(t)]

    def _formatear_fecha(self, tarea):
        if not tarea.fecha_limite: return "Sin fecha límite"
        try:
            return "Vence: " + datetime.strptime(tarea.fecha_limite, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return f"Vence: {tarea.fecha_limite}"

    # Calificaciones del estudiante actual
    def _calificaciones_estudiante(self):
        return [c for c in self.calificaciones
                if c.estudiante.email == self.current_user.email]

    # ── LOGIN ─────────────────────────────────────────────────────────────────
    def show_login(self):
        for w in self.root.winfo_children(): w.destroy()

        left = tk.Frame(self.root, bg=C["sidebar"], width=400)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Frame(left, bg=C["sidebar"]).pack(expand=True)
        tk.Label(left, text="🎓", font=("Segoe UI", 56), bg=C["sidebar"], fg=C["white"]).pack()
        tk.Label(left, text="AulaVirtual", font=("Segoe UI", 24, "bold"),
                 bg=C["sidebar"], fg=C["white"]).pack()
        tk.Label(left, text="Sistema de Admisión\nProceso de Nivelación",
                 font=("Segoe UI", 11), bg=C["sidebar"], fg="#9FA8DA", justify="center").pack(pady=6)
        tk.Frame(left, bg=C["sidebar"]).pack(expand=True)
        tk.Label(left, text="© 2026 – Proyecto POO", font=("Segoe UI", 9),
                 bg=C["sidebar"], fg="#7986CB").pack(pady=10)

        right = tk.Frame(self.root, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True)
        form = tk.Frame(right, bg=C["bg"])
        form.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(form, text="Iniciar Sesión", font=("Segoe UI", 22, "bold"),
                 bg=C["bg"], fg=C["sidebar"]).pack(pady=(0, 4))
        tk.Label(form, text="Ingrese sus credenciales para continuar",
                 font=("Segoe UI", 10), bg=C["bg"], fg=C["text_sec"]).pack(pady=(0, 20))

        tk.Label(form, text="Correo electrónico", font=("Segoe UI", 10, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(anchor="w")
        self.email_entry = ttk.Entry(form, width=36, font=("Segoe UI", 11))
        self.email_entry.pack(ipady=4, pady=(2, 12), fill="x")

        tk.Label(form, text="Contraseña", font=("Segoe UI", 10, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(anchor="w")
        self.pass_entry = ttk.Entry(form, width=36, show="●", font=("Segoe UI", 11))
        self.pass_entry.pack(ipady=4, pady=(2, 20), fill="x")
        self.pass_entry.bind("<Return>", lambda e: self.do_login())

        tk.Button(form, text="Ingresar →", bg=C["accent"], fg=C["white"],
                  font=("Segoe UI", 12, "bold"), relief="flat", cursor="hand2",
                  padx=20, pady=10, command=self.do_login).pack(fill="x")
        self.email_entry.focus()

    def do_login(self):
        email = self.email_entry.get().strip()
        pwd = self.pass_entry.get()
        if not email or not pwd:
            self._mostrar_error("Ingrese email y contraseña"); return
        user = self.usuarios.get(email)
        if user and user.iniciarSesion(email, pwd):
            self.current_user = user
            self.show_main_panel()
        else:
            self._mostrar_error("Credenciales incorrectas")

    # ── PANEL PRINCIPAL ───────────────────────────────────────────────────────
    def show_main_panel(self):
        for w in self.root.winfo_children(): w.destroy()
        u = self.current_user
        rol = u.obtener_rol()
        color = ROL_COLORES.get(rol, C["accent"])

        topbar = tk.Frame(self.root, bg=color, height=56)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Label(topbar, text="🎓  AulaVirtual – Nivelación", font=("Segoe UI", 13, "bold"),
                 bg=color, fg=C["white"]).pack(side="left", padx=18)
        tk.Button(topbar, text="⏻  Cerrar sesión", bg=color, fg=C["white"],
                  font=("Segoe UI", 10), relief="flat", cursor="hand2",
                  activebackground=C["sidebar"], activeforeground=C["white"],
                  command=self.cerrar_sesion).pack(side="right", padx=14, pady=10)
        tk.Label(topbar, text=f"  {rol.upper()}  ", bg=C["white"], fg=color,
                 font=("Segoe UI", 9, "bold"), padx=6, pady=2).pack(side="right", padx=4, pady=14)
        tk.Label(topbar, text=f"{u.nombre} {u.apellido}", font=("Segoe UI", 11),
                 bg=color, fg=C["white"]).pack(side="right", padx=6)

        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True)
        {"estudiante": self.panel_estudiante, "docente": self.panel_docente,
         "coordinador": self.panel_coordinador, "administrador": self.panel_administrador
         }.get(rol, lambda p: None)(body)

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión", "¿Está seguro de que desea salir?"):
            self.current_user = None
            self.show_login()

    # ── PANEL ESTUDIANTE ──────────────────────────────────────────────────────
    def panel_estudiante(self, parent):
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        tabs = [("  📅 Actividades  ", self.show_timeline_est),
                ("  📚 Mis Cursos  ", self.show_cursos_estudiante),
                ("  📊 Mis Notas  ", self.show_notas_estudiante),
                ("  👤 Mi Perfil  ", self.show_perfil),
                ("  🔬 Conceptos POO  ", self.show_poo_demo)]
        for txt, fn in tabs:
            f = ttk.Frame(nb); nb.add(f, text=txt); fn(f)

    def show_timeline_est(self, parent):
        main = tk.Frame(parent, bg=C["bg"]); main.pack(fill="both", expand=True)
        canvas = tk.Canvas(main, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=C["bg"])
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(1, width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        pendientes = self._tareas_pendientes()
        COLS = [C["sidebar"], C["accent"], C["success"], C["warning"]]

        if not pendientes:
            tk.Label(sf, text="✅ ¡Sin tareas pendientes!", font=("Segoe UI", 12, "bold"),
                     bg=C["bg"], fg=C["success"]).pack(pady=30)
        for i, t in enumerate(pendientes):
            col = COLS[i % len(COLS)]
            outer = tk.Frame(sf, bg=col, pady=2); outer.pack(fill="x", pady=5, padx=12)
            card = tk.Frame(outer, bg=C["card"], padx=14, pady=10); card.pack(fill="x", padx=2)
            tk.Frame(card, bg=col, width=5).pack(side="left", fill="y")
            ct = tk.Frame(card, bg=C["card"]); ct.pack(side="left", fill="both", expand=True, padx=10)
            tk.Label(ct, text=self._formatear_fecha(t), font=("Segoe UI", 8, "bold"),
                     bg=C["card"], fg=col).pack(anchor="w")
            tk.Label(ct, text=t.titulo, font=("Segoe UI", 10, "bold"),
                     bg=C["card"], fg=C["text"]).pack(anchor="w", pady=(2, 1))
            tk.Label(ct, text=t.descripcion or "Sin descripción", font=("Segoe UI", 9),
                     bg=C["card"], fg=C["text_sec"], wraplength=500).pack(anchor="w")
            self._btn(ct, "Entregar", col,
                      lambda tarea=t: self.subir_tarea(tarea),
                      padx=8, pady=3).pack(anchor="e", pady=(5, 0))

        # Actividades fijas del proceso de nivelación
        fijas = [
            {"col": C["sidebar2"], "fecha": "Próximos 30 días",
             "titulo": "📅 Calendario de exámenes",
             "desc": "Consulta las fechas de parciales y finales del proceso de nivelación"},
        ]
        for a in fijas:
            col = a["col"]
            outer = tk.Frame(sf, bg=col, pady=2); outer.pack(fill="x", pady=5, padx=12)
            card = tk.Frame(outer, bg=C["card"], padx=14, pady=10); card.pack(fill="x", padx=2)
            tk.Frame(card, bg=col, width=5).pack(side="left", fill="y")
            ct = tk.Frame(card, bg=C["card"]); ct.pack(side="left", fill="both", expand=True, padx=10)
            tk.Label(ct, text=a["fecha"], font=("Segoe UI", 8, "bold"),
                     bg=C["card"], fg=col).pack(anchor="w")
            tk.Label(ct, text=a["titulo"], font=("Segoe UI", 10, "bold"),
                     bg=C["card"], fg=C["text"]).pack(anchor="w")
            tk.Label(ct, text=a["desc"], font=("Segoe UI", 9),
                     bg=C["card"], fg=C["text_sec"]).pack(anchor="w")

    def show_cursos_estudiante(self, parent):
        wrap = tk.Frame(parent, bg=C["bg"]); wrap.pack(fill="both", expand=True, padx=14, pady=10)
        tk.Label(wrap, text="Mis Cursos Matriculados", font=("Segoe UI", 12, "bold"),
                 bg=C["bg"], fg=C["sidebar"]).pack(pady=(0, 10))

        # Solo cursos de la carrera del estudiante
        carrera = self.current_user.carrera if hasattr(self.current_user, "carrera") else ""
        cursos = [c for c in self.cursos_lista if c.carrera == carrera or c.carrera == ""]

        if not cursos:
            tk.Label(wrap, text="No hay cursos disponibles para tu carrera.",
                     font=("Segoe UI", 10), bg=C["bg"], fg=C["text_sec"]).pack()
            return

        COLS = [C["sidebar"], C["accent"], C["success"]]
        for i, curso in enumerate(cursos):
            col = COLS[i % len(COLS)]
            card = tk.Frame(wrap, bg=C["card"], bd=1, relief="solid"); card.pack(fill="x", pady=6, padx=4)
            tk.Frame(card, bg=col, width=8).pack(side="left", fill="y")
            inner = tk.Frame(card, bg=C["card"], padx=14, pady=10)
            inner.pack(side="left", fill="both", expand=True)
            tk.Label(inner, text=curso.nombre, font=("Segoe UI", 11, "bold"),
                     bg=C["card"], fg=col).pack(anchor="w")
            h = str(curso.horario) if curso.horario else "Sin horario"
            m = curso.modalidad.nombre if curso.modalidad else "Sin modalidad"
            tk.Label(inner, text=f"🕐 {h}  |  📡 {m}  |  🏫 {curso.carrera or 'General'}",
                     font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(anchor="w", pady=2)
            self._btn(inner, "Ver tareas del curso", col,
                      lambda c=curso: self.ver_tareas_curso(c),
                      padx=10, pady=4).pack(anchor="e", pady=(4, 0))

    def ver_tareas_curso(self, curso):
        # Tareas que el estudiante puede ver en ese curso específico
        # Solo tareas sin asignatura o de asignaturas donde está matriculado
        asigs_ids = {m.asignatura.id for m in self.matriculas_lista
                     if m.estudiante and m.estudiante.email == self.current_user.email
                     and m.asignatura and m.estado == "Activa"}
        tareas = [t for t in self.tareas if t.asignatura_id is None or t.asignatura_id in asigs_ids]

        v = self._crear_ventana_secundaria(f"Tareas – {curso.nombre}", 560, 460)
        body = tk.Frame(v, bg=C["bg"], padx=16, pady=12); body.pack(fill="both", expand=True)

        if not tareas:
            tk.Label(body, text="No hay tareas disponibles.", font=("Segoe UI", 10),
                     bg=C["bg"], fg=C["text_sec"]).pack(pady=20)
            return

        canvas = tk.Canvas(body, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=C["bg"])
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(1, width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        for tarea in tareas:
            entregada = self._tarea_entregada(tarea)
            col = C["success"] if entregada else C["accent"]
            fila = tk.Frame(sf, bg=C["card"], bd=1, relief="solid", padx=12, pady=8)
            fila.pack(fill="x", pady=4)
            tk.Label(fila, text=tarea.titulo, font=("Segoe UI", 10, "bold"),
                     bg=C["card"], fg=C["text"]).pack(side="left")
            self._btn(fila, "✅ Entregada" if entregada else "Entregar", col,
                      lambda: None if entregada else lambda t=tarea: self.subir_tarea(t),
                      padx=8, pady=3,
                      state="disabled" if entregada else "normal",
                      cursor="arrow" if entregada else "hand2"
                      ).pack(side="right")

    def show_notas_estudiante(self, parent):
        wrap = tk.Frame(parent, bg=C["bg"]); wrap.pack(fill="both", expand=True, padx=14, pady=10)
        tk.Label(wrap, text="Mis Calificaciones", font=("Segoe UI", 12, "bold"),
                 bg=C["bg"], fg=C["sidebar"]).pack(pady=(0, 10))

        califs = self._calificaciones_estudiante()
        if not califs:
            tk.Label(wrap, text="No hay calificaciones registradas.",
                     font=("Segoe UI", 10), bg=C["bg"], fg=C["text_sec"]).pack(pady=20)
            return

        cols = ("Asignatura", "Nota", "Estado", "Observación")
        tree = ttk.Treeview(wrap, columns=cols, show="headings", height=12)
        for col in cols: tree.heading(col, text=col)
        tree.column("Asignatura", width=220); tree.column("Nota", width=70)
        tree.column("Estado", width=100); tree.column("Observación", width=200)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")

        total = 0
        for c in califs:
            estado = "Aprobado" if c.nota >= 7.0 else "Reprobado"
            tree.insert("", "end", values=(c.asignatura, f"{c.nota:.1f}", estado, c.observacion))
            total += c.nota
        if califs:
            prom = total / len(califs)
            tk.Label(wrap, text=f"Promedio general: {prom:.2f}",
                     font=("Segoe UI", 11, "bold"), bg=C["bg"],
                     fg=C["success"] if prom >= 7.0 else C["danger"]).pack(pady=8)

    # ── PANEL DOCENTE ─────────────────────────────────────────────────────────
    def panel_docente(self, parent):
        main = tk.Frame(parent, bg=C["bg"]); main.pack(fill="both", expand=True, padx=10, pady=10)
        left = tk.LabelFrame(main, text="  📅 Actividades  ",
                             bg=C["bg"], font=("Segoe UI", 10, "bold"), fg=C["sidebar"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self._timeline_docente(left)

        right = tk.Frame(main, bg=C["card"], bd=1, relief="solid")
        right.pack(side="right", fill="y", padx=(6, 0), ipadx=10, ipady=10)
        tk.Label(right, text="Acciones rápidas", font=("Segoe UI", 12, "bold"),
                 bg=C["card"], fg=C["sidebar"]).pack(pady=(12, 8), padx=14)
        ttk.Separator(right).pack(fill="x", padx=8)
        botones = [
            ("📝  Registrar nota",   C["success"],  self.registrar_nota),
            ("📋  Crear tarea",      C["accent"],   self.crear_tarea),
            ("📂  Ver entregas",     C["accent2"],  self.ver_entregas_ventana),
            ("🎓  Mis cursos",       C["sidebar2"], self.mis_cursos_docente),
            ("📊  Calificaciones",   C["success"],  self.ver_calificaciones_docente),
            ("👤  Mi Perfil",        C["text_sec"], lambda: self._ventana_con(self.show_perfil, "Mi Perfil")),
            ("🔬  Conceptos POO",    C["text_sec"], lambda: self._ventana_con(self.show_poo_demo, "POO")),
        ]
        for txt, col, cmd in botones:
            self._btn(right, txt, col, cmd, padx=12, pady=7, width=22, anchor="w").pack(pady=4, padx=14)

    def _timeline_docente(self, parent):
        main = tk.Frame(parent, bg=C["bg"]); main.pack(fill="both", expand=True)
        canvas = tk.Canvas(main, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=C["bg"])
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(1, width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Entregas pendientes del docente actual
        mis_tareas = [t for t in self.tareas if t.creador_email == self.current_user.email]
        por_calificar = sum(len(t.entregas) for t in mis_tareas)

        items = [
            (C["sidebar"], "Hoy", f"📬 {por_calificar} entregas por calificar",
             "Revisa y califica las entregas de tus estudiantes",
             "Ver entregas", self.ver_entregas_ventana),
            (C["accent"], "Próximo corte", "⏰ Cierre de notas del primer corte",
             "Registra las notas antes de que cierre el periodo",
             "Registrar notas", self.registrar_nota),
            (C["success"], "Mis cursos", "🎓 Gestionar cursos asignados",
             "Ve los cursos que tienes asignados y sus tareas",
             "Ver cursos", self.mis_cursos_docente),
        ]
        COLS = [C["sidebar"], C["accent"], C["success"], C["warning"]]
        for i, (col, fecha, titulo, desc, btn_txt, cmd) in enumerate(items):
            outer = tk.Frame(sf, bg=col, pady=2); outer.pack(fill="x", pady=5, padx=12)
            card = tk.Frame(outer, bg=C["card"], padx=14, pady=10); card.pack(fill="x", padx=2)
            tk.Frame(card, bg=col, width=5).pack(side="left", fill="y")
            ct = tk.Frame(card, bg=C["card"]); ct.pack(side="left", fill="both", expand=True, padx=10)
            tk.Label(ct, text=fecha, font=("Segoe UI", 8, "bold"), bg=C["card"], fg=col).pack(anchor="w")
            tk.Label(ct, text=titulo, font=("Segoe UI", 10, "bold"), bg=C["card"], fg=C["text"]).pack(anchor="w")
            tk.Label(ct, text=desc, font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"],
                     wraplength=400).pack(anchor="w")
            self._btn(ct, btn_txt, col, cmd, padx=8, pady=3).pack(anchor="e", pady=(5, 0))

    def _ventana_con(self, metodo, titulo, ancho=500, alto=400):
        v = self._crear_ventana_secundaria(titulo, ancho, alto); metodo(v)

    def ver_entregas_ventana(self):
        v = self._crear_ventana_secundaria("Entregas de estudiantes", 800, 520)
        self.show_entregas(v)

    # ── PANEL COORDINADOR ─────────────────────────────────────────────────────
    def panel_coordinador(self, parent):
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        tabs = [("  📅 Actividades  ", self._timeline_coordinador),
                ("  🎓 Cursos  ", self._tab_cursos_coord),
                ("  🕐 Horarios  ", self._tab_horarios_coord),
                ("  👨‍🏫 Asignar Docentes  ", self._tab_asignar_docente_coord),
                ("  📋 Matrículas  ", self._tab_matriculas_coord),
                ("  👤 Mi Perfil  ", self.show_perfil),
                ("  🔬 Conceptos POO  ", self.show_poo_demo)]
        for txt, fn in tabs:
            f = ttk.Frame(nb); nb.add(f, text=txt); fn(f)

    def _timeline_coordinador(self, parent):
        main = tk.Frame(parent, bg=C["bg"]); main.pack(fill="both", expand=True)
        canvas = tk.Canvas(main, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=C["bg"])
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(1, width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        sin_docente = [c for c in self.cursos_lista if not c.docente_email]
        mats_pendientes = [m for m in self.matriculas_lista if m.estado == "Pendiente"]
        items = [
            (C["danger"], "⚠ Urgente",
             f"🚫 {len(sin_docente)} curso(s) sin docente asignado",
             "Asigna docentes para que los estudiantes tengan clase"),
            (C["warning"], "Pendiente",
             f"📋 {len(mats_pendientes)} matrícula(s) por aprobar",
             "Revisa y aprueba o rechaza las solicitudes de matrícula"),
            (C["accent"], "Esta semana",
             "🕐 Revisar horarios del ciclo actual",
             "Verifica que los horarios estén completos y sin conflictos"),
        ]
        for col, fecha, titulo, desc in items:
            outer = tk.Frame(sf, bg=col, pady=2); outer.pack(fill="x", pady=5, padx=12)
            card = tk.Frame(outer, bg=C["card"], padx=14, pady=10); card.pack(fill="x", padx=2)
            tk.Frame(card, bg=col, width=5).pack(side="left", fill="y")
            ct = tk.Frame(card, bg=C["card"]); ct.pack(side="left", fill="both", expand=True, padx=10)
            tk.Label(ct, text=fecha, font=("Segoe UI", 8, "bold"), bg=C["card"], fg=col).pack(anchor="w")
            tk.Label(ct, text=titulo, font=("Segoe UI", 10, "bold"), bg=C["card"], fg=C["text"]).pack(anchor="w")
            tk.Label(ct, text=desc, font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(anchor="w")

    def _tab_cursos_coord(self, parent):
        body = tk.Frame(parent, bg=C["bg"], padx=12, pady=8)
        body.pack(fill="both", expand=True)

        cols = ("ID", "Nombre del Curso", "Carrera", "Semanas", "Horas", "Horario", "Modalidad", "Docente")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=12)
        anchos = [35, 200, 150, 60, 60, 160, 90, 180]
        for col, w in zip(cols, anchos):
            tree.heading(col, text=col); tree.column(col, width=w)
        sb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="top", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def refrescar():
            for i in tree.get_children(): tree.delete(i)
            for c in self.cursos_lista:
                h = str(c.horario) if c.horario else ""
                m = c.modalidad.nombre if c.modalidad else ""
                d_obj = self.usuarios.get(c.docente_email or "")
                d = f"{d_obj.nombre} {d_obj.apellido}" if d_obj else "Sin asignar"
                tree.insert("", "end", values=(c.id, c.nombre, c.carrera or "General",
                                                f"{c._duracion_semanas}s", c._total_horas, h, m, d))
        refrescar()

        form = tk.Frame(body, bg=C["bg"]); form.pack(fill="x", pady=6)

        def nuevo_curso():
            vn = self._crear_ventana_secundaria("Nuevo Curso", 480, 440)
            bf = tk.Frame(vn, bg=C["bg"], padx=18, pady=12); bf.pack(fill="both", expand=True)
            campos = {}
            etiquetas = [("Nombre del curso:", "nombre"), ("Carrera/Área:", "carrera"),
                         ("Duración (semanas):", "dur"), ("Total horas:", "horas")]
            for lbl, key in etiquetas:
                tk.Label(bf, text=lbl, font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
                e = ttk.Entry(bf, width=50); e.pack(ipady=3, pady=(1, 7), fill="x")
                campos[key] = e

            tk.Label(bf, text="Docente:", font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
            d_vals = ["Sin asignar"] + [f"{d.nombre} {d.apellido} ({d.email})" for d in self.docentes_lista]
            d_cb = ttk.Combobox(bf, values=d_vals, width=48); d_cb.current(0)
            d_cb.pack(ipady=3, pady=(1, 7), fill="x")

            tk.Label(bf, text="Modalidad:", font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
            mod_cb = ttk.Combobox(bf, values=MODALIDADES, width=48)
            mod_cb.pack(ipady=3, pady=(1, 7), fill="x"); mod_cb.current(0)

            def guardar():
                nombre = campos["nombre"].get().strip()
                if not nombre: self._mostrar_error("El nombre es obligatorio"); return
                try: dur = int(campos["dur"].get()); horas = int(campos["horas"].get())
                except ValueError: self._mostrar_error("Duración y horas deben ser enteros"); return
                nuevo_id = max((c.id for c in self.cursos_lista), default=0) + 1
                carrera = campos["carrera"].get().strip()
                curso = Curso(nuevo_id, nombre, dur, horas, carrera)
                mod = mod_cb.get()
                if mod: curso.asignar_modalidad(Modalidad(nuevo_id, mod, "", True))
                sel_d = d_cb.get()
                if sel_d and sel_d != "Sin asignar":
                    curso.docente_email = sel_d.split("(")[-1].rstrip(")")
                self.cursos_lista.append(curso)
                self.repo.guardar_cursos()
                refrescar(); self._mostrar_info("✅ Curso creado"); vn.destroy()

            self._btn(bf, "✔ Crear curso", C["success"], guardar, pady=8).pack(fill="x", pady=6)

        def eliminar_curso():
            sel = tree.selection()
            if not sel: self._mostrar_error("Seleccione un curso"); return
            cid = tree.item(sel[0])["values"][0]
            if messagebox.askyesno("Confirmar", f"¿Eliminar el curso ID {cid}?"):
                self.cursos_lista[:] = [c for c in self.cursos_lista if c.id != cid]
                self.repo.guardar_cursos(); refrescar()

        self._btn(form, "➕ Nuevo curso", C["success"], nuevo_curso, padx=8, pady=5).pack(side="left", padx=6)
        self._btn(form, "🗑 Eliminar", C["danger"], eliminar_curso, padx=8, pady=5).pack(side="left", padx=4)
        self._btn(form, "🔄 Refrescar", C["text_sec"], refrescar, padx=8, pady=5).pack(side="left", padx=4)

    def _tab_horarios_coord(self, parent):
        # Gestión completa de horarios por el coordinador
        body = tk.Frame(parent, bg=C["bg"], padx=12, pady=8)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Gestión de Horarios", font=("Segoe UI", 12, "bold"),
                 bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", pady=(0, 8))

        cols = ("ID", "Curso", "Día", "Inicio", "Fin", "Modalidad", "Aula")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=12)
        anchos = [35, 220, 100, 80, 80, 100, 100]
        for col, w in zip(cols, anchos):
            tree.heading(col, text=col); tree.column(col, width=w)
        sb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="top", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def refrescar():
            for i in tree.get_children(): tree.delete(i)
            for h in self.repo.horarios:
                tree.insert("", "end", values=(
                    h.get("id", ""), h.get("curso", ""), h.get("dia", ""),
                    h.get("inicio", ""), h.get("fin", ""),
                    h.get("modalidad", ""), h.get("aula", "")
                ))
        refrescar()

        form = tk.Frame(body, bg=C["bg"]); form.pack(fill="x", pady=6)

        def nuevo_horario():
            vh = self._crear_ventana_secundaria("Nuevo Horario", 480, 420)
            bf = tk.Frame(vh, bg=C["bg"], padx=18, pady=12); bf.pack(fill="both", expand=True)

            tk.Label(bf, text="Curso:", font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
            curso_vals = [f"{c.nombre} (ID:{c.id})" for c in self.cursos_lista]
            curso_cb = ttk.Combobox(bf, values=curso_vals, width=50)
            curso_cb.pack(ipady=3, pady=(1, 8), fill="x")

            tk.Label(bf, text="Día:", font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
            dia_cb = ttk.Combobox(bf, values=DIAS, width=50)
            dia_cb.pack(ipady=3, pady=(1, 8), fill="x"); dia_cb.current(0)

            fila_horas = tk.Frame(bf, bg=C["bg"]); fila_horas.pack(fill="x", pady=(0, 8))
            tk.Label(fila_horas, text="Hora inicio:", font=("Segoe UI", 9, "bold"),
                     bg=C["bg"], fg=C["text"]).pack(side="left")
            inicio_e = ttk.Entry(fila_horas, width=10); inicio_e.pack(side="left", padx=6, ipady=3)
            inicio_e.insert(0, "08:00")
            tk.Label(fila_horas, text="Hora fin:", font=("Segoe UI", 9, "bold"),
                     bg=C["bg"], fg=C["text"]).pack(side="left", padx=(12, 0))
            fin_e = ttk.Entry(fila_horas, width=10); fin_e.pack(side="left", padx=6, ipady=3)
            fin_e.insert(0, "10:00")

            tk.Label(bf, text="Modalidad:", font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
            mod_cb = ttk.Combobox(bf, values=MODALIDADES, width=50)
            mod_cb.pack(ipady=3, pady=(1, 8), fill="x"); mod_cb.current(0)

            tk.Label(bf, text="Aula / Enlace:", font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
            aula_e = ttk.Entry(bf, width=50); aula_e.pack(ipady=3, pady=(1, 8), fill="x")

            def guardar_horario():
                sel_curso = curso_cb.get()
                if not sel_curso: self._mostrar_error("Seleccione un curso"); return
                try: curso_id = int(sel_curso.split("ID:")[-1].rstrip(")"))
                except ValueError: self._mostrar_error("Curso inválido"); return
                curso_obj = next((c for c in self.cursos_lista if c.id == curso_id), None)
                if not curso_obj: return
                inicio = inicio_e.get().strip()
                fin = fin_e.get().strip()
                if not inicio or not fin:
                    self._mostrar_error("Ingrese horas de inicio y fin"); return
                nuevo_id = max((h.get("id", 0) for h in self.repo.horarios), default=0) + 1
                nuevo_h = {"id": nuevo_id, "curso": curso_obj.nombre,
                           "curso_id": curso_id, "dia": dia_cb.get(),
                           "inicio": inicio, "fin": fin,
                           "modalidad": mod_cb.get(), "aula": aula_e.get().strip()}
                # Actualizar horario del curso también
                curso_obj.asignar_horario(Horario(curso_id, dia_cb.get(), inicio, fin))
                curso_obj.asignar_modalidad(Modalidad(curso_id, mod_cb.get(), "", True))
                self.repo.horarios.append(nuevo_h)
                self.repo.guardar_horarios()
                self.repo.guardar_cursos()
                refrescar()
                self._mostrar_info(f"✅ Horario creado: {dia_cb.get()} {inicio}-{fin}")
                vh.destroy()

            self._btn(bf, "✔ Guardar horario", C["success"], guardar_horario, pady=8).pack(fill="x", pady=6)

        def editar_horario():
            sel = tree.selection()
            if not sel: self._mostrar_error("Seleccione un horario"); return
            vals = tree.item(sel[0])["values"]
            hid = vals[0]
            h_obj = next((h for h in self.repo.horarios if h.get("id") == hid), None)
            if not h_obj: return

            ve = self._crear_ventana_secundaria("Editar Horario", 400, 340)
            bf = tk.Frame(ve, bg=C["bg"], padx=18, pady=12); bf.pack(fill="both", expand=True)
            tk.Label(bf, text=f"Curso: {h_obj.get('curso', '')}", font=("Segoe UI", 10, "bold"),
                     bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", pady=(0, 10))

            tk.Label(bf, text="Día:", font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
            dia_cb = ttk.Combobox(bf, values=DIAS, width=44)
            dia_cb.set(h_obj.get("dia", DIAS[0])); dia_cb.pack(ipady=3, pady=(1, 8), fill="x")

            fila = tk.Frame(bf, bg=C["bg"]); fila.pack(fill="x", pady=(0, 8))
            tk.Label(fila, text="Inicio:", font=("Segoe UI", 9, "bold"),
                     bg=C["bg"], fg=C["text"]).pack(side="left")
            ini_e = ttk.Entry(fila, width=10); ini_e.pack(side="left", padx=6, ipady=3)
            ini_e.insert(0, h_obj.get("inicio", "08:00"))
            tk.Label(fila, text="Fin:", font=("Segoe UI", 9, "bold"),
                     bg=C["bg"], fg=C["text"]).pack(side="left", padx=(12, 0))
            fin_e = ttk.Entry(fila, width=10); fin_e.pack(side="left", padx=6, ipady=3)
            fin_e.insert(0, h_obj.get("fin", "10:00"))

            tk.Label(bf, text="Modalidad:", font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
            mod_cb = ttk.Combobox(bf, values=MODALIDADES, width=44)
            mod_cb.set(h_obj.get("modalidad", MODALIDADES[0])); mod_cb.pack(ipady=3, pady=(1, 8), fill="x")

            tk.Label(bf, text="Aula / Enlace:", font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
            aula_e = ttk.Entry(bf, width=44); aula_e.pack(ipady=3, pady=(1, 8), fill="x")
            aula_e.insert(0, h_obj.get("aula", ""))

            def guardar_edicion():
                h_obj["dia"] = dia_cb.get()
                h_obj["inicio"] = ini_e.get().strip()
                h_obj["fin"] = fin_e.get().strip()
                h_obj["modalidad"] = mod_cb.get()
                h_obj["aula"] = aula_e.get().strip()
                # Actualizar curso
                cid = h_obj.get("curso_id")
                curso_obj = next((c for c in self.cursos_lista if c.id == cid), None)
                if curso_obj:
                    curso_obj.asignar_horario(Horario(cid, dia_cb.get(), ini_e.get().strip(), fin_e.get().strip()))
                    curso_obj.asignar_modalidad(Modalidad(cid, mod_cb.get(), "", True))
                self.repo.guardar_horarios(); self.repo.guardar_cursos()
                refrescar(); self._mostrar_info("✅ Horario actualizado"); ve.destroy()

            self._btn(bf, "✔ Guardar cambios", C["success"], guardar_edicion, pady=8).pack(fill="x", pady=6)

        def eliminar_horario():
            sel = tree.selection()
            if not sel: self._mostrar_error("Seleccione un horario"); return
            hid = tree.item(sel[0])["values"][0]
            if messagebox.askyesno("Confirmar", "¿Eliminar este horario?"):
                self.repo.horarios[:] = [h for h in self.repo.horarios if h.get("id") != hid]
                self.repo.guardar_horarios(); refrescar()

        self._btn(form, "➕ Nuevo horario", C["success"], nuevo_horario, padx=8, pady=5).pack(side="left", padx=6)
        self._btn(form, "✏ Editar", C["accent"], editar_horario, padx=8, pady=5).pack(side="left", padx=4)
        self._btn(form, "🗑 Eliminar", C["danger"], eliminar_horario, padx=8, pady=5).pack(side="left", padx=4)
        self._btn(form, "🔄 Refrescar", C["text_sec"], refrescar, padx=8, pady=5).pack(side="left", padx=4)

    def _tab_asignar_docente_coord(self, parent):
        body = tk.Frame(parent, bg=C["bg"], padx=14, pady=10)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Asignación de Docentes a Cursos",
                 font=("Segoe UI", 12, "bold"), bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", pady=(0, 10))

        cols = ("Curso", "Carrera", "Docente Actual")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=10)
        for col in cols: tree.heading(col, text=col)
        tree.column("Curso", width=220); tree.column("Carrera", width=160); tree.column("Docente Actual", width=200)
        sb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="top", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def refrescar():
            for i in tree.get_children(): tree.delete(i)
            for c in self.cursos_lista:
                d = self.usuarios.get(c.docente_email or "")
                d_txt = f"{d.nombre} {d.apellido}" if d else "⚠ Sin docente"
                tree.insert("", "end", values=(c.nombre, c.carrera or "General", d_txt))
        refrescar()

        form = tk.Frame(body, bg=C["bg"]); form.pack(fill="x", pady=8)
        tk.Label(form, text="Docente:", font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(side="left")
        d_v = tk.StringVar()
        d_vals = [f"{d.nombre} {d.apellido} ({d.email})" for d in self.docentes_lista]
        ttk.Combobox(form, textvariable=d_v, values=d_vals, width=36).pack(side="left", padx=8, ipady=3)

        def asignar():
            sel = tree.selection()
            if not sel: self._mostrar_error("Seleccione un curso"); return
            if not d_v.get(): self._mostrar_error("Seleccione un docente"); return
            curso_nombre = tree.item(sel[0])["values"][0]
            curso = next((c for c in self.cursos_lista if c.nombre == curso_nombre), None)
            if not curso: return
            email = d_v.get().split("(")[-1].rstrip(")")
            curso.docente_email = email
            self.repo.guardar_cursos()
            refrescar()
            self._mostrar_info(f"✅ Docente asignado a {curso.nombre}")

        self._btn(form, "✔ Asignar", C["accent"], asignar, padx=8, pady=5).pack(side="left", padx=6)

    def _tab_matriculas_coord(self, parent):
        body = tk.Frame(parent, bg=C["bg"], padx=12, pady=8); body.pack(fill="both", expand=True)
        cols = ("ID", "Estudiante", "Asignatura", "Fecha", "Tipo", "Estado")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=12)
        for col in cols: tree.heading(col, text=col)
        sb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="top", fill="both", expand=True); sb.pack(side="right", fill="y")

        def refrescar():
            for i in tree.get_children(): tree.delete(i)
            for m in self.matriculas_lista:
                est = f"{m.estudiante.nombre} {m.estudiante.apellido}" if m.estudiante else "N/A"
                asig = m.asignatura.nombre if m.asignatura else "N/A"
                tree.insert("", "end", values=(m.id, est, asig, m.fecha, m.tipo, m.estado))
        refrescar()

        form = tk.Frame(body, bg=C["bg"]); form.pack(fill="x", pady=6)

        def cambiar_estado():
            sel = tree.selection()
            if not sel: self._mostrar_error("Seleccione una matrícula"); return
            mid = tree.item(sel[0])["values"][0]
            nuevo = simpledialog.askstring("Cambiar estado", "Nuevo estado (Activa / Anulada / Pendiente):")
            if nuevo:
                for m in self.matriculas_lista:
                    if m.id == mid: m.estado = nuevo; break
                self.repo.guardar_matriculas(); refrescar()

        self._btn(form, "✏ Cambiar estado", C["warning"], cambiar_estado, padx=8, pady=5).pack(side="left", padx=6)
        self._btn(form, "🔄 Refrescar", C["text_sec"], refrescar, padx=8, pady=5).pack(side="left", padx=4)

    # ── PANEL ADMINISTRADOR ───────────────────────────────────────────────────
    def panel_administrador(self, parent):
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        tabs = [("  📅 Actividades  ", self._timeline_admin),
                ("  👥 Usuarios  ", self._tab_usuarios_admin),
                ("  📚 Asignaturas  ", self._tab_asignaturas_admin),
                ("  🎓 Matrículas  ", self._tab_matriculas_admin),
                ("  📊 Logs  ", self._tab_logs_admin),
                ("  👤 Mi Perfil  ", self.show_perfil),
                ("  🔬 Conceptos POO  ", self.show_poo_demo)]
        for txt, fn in tabs:
            f = ttk.Frame(nb); nb.add(f, text=txt); fn(f)

    def _timeline_admin(self, parent):
        main = tk.Frame(parent, bg=C["bg"]); main.pack(fill="both", expand=True)
        canvas = tk.Canvas(main, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=C["bg"])
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(1, width=e.width))
        canvas.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")

        items = [
            (C["sidebar"], "Hoy",
             f"👥 {len(self.estudiantes_lista)} estudiantes registrados",
             "Total de estudiantes activos en el sistema"),
            (C["accent"], "Sistema",
             f"📚 {len(self.asignaturas_lista)} asignaturas  |  {len(self.cursos_lista)} cursos",
             "Resumen de la oferta académica actual"),
            (C["success"], "Proceso",
             f"🎓 {len(self.matriculas_lista)} matrículas registradas",
             "Total de matrículas en todos los estados"),
        ]
        for col, fecha, titulo, desc in items:
            outer = tk.Frame(sf, bg=col, pady=2); outer.pack(fill="x", pady=5, padx=12)
            card = tk.Frame(outer, bg=C["card"], padx=14, pady=10); card.pack(fill="x", padx=2)
            tk.Frame(card, bg=col, width=5).pack(side="left", fill="y")
            ct = tk.Frame(card, bg=C["card"]); ct.pack(side="left", fill="both", expand=True, padx=10)
            tk.Label(ct, text=fecha, font=("Segoe UI", 8, "bold"), bg=C["card"], fg=col).pack(anchor="w")
            tk.Label(ct, text=titulo, font=("Segoe UI", 10, "bold"), bg=C["card"], fg=C["text"]).pack(anchor="w")
            tk.Label(ct, text=desc, font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(anchor="w")

    def _tab_usuarios_admin(self, parent):
        body = tk.Frame(parent, bg=C["bg"], padx=12, pady=8); body.pack(fill="both", expand=True)
        cols = ("Email", "Nombre completo", "Rol", "Info extra")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=12)
        tree.column("Email", width=200); tree.column("Nombre completo", width=180)
        tree.column("Rol", width=110); tree.column("Info extra", width=200)
        for col in cols: tree.heading(col, text=col)
        sb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="top", fill="both", expand=True); sb.pack(side="right", fill="y")

        def refrescar():
            for i in tree.get_children(): tree.delete(i)
            for u in self.usuarios.values():
                extra = ""
                if hasattr(u, "carrera"): extra = f"Carrera: {u.carrera}"
                elif hasattr(u, "especialidad"): extra = f"Esp: {u.especialidad}"
                tree.insert("", "end", values=(u.email, f"{u.nombre} {u.apellido}", u.obtener_rol(), extra))
        refrescar()

        form = tk.Frame(body, bg=C["bg"]); form.pack(fill="x", pady=6)
        self._btn(form, "➕ Crear usuario", C["success"], self.crear_usuario, padx=8, pady=5).pack(side="left", padx=6)
        self._btn(form, "🗑 Eliminar", C["danger"], self.eliminar_usuario, padx=8, pady=5).pack(side="left", padx=4)
        self._btn(form, "🔄 Refrescar", C["text_sec"], refrescar, padx=8, pady=5).pack(side="left", padx=4)

    def _tab_asignaturas_admin(self, parent):
        body = tk.Frame(parent, bg=C["bg"], padx=12, pady=8); body.pack(fill="both", expand=True)
        cols = ("ID", "Nombre", "Horas", "Créditos", "Estado")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=12)
        tree.column("ID", width=40); tree.column("Nombre", width=280)
        for col in cols: tree.heading(col, text=col)
        sb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="top", fill="both", expand=True); sb.pack(side="right", fill="y")

        def refrescar():
            for i in tree.get_children(): tree.delete(i)
            for a in self.asignaturas_lista:
                tree.insert("", "end", values=(a.id, a.nombre, a.horas, a.creditos, a.estado))
        refrescar()

        form = tk.Frame(body, bg=C["bg"]); form.pack(fill="x", pady=6)
        fields = {}
        for lbl, key, w in [("Nombre:", "nombre", 20), ("Horas:", "horas", 6), ("Créditos:", "cred", 6)]:
            tk.Label(form, text=lbl, font=("Segoe UI", 9, "bold"),
                     bg=C["bg"], fg=C["text"]).pack(side="left", padx=4)
            e = ttk.Entry(form, width=w); e.pack(side="left", padx=2, ipady=3)
            fields[key] = e

        def agregar():
            nombre = fields["nombre"].get().strip()
            if not nombre: self._mostrar_error("Ingrese el nombre"); return
            try: horas = int(fields["horas"].get()); cred = int(fields["cred"].get())
            except ValueError: self._mostrar_error("Horas y créditos deben ser enteros"); return
            nuevo_id = max((a.id for a in self.asignaturas_lista), default=0) + 1
            self.asignaturas_lista.append(Asignatura(nuevo_id, nombre, horas, cred, "Activa"))
            self.repo.guardar_asignaturas(); refrescar()
            for f in fields.values(): f.delete(0, tk.END)
            self._mostrar_info("✅ Asignatura creada")

        def eliminar():
            sel = tree.selection()
            if not sel: return
            id_asi = tree.item(sel[0])["values"][0]
            if messagebox.askyesno("Confirmar", "¿Eliminar esta asignatura?"):
                self.asignaturas_lista[:] = [a for a in self.asignaturas_lista if a.id != id_asi]
                self.repo.guardar_asignaturas(); refrescar()

        self._btn(form, "➕ Agregar", C["success"], agregar, padx=8, pady=4).pack(side="left", padx=8)
        self._btn(form, "🗑 Eliminar", C["danger"], eliminar, padx=8, pady=4).pack(side="left", padx=4)

    def _tab_matriculas_admin(self, parent):
        body = tk.Frame(parent, bg=C["bg"], padx=12, pady=8); body.pack(fill="both", expand=True)
        cols = ("ID", "Estudiante", "Carrera", "Asignatura", "Fecha", "Tipo", "Estado")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=10)
        for col in cols: tree.heading(col, text=col)
        tree.column("ID", width=35); tree.column("Estudiante", width=160)
        tree.column("Carrera", width=140); tree.column("Asignatura", width=180)
        sb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="top", fill="both", expand=True); sb.pack(side="right", fill="y")

        def refrescar():
            for i in tree.get_children(): tree.delete(i)
            for m in self.matriculas_lista:
                est = m.estudiante
                carrera = est.carrera if est and hasattr(est, "carrera") else "N/A"
                est_txt = f"{est.nombre} {est.apellido}" if est else "N/A"
                asig = m.asignatura.nombre if m.asignatura else "N/A"
                tree.insert("", "end", values=(m.id, est_txt, carrera, asig, m.fecha, m.tipo, m.estado))
        refrescar()

        form = tk.Frame(body, bg=C["bg"]); form.pack(fill="x", pady=6)
        tk.Label(form, text="Estudiante:", font=("Segoe UI", 9, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(side="left", padx=4)
        est_v = tk.StringVar()
        ttk.Combobox(form, textvariable=est_v,
                     values=[f"{e.nombre} {e.apellido} ({e.matricula})" for e in self.estudiantes_lista],
                     width=26).pack(side="left", padx=4, ipady=3)
        tk.Label(form, text="Asignatura:", font=("Segoe UI", 9, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(side="left", padx=4)
        asig_v = tk.StringVar()
        ttk.Combobox(form, textvariable=asig_v,
                     values=[f"{a.nombre} ({a.id})" for a in self.asignaturas_lista],
                     width=22).pack(side="left", padx=4, ipady=3)
        tk.Label(form, text="Tipo:", font=("Segoe UI", 9, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(side="left", padx=4)
        tipo_v = tk.StringVar(value="Regular")
        ttk.Combobox(form, textvariable=tipo_v, values=["Regular", "Segunda"], width=10
                     ).pack(side="left", padx=2, ipady=3)

        def matricular():
            sel = est_v.get()
            if not sel: self._mostrar_error("Seleccione un estudiante"); return
            mat_cod = sel.split("(")[-1].rstrip(")")
            est = next((e for e in self.estudiantes_lista if e.matricula == mat_cod), None)
            if not est: return
            sel_asig = asig_v.get()
            if not sel_asig: self._mostrar_error("Seleccione una asignatura"); return
            try: id_asig = int(sel_asig.split("(")[-1].rstrip(")"))
            except ValueError: self._mostrar_error("Asignatura inválida"); return
            asignatura = next((a for a in self.asignaturas_lista if a.id == id_asig), None)
            if not asignatura: return
            # Verificar duplicado
            ya = any(m.estudiante and m.estudiante.email == est.email
                     and m.asignatura and m.asignatura.id == id_asig
                     and m.estado == "Activa" for m in self.matriculas_lista)
            if ya:
                self._mostrar_error(f"{est.nombre} ya está matriculado en {asignatura.nombre}"); return
            nuevo_id = max((m.id for m in self.matriculas_lista), default=0) + 1
            m = Matricula(nuevo_id, datetime.now().strftime("%Y-%m-%d"),
                          tipo_v.get(), "Activa", tipo_v.get() == "Segunda", est, asignatura)
            self.matriculas_lista.append(m)
            self.repo.guardar_matriculas(); refrescar()
            self._mostrar_info(f"✅ Matrícula registrada: {est.nombre} → {asignatura.nombre}")

        def cambiar_estado():
            sel = tree.selection()
            if not sel: return
            mid = tree.item(sel[0])["values"][0]
            nuevo = simpledialog.askstring("Cambiar estado", "Nuevo estado (Activa / Anulada / Pendiente):")
            if nuevo:
                for m in self.matriculas_lista:
                    if m.id == mid: m.estado = nuevo; break
                self.repo.guardar_matriculas(); refrescar()

        self._btn(form, "➕ Matricular", C["success"], matricular, padx=8, pady=4).pack(side="left", padx=8)
        self._btn(form, "✏ Estado", C["warning"], cambiar_estado, padx=8, pady=4).pack(side="left", padx=4)

    def _tab_logs_admin(self, parent):
        body = tk.Frame(parent, bg=C["bg"], padx=12, pady=8); body.pack(fill="both", expand=True)
        txt = tk.Text(body, font=("Consolas", 9), bg="#1E1E1E", fg="#DCDCDC",
                      insertbackground="white", wrap="word")
        txt.pack(fill="both", expand=True)
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        contenido = f"""[{ahora}] INFO  – Sistema de Admisión – Proceso de Nivelación iniciado
[{ahora}] INFO  – Usuario autenticado: {self.current_user.email} (rol: {self.current_user.obtener_rol()})
[{ahora}] INFO  – Cargados {len(self.estudiantes_lista)} estudiantes
[{ahora}] INFO  – Cargados {len(self.docentes_lista)} docentes
[{ahora}] INFO  – Cargados {len(self.cursos_lista)} cursos
[{ahora}] INFO  – Cargadas {len(self.asignaturas_lista)} asignaturas
[{ahora}] INFO  – Cargadas {len(self.matriculas_lista)} matrículas
[{ahora}] INFO  – Cargadas {len(self.tareas)} tareas
[{ahora}] INFO  – Cargadas {len(self.calificaciones)} calificaciones
[{ahora}] INFO  – Cargados {len(self.repo.horarios)} horarios
[{ahora}] INFO  – RepositorioAcademico inyectado en SistemaAcademicoApp ✅
[{ahora}] INFO  – Repository Pattern activo (JsonManager + RepositorioAcademico)
[{ahora}] INFO  – Herencia: Persona ← Estudiante, Docente, Coordinador, Administrador
[{ahora}] INFO  – Polimorfismo: obtener_rol() implementado en cada clase hija
[{ahora}] INFO  – Abstracción: Persona y Evaluacion son clases abstractas (ABC)
[{ahora}] INFO  – Encapsulamiento: atributos privados con @property en todos los modelos
"""
        txt.insert("1.0", contenido)
        txt.config(state="disabled")

    # ── FUNCIONES COMPARTIDAS ─────────────────────────────────────────────────
    def show_perfil(self, parent):
        u = self.current_user
        rol = u.obtener_rol()
        color = ROL_COLORES.get(rol, C["accent"])
        wrap = tk.Frame(parent, bg=C["bg"]); wrap.pack(expand=True)
        av = tk.Frame(wrap, bg=color, width=80, height=80); av.pack(pady=(20, 6)); av.pack_propagate(False)
        tk.Label(av, text=(u.nombre[0].upper() if u.nombre else "?"),
                 font=("Segoe UI", 30, "bold"), bg=color, fg=C["white"]).place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(wrap, text=f"{u.nombre} {u.apellido}", font=("Segoe UI", 14, "bold"),
                 bg=C["bg"], fg=C["text"]).pack()
        tk.Label(wrap, text=rol.capitalize(), font=("Segoe UI", 10),
                 bg=color, fg=C["white"], padx=10, pady=2).pack(pady=4)
        card = tk.Frame(wrap, bg=C["card"], bd=1, relief="solid", padx=20, pady=14)
        card.pack(padx=30, pady=10, fill="x")
        campos = [("📧 Email", u.email), ("👤 Nombre", u.nombre), ("👤 Apellido", u.apellido)]
        if hasattr(u, "matricula"): campos.append(("🎫 Matrícula", u.matricula))
        if hasattr(u, "carrera"): campos.append(("🏫 Carrera", u.carrera))
        if hasattr(u, "especialidad"): campos.append(("🔬 Especialidad", u.especialidad))
        for label, valor in campos:
            row = tk.Frame(card, bg=C["card"]); row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=("Segoe UI", 10, "bold"),
                     bg=C["card"], fg=C["text_sec"], width=16, anchor="w").pack(side="left")
            tk.Label(row, text=valor, font=("Segoe UI", 10),
                     bg=C["card"], fg=C["text"]).pack(side="left", padx=8)

    def show_poo_demo(self, parent):
        wrap = tk.Frame(parent, bg=C["bg"]); wrap.pack(fill="both", expand=True, padx=14, pady=10)
        tk.Label(wrap, text="Conceptos de Programación Orientada a Objetos",
                 font=("Segoe UI", 12, "bold"), bg=C["bg"], fg=C["sidebar"]).pack(pady=(0, 8))
        conceptos = [
            ("🔗 Herencia", "Estudiante, Docente, Coordinador, Administrador heredan de Persona."),
            ("🔄 Polimorfismo", "obtener_rol() devuelve diferente valor según el objeto instanciado."),
            ("🔒 Abstracción", "Persona y Evaluacion son clases abstractas (ABC), no instanciables directamente."),
            ("📦 Encapsulamiento", "Atributos privados (__nombre, __email) protegidos con @property y @setter."),
            ("⬆️ super()", "Los constructores de clases hijas llaman super().__init__() para inicializar Persona."),
            ("🧮 Sobrecarga", "calcularPromedio(n1, n2, n3=0) acepta 2 o 3 notas con argumento opcional."),
            ("🌐 Herencia múltiple", "Persona hereda de ABC (clase abstracta) y de IniciarSesion (interfaz)."),
            ("📜 Interfaz", "IniciarSesion define el contrato: iniciarSesion(), cerrarSesion(), _verificarCuenta()."),
            ("💉 Inyección de dependencia", "RepositorioAcademico se inyecta en SistemaAcademicoApp(repo)."),
            ("🗄 Repository Pattern", "JsonManager + RepositorioAcademico separan la lógica de acceso a datos."),
            ("🔐 Control de acceso", "Tareas filtradas por matrícula: estudiantes de otra carrera no ven tareas ajenas."),
            ("🆔 Identificación por carrera", "Curso.carrera garantiza que solo los estudiantes correspondientes lo vean."),
        ]
        canvas = tk.Canvas(wrap, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=C["bg"])
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(1, width=e.width))
        canvas.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")
        COLS = [C["sidebar"], C["accent"], C["success"], C["warning"], C["sidebar2"],
                C["accent2"], C["danger"], C["sidebar"], C["accent"], C["success"], C["warning"], C["sidebar2"]]
        for i, (titulo, desc) in enumerate(conceptos):
            col = COLS[i % len(COLS)]
            card = tk.Frame(sf, bg=C["card"], bd=1, relief="solid"); card.pack(fill="x", pady=4, padx=4)
            tk.Frame(card, bg=col, width=6).pack(side="left", fill="y")
            inner = tk.Frame(card, bg=C["card"], padx=12, pady=8)
            inner.pack(side="left", fill="both", expand=True)
            tk.Label(inner, text=titulo, font=("Segoe UI", 10, "bold"), bg=C["card"], fg=col).pack(anchor="w")
            tk.Label(inner, text=desc, font=("Segoe UI", 9), bg=C["card"],
                     fg=C["text_sec"], wraplength=520, justify="left").pack(anchor="w")

    # ── ACCIONES DOCENTE ──────────────────────────────────────────────────────
    def registrar_nota(self):
        # Solo estudiantes de las asignaturas del docente
        mis_cursos = [c for c in self.cursos_lista if c.docente_email == self.current_user.email]
        if not self.estudiantes_lista:
            self._mostrar_error("No hay estudiantes registrados"); return
        v = self._crear_ventana_secundaria("Registrar nota", 520, 420)
        body = tk.Frame(v, bg=C["bg"], padx=20, pady=14); body.pack(fill="both", expand=True)

        tk.Label(body, text="Estudiante:", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        est_v = tk.StringVar()
        vals = [f"{e.nombre} {e.apellido} ({e.matricula})" for e in self.estudiantes_lista]
        ttk.Combobox(body, textvariable=est_v, values=vals, width=50).pack(ipady=3, pady=(2, 10), fill="x")

        tk.Label(body, text="Asignatura:", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        asig_cb = ttk.Combobox(body, values=[a.nombre for a in self.asignaturas_lista], width=50)
        asig_cb.pack(ipady=3, pady=(2, 10), fill="x")

        tk.Label(body, text="Nota (0 – 10):", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        nota_sb = ttk.Spinbox(body, from_=0, to=10, increment=0.1, width=10)
        nota_sb.pack(anchor="w", ipady=3, pady=(2, 8))

        tk.Label(body, text="Observación (opcional):", font=("Segoe UI", 10, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(anchor="w")
        obs_e = ttk.Entry(body, width=50); obs_e.pack(ipady=3, pady=(2, 14), fill="x")

        def guardar():
            sel = est_v.get()
            if not sel: self._mostrar_error("Seleccione un estudiante"); return
            if not asig_cb.get(): self._mostrar_error("Seleccione una asignatura"); return
            try:
                nota_val = float(nota_sb.get())
                if not 0 <= nota_val <= 10: raise ValueError
            except ValueError:
                self._mostrar_error("Nota debe ser un número entre 0 y 10"); return
            matricula = sel.split("(")[-1].replace(")", "")
            est = next((e for e in self.estudiantes_lista if e.matricula == matricula), None)
            if not est: self._mostrar_error("Estudiante no encontrado"); return
            calif = Calificacion(est, asig_cb.get(), nota_val, obs_e.get().strip())
            calif.asignar_nota(self.current_user)
            self.calificaciones.append(calif)
            self.repo.guardar_calificaciones()
            self._mostrar_info(f"✅ Nota {nota_val} registrada para {est.nombre}"); v.destroy()

        self._btn(body, "✔ Registrar nota", C["success"], guardar, pady=8).pack(fill="x")

    def ver_calificaciones_docente(self):
        v = self._crear_ventana_secundaria("Calificaciones registradas", 700, 480)
        body = tk.Frame(v, bg=C["bg"], padx=12, pady=8); body.pack(fill="both", expand=True)
        cols = ("Estudiante", "Asignatura", "Nota", "Estado", "Observación")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=14)
        for col in cols: tree.heading(col, text=col)
        tree.column("Estudiante", width=180); tree.column("Asignatura", width=180)
        tree.column("Nota", width=60); tree.column("Estado", width=90)
        sb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True); sb.pack(side="left", fill="y")
        for c in self.calificaciones:
            est = f"{c.estudiante.nombre} {c.estudiante.apellido}"
            estado = "Aprobado" if c.nota >= 7.0 else "Reprobado"
            tree.insert("", "end", values=(est, c.asignatura, f"{c.nota:.1f}", estado, c.observacion))

    def crear_tarea(self):
        v = self._crear_ventana_secundaria("Crear tarea", 520, 440)
        body = tk.Frame(v, bg=C["bg"], padx=20, pady=14); body.pack(fill="both", expand=True)

        tk.Label(body, text="Título:", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        titulo_e = ttk.Entry(body, width=52); titulo_e.pack(ipady=4, pady=(2, 10), fill="x")

        tk.Label(body, text="Descripción:", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        desc_t = tk.Text(body, height=4, font=("Segoe UI", 10)); desc_t.pack(pady=(2, 10), fill="x")

        tk.Label(body, text="Fecha límite (YYYY-MM-DD):", font=("Segoe UI", 10, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(anchor="w")
        fecha_e = ttk.Entry(body, width=30); fecha_e.pack(ipady=4, pady=(2, 10), fill="x")

        # Vincular a asignatura (para control de acceso)
        tk.Label(body, text="Asignatura (opcional – filtra quién puede verla):",
                 font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        asig_v = tk.StringVar()
        asig_vals = ["Todas las asignaturas"] + [f"{a.nombre} ({a.id})" for a in self.asignaturas_lista]
        asig_cb = ttk.Combobox(body, textvariable=asig_v, values=asig_vals, width=52)
        asig_cb.current(0); asig_cb.pack(ipady=3, pady=(2, 14), fill="x")

        def guardar():
            titulo = titulo_e.get().strip()
            if not titulo: self._mostrar_error("El título es obligatorio"); return
            fecha = fecha_e.get().strip()
            if fecha and not self._validar_fecha(fecha):
                self._mostrar_error("Formato de fecha inválido. Use YYYY-MM-DD"); return
            nuevo_id = max((t.id or 0 for t in self.tareas), default=0) + 1
            asig_sel = asig_v.get()
            asig_id = None
            if asig_sel and asig_sel != "Todas las asignaturas":
                try: asig_id = int(asig_sel.split("(")[-1].rstrip(")"))
                except ValueError: pass
            tarea = Tarea(titulo, desc_t.get("1.0", tk.END).strip(), fecha,
                          self.current_user.email, nuevo_id, [], asig_id)
            self.tareas.append(tarea)
            self.repo.guardar_tareas()
            self._mostrar_info("✅ Tarea creada"); v.destroy()

        self._btn(body, "➕ Crear tarea", C["accent"], guardar, pady=8).pack(fill="x")

    def mis_cursos_docente(self):
        cursos = [c for c in self.cursos_lista if c.docente_email == self.current_user.email]
        if not cursos:
            self._mostrar_info("No tiene cursos asignados actualmente."); return
        v = self._crear_ventana_secundaria("Mis Cursos", 640, 440)
        body = tk.Frame(v, bg=C["bg"], padx=16, pady=12); body.pack(fill="both", expand=True)
        COLS = [C["sidebar"], C["accent"], C["success"]]
        for i, curso in enumerate(cursos):
            col = COLS[i % len(COLS)]
            card = tk.Frame(body, bg=C["card"], bd=1, relief="solid"); card.pack(fill="x", pady=6)
            tk.Frame(card, bg=col, width=6).pack(side="left", fill="y")
            inner = tk.Frame(card, bg=C["card"], padx=12, pady=10)
            inner.pack(side="left", fill="both", expand=True)
            tk.Label(inner, text=curso.nombre, font=("Segoe UI", 11, "bold"),
                     bg=C["card"], fg=col).pack(anchor="w")
            h = str(curso.horario) if curso.horario else "Sin horario"
            m = curso.modalidad.nombre if curso.modalidad else "Sin modalidad"
            tk.Label(inner, text=f"🕐 {h}  |  📡 {m}  |  🏫 {curso.carrera or 'General'}",
                     font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(anchor="w")
            # Tareas del docente
            mis_tareas = [t for t in self.tareas if t.creador_email == self.current_user.email]
            tk.Label(inner, text=f"📋 {len(mis_tareas)} tareas creadas",
                     font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(anchor="w")

    def show_entregas(self, parent):
        body = tk.Frame(parent, bg=C["bg"]); body.pack(fill="both", expand=True, padx=10, pady=10)
        # Solo entregas de tareas del docente actual
        cols = ("Tarea", "Estudiante", "Carrera", "Descripción", "Archivo", "Fecha", "Estado")
        tree = ttk.Treeview(body, columns=cols, show="headings")
        for col in cols: tree.heading(col, text=col); tree.column(col, width=120)
        tree.column("Tarea", width=160); tree.column("Descripción", width=180)
        sb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")

        mis_tareas = [t for t in self.tareas if t.creador_email == self.current_user.email]
        for tarea in mis_tareas:
            for entrega in tarea.entregas:
                est = self.usuarios.get(entrega.get("estudiante_email"))
                est_txt = f"{est.nombre} {est.apellido}" if est else entrega.get("estudiante_email", "")
                carrera = est.carrera if est and hasattr(est, "carrera") else ""
                tree.insert("", "end", values=(
                    tarea.titulo, est_txt, carrera,
                    entrega.get("descripcion", ""), entrega.get("archivo", ""),
                    entrega.get("fecha", ""), entrega.get("estado", "Realizada")
                ))

    def subir_tarea(self, tarea):
        v = self._crear_ventana_secundaria("Entregar tarea", 520, 380)
        body = tk.Frame(v, bg=C["bg"], padx=20, pady=14); body.pack(fill="both", expand=True)
        tk.Label(body, text=f"Tarea: {tarea.titulo}", font=("Segoe UI", 11, "bold"),
                 bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", pady=(0, 6))
        tk.Label(body, text=tarea.descripcion or "Sin descripción", font=("Segoe UI", 9),
                 bg=C["bg"], fg=C["text_sec"], wraplength=460).pack(anchor="w", pady=(0, 10))

        tk.Label(body, text="Descripción de tu entrega:", font=("Segoe UI", 10, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(anchor="w")
        desc_t = tk.Text(body, height=4, font=("Segoe UI", 10)); desc_t.pack(pady=(2, 10), fill="x")

        tk.Label(body, text="Archivo (opcional):", font=("Segoe UI", 10, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(anchor="w")
        fila = tk.Frame(body, bg=C["bg"]); fila.pack(fill="x", pady=(2, 10))
        archivo_v = tk.StringVar()
        ttk.Entry(fila, textvariable=archivo_v, width=42).pack(side="left", ipady=4)
        self._btn(fila, "📂 Buscar", C["accent2"],
                  lambda: archivo_v.set(filedialog.askopenfilename()),
                  padx=8, pady=3).pack(side="left", padx=8)

        def guardar():
            if self._tarea_entregada(tarea):
                self._mostrar_info("Esta tarea ya fue entregada"); v.destroy(); return
            tarea.agregar_entrega(self.current_user.email, archivo_v.get(),
                                  datetime.now().strftime("%Y-%m-%d %H:%M"),
                                  desc_t.get("1.0", tk.END).strip())
            self.repo.guardar_tareas()
            self._mostrar_info("✅ ¡Tarea entregada exitosamente!")
            v.destroy()

        self._btn(body, "⬆ Entregar tarea", C["success"], guardar, pady=8).pack(fill="x", pady=8)

    # ── ACCIONES ADMINISTRADOR ────────────────────────────────────────────────
    def crear_usuario(self):
        v = self._crear_ventana_secundaria("Crear usuario", 440, 540)
        body = tk.Frame(v, bg=C["bg"], padx=18, pady=14); body.pack(fill="both", expand=True)
        fields = {}
        for lbl, key, show in [("Nombre:", "nombre", ""), ("Apellido:", "apellido", ""),
                                ("Email:", "email", ""), ("Contraseña:", "password", "●")]:
            tk.Label(body, text=lbl, font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
            e = ttk.Entry(body, width=48, show=show); e.pack(ipady=4, pady=(2, 8), fill="x")
            fields[key] = e

        tk.Label(body, text="Rol:", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        rol_cb = ttk.Combobox(body, values=["estudiante", "docente", "coordinador", "administrador"], width=46)
        rol_cb.pack(ipady=3, pady=(2, 14), fill="x")

        def guardar():
            nombre = fields["nombre"].get().strip(); apellido = fields["apellido"].get().strip()
            email = fields["email"].get().strip(); pwd = fields["password"].get(); rol = rol_cb.get()
            if not all([nombre, apellido, email, pwd, rol]):
                self._mostrar_error("Todos los campos son obligatorios"); return
            if not self._validar_email(email):
                self._mostrar_error("Email inválido"); return
            if email in self.usuarios:
                self._mostrar_error("El email ya está registrado"); return
            if rol == "estudiante":
                matricula = simpledialog.askstring("Matrícula", "Ingrese matrícula:")
                carrera = simpledialog.askstring("Carrera", "Ingrese carrera/área de nivelación:")
                if not matricula or not carrera: return
                nuevo = Estudiante(nombre, apellido, email, pwd, matricula, carrera)
                self.estudiantes_lista.append(nuevo)
                self.repo.guardar_estudiantes()
            elif rol == "docente":
                esp = simpledialog.askstring("Especialidad", "Ingrese especialidad:")
                if not esp: return
                nuevo = Docente(nombre, apellido, email, pwd, esp)
                self.docentes_lista.append(nuevo)
                self.repo.guardar_docentes()
            elif rol == "coordinador":
                nuevo = Coordinador(nombre, apellido, email, pwd)
                self.repo.guardar_coordinadores()
            else:
                nuevo = Administrador(nombre, apellido, email, pwd)
                self.repo.guardar_administradores()
            self.usuarios[nuevo.email] = nuevo
            self._mostrar_info(f"✅ Usuario {email} creado"); v.destroy()

        self._btn(body, "✔ Crear usuario", C["success"], guardar, pady=8).pack(fill="x")

    def eliminar_usuario(self):
        emails = [e for e in self.usuarios if self.usuarios[e] != self.current_user]
        if not emails:
            self._mostrar_info("No hay usuarios para eliminar"); return
        v = self._crear_ventana_secundaria("Eliminar usuario", 500, 400)
        body = tk.Frame(v, bg=C["bg"], padx=14, pady=10); body.pack(fill="both", expand=True)
        tk.Label(body, text="Seleccione el usuario a eliminar:",
                 font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w", pady=(0, 8))
        lb = tk.Listbox(body, font=("Segoe UI", 10), height=12,
                        bg=C["white"], fg=C["text"], selectbackground=C["accent"])
        for email in emails:
            u = self.usuarios[email]
            lb.insert(tk.END, f"{u.nombre} {u.apellido}  <{email}>  [{u.obtener_rol()}]")
        lb.pack(fill="both", expand=True, pady=6)

        def confirmar():
            sel = lb.curselection()
            if not sel: self._mostrar_error("Seleccione un usuario"); return
            email = emails[sel[0]]
            if messagebox.askyesno("Confirmar", f"¿Eliminar usuario {email}?"):
                del self.usuarios[email]
                self.estudiantes_lista[:] = [e for e in self.estudiantes_lista if e.email != email]
                self.docentes_lista[:] = [d for d in self.docentes_lista if d.email != email]
                self.repo.guardar_estudiantes(); self.repo.guardar_docentes()
                self.repo.guardar_administradores(); self.repo.guardar_coordinadores()
                self._mostrar_info(f"✅ Usuario {email} eliminado"); v.destroy()

        self._btn(body, "🗑 Eliminar", C["danger"], confirmar, pady=8).pack(fill="x", pady=8)

    def manage_users(self, parent=None):
        self._tab_usuarios_admin(parent or tk.Toplevel(self.root))

    def ver_logs(self):
        v = self._crear_ventana_secundaria("Logs", 620, 400)
        self._tab_logs_admin(tk.Frame(v, bg=C["bg"]))

    def show_config(self, parent=None):
        pass

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    repo = RepositorioAcademico()
    app = SistemaAcademicoApp(repo)
    app.run()

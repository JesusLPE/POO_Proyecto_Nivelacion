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
from models.reporte import Reporte
from repositories.repositorio_academico import RepositorioAcademico

# ═══════════════════════════════════════════════════════════
#  PALETA DE COLORES
# ═══════════════════════════════════════════════════════════
C = {
    "bg":        "#F0F4F8",   # fondo principal
    "sidebar":   "#1A237E",   # azul oscuro lateral
    "sidebar2":  "#283593",   # azul medio
    "accent":    "#3949AB",   # botones principales
    "accent2":   "#5C6BC0",   # botones secundarios
    "success":   "#2E7D32",   # verde
    "danger":    "#C62828",   # rojo
    "warning":   "#E65100",   # naranja
    "white":     "#FFFFFF",
    "card":      "#FFFFFF",
    "text":      "#212121",
    "text_sec":  "#546E7A",
    "border":    "#CFD8DC",
    "header_bg": "#E8EAF6",
}

ROL_COLORES = {
    "estudiante":    "#1565C0",
    "docente":       "#2E7D32",
    "coordinador":   "#6A1B9A",
    "administrador": "#BF360C",
}


def aplicar_estilo():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TFrame",       background=C["bg"])
    style.configure("TLabel",       background=C["bg"],  foreground=C["text"])
    style.configure("TNotebook",    background=C["bg"])
    style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=[12, 6])
    style.configure("Treeview",      background=C["white"], fieldbackground=C["white"],
                                     foreground=C["text"], rowheight=26, font=("Segoe UI", 9))
    style.configure("Treeview.Heading", background=C["header_bg"], foreground=C["text"],
                                        font=("Segoe UI", 9, "bold"))
    style.map("Treeview", background=[("selected", C["accent2"])])

    # Botones principales
    style.configure("Primary.TButton", background=C["accent"], foreground=C["white"],
                    font=("Segoe UI", 10, "bold"), padding=[10, 6], relief="flat")
    style.map("Primary.TButton",
              background=[("active", C["accent2"]), ("pressed", C["sidebar"])])

    # Botones peligrosos
    style.configure("Danger.TButton", background=C["danger"], foreground=C["white"],
                    font=("Segoe UI", 10, "bold"), padding=[10, 6], relief="flat")
    style.map("Danger.TButton", background=[("active", "#D32F2F")])

    # Botones éxito
    style.configure("Success.TButton", background=C["success"], foreground=C["white"],
                    font=("Segoe UI", 10, "bold"), padding=[10, 6], relief="flat")
    style.map("Success.TButton", background=[("active", "#388E3C")])

    # Botones warning
    style.configure("Warning.TButton", background=C["warning"], foreground=C["white"],
                    font=("Segoe UI", 10, "bold"), padding=[10, 6], relief="flat")
    style.map("Warning.TButton", background=[("active", "#EF6C00")])

    # Entradas
    style.configure("TEntry", fieldbackground=C["white"], foreground=C["text"],
                    padding=6, font=("Segoe UI", 10))
    style.configure("TCombobox", fieldbackground=C["white"], foreground=C["text"],
                    font=("Segoe UI", 10))
    style.configure("TSpinbox", fieldbackground=C["white"], foreground=C["text"],
                    font=("Segoe UI", 10))

    # Card
    style.configure("Card.TFrame", background=C["card"], relief="solid", borderwidth=1)

    return style


class SistemaAcademicoApp:

    def __init__(self, repositorio: RepositorioAcademico):
        self.root = tk.Tk()
        self.root.title("Sistema de Gestión Académica")
        self.root.state("zoomed")
        self.root.configure(bg=C["bg"])
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        aplicar_estilo()

        # ── Inyección de dependencia ──────────────────────────
        self.repo = repositorio
        self.usuarios         = repositorio.usuarios
        self.estudiantes_lista = repositorio.estudiantes
        self.docentes_lista    = repositorio.docentes
        self.asignaturas_lista = repositorio.asignaturas
        self.cursos_lista      = repositorio.cursos
        self.matriculas_lista  = repositorio.matriculas
        self.tareas    = []
        self.entregas  = []
        self.current_user = None

        self.show_login()

    # ══════════════════════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════════════════════
    def _crear_ventana_secundaria(self, titulo, ancho=520, alto=420):
        v = tk.Toplevel(self.root)
        v.title(titulo)
        v.geometry(f"{ancho}x{alto}")
        v.configure(bg=C["bg"])
        v.transient(self.root)
        v.grab_set()
        v.resizable(True, True)
        # Barra de título coloreada
        header = tk.Frame(v, bg=C["sidebar"], height=40)
        header.pack(fill="x")
        tk.Label(header, text=titulo, bg=C["sidebar"], fg=C["white"],
                 font=("Segoe UI", 11, "bold")).pack(side="left", padx=14, pady=8)
        return v

    def _validar_email(self, email):
        return "@" in email and "." in email and len(email) > 5

    def _mostrar_error(self, msg):
        messagebox.showerror("Error", msg, parent=self.root)

    def _mostrar_info(self, msg):
        messagebox.showinfo("Información", msg, parent=self.root)

    def _lbl(self, parent, text, **kw):
        return tk.Label(parent, text=text, bg=kw.pop("bg", C["bg"]),
                        fg=kw.pop("fg", C["text"]), font=kw.pop("font", ("Segoe UI", 10)), **kw)

    def _sep(self, parent):
        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=6)

    def _validar_fecha(self, fecha_str):
        try:
            datetime.strptime(fecha_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    # ══════════════════════════════════════════════════════════
    #  LOGIN
    # ══════════════════════════════════════════════════════════
    def show_login(self):
        for w in self.root.winfo_children():
            w.destroy()

        # Fondo dividido
        left = tk.Frame(self.root, bg=C["sidebar"], width=420)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        right = tk.Frame(self.root, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True)

        # Panel izquierdo – branding
        tk.Frame(left, bg=C["sidebar"]).pack(expand=True)
        tk.Label(left, text="🎓", font=("Segoe UI", 60), bg=C["sidebar"], fg=C["white"]).pack(pady=(0, 10))
        tk.Label(left, text="AulaVirtual", font=("Segoe UI", 26, "bold"),
                 bg=C["sidebar"], fg=C["white"]).pack()
        tk.Label(left, text="Sistema de Gestión Académica",
                 font=("Segoe UI", 11), bg=C["sidebar"], fg="#9FA8DA").pack(pady=4)
        tk.Frame(left, bg=C["sidebar"]).pack(expand=True)
        tk.Label(left, text="© 2024 – Proyecto POO", font=("Segoe UI", 9),
                 bg=C["sidebar"], fg="#7986CB").pack(pady=10)

        # Panel derecho – formulario
        form = tk.Frame(right, bg=C["bg"])
        form.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(form, text="Iniciar Sesión", font=("Segoe UI", 22, "bold"),
                 bg=C["bg"], fg=C["sidebar"]).pack(pady=(0, 6))
        tk.Label(form, text="Ingrese sus credenciales para continuar",
                 font=("Segoe UI", 10), bg=C["bg"], fg=C["text_sec"]).pack(pady=(0, 24))

        # Email
        tk.Label(form, text="Correo electrónico", font=("Segoe UI", 10, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(anchor="w")
        self.email_entry = ttk.Entry(form, width=36, font=("Segoe UI", 11))
        self.email_entry.pack(ipady=4, pady=(2, 14), fill="x")

        # Contraseña
        tk.Label(form, text="Contraseña", font=("Segoe UI", 10, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(anchor="w")
        self.pass_entry = ttk.Entry(form, width=36, show="●", font=("Segoe UI", 11))
        self.pass_entry.pack(ipady=4, pady=(2, 24), fill="x")
        self.pass_entry.bind("<Return>", lambda e: self.do_login())

        btn = tk.Button(form, text="Ingresar →", bg=C["accent"], fg=C["white"],
                        font=("Segoe UI", 12, "bold"), relief="flat", cursor="hand2",
                        padx=20, pady=10, command=self.do_login)
        btn.pack(fill="x")

        self.email_entry.focus()

    def do_login(self):
        email = self.email_entry.get().strip()
        password = self.pass_entry.get()
        if not email or not password:
            self._mostrar_error("Ingrese email y contraseña")
            return
        user = self.usuarios.get(email)
        if user and user.iniciarSesion(email, password):
            self.current_user = user
            self.show_main_panel()
        else:
            self._mostrar_error("Credenciales incorrectas")

    # ══════════════════════════════════════════════════════════
    #  PANEL PRINCIPAL
    # ══════════════════════════════════════════════════════════
    def show_main_panel(self):
        for w in self.root.winfo_children():
            w.destroy()

        u = self.current_user
        rol = u.obtener_rol()
        color_rol = ROL_COLORES.get(rol, C["accent"])

        # ── Barra superior ──────────────────────────────────
        topbar = tk.Frame(self.root, bg=color_rol, height=56)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="🎓  AulaVirtual", font=("Segoe UI", 14, "bold"),
                 bg=color_rol, fg=C["white"]).pack(side="left", padx=18)

        tk.Button(topbar, text="⏻  Cerrar sesión", bg=color_rol, fg=C["white"],
                  font=("Segoe UI", 10), relief="flat", cursor="hand2",
                  activebackground=C["sidebar"], activeforeground=C["white"],
                  command=self.cerrar_sesion).pack(side="right", padx=14, pady=10)

        # Badge rol
        badge = tk.Label(topbar,
                         text=f"  {rol.upper()}  ",
                         bg=C["white"], fg=color_rol,
                         font=("Segoe UI", 9, "bold"), relief="flat", padx=6, pady=2)
        badge.pack(side="right", padx=4, pady=14)

        tk.Label(topbar, text=f"{u.nombre} {u.apellido}",
                 font=("Segoe UI", 11), bg=color_rol, fg=C["white"]).pack(side="right", padx=6)

        # ── Cuerpo ───────────────────────────────────────────
        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True)

        if rol == "estudiante":
            self.panel_estudiante(body)
        elif rol == "docente":
            self.panel_docente(body)
        elif rol == "coordinador":
            self.panel_coordinador(body)
        elif rol == "administrador":
            self.panel_administrador(body)

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión", "¿Está seguro de que desea salir?"):
            self.current_user = None
            self.show_login()

    # ══════════════════════════════════════════════════════════
    #  PANEL ESTUDIANTE
    # ══════════════════════════════════════════════════════════
    def panel_estudiante(self, parent):
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        f1 = ttk.Frame(nb); nb.add(f1, text="  📅 Actividades  ")
        self.show_timeline(f1, "estudiante")

        f2 = ttk.Frame(nb); nb.add(f2, text="  📚 Mis Cursos  ")
        self.show_cursos(f2)

        f3 = ttk.Frame(nb); nb.add(f3, text="  👤 Mi Perfil  ")
        self.show_perfil(f3)

        f4 = ttk.Frame(nb); nb.add(f4, text="  🔬 Conceptos POO  ")
        self.show_poo_demo(f4)

    # ══════════════════════════════════════════════════════════
    #  PANEL DOCENTE
    # ══════════════════════════════════════════════════════════
    def panel_docente(self, parent):
        main = tk.Frame(parent, bg=C["bg"])
        main.pack(fill="both", expand=True, padx=10, pady=10)

        left = tk.LabelFrame(main, text="  📅 Línea de tiempo  ",
                              bg=C["bg"], font=("Segoe UI", 10, "bold"), fg=C["sidebar"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.show_timeline(left, "docente")

        right = tk.Frame(main, bg=C["card"], bd=1, relief="solid")
        right.pack(side="right", fill="y", padx=(6, 0), ipadx=10, ipady=10)

        tk.Label(right, text="Acciones rápidas", font=("Segoe UI", 12, "bold"),
                 bg=C["card"], fg=C["sidebar"]).pack(pady=(12, 8), padx=14)
        ttk.Separator(right).pack(fill="x", padx=8)

        botones = [
            ("📝  Registrar nota",     C["success"],  self.registrar_nota),
            ("📋  Crear tarea",        C["accent"],   self.crear_tarea),
            ("📂  Ver entregas",       C["accent2"],  self.ver_entregas_ventana),
            ("🎓  Mis cursos",         C["sidebar2"], self.mis_cursos_docente),
            ("👤  Mi Perfil",          C["text_sec"], lambda: self._ventana_con(self.show_perfil, "Mi Perfil")),
            ("🔬  Conceptos POO",      C["text_sec"], lambda: self._ventana_con(self.show_poo_demo, "Conceptos POO")),
        ]
        for txt, color, cmd in botones:
            b = tk.Button(right, text=txt, bg=color, fg=C["white"],
                          font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                          padx=12, pady=7, width=22, anchor="w", command=cmd)
            b.pack(pady=4, padx=14)

    def _ventana_con(self, metodo, titulo, ancho=500, alto=400):
        v = self._crear_ventana_secundaria(titulo, ancho, alto)
        metodo(v)

    def ver_entregas_ventana(self):
        v = self._crear_ventana_secundaria("Entregas de estudiantes", 750, 500)
        self.show_entregas(v)

    # ══════════════════════════════════════════════════════════
    #  PANEL COORDINADOR
    # ══════════════════════════════════════════════════════════
    def panel_coordinador(self, parent):
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        f1 = ttk.Frame(nb); nb.add(f1, text="  📅 Actividades  ")
        self.show_timeline(f1, "coordinador")

        f2 = ttk.Frame(nb); nb.add(f2, text="  ⚡ Acciones  ")
        self._coord_acciones(f2)

        f3 = ttk.Frame(nb); nb.add(f3, text="  👤 Mi Perfil  ")
        self.show_perfil(f3)

        f4 = ttk.Frame(nb); nb.add(f4, text="  🔬 Conceptos POO  ")
        self.show_poo_demo(f4)

    def _coord_acciones(self, parent):
        wrap = tk.Frame(parent, bg=C["bg"])
        wrap.pack(expand=True, pady=40)

        tk.Label(wrap, text="Gestión Académica", font=("Segoe UI", 14, "bold"),
                 bg=C["bg"], fg=C["sidebar"]).pack(pady=(0, 20))

        items = [
            ("🎓  Gestionar Cursos",            C["sidebar"],  self.gestionar_cursos),
            ("👨‍🏫  Asignar docente a asignatura", C["accent"],   self.asignar_docente_asignatura),
            ("🕐  Gestionar horarios",           C["success"],  self.gestionar_horarios),
            ("📂  Ver entregas de tareas",       C["accent2"],  self.ver_entregas_ventana),
        ]
        for txt, color, cmd in items:
            b = tk.Button(wrap, text=txt, bg=color, fg=C["white"],
                          font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                          padx=16, pady=10, width=34, anchor="w", command=cmd)
            b.pack(pady=6)

    # ══════════════════════════════════════════════════════════
    #  PANEL ADMINISTRADOR
    # ══════════════════════════════════════════════════════════
    def panel_administrador(self, parent):
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        f1 = ttk.Frame(nb); nb.add(f1, text="  📅 Actividades  ")
        self.show_timeline(f1, "administrador")

        f2 = ttk.Frame(nb); nb.add(f2, text="  ⚙️ Administración  ")
        self._admin_acciones(f2)

        f3 = ttk.Frame(nb); nb.add(f3, text="  👤 Mi Perfil  ")
        self.show_perfil(f3)

        f4 = ttk.Frame(nb); nb.add(f4, text="  🔬 Conceptos POO  ")
        self.show_poo_demo(f4)

    def _admin_acciones(self, parent):
        wrap = tk.Frame(parent, bg=C["bg"])
        wrap.pack(expand=True, pady=40)

        tk.Label(wrap, text="Panel de Administración", font=("Segoe UI", 14, "bold"),
                 bg=C["bg"], fg=ROL_COLORES["administrador"]).pack(pady=(0, 20))

        items = [
            ("➕  Crear usuario",          C["success"],                 self.crear_usuario),
            ("🗑  Eliminar usuario",       C["danger"],                  self.eliminar_usuario),
            ("📚  Gestionar asignaturas",  C["accent"],                  self.gestionar_asignaturas),
            ("🎓  Gestionar matrículas",   C["sidebar2"],                self.gestionar_matriculas),
            ("📋  Ver usuarios",           C["text_sec"],                self.manage_users),
            ("📊  Ver logs",               C["text_sec"],                self.ver_logs),
        ]
        for txt, color, cmd in items:
            b = tk.Button(wrap, text=txt, bg=color, fg=C["white"],
                          font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                          padx=16, pady=10, width=34, anchor="w", command=cmd)
            b.pack(pady=6)

    # ══════════════════════════════════════════════════════════
    #  FUNCIONES COMPARTIDAS
    # ══════════════════════════════════════════════════════════
    def show_perfil(self, parent):
        u = self.current_user
        rol = u.obtener_rol()
        color = ROL_COLORES.get(rol, C["accent"])

        wrap = tk.Frame(parent, bg=C["bg"])
        wrap.pack(expand=True)

        # Avatar
        avatar = tk.Frame(wrap, bg=color, width=80, height=80)
        avatar.pack(pady=(20, 6))
        avatar.pack_propagate(False)
        inicial = u.nombre[0].upper() if u.nombre else "?"
        tk.Label(avatar, text=inicial, font=("Segoe UI", 30, "bold"),
                 bg=color, fg=C["white"]).place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(wrap, text=f"{u.nombre} {u.apellido}", font=("Segoe UI", 14, "bold"),
                 bg=C["bg"], fg=C["text"]).pack()
        tk.Label(wrap, text=rol.capitalize(), font=("Segoe UI", 10),
                 bg=color, fg=C["white"], padx=10, pady=2).pack(pady=4)

        card = tk.Frame(wrap, bg=C["card"], bd=1, relief="solid", padx=20, pady=14)
        card.pack(padx=30, pady=10, fill="x")

        campos = [("📧 Email", u.email), ("👤 Nombre", u.nombre), ("👤 Apellido", u.apellido)]
        if hasattr(u, "matricula"):   campos.append(("🎫 Matrícula", u.matricula))
        if hasattr(u, "carrera"):     campos.append(("🏫 Carrera", u.carrera))
        if hasattr(u, "especialidad"): campos.append(("🔬 Especialidad", u.especialidad))

        for label, valor in campos:
            row = tk.Frame(card, bg=C["card"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=("Segoe UI", 10, "bold"),
                     bg=C["card"], fg=C["text_sec"], width=16, anchor="w").pack(side="left")
            tk.Label(row, text=valor, font=("Segoe UI", 10),
                     bg=C["card"], fg=C["text"]).pack(side="left", padx=8)

    def show_timeline(self, parent, rol):
        main = tk.Frame(parent, bg=C["bg"])
        main.pack(fill="both", expand=True)

        canvas = tk.Canvas(main, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=C["bg"])

        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)

        canvas.bind("<Configure>", lambda e: canvas.itemconfig(1, width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        actividades = self._get_actividades(rol)
        CARD_COLORS = [C["sidebar"], C["accent"], C["success"], C["warning"]]

        for i, act in enumerate(actividades):
            col = CARD_COLORS[i % len(CARD_COLORS)]
            outer = tk.Frame(sf, bg=col, pady=2)
            outer.pack(fill="x", pady=6, padx=12)

            card = tk.Frame(outer, bg=C["card"], padx=14, pady=10)
            card.pack(fill="x", padx=2, pady=0)

            # Línea de color izquierda
            tk.Frame(card, bg=col, width=5).pack(side="left", fill="y")
            content = tk.Frame(card, bg=C["card"])
            content.pack(side="left", fill="both", expand=True, padx=10)

            tk.Label(content, text=act["fecha"], font=("Segoe UI", 8, "bold"),
                     bg=C["card"], fg=col).pack(anchor="w")
            tk.Label(content, text=act["titulo"], font=("Segoe UI", 10, "bold"),
                     bg=C["card"], fg=C["text"]).pack(anchor="w", pady=(3, 1))
            tk.Label(content, text=act["descripcion"], font=("Segoe UI", 9),
                     bg=C["card"], fg=C["text_sec"], wraplength=500, justify="left").pack(anchor="w")

            if act.get("boton_texto") and act.get("boton_comando"):
                b = tk.Button(content, text=act["boton_texto"], bg=col, fg=C["white"],
                              font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                              padx=8, pady=3, command=act["boton_comando"])
                b.pack(anchor="e", pady=(6, 0))

    def _get_actividades(self, rol):
        if rol == "estudiante":
            return [
                {"fecha": "Vencimiento: Viernes 22 mayo – 23:00",
                 "titulo": "📄 Proyecto Final – Diseño de Algoritmos",
                 "descripcion": "Entregar documentación y código fuente",
                 "boton_texto": "Agregar entrega", "boton_comando": self.subir_tarea},
                {"fecha": "Sábado 23 mayo – 00:59",
                 "titulo": "📄 Entrega de Avance – Estructuras de Datos",
                 "descripcion": "Implementar árboles binarios",
                 "boton_texto": "Agregar entrega", "boton_comando": self.subir_tarea},
                {"fecha": "Martes 26 mayo – 21:53",
                 "titulo": "💬 Debate: Ética en la Inteligencia Artificial",
                 "descripcion": "Foro obligatorio – Participación mínima 3 intervenciones",
                 "boton_texto": "Ver foro", "boton_comando": lambda: self._mostrar_info("Acceso al foro")},
                {"fecha": "Próximos 30 días",
                 "titulo": "📅 Calendario de exámenes",
                 "descripcion": "Consulta las fechas de parciales y finales",
                 "boton_texto": "Ver más", "boton_comando": lambda: self._mostrar_info("Exámenes: 10/06, 20/06, 30/06")},
            ]
        elif rol == "docente":
            return [
                {"fecha": "Hoy – 18:00",
                 "titulo": "📬 Entregas por calificar",
                 "descripcion": "3 estudiantes han subido la tarea 'Algoritmos de ordenamiento'",
                 "boton_texto": "Calificar", "boton_comando": self.ver_entregas_ventana},
                {"fecha": "Mañana – 10:00",
                 "titulo": "📡 Clase: Recursividad",
                 "descripcion": "Curso Diseño de Algoritmos – Preparar ejemplos",
                 "boton_texto": "Ver detalles", "boton_comando": lambda: self._mostrar_info("Clase virtual a las 10:00")},
                {"fecha": "2024-05-30",
                 "titulo": "⏰ Cierre de notas",
                 "descripcion": "Plazo para registrar notas del primer corte",
                 "boton_texto": "Registrar notas", "boton_comando": self.registrar_nota},
            ]
        elif rol == "coordinador":
            return [
                {"fecha": "⚠ Urgente",
                 "titulo": "🚫 Asignatura sin docente",
                 "descripcion": "Bases de Datos Avanzadas no tiene docente asignado",
                 "boton_texto": "Asignar", "boton_comando": self.asignar_docente_asignatura},
                {"fecha": "Pendiente",
                 "titulo": "📋 Matrículas por aprobar",
                 "descripcion": "3 solicitudes de matrícula en espera",
                 "boton_texto": "Revisar", "boton_comando": self.gestionar_matriculas},
                {"fecha": "Próxima semana",
                 "titulo": "📆 Reunión de coordinación",
                 "descripcion": "Planificación del siguiente ciclo",
                 "boton_texto": "Confirmar", "boton_comando": lambda: self._mostrar_info("Asistencia confirmada")},
            ]
        elif rol == "administrador":
            return [
                {"fecha": "2024-05-21",
                 "titulo": "🆕 Nuevo usuario registrado",
                 "descripcion": "Laura Méndez (Docente) se ha unido al sistema",
                 "boton_texto": "Ver usuarios", "boton_comando": self.manage_users},
                {"fecha": "Ayer",
                 "titulo": "📊 Reporte de accesos generado",
                 "descripcion": "Se exportó reporte de logs del mes",
                 "boton_texto": "Ver logs", "boton_comando": self.ver_logs},
                {"fecha": "Configuración pendiente",
                 "titulo": "⚙️ Actualizar parámetros del sistema",
                 "descripcion": "Cambiar período académico",
                 "boton_texto": "Configurar", "boton_comando": self.show_config},
            ]
        return []

    def show_poo_demo(self, parent):
        wrap = tk.Frame(parent, bg=C["bg"])
        wrap.pack(fill="both", expand=True, padx=14, pady=10)

        tk.Label(wrap, text="Conceptos de Programación Orientada a Objetos",
                 font=("Segoe UI", 12, "bold"), bg=C["bg"], fg=C["sidebar"]).pack(pady=(0, 8))

        conceptos = [
            ("🔗 Herencia",           "Estudiante, Docente, Coordinador y Administrador heredan de Persona."),
            ("🔄 Polimorfismo",       "obtener_rol() retorna diferentes valores según el objeto instanciado."),
            ("🔒 Abstracción",        "Persona y Evaluacion son clases abstractas (no instanciables directamente)."),
            ("📦 Encapsulamiento",    "Atributos privados __nombre, __email protegidos con @property y @setter."),
            ("⬆️ super()",            "Los constructores de clases hijas llaman super().__init__() para inicializar Persona."),
            ("🧮 Sobrecarga",         "calcularPromedio(n1, n2, n3=0) acepta 2 o 3 notas con argumento opcional."),
            ("🌐 Herencia múltiple",  "Persona hereda de ABC (clase abstracta) y de IniciarSesion (interfaz)."),
            ("📜 Interfaz",           "IniciarSesion define el contrato: iniciarSesion(), cerrarSesion(), _verificarCuenta()."),
            ("💉 Inyección dep.",     "RepositorioAcademico se inyecta en SistemaAcademicoApp(repo)."),
            ("🗄 Repository Pattern","JsonManager y RepositorioAcademico separan la lógica de acceso a datos."),
        ]

        canvas = tk.Canvas(wrap, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=C["bg"])
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(1, width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        COLORS = [C["sidebar"], C["accent"], C["success"], C["warning"], C["sidebar2"],
                  C["accent2"], C["danger"], C["sidebar"], C["accent"], C["success"]]
        for i, (titulo, desc) in enumerate(conceptos):
            col = COLORS[i]
            card = tk.Frame(sf, bg=C["card"], bd=1, relief="solid")
            card.pack(fill="x", pady=4, padx=4)
            stripe = tk.Frame(card, bg=col, width=6)
            stripe.pack(side="left", fill="y")
            inner = tk.Frame(card, bg=C["card"], padx=12, pady=8)
            inner.pack(side="left", fill="both", expand=True)
            tk.Label(inner, text=titulo, font=("Segoe UI", 10, "bold"),
                     bg=C["card"], fg=col).pack(anchor="w")
            tk.Label(inner, text=desc, font=("Segoe UI", 9), bg=C["card"],
                     fg=C["text_sec"], wraplength=500, justify="left").pack(anchor="w")

    def show_cursos(self, parent):
        wrap = tk.Frame(parent, bg=C["bg"])
        wrap.pack(fill="both", expand=True, padx=14, pady=10)

        tk.Label(wrap, text="Mis Cursos Matriculados", font=("Segoe UI", 12, "bold"),
                 bg=C["bg"], fg=C["sidebar"]).pack(pady=(0, 10))

        if not self.cursos_lista:
            tk.Label(wrap, text="No hay cursos disponibles.", font=("Segoe UI", 10),
                     bg=C["bg"], fg=C["text_sec"]).pack()
            return

        COLORS = [C["sidebar"], C["accent"], C["success"]]
        for i, curso in enumerate(self.cursos_lista):
            col = COLORS[i % len(COLORS)]
            card = tk.Frame(wrap, bg=C["card"], bd=1, relief="solid")
            card.pack(fill="x", pady=6, padx=4)
            stripe = tk.Frame(card, bg=col, width=8)
            stripe.pack(side="left", fill="y")
            inner = tk.Frame(card, bg=C["card"], padx=14, pady=10)
            inner.pack(side="left", fill="both", expand=True)
            tk.Label(inner, text=curso.nombre, font=("Segoe UI", 11, "bold"),
                     bg=C["card"], fg=col).pack(anchor="w")
            horario = str(curso.horario) if curso.horario else "Sin horario"
            modalidad = str(curso.modalidad) if curso.modalidad else "Sin modalidad"
            tk.Label(inner, text=f"🕐 {horario}  |  📡 {modalidad}",
                     font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(anchor="w", pady=2)

    # ══════════════════════════════════════════════════════════
    #  ESTUDIANTE – acciones
    # ══════════════════════════════════════════════════════════
    def subir_tarea(self):
        v = self._crear_ventana_secundaria("Subir tarea", 520, 420)
        body = tk.Frame(v, bg=C["bg"], padx=20, pady=14)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Título:", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        titulo_e = ttk.Entry(body, width=55); titulo_e.pack(ipady=4, pady=(2, 10), fill="x")

        tk.Label(body, text="Descripción:", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        desc_t = tk.Text(body, height=5, font=("Segoe UI", 10)); desc_t.pack(pady=(2, 10), fill="x")

        tk.Label(body, text="Archivo (opcional):", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        fila = tk.Frame(body, bg=C["bg"]); fila.pack(fill="x", pady=(2, 10))
        archivo_v = tk.StringVar()
        ttk.Entry(fila, textvariable=archivo_v, width=42).pack(side="left", ipady=4)
        tk.Button(fila, text="📂 Buscar", bg=C["accent2"], fg=C["white"],
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=lambda: archivo_v.set(filedialog.askopenfilename())
                  ).pack(side="left", padx=8)

        def guardar():
            titulo = titulo_e.get().strip()
            if not titulo:
                self._mostrar_error("El título es obligatorio"); return
            t = Tarea(titulo, desc_t.get("1.0", tk.END).strip(),
                      datetime.now().strftime("%Y-%m-%d"), self.current_user.email)
            self.tareas.append(t)
            self.entregas.append({"tarea": t, "estudiante": self.current_user,
                                  "archivo": archivo_v.get(),
                                  "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")})
            self._mostrar_info("¡Tarea subida exitosamente!")
            v.destroy()

        tk.Button(body, text="⬆  Subir tarea", bg=C["success"], fg=C["white"],
                  font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                  pady=8, command=guardar).pack(fill="x", pady=8)

    # ══════════════════════════════════════════════════════════
    #  DOCENTE – acciones
    # ══════════════════════════════════════════════════════════
    def registrar_nota(self):
        if not self.estudiantes_lista:
            self._mostrar_error("No hay estudiantes registrados"); return
        v = self._crear_ventana_secundaria("Registrar nota", 500, 380)
        body = tk.Frame(v, bg=C["bg"], padx=20, pady=14)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Estudiante:", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        est_v = tk.StringVar()
        vals = [f"{e.nombre} {e.apellido} ({e.matricula})" for e in self.estudiantes_lista]
        ttk.Combobox(body, textvariable=est_v, values=vals, width=48).pack(ipady=3, pady=(2, 10), fill="x")

        tk.Label(body, text="Asignatura:", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        asig_cb = ttk.Combobox(body, values=[a.nombre for a in self.asignaturas_lista], width=48)
        asig_cb.pack(ipady=3, pady=(2, 10), fill="x")

        tk.Label(body, text="Nota (0 – 20):", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        nota_sb = ttk.Spinbox(body, from_=0, to=20, increment=0.1, width=10)
        nota_sb.pack(anchor="w", ipady=3, pady=(2, 14))

        def guardar():
            sel = est_v.get()
            if not sel: self._mostrar_error("Seleccione un estudiante"); return
            try:
                nota_val = float(nota_sb.get())
                if not 0 <= nota_val <= 20: raise ValueError
            except ValueError:
                self._mostrar_error("Nota debe ser un número entre 0 y 20"); return
            matricula = sel.split("(")[-1].replace(")", "")
            est = next((e for e in self.estudiantes_lista if e.matricula == matricula), None)
            if est:
                Calificacion(est, asig_cb.get(), nota_val).asignar_nota(self.current_user)
                self._mostrar_info(f"✅ Nota {nota_val} registrada para {est.nombre}")
                v.destroy()
            else:
                self._mostrar_error("Estudiante no encontrado")

        tk.Button(body, text="✔ Registrar nota", bg=C["success"], fg=C["white"],
                  font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                  pady=8, command=guardar).pack(fill="x")

    def crear_tarea(self):
        v = self._crear_ventana_secundaria("Crear tarea", 500, 380)
        body = tk.Frame(v, bg=C["bg"], padx=20, pady=14)
        body.pack(fill="both", expand=True)

        for lbl, entry_ref_name, is_text in [
            ("Título:", "titulo_e", False),
            ("Descripción:", "desc_t", True),
            ("Fecha límite (YYYY-MM-DD):", "fecha_e", False),
        ]:
            tk.Label(body, text=lbl, font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
            if is_text:
                w = tk.Text(body, height=4, font=("Segoe UI", 10)); w.pack(pady=(2, 10), fill="x")
            else:
                w = ttk.Entry(body, width=50); w.pack(ipady=4, pady=(2, 10), fill="x")
            setattr(v, entry_ref_name, w)

        def guardar():
            titulo = v.titulo_e.get().strip()
            if not titulo: self._mostrar_error("El título es obligatorio"); return
            fecha = v.fecha_e.get().strip()
            if fecha and not self._validar_fecha(fecha):
                self._mostrar_error("Formato de fecha inválido. Use YYYY-MM-DD"); return
            tarea = Tarea(titulo, v.desc_t.get("1.0", tk.END).strip(), fecha, self.current_user.email)
            self.tareas.append(tarea)
            self._mostrar_info("✅ Tarea creada")
            v.destroy()

        tk.Button(body, text="➕ Crear tarea", bg=C["accent"], fg=C["white"],
                  font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                  pady=8, command=guardar).pack(fill="x")

    def mis_cursos_docente(self):
        cursos = [c for c in self.cursos_lista if c.docente_email == self.current_user.email]
        if not cursos:
            self._mostrar_info("No tiene cursos asignados actualmente.")
            return
        v = self._crear_ventana_secundaria("Mis Cursos", 600, 400)
        body = tk.Frame(v, bg=C["bg"], padx=16, pady=12)
        body.pack(fill="both", expand=True)
        for curso in cursos:
            col = C["sidebar"]
            card = tk.Frame(body, bg=C["card"], bd=1, relief="solid")
            card.pack(fill="x", pady=6)
            tk.Frame(card, bg=col, width=6).pack(side="left", fill="y")
            inner = tk.Frame(card, bg=C["card"], padx=12, pady=10)
            inner.pack(side="left", fill="both", expand=True)
            tk.Label(inner, text=curso.nombre, font=("Segoe UI", 11, "bold"),
                     bg=C["card"], fg=col).pack(anchor="w")
            h = str(curso.horario) if curso.horario else "Sin horario"
            m = str(curso.modalidad) if curso.modalidad else "Sin modalidad"
            tk.Label(inner, text=f"🕐 {h}  |  📡 {m}", font=("Segoe UI", 9),
                     bg=C["card"], fg=C["text_sec"]).pack(anchor="w")

    def show_entregas(self, parent):
        body = tk.Frame(parent, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=10, pady=10)

        tree = ttk.Treeview(body, columns=("Tarea", "Estudiante", "Archivo", "Fecha"), show="headings")
        for col in ("Tarea", "Estudiante", "Archivo", "Fecha"):
            tree.heading(col, text=col)
            tree.column(col, width=160)
        sb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        for e in self.entregas:
            tree.insert("", "end", values=(
                e["tarea"].titulo,
                f"{e['estudiante'].nombre} {e['estudiante'].apellido}",
                e["archivo"], e["fecha"]
            ))

    # ══════════════════════════════════════════════════════════
    #  COORDINADOR – acciones
    # ══════════════════════════════════════════════════════════
    def gestionar_cursos(self):
        v = self._crear_ventana_secundaria("Gestión de Cursos", 820, 560)
        body = tk.Frame(v, bg=C["bg"], padx=14, pady=10)
        body.pack(fill="both", expand=True)

        # Treeview
        cols = ("ID", "Nombre", "Duración", "Horario", "Modalidad", "Docente")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=12)
        widths = [40, 220, 80, 160, 100, 180]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w)
        sb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")

        def refrescar():
            for i in tree.get_children(): tree.delete(i)
            for c in self.cursos_lista:
                h = str(c.horario) if c.horario else ""
                m = c.modalidad.nombre if c.modalidad else ""
                d_email = c.docente_email or "Sin asignar"
                docente_obj = self.usuarios.get(d_email)
                d_nombre = f"{docente_obj.nombre} {docente_obj.apellido}" if docente_obj else d_email
                tree.insert("", "end", values=(c.id, c.nombre, f"{c._duracion_semanas}s", h, m, d_nombre))
        refrescar()

        # Botones
        btn_frame = tk.Frame(body, bg=C["bg"], padx=8)
        btn_frame.pack(side="left", fill="y", padx=(10, 0))

        def nuevo_curso():
            vn = self._crear_ventana_secundaria("Nuevo Curso", 440, 360)
            bf = tk.Frame(vn, bg=C["bg"], padx=18, pady=12)
            bf.pack(fill="both", expand=True)
            campos = {}
            for lbl, key in [("Nombre:", "nombre"), ("Duración (semanas):", "dur"),
                              ("Total horas:", "horas"), ("Horario (ej. Lunes 18:00-20:00):", "horario"),
                              ("Modalidad:", "modalidad")]:
                tk.Label(bf, text=lbl, font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
                e = ttk.Entry(bf, width=46); e.pack(ipady=3, pady=(1, 7), fill="x")
                campos[key] = e

            # Docente selector
            tk.Label(bf, text="Docente:", font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
            d_vals = ["Sin asignar"] + [f"{d.nombre} {d.apellido} ({d.email})" for d in self.docentes_lista]
            d_cb = ttk.Combobox(bf, values=d_vals, width=44)
            d_cb.current(0); d_cb.pack(ipady=3, pady=(1, 7), fill="x")

            def guardar_curso():
                nombre = campos["nombre"].get().strip()
                if not nombre: self._mostrar_error("El nombre es obligatorio"); return
                try:
                    dur = int(campos["dur"].get()); horas = int(campos["horas"].get())
                except ValueError:
                    self._mostrar_error("Duración y horas deben ser enteros"); return
                nuevo_id = max((c.id for c in self.cursos_lista), default=0) + 1
                curso = Curso(nuevo_id, nombre, dur, horas)
                horario_str = campos["horario"].get().strip()
                if horario_str:
                    ps = horario_str.split()
                    dia = ps[0]; rango = ps[1] if len(ps) > 1 else ""
                    ini, fin = (rango.split("-") + [""])[:2]
                    curso.asignar_horario(Horario(nuevo_id, dia, ini, fin))
                mod_str = campos["modalidad"].get().strip()
                if mod_str:
                    curso.asignar_modalidad(Modalidad(nuevo_id, mod_str, "", True))
                sel_d = d_cb.get()
                if sel_d and sel_d != "Sin asignar":
                    email = sel_d.split("(")[-1].rstrip(")")
                    curso.docente_email = email
                self.cursos_lista.append(curso)
                self.repo.guardar_cursos()
                refrescar()
                self._mostrar_info("✅ Curso creado")
                vn.destroy()

            tk.Button(bf, text="✔ Crear curso", bg=C["success"], fg=C["white"],
                      font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                      pady=7, command=guardar_curso).pack(fill="x", pady=6)

        def asignar_docente():
            sel = tree.selection()
            if not sel: self._mostrar_error("Seleccione un curso"); return
            item = tree.item(sel[0])
            curso_id = item["values"][0]
            curso = next((c for c in self.cursos_lista if c.id == curso_id), None)
            if not curso: return

            vd = self._crear_ventana_secundaria("Asignar Docente", 400, 220)
            bf = tk.Frame(vd, bg=C["bg"], padx=18, pady=18)
            bf.pack(fill="both", expand=True)
            tk.Label(bf, text=f"Curso: {curso.nombre}", font=("Segoe UI", 10, "bold"),
                     bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", pady=(0, 10))
            tk.Label(bf, text="Seleccionar docente:", font=("Segoe UI", 10, "bold"),
                     bg=C["bg"], fg=C["text"]).pack(anchor="w")
            d_vals = [f"{d.nombre} {d.apellido} ({d.email})" for d in self.docentes_lista]
            d_cb = ttk.Combobox(bf, values=d_vals, width=44)
            d_cb.pack(ipady=3, pady=(2, 12), fill="x")
            # Pre-seleccionar si ya tiene docente
            if curso.docente_email:
                actual = next((d for d in self.docentes_lista if d.email == curso.docente_email), None)
                if actual:
                    idx = next((i for i, d in enumerate(self.docentes_lista)
                                if d.email == curso.docente_email), None)
                    if idx is not None: d_cb.current(idx)

            def confirmar():
                sel_d = d_cb.get()
                if not sel_d: self._mostrar_error("Seleccione un docente"); return
                email = sel_d.split("(")[-1].rstrip(")")
                curso.docente_email = email
                self.repo.guardar_cursos()
                refrescar()
                self._mostrar_info("✅ Docente asignado")
                vd.destroy()

            tk.Button(bf, text="✔ Confirmar", bg=C["success"], fg=C["white"],
                      font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                      pady=7, command=confirmar).pack(fill="x")

        def eliminar_curso():
            sel = tree.selection()
            if not sel: self._mostrar_error("Seleccione un curso"); return
            item = tree.item(sel[0])
            curso_id = item["values"][0]
            if messagebox.askyesno("Confirmar", f"¿Eliminar el curso ID {curso_id}?"):
                self.cursos_lista[:] = [c for c in self.cursos_lista if c.id != curso_id]
                self.repo.guardar_cursos()
                refrescar()
                self._mostrar_info("Curso eliminado")

        for txt, col, cmd in [
            ("➕ Nuevo curso",        C["success"],  nuevo_curso),
            ("👨‍🏫 Asignar docente",   C["accent"],   asignar_docente),
            ("🗑 Eliminar curso",     C["danger"],   eliminar_curso),
            ("🔄 Refrescar",          C["text_sec"], refrescar),
        ]:
            tk.Button(btn_frame, text=txt, bg=col, fg=C["white"],
                      font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                      padx=8, pady=8, width=18, anchor="w", command=cmd).pack(pady=5)

    def asignar_docente_asignatura(self):
        if not self.docentes_lista:
            self._mostrar_error("No hay docentes registrados"); return
        v = self._crear_ventana_secundaria("Asignar docente a asignatura", 420, 240)
        body = tk.Frame(v, bg=C["bg"], padx=18, pady=14)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Docente:", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        d_v = tk.StringVar()
        ttk.Combobox(body, textvariable=d_v,
                     values=[f"{d.nombre} {d.apellido} ({d.email})" for d in self.docentes_lista],
                     width=46).pack(ipady=3, pady=(2, 10), fill="x")

        tk.Label(body, text="Asignatura:", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        a_v = tk.StringVar()
        ttk.Combobox(body, textvariable=a_v,
                     values=[a.nombre for a in self.asignaturas_lista],
                     width=46).pack(ipady=3, pady=(2, 14), fill="x")

        def asignar():
            if not d_v.get() or not a_v.get():
                self._mostrar_error("Seleccione docente y asignatura"); return
            self._mostrar_info(f"✅ {d_v.get().split(' (')[0]} asignado a {a_v.get()}")
            v.destroy()

        tk.Button(body, text="✔ Asignar", bg=C["accent"], fg=C["white"],
                  font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                  pady=8, command=asignar).pack(fill="x")

    def gestionar_horarios(self):
        v = self._crear_ventana_secundaria("Gestión de horarios y modalidades", 600, 400)
        body = tk.Frame(v, bg=C["bg"], padx=12, pady=8)
        body.pack(fill="both", expand=True)

        if not self.cursos_lista:
            tk.Label(body, text="No hay cursos disponibles.", bg=C["bg"], fg=C["text_sec"],
                     font=("Segoe UI", 10)).pack(pady=20)
            return

        for curso in self.cursos_lista:
            card = tk.Frame(body, bg=C["card"], bd=1, relief="solid")
            card.pack(fill="x", pady=6)
            tk.Frame(card, bg=C["accent"], width=6).pack(side="left", fill="y")
            inner = tk.Frame(card, bg=C["card"], padx=12, pady=8)
            inner.pack(side="left", fill="both", expand=True)
            tk.Label(inner, text=curso.nombre, font=("Segoe UI", 10, "bold"),
                     bg=C["card"], fg=C["sidebar"]).pack(anchor="w")
            h = str(curso.horario) if curso.horario else "Sin horario"
            m = curso.modalidad.nombre if curso.modalidad else "Sin modalidad"
            tk.Label(inner, text=f"🕐 {h}  |  📡 {m}", font=("Segoe UI", 9),
                     bg=C["card"], fg=C["text_sec"]).pack(anchor="w", pady=2)
            btns = tk.Frame(inner, bg=C["card"]); btns.pack(anchor="w", pady=4)
            tk.Button(btns, text="✏ Horario", bg=C["accent2"], fg=C["white"],
                      font=("Segoe UI", 9), relief="flat", cursor="hand2", padx=8, pady=3,
                      command=lambda c=curso: self.editar_horario(c)).pack(side="left", padx=4)
            tk.Button(btns, text="✏ Modalidad", bg=C["success"], fg=C["white"],
                      font=("Segoe UI", 9), relief="flat", cursor="hand2", padx=8, pady=3,
                      command=lambda c=curso: self.editar_modalidad(c)).pack(side="left", padx=4)

    def editar_horario(self, curso):
        nuevo = simpledialog.askstring("Editar horario",
                                       f"Nuevo horario para {curso.nombre}\nEjemplo: Lunes 18:00-20:00")
        if nuevo:
            ps = nuevo.split()
            dia = ps[0] if ps else ""
            rango = ps[1] if len(ps) > 1 else ""
            ini, fin = (rango.split("-") + [""])[:2]
            curso.asignar_horario(Horario(curso.id, dia, ini, fin))
            self.repo.guardar_cursos()
            self._mostrar_info(f"✅ Horario actualizado: {nuevo}")

    def editar_modalidad(self, curso):
        nueva = simpledialog.askstring("Editar modalidad",
                                       "Nueva modalidad (Presencial / Virtual / Híbrida):")
        if nueva:
            curso.asignar_modalidad(Modalidad(curso.id, nueva, "", True))
            self.repo.guardar_cursos()
            self._mostrar_info(f"✅ Modalidad actualizada: {nueva}")

    # ══════════════════════════════════════════════════════════
    #  ADMINISTRADOR – acciones
    # ══════════════════════════════════════════════════════════
    def gestionar_asignaturas(self):
        v = self._crear_ventana_secundaria("Gestión de Asignaturas", 780, 520)
        body = tk.Frame(v, bg=C["bg"], padx=12, pady=8)
        body.pack(fill="both", expand=True)

        cols = ("ID", "Nombre", "Horas", "Créditos", "Estado")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=12)
        for col in cols: tree.heading(col, text=col)
        tree.column("ID", width=40); tree.column("Nombre", width=260)
        sb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="top", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def refrescar():
            for i in tree.get_children(): tree.delete(i)
            for a in self.asignaturas_lista:
                tree.insert("", "end", values=(a.id, a.nombre, a.horas, a.creditos, a.estado))
        refrescar()

        form = tk.Frame(body, bg=C["bg"])
        form.pack(fill="x", pady=8)
        fields = {}
        for lbl, key, w in [("Nombre:", "nombre", 18), ("Horas:", "horas", 6), ("Créditos:", "cred", 6)]:
            tk.Label(form, text=lbl, font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(side="left", padx=4)
            e = ttk.Entry(form, width=w); e.pack(side="left", padx=2, ipady=3)
            fields[key] = e

        def agregar():
            nombre = fields["nombre"].get().strip()
            if not nombre: self._mostrar_error("Ingrese el nombre"); return
            try:
                horas = int(fields["horas"].get()); cred = int(fields["cred"].get())
            except ValueError:
                self._mostrar_error("Horas y créditos deben ser enteros"); return
            nuevo_id = max((a.id for a in self.asignaturas_lista), default=0) + 1
            self.asignaturas_lista.append(Asignatura(nuevo_id, nombre, horas, cred, "Activa"))
            self.repo.guardar_asignaturas()
            refrescar()
            for f in fields.values(): f.delete(0, tk.END)
            self._mostrar_info("✅ Asignatura creada")

        def eliminar():
            sel = tree.selection()
            if not sel: return
            id_asi = tree.item(sel[0])["values"][0]
            if messagebox.askyesno("Confirmar", "¿Eliminar esta asignatura?"):
                self.asignaturas_lista[:] = [a for a in self.asignaturas_lista if a.id != id_asi]
                self.repo.guardar_asignaturas()
                refrescar()

        tk.Button(form, text="➕ Agregar", bg=C["success"], fg=C["white"],
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  padx=8, pady=4, command=agregar).pack(side="left", padx=8)
        tk.Button(form, text="🗑 Eliminar sel.", bg=C["danger"], fg=C["white"],
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  padx=8, pady=4, command=eliminar).pack(side="left", padx=4)

    def gestionar_matriculas(self):
        v = self._crear_ventana_secundaria("Gestión de Matrículas", 780, 520)
        body = tk.Frame(v, bg=C["bg"], padx=12, pady=8)
        body.pack(fill="both", expand=True)

        cols = ("ID", "Estudiante", "Fecha", "Tipo", "Estado")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=12)
        for col in cols: tree.heading(col, text=col)
        sb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="top", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def refrescar():
            for i in tree.get_children(): tree.delete(i)
            for m in self.matriculas_lista:
                est = f"{m.estudiante.nombre} {m.estudiante.apellido}" if m.estudiante else "N/A"
                tree.insert("", "end", values=(m.id, est, m.fecha, m.tipo, m.estado))
        refrescar()

        form = tk.Frame(body, bg=C["bg"])
        form.pack(fill="x", pady=8)

        # Crear nueva matrícula
        tk.Label(form, text="Estudiante:", font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(side="left", padx=4)
        est_v = tk.StringVar()
        ttk.Combobox(form, textvariable=est_v,
                     values=[f"{e.nombre} {e.apellido} ({e.matricula})" for e in self.estudiantes_lista],
                     width=28).pack(side="left", padx=4, ipady=3)

        tk.Label(form, text="Tipo:", font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text"]).pack(side="left", padx=4)
        tipo_v = tk.StringVar(value="Regular")
        ttk.Combobox(form, textvariable=tipo_v, values=["Regular", "Segunda"], width=10).pack(side="left", padx=2, ipady=3)

        def nueva_matricula():
            sel = est_v.get()
            if not sel: self._mostrar_error("Seleccione un estudiante"); return
            mat_cod = sel.split("(")[-1].rstrip(")")
            est = next((e for e in self.estudiantes_lista if e.matricula == mat_cod), None)
            if not est: self._mostrar_error("Estudiante no encontrado"); return
            nuevo_id = max((m.id for m in self.matriculas_lista), default=0) + 1
            m = Matricula(nuevo_id, datetime.now().strftime("%Y-%m-%d"),
                          tipo_v.get(), "Activa", tipo_v.get() == "Segunda", est)
            self.matriculas_lista.append(m)
            self.repo.guardar_matriculas()
            refrescar()
            self._mostrar_info("✅ Matrícula registrada")

        def cambiar_estado():
            sel = tree.selection()
            if not sel: self._mostrar_error("Seleccione una matrícula"); return
            id_mat = tree.item(sel[0])["values"][0]
            nuevo = simpledialog.askstring("Cambiar estado", "Nuevo estado (Activa / Anulada / Pendiente):")
            if nuevo:
                for m in self.matriculas_lista:
                    if m.id == id_mat: m.estado = nuevo; break
                self.repo.guardar_matriculas()
                refrescar()

        tk.Button(form, text="➕ Matricular", bg=C["success"], fg=C["white"],
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  padx=8, pady=4, command=nueva_matricula).pack(side="left", padx=8)
        tk.Button(form, text="✏ Cambiar estado", bg=C["warning"], fg=C["white"],
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  padx=8, pady=4, command=cambiar_estado).pack(side="left", padx=4)

    def manage_users(self, parent=None):
        v = self._crear_ventana_secundaria("Usuarios del sistema", 640, 440)
        body = tk.Frame(v, bg=C["bg"], padx=12, pady=8)
        body.pack(fill="both", expand=True)

        cols = ("Email", "Nombre", "Rol")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=14)
        for col in cols: tree.heading(col, text=col)
        tree.column("Email", width=220); tree.column("Nombre", width=200); tree.column("Rol", width=120)
        sb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")

        def refrescar():
            for i in tree.get_children(): tree.delete(i)
            for u in self.usuarios.values():
                tree.insert("", "end", values=(u.email, f"{u.nombre} {u.apellido}", u.obtener_rol()))
        refrescar()
        tk.Button(body, text="🔄 Refrescar", bg=C["text_sec"], fg=C["white"],
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  padx=8, pady=4, command=refrescar).pack(pady=8)

    def crear_usuario(self):
        v = self._crear_ventana_secundaria("Crear usuario", 420, 500)
        body = tk.Frame(v, bg=C["bg"], padx=18, pady=14)
        body.pack(fill="both", expand=True)

        fields = {}
        for lbl, key, show in [("Nombre:", "nombre", ""), ("Apellido:", "apellido", ""),
                                 ("Email:", "email", ""), ("Contraseña:", "password", "●")]:
            tk.Label(body, text=lbl, font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
            e = ttk.Entry(body, width=46, show=show); e.pack(ipady=4, pady=(2, 8), fill="x")
            fields[key] = e

        tk.Label(body, text="Rol:", font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        rol_cb = ttk.Combobox(body, values=["estudiante", "docente", "coordinador", "administrador"], width=44)
        rol_cb.pack(ipady=3, pady=(2, 14), fill="x")

        def guardar():
            nombre = fields["nombre"].get().strip()
            apellido = fields["apellido"].get().strip()
            email = fields["email"].get().strip()
            password = fields["password"].get()
            rol = rol_cb.get()
            if not all([nombre, apellido, email, password, rol]):
                self._mostrar_error("Todos los campos son obligatorios"); return
            if not self._validar_email(email):
                self._mostrar_error("Email inválido"); return
            if email in self.usuarios:
                self._mostrar_error("El email ya está registrado"); return

            if rol == "estudiante":
                matricula = simpledialog.askstring("Matrícula", "Ingrese matrícula:")
                carrera = simpledialog.askstring("Carrera", "Ingrese carrera:")
                if not matricula or not carrera: return
                nuevo = Estudiante(nombre, apellido, email, password, matricula, carrera)
                self.estudiantes_lista.append(nuevo)
                self.repo.guardar_estudiantes()
            elif rol == "docente":
                esp = simpledialog.askstring("Especialidad", "Ingrese especialidad:")
                if not esp: return
                nuevo = Docente(nombre, apellido, email, password, esp)
                self.docentes_lista.append(nuevo)
                self.repo.guardar_docentes()
            elif rol == "coordinador":
                nuevo = Coordinador(nombre, apellido, email, password)
                self.repo.guardar_coordinadores()
            else:
                nuevo = Administrador(nombre, apellido, email, password)
                self.repo.guardar_administradores()

            self.usuarios[nuevo.email] = nuevo
            self._mostrar_info(f"✅ Usuario {email} creado")
            v.destroy()

        tk.Button(body, text="✔ Crear usuario", bg=C["success"], fg=C["white"],
                  font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                  pady=8, command=guardar).pack(fill="x")

    def eliminar_usuario(self):
        emails = [e for e in self.usuarios.keys() if self.usuarios[e] != self.current_user]
        if not emails:
            self._mostrar_info("No hay usuarios para eliminar"); return

        v = self._crear_ventana_secundaria("Eliminar usuario", 480, 380)
        body = tk.Frame(v, bg=C["bg"], padx=14, pady=10)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Seleccione el usuario a eliminar:",
                 font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w", pady=(0, 8))

        listbox = tk.Listbox(body, font=("Segoe UI", 10), height=10,
                             bg=C["white"], fg=C["text"], selectbackground=C["accent"])
        for email in emails:
            u = self.usuarios[email]
            listbox.insert(tk.END, f"{u.nombre} {u.apellido}  <{email}>  [{u.obtener_rol()}]")
        listbox.pack(fill="both", expand=True, pady=6)

        def confirmar():
            sel = listbox.curselection()
            if not sel: self._mostrar_error("Seleccione un usuario"); return
            email = emails[sel[0]]
            if messagebox.askyesno("Confirmar", f"¿Eliminar usuario {email}?"):
                del self.usuarios[email]
                self.estudiantes_lista[:] = [e for e in self.estudiantes_lista if e.email != email]
                self.docentes_lista[:] = [d for d in self.docentes_lista if d.email != email]
                self.repo.guardar_estudiantes()
                self.repo.guardar_docentes()
                self.repo.guardar_administradores()
                self.repo.guardar_coordinadores()
                self._mostrar_info(f"✅ Usuario {email} eliminado")
                v.destroy()

        tk.Button(body, text="🗑 Eliminar", bg=C["danger"], fg=C["white"],
                  font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                  pady=8, command=confirmar).pack(fill="x", pady=8)

    def ver_logs(self):
        v = self._crear_ventana_secundaria("Logs del sistema", 600, 400)
        body = tk.Frame(v, bg=C["bg"], padx=12, pady=8)
        body.pack(fill="both", expand=True)
        txt = tk.Text(body, font=("Consolas", 9), bg="#1E1E1E", fg="#DCDCDC",
                      insertbackground="white", wrap="word")
        txt.pack(fill="both", expand=True)
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logs = f"""[{ahora}] INFO  – Sistema iniciado
[{ahora}] INFO  – Usuario {self.current_user.email} autenticado (rol: {self.current_user.obtener_rol()})
[{ahora}] INFO  – Cargados {len(self.estudiantes_lista)} estudiantes desde JSON
[{ahora}] INFO  – Cargados {len(self.docentes_lista)} docentes desde JSON
[{ahora}] INFO  – Cargados {len(self.cursos_lista)} cursos desde JSON
[{ahora}] INFO  – Cargadas {len(self.asignaturas_lista)} asignaturas desde JSON
[{ahora}] INFO  – Cargadas {len(self.matriculas_lista)} matrículas desde JSON
[{ahora}] INFO  – RepositorioAcademico → SistemaAcademicoApp (inyección de dependencia)
"""
        txt.insert("1.0", logs)
        txt.config(state="disabled")

    def show_config(self, parent=None):
        v = self._crear_ventana_secundaria("Configuración", 420, 260)
        body = tk.Frame(v, bg=C["bg"], padx=18, pady=14)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Configuración del sistema", font=("Segoe UI", 12, "bold"),
                 bg=C["bg"], fg=C["sidebar"]).pack(pady=(0, 14))
        for txt, col, cmd in [
            ("🎨 Cambiar tema",     C["accent"],   lambda: self._mostrar_info("Tema cambiado (simulación)")),
            ("💾 Respaldar datos",  C["success"],  lambda: self._mostrar_info("Respaldo completado (simulación)")),
            ("📤 Exportar JSON",    C["sidebar2"], lambda: self._mostrar_info("Datos exportados")),
        ]:
            tk.Button(body, text=txt, bg=col, fg=C["white"],
                      font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                      pady=8, command=cmd).pack(fill="x", pady=5)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    repo = RepositorioAcademico()
    app = SistemaAcademicoApp(repo)
    app.run()

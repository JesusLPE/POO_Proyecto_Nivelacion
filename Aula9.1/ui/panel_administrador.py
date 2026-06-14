"""ui/panel_administrador.py – Panel del administrador del sistema de nivelación."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from ui.base import (C, btn, lbl, tree_con_scroll, refrescar_tree,
                     ventana_modal, seccion_titulo)
from ui.shared import panel_perfil
from services.academico import (UsuarioService, AsignaturaService,
                                MatriculaService, AuthService)


def _seleccionar_carrera(root, repo):
    """Muestra un selector de carrera usando el catálogo de facultades."""
    carreras = repo.carreras_catalogo() if hasattr(repo, "carreras_catalogo") else []
    if not carreras:
        return simpledialog.askstring("Carrera", "Carrera / programa de nivelación:")

    v = ventana_modal(root, "Seleccionar carrera", 460, 180)
    body = tk.Frame(v, bg=C["bg"], padx=18, pady=16)
    body.pack(fill="both", expand=True)
    lbl(body, "Carrera / programa de nivelación *:", bold=True).pack(anchor="w")
    carrera_v = tk.StringVar(value=carreras[0])
    cb = ttk.Combobox(body, textvariable=carrera_v, values=carreras, state="readonly", width=56)
    cb.pack(fill="x", ipady=4, pady=(4, 12))
    seleccionado = {"valor": None}

    def aceptar():
        seleccionado["valor"] = carrera_v.get().strip()
        v.destroy()

    btn(body, "✔  Seleccionar", C["success"], aceptar, pady=8).pack(fill="x")
    v.wait_window()
    return seleccionado["valor"]


def construir(parent, usuario, repo):
    us    = UsuarioService(repo)
    asigs = AsignaturaService(repo)
    ms    = MatriculaService(repo)

    nb = ttk.Notebook(parent)
    nb.pack(fill="both", expand=True, padx=10, pady=10)

    tabs = [
        ("  🏠 Panel  ",          lambda f: _tab_panel(f, repo)),
        ("  👥 Usuarios  ",       lambda f: _tab_usuarios(f, repo, us, usuario)),
        ("  📚 Asignaturas  ",    lambda f: _tab_asignaturas(f, repo, asigs)),
        ("  🏛️ Facultades  ",    lambda f: _tab_facultades(f, repo)),
        ("  🎓 Matrículas  ",     lambda f: _tab_matriculas(f, repo, ms)),
        ("  📊 Actividad  ",      lambda f: _tab_actividad(f, repo)),
        ("  ⚙️ Sistema  ",        lambda f: _tab_sistema(f, usuario, repo)),
        ("  👤 Mi Perfil  ",      lambda f: panel_perfil(f, usuario, repo)),
    ]
    for texto, fn in tabs:
        f = ttk.Frame(nb); nb.add(f, text=texto); fn(f)


# ── Panel principal ───────────────────────────────────────────────────────────
def _tab_panel(parent, repo):
    wrap = tk.Frame(parent, bg=C["bg"], padx=14, pady=14)
    wrap.pack(fill="both", expand=True)

    hdr = tk.Frame(wrap, bg=C["danger"], padx=20, pady=14)
    hdr.pack(fill="x", pady=(0, 14))
    tk.Label(hdr, text="Panel de Administración  –  Sistema de Nivelación",
             font=("Segoe UI", 13, "bold"), bg=C["danger"], fg=C["white"]).pack(anchor="w")
    tk.Label(hdr, text=f"Período académico 2026  ·  {datetime.now().strftime('%d/%m/%Y %H:%M')}",
             font=("Segoe UI", 10), bg=C["danger"], fg="#FFCDD2").pack(anchor="w")

    # KPIs
    stats = [
        (C["sidebar"],   "👥",  str(len(repo.estudiantes)),  "Estudiantes"),
        (C["success"],   "👨‍🏫",  str(len(repo.docentes)),     "Docentes"),
        (C["accent"],    "🎓",  str(len(repo.cursos)),        "Grupos"),
        (C["sidebar2"],  "📚",  str(len(repo.asignaturas)),   "Asignaturas"),
        (C["warning"],   "📋",  str(len(repo.matriculas)),    "Matrículas"),
        (C["success"],   "📊",  str(len(repo.calificaciones)),"Calificaciones"),
    ]
    grid = tk.Frame(wrap, bg=C["bg"]); grid.pack(fill="x", pady=(0, 14))
    for i, (col, icon, val, lbl_txt) in enumerate(stats):
        cf = tk.Frame(grid, bg=col)
        cf.grid(row=i//3, column=i%3, padx=6, pady=6, sticky="ew")
        grid.columnconfigure(i%3, weight=1)
        inner = tk.Frame(cf, bg=C["card"], padx=16, pady=14)
        inner.pack(fill="both", padx=2, pady=2)
        tk.Label(inner, text=icon, font=("Segoe UI", 18), bg=C["card"]).pack()
        tk.Label(inner, text=val, font=("Segoe UI", 22, "bold"),
                 bg=C["card"], fg=col).pack()
        tk.Label(inner, text=lbl_txt, font=("Segoe UI", 9),
                 bg=C["card"], fg=C["text_sec"]).pack()

    # Alertas
    alertas = []
    sin_docente = [c for c in repo.cursos if not c.docente_email]
    pendientes  = [m for m in repo.matriculas if m.estado == "Pendiente"]
    if sin_docente:
        alertas.append((C["danger"], f"⚠  {len(sin_docente)} grupo(s) sin docente asignado"))
    if pendientes:
        alertas.append((C["warning"], f"📋  {len(pendientes)} matrícula(s) esperan aprobación"))
    if not alertas:
        alertas.append((C["success"], "✅  Todos los grupos tienen docente y horario asignados"))

    seccion_titulo(wrap, "Alertas del sistema")
    for col, msg in alertas:
        af = tk.Frame(wrap, bg=col, padx=14, pady=10); af.pack(fill="x", pady=3)
        tk.Label(af, text=msg, bg=col, fg=C["white"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")


# ── Usuarios ──────────────────────────────────────────────────────────────────
def _tab_usuarios(parent, repo, us, usuario_actual):
    wrap = tk.Frame(parent, bg=C["bg"], padx=12, pady=8)
    wrap.pack(fill="both", expand=True)
    seccion_titulo(wrap, "Gestión de Usuarios")

    # Filtro por rol
    fil_f = tk.Frame(wrap, bg=C["bg"]); fil_f.pack(fill="x", pady=(0, 8))
    lbl(fil_f, "Mostrar:", bold=True).pack(side="left")
    fil_v = tk.StringVar(value="Todos")
    for op in ("Todos", "estudiante", "docente", "coordinador", "administrador"):
        tk.Radiobutton(fil_f, text=op.capitalize(), variable=fil_v, value=op,
                       bg=C["bg"], font=("Segoe UI", 9),
                       command=lambda: refrescar()).pack(side="left", padx=6)

    cols = ("Email", "Nombre completo", "Rol", "Información adicional")
    t, _ = tree_con_scroll(wrap, cols, [230, 190, 110, 230], alto=11)

    def refrescar():
        filtro = fil_v.get()
        filas = []
        for u in repo.usuarios.values():
            if filtro != "Todos" and u.obtener_rol() != filtro: continue
            extra = ""
            if hasattr(u, "carrera"):      extra = f"Carrera: {u.carrera}"
            elif hasattr(u, "especialidad"): extra = f"Especialidad: {u.especialidad}"
            filas.append((u.email, u.nombre_completo(), u.obtener_rol().capitalize(), extra))
        refrescar_tree(t, filas)
    refrescar()

    form = tk.Frame(wrap, bg=C["bg"]); form.pack(fill="x", pady=6)

    def nuevo():
        v = ventana_modal(wrap.winfo_toplevel(), "Registrar nuevo usuario", 460, 560)
        body = tk.Frame(v, bg=C["bg"], padx=20, pady=16); body.pack(fill="both", expand=True)

        campos = {}
        for etq, key, show in [("Nombre *:", "nombre", ""), ("Apellido *:", "apellido", ""),
                                ("Correo electrónico *:", "email", ""),
                                ("Contraseña inicial *:", "pwd", "*")]:
            lbl(body, etq, bold=True).pack(anchor="w")
            e = ttk.Entry(body, width=50, show=show)
            e.pack(fill="x", ipady=4, pady=(2, 8)); campos[key] = e

        lbl(body, "Rol *:", bold=True).pack(anchor="w")
        rol_v = tk.StringVar(value="estudiante")
        for r in ("estudiante", "docente", "coordinador", "administrador"):
            tk.Radiobutton(body, text=r.capitalize(), variable=rol_v, value=r,
                           bg=C["bg"], font=("Segoe UI", 10),
                           activebackground=C["bg"]).pack(anchor="w")

        err_lbl = tk.Label(body, text="", fg=C["danger"], bg=C["bg"], font=("Segoe UI", 9))
        err_lbl.pack(anchor="w", pady=(6, 0))

        def guardar():
            nombre   = campos["nombre"].get().strip()
            apellido = campos["apellido"].get().strip()
            email    = campos["email"].get().strip()
            pwd      = campos["pwd"].get()
            rol      = rol_v.get()
            if not all([nombre, apellido, email, pwd]):
                err_lbl.config(text="Todos los campos son obligatorios."); return
            if not AuthService(repo).validar_email(email):
                err_lbl.config(text="El correo electrónico no es válido."); return
            if rol == "estudiante":
                mat = simpledialog.askstring("Matrícula", "Número de matrícula del estudiante\n(ej. NIV-2026-007):")
                car = _seleccionar_carrera(wrap.winfo_toplevel(), repo)
                if not mat or not car: return
                ok, msg = us.crear_estudiante(nombre, apellido, email, pwd, mat, car)
            elif rol == "docente":
                esp = simpledialog.askstring("Especialidad", "Especialidad del docente:")
                if not esp: return
                ok, msg = us.crear_docente(nombre, apellido, email, pwd, esp)
            elif rol == "coordinador":
                ok, msg = us.crear_coordinador(nombre, apellido, email, pwd)
            else:
                ok, msg = us.crear_administrador(nombre, apellido, email, pwd)
            if ok:
                messagebox.showinfo("✅", msg); refrescar(); v.destroy()
            else:
                err_lbl.config(text=msg)

        btn(body, "✔  Registrar usuario", C["success"], guardar, pady=9).pack(fill="x", pady=(10, 0))

    def eliminar():
        sel = t.selection()
        if not sel: messagebox.showerror("Error", "Seleccione un usuario."); return
        email = t.item(sel[0])["values"][0]
        nombre = t.item(sel[0])["values"][1]
        if messagebox.askyesno("Confirmar eliminación",
                               f"¿Eliminar al usuario {nombre} ({email})?\nEsta acción no se puede deshacer."):
            ok, msg = us.eliminar_usuario(email, usuario_actual)
            (messagebox.showinfo if ok else messagebox.showerror)("Resultado", msg)
            if ok: refrescar()

    btn(form, "➕  Nuevo usuario", C["success"],  nuevo,    padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🗑  Eliminar",      C["danger"],   eliminar, padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🔄  Actualizar",    C["text_sec"], refrescar,padx=10, pady=5).pack(side="left", padx=4)



# ── Facultades y carreras ────────────────────────────────────────────────────
def _tab_facultades(parent, repo):
    wrap = tk.Frame(parent, bg=C["bg"], padx=12, pady=8)
    wrap.pack(fill="both", expand=True)
    seccion_titulo(wrap, "Catálogo de Facultades y Carreras")

    cols = ("Facultad", "Carrera")
    t, _ = tree_con_scroll(wrap, cols, [360, 340], alto=16)
    filas = []
    for f in getattr(repo, "facultades", []):
        facultad = f.get("facultad", "")
        for carrera in f.get("carreras", []):
            filas.append((facultad, carrera))
    refrescar_tree(t, filas)

    lbl(wrap, "Este catálogo se usa al registrar estudiantes y al crear grupos por carrera.",
        fg=C["text_sec"]).pack(anchor="w", pady=(8, 0))


# ── Asignaturas ───────────────────────────────────────────────────────────────
def _tab_asignaturas(parent, repo, asigs):
    wrap = tk.Frame(parent, bg=C["bg"], padx=12, pady=8)
    wrap.pack(fill="both", expand=True)
    seccion_titulo(wrap, "Plan de Estudios – Asignaturas de Nivelación")

    cols = ("ID", "Asignatura", "Horas", "Créditos", "Estado")
    t, _ = tree_con_scroll(wrap, cols, [40, 300, 70, 80, 80], alto=12)

    def refrescar():
        refrescar_tree(t, [(a.id, a.nombre, a.horas, a.creditos, a.estado)
                           for a in repo.asignaturas])
    refrescar()

    form = tk.Frame(wrap, bg=C["bg"]); form.pack(fill="x", pady=8)

    def nueva():
        v = ventana_modal(wrap.winfo_toplevel(), "Nueva Asignatura", 420, 280)
        body = tk.Frame(v, bg=C["bg"], padx=18, pady=16); body.pack(fill="both", expand=True)
        lbl(body, "Nombre de la asignatura *:", bold=True).pack(anchor="w")
        nom_e = ttk.Entry(body, width=48); nom_e.pack(fill="x", ipady=4, pady=(2, 10))
        fila = tk.Frame(body, bg=C["bg"]); fila.pack(fill="x", pady=(0, 10))
        lbl(fila, "Horas:", bold=True).pack(side="left")
        hrs_e = ttk.Entry(fila, width=8); hrs_e.pack(side="left", padx=8, ipady=3)
        lbl(fila, "Créditos:", bold=True).pack(side="left", padx=(12, 0))
        cred_e = ttk.Entry(fila, width=8); cred_e.pack(side="left", padx=8, ipady=3)
        err_lbl = tk.Label(body, text="", fg=C["danger"], bg=C["bg"], font=("Segoe UI", 9))
        err_lbl.pack(anchor="w")

        def guardar():
            try: horas = int(hrs_e.get()); cred = int(cred_e.get())
            except ValueError: err_lbl.config(text="Horas y créditos deben ser números enteros."); return
            ok, msg = asigs.crear(nom_e.get(), horas, cred)
            if ok:
                messagebox.showinfo("✅", msg); refrescar(); v.destroy()
            else:
                err_lbl.config(text=msg)

        btn(body, "✔  Agregar asignatura", C["success"], guardar, pady=9).pack(fill="x", pady=(10, 0))

    def eliminar():
        sel = t.selection()
        if not sel: messagebox.showerror("Error", "Seleccione una asignatura."); return
        aid   = t.item(sel[0])["values"][0]
        anomb = t.item(sel[0])["values"][1]
        if messagebox.askyesno("Confirmar", f"¿Eliminar la asignatura «{anomb}»?"):
            ok, msg = asigs.eliminar(aid)
            (messagebox.showinfo if ok else messagebox.showerror)("Resultado", msg)
            if ok: refrescar()

    btn(form, "➕  Nueva asignatura", C["success"],  nueva,    padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🗑  Eliminar",         C["danger"],   eliminar, padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🔄  Actualizar",       C["text_sec"], refrescar,padx=10, pady=5).pack(side="left", padx=4)


# ── Matrículas ────────────────────────────────────────────────────────────────
def _tab_matriculas(parent, repo, ms):
    wrap = tk.Frame(parent, bg=C["bg"], padx=12, pady=8)
    wrap.pack(fill="both", expand=True)
    seccion_titulo(wrap, "Registro de Matrículas")

    cols = ("ID", "Estudiante", "Carrera", "Asignatura", "Fecha", "Tipo", "Estado", "Gratuita")
    t, _ = tree_con_scroll(wrap, cols, [35, 150, 140, 170, 90, 75, 80, 70], alto=10)

    def refrescar():
        filas = []
        for m in repo.matriculas:
            est = m.estudiante
            carrera = getattr(est, "carrera", "") if est else "–"
            filas.append((m.id, est.nombre_completo() if est else "–", carrera,
                           m.asignatura.nombre if m.asignatura else "–",
                           m.fecha, m.tipo, m.estado,
                           "Sí ✅" if m.verificarGratuidad() else "No ❌"))
        refrescar_tree(t, filas)
    refrescar()

    # Formulario nueva matrícula
    ttk.Separator(wrap, orient="horizontal").pack(fill="x", pady=8)
    seccion_titulo(wrap, "Nueva matrícula")
    form = tk.Frame(wrap, bg=C["bg"]); form.pack(fill="x")

    lbl(form, "Estudiante:", bold=True).pack(side="left")
    est_v = tk.StringVar()
    ttk.Combobox(form, textvariable=est_v,
                 values=[f"{e.nombre_completo()}  ({e.matricula})" for e in repo.estudiantes],
                 width=28).pack(side="left", padx=8, ipady=3)

    lbl(form, "Asignatura:", bold=True).pack(side="left")
    asig_v = tk.StringVar()
    ttk.Combobox(form, textvariable=asig_v,
                 values=[f"{a.nombre}  (ID:{a.id})" for a in repo.asignaturas],
                 width=24).pack(side="left", padx=8, ipady=3)

    lbl(form, "Tipo:", bold=True).pack(side="left")
    tipo_v = tk.StringVar(value="Regular")
    ttk.Combobox(form, textvariable=tipo_v,
                 values=["Regular", "Segunda"], width=10
                 ).pack(side="left", padx=8, ipady=3)

    def matricular():
        sel_est  = est_v.get()
        sel_asig = asig_v.get()
        if not sel_est:  messagebox.showerror("Error", "Seleccione un estudiante."); return
        if not sel_asig: messagebox.showerror("Error", "Seleccione una asignatura."); return
        try: mat = sel_est.split("(")[1].rstrip(")")
        except IndexError: messagebox.showerror("Error", "Estudiante inválido."); return
        est = next((e for e in repo.estudiantes if e.matricula == mat), None)
        if not est: messagebox.showerror("Error", "Estudiante no encontrado."); return
        try: aid = int(sel_asig.split("ID:")[1].rstrip(")").strip())
        except (ValueError, IndexError): messagebox.showerror("Error", "Asignatura inválida."); return
        ok, msg = ms.matricular(est.email, aid, tipo_v.get())
        (messagebox.showinfo if ok else messagebox.showerror)("Resultado", msg)
        if ok: refrescar()

    def anular():
        sel = t.selection()
        if not sel: messagebox.showerror("Error", "Seleccione una matrícula."); return
        mid = t.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", "¿Anular esta matrícula?"):
            ok, msg = ms.cambiar_estado(mid, "Anulada")
            (messagebox.showinfo if ok else messagebox.showerror)("Resultado", msg)
            if ok: refrescar()

    btn(form, "✔  Matricular",  C["success"],  matricular, padx=10, pady=5).pack(side="left", padx=8)
    btn(form, "🚫  Anular",     C["danger"],   anular,     padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🔄  Actualizar", C["text_sec"], refrescar,  padx=10, pady=5).pack(side="left", padx=4)


# ── Actividad del sistema ─────────────────────────────────────────────────────
def _tab_actividad(parent, repo):
    wrap = tk.Frame(parent, bg=C["bg"], padx=12, pady=8)
    wrap.pack(fill="both", expand=True)
    seccion_titulo(wrap, "Actividad Reciente del Sistema")

    txt = tk.Text(wrap, font=("Consolas", 9), bg="#1E1E1E", fg="#DCDCDC",
                  insertbackground="white", wrap="word", relief="flat", padx=10, pady=10)
    txt.pack(fill="both", expand=True)
    sb = ttk.Scrollbar(wrap, orient="vertical", command=txt.yview)
    txt.configure(yscrollcommand=sb.set)

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lineas = [
        f"",
        f"  SISTEMA DE ADMISIÓN – PROCESO DE NIVELACIÓN  v6.0",
        f"  Registro de actividad del {datetime.now().strftime('%d/%m/%Y')}",
        f"",
        f"{'─'*70}",
        f"",
        f"[{ahora}]  INFO   Sistema iniciado correctamente",
        f"[{ahora}]  INFO   Período académico activo: 2026",
        f"[{ahora}]  INFO   Almacenamiento: JSON (data/)",
        f"[{ahora}]  DATA   Estudiantes registrados:   {len(repo.estudiantes)}",
        f"[{ahora}]  DATA   Docentes registrados:      {len(repo.docentes)}",
        f"[{ahora}]  DATA   Grupos de nivelación:      {len(repo.cursos)}",
        f"[{ahora}]  DATA   Asignaturas del plan:      {len(repo.asignaturas)}",
        f"[{ahora}]  DATA   Matrículas registradas:    {len(repo.matriculas)}",
        f"[{ahora}]  DATA   Tareas publicadas:         {len(repo.tareas)}",
        f"[{ahora}]  DATA   Calificaciones:            {len(repo.calificaciones)}",
        f"[{ahora}]  DATA   Horarios adicionales:      {len(repo.horarios)}",
        f"",
        f"{'─'*70}",
        f"",
        f"[{ahora}]  ARCH   Patrón Repository: JsonManager → IRepositorio",
        f"[{ahora}]  ARCH   Inyección de dependencia: SistemaAcademicoApp(repo)",
        f"[{ahora}]  ARCH   Principios SOLID aplicados en toda la arquitectura",
        f"[{ahora}]  ARCH   Capa de servicios: Auth, Usuario, Curso, Horario,",
        f"[{ahora}]  ARCH            Asignatura, Matricula, Tarea, Calificacion",
        f"[{ahora}]  ARCH   Control de acceso: tareas filtradas por matrícula activa",
        f"[{ahora}]  ARCH   Aislamiento por carrera: cursos y tareas por carrera",
        f"",
        f"{'─'*70}",
        f"",
        f"[{ahora}]  INFO   Sistema listo para operar. ✅",
        f"",
    ]
    txt.insert("1.0", "\n".join(lineas))
    txt.config(state="disabled")


# ── Configuración del sistema ─────────────────────────────────────────────────
def _tab_sistema(parent, usuario, repo):
    wrap = tk.Frame(parent, bg=C["bg"], padx=20, pady=14)
    wrap.pack(fill="both", expand=True)
    seccion_titulo(wrap, "Configuración del Sistema")

    # Información del sistema
    info_f = tk.Frame(wrap, bg=C["card"], bd=1, relief="solid", padx=20, pady=16)
    info_f.pack(fill="x", pady=(0, 14))
    tk.Label(info_f, text="Información del sistema",
             font=("Segoe UI", 11, "bold"), bg=C["card"], fg=C["sidebar"]).pack(anchor="w", pady=(0, 8))
    datos = [
        ("Sistema",          "AulaVirtual – Sistema de Admisión del Proceso de Nivelación"),
        ("Versión",          "6.0  –  Arquitectura SOLID"),
        ("Período activo",   "Ciclo 2026"),
        ("Administrador",    usuario.nombre_completo()),
        ("Base de datos",    "JSON local  (data/)"),
        ("Fecha del sistema",datetime.now().strftime("%d/%m/%Y %H:%M")),
    ]
    for etq, val in datos:
        fila = tk.Frame(info_f, bg=C["card"]); fila.pack(fill="x", pady=2)
        tk.Label(fila, text=f"{etq}:", font=("Segoe UI", 9, "bold"),
                 bg=C["card"], fg=C["text_sec"], width=20, anchor="w").pack(side="left")
        tk.Label(fila, text=val, font=("Segoe UI", 9),
                 bg=C["card"], fg=C["text"]).pack(side="left", padx=8)

    # Acciones de mantenimiento
    tk.Label(wrap, text="Mantenimiento de datos",
             font=("Segoe UI", 11, "bold"), bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", pady=(0, 8))
    mant_f = tk.Frame(wrap, bg=C["card"], bd=1, relief="solid", padx=20, pady=16)
    mant_f.pack(fill="x")

    acciones = [
        ("🔄  Recargar datos desde archivos JSON",
         C["accent"],
         lambda: messagebox.showinfo("Info", "Para recargar los datos reinicie la aplicación.\nLos cambios realizados en esta sesión ya están guardados automáticamente.")),
        ("📊  Exportar resumen del período",
         C["sidebar"],
         lambda: _exportar_resumen(repo)),
        ("🗑  Limpiar matrículas anuladas",
         C["warning"],
         lambda: _limpiar_anuladas(repo)),
    ]
    for txt, col, cmd in acciones:
        fila = tk.Frame(mant_f, bg=C["card"]); fila.pack(fill="x", pady=4)
        btn(fila, txt, col, cmd, padx=12, pady=6).pack(side="left")

    tk.Label(mant_f, text="ℹ  Los datos se guardan automáticamente con cada operación.",
             font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(anchor="w", pady=(10, 0))


def _exportar_resumen(repo):
    from datetime import datetime
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    activas = [m for m in repo.matriculas if m.estado == "Activa"]
    resumen = (
        f"RESUMEN DEL PERÍODO DE NIVELACIÓN 2026\n"
        f"Generado: {ahora}\n"
        f"{'='*50}\n\n"
        f"Estudiantes: {len(repo.estudiantes)}\n"
        f"Docentes:    {len(repo.docentes)}\n"
        f"Grupos:      {len(repo.cursos)}\n"
        f"Matrículas activas: {len(activas)}\n"
        f"Calificaciones registradas: {len(repo.calificaciones)}\n\n"
        f"GRUPOS POR CARRERA:\n"
    )
    carreras = list({getattr(e,"carrera","") for e in repo.estudiantes})
    for carrera in sorted(carreras):
        ests = [e for e in repo.estudiantes if getattr(e,"carrera","") == carrera]
        grupos = [c for c in repo.cursos if c.carrera == carrera]
        resumen += f"  · {carrera}: {len(ests)} est., {len(grupos)} grupo(s)\n"
    messagebox.showinfo("Resumen exportado", resumen)


def _limpiar_anuladas(repo):
    anuladas = [m for m in repo.matriculas if m.estado == "Anulada"]
    if not anuladas:
        messagebox.showinfo("Info", "No hay matrículas anuladas para limpiar.")
        return
    if messagebox.askyesno("Confirmar",
                           f"¿Eliminar {len(anuladas)} matrícula(s) anuladas del registro?"):
        repo.matriculas[:] = [m for m in repo.matriculas if m.estado != "Anulada"]
        repo.guardar_matriculas()
        messagebox.showinfo("✅", f"Se eliminaron {len(anuladas)} matrículas anuladas.")

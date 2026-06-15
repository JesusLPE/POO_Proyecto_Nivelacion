"""ui/panel_docente.py – Panel del docente de nivelación."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from ui.base import (C, btn, lbl, tree_con_scroll, refrescar_tree,
                     ventana_modal, card, scroll_canvas, seccion_titulo)
from ui.shared import panel_perfil, render_reporte
from services.academico import TareaService, CalificacionService, CursoService
from services.reporte_service import DirectorReportes, ReporteService
from models import Notas


def construir(parent, usuario, repo):
    ts  = TareaService(repo)
    cs  = CalificacionService(repo)
    crs = CursoService(repo)

    nb = ttk.Notebook(parent)
    nb.pack(fill="both", expand=True, padx=10, pady=10)

    tabs = [
        ("  🏠 Inicio  ",         lambda f: _tab_inicio(f, usuario, repo, ts, cs)),
        ("  📋 Mis Tareas  ",     lambda f: _tab_tareas(f, usuario, repo, ts, cs)),
        ("  📂 Entregas  ",       lambda f: _tab_entregas(f, usuario, repo, ts)),
        ("  📊 Calificaciones  ", lambda f: _tab_calificaciones(f, usuario, repo, cs)),
        ("  🎓 Mis Cursos  ",     lambda f: _tab_cursos(f, usuario, crs, repo)),
        ("  Reportes  ",          lambda f: _tab_reportes(f, usuario, repo, ts)),
        ("  👤 Mi Perfil  ",      lambda f: panel_perfil(f, usuario, repo)),
    ]
    for texto, fn in tabs:
        f = ttk.Frame(nb); nb.add(f, text=texto); fn(f)


# ── Inicio ────────────────────────────────────────────────────────────────────
def _tab_inicio(parent, usuario, repo, ts, cs):
    wrap = tk.Frame(parent, bg=C["bg"]); wrap.pack(fill="both", expand=True)
    _, sf = scroll_canvas(wrap)

    # Encabezado
    hora = datetime.now().hour
    saludo = "Buenos días" if hora < 12 else ("Buenas tardes" if hora < 18 else "Buenas noches")
    hdr = tk.Frame(sf, bg=C["success"], padx=24, pady=18)
    hdr.pack(fill="x", padx=12, pady=(10, 6))
    tk.Label(hdr, text=f"{saludo}, {usuario.nombre} 👋",
             font=("Segoe UI", 15, "bold"), bg=C["success"], fg=C["white"]).pack(anchor="w")
    tk.Label(hdr, text=f"Docente de {usuario.especialidad}  ·  Sistema de Nivelación",
             font=("Segoe UI", 10), bg=C["success"], fg="#C8E6C9").pack(anchor="w")

    # Stats
    mis_cursos = [c for c in repo.cursos if c.docente_email == usuario.email]
    mis_tareas = ts.del_docente(usuario.email)
    total_entregas = sum(len(t.entregas) for t in mis_tareas)
    mis_notas = len([c for c in repo.calificaciones])

    stats = [
        (C["sidebar"],  str(len(mis_cursos)),      "Grupos asignados"),
        (C["accent"],   str(len(mis_tareas)),       "Tareas publicadas"),
        (C["warning"],  str(total_entregas),        "Entregas recibidas"),
        (C["success"],  str(mis_notas),             "Calificaciones registradas"),
    ]
    grid = tk.Frame(sf, bg=C["bg"]); grid.pack(fill="x", padx=12, pady=8)
    for i, (col, val, lbl_txt) in enumerate(stats):
        cf = tk.Frame(grid, bg=col)
        cf.grid(row=0, column=i, padx=6, pady=4, sticky="ew")
        grid.columnconfigure(i, weight=1)
        inner = tk.Frame(cf, bg=C["card"], padx=16, pady=12)
        inner.pack(fill="both", padx=2, pady=2)
        tk.Label(inner, text=val, font=("Segoe UI", 22, "bold"),
                 bg=C["card"], fg=col).pack()
        tk.Label(inner, text=lbl_txt, font=("Segoe UI", 9),
                 bg=C["card"], fg=C["text_sec"]).pack()

    # Entregas recientes sin revisar
    sin_nota = []
    for tarea in mis_tareas:
        for e in tarea.entregas:
            est = repo.usuarios.get(e.get("estudiante_email", ""))
            ya_nota = any(c.estudiante.email == e["estudiante_email"]
                          and c.asignatura == tarea.titulo
                          for c in repo.calificaciones)
            if not ya_nota:
                sin_nota.append((tarea, e, est))

    if sin_nota:
        tk.Label(sf, text="  📬  Entregas pendientes de calificar",
                 font=("Segoe UI", 11, "bold"), bg=C["bg"], fg=C["danger"]
                 ).pack(anchor="w", padx=14, pady=(14, 2))
        for tarea, e, est in sin_nota[:5]:
            ct = card(sf, C["warning"])
            tk.Label(ct, text=tarea.titulo, font=("Segoe UI", 10, "bold"),
                     bg=C["card"], fg=C["text"]).pack(anchor="w")
            est_txt = est.nombre_completo() if est else e["estudiante_email"]
            tk.Label(ct, text=f"Enviado por {est_txt}  ·  {e.get('fecha', '')}",
                     font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(anchor="w")
    else:
        ct = card(sf, C["success"])
        tk.Label(ct, text="✅ No hay entregas pendientes de calificar",
                 font=("Segoe UI", 10, "bold"), bg=C["card"], fg=C["success"]).pack(anchor="w")

    # Mis cursos hoy
    hoy_dia = datetime.now().strftime("%A").capitalize()
    DIAS_ES = {"Monday":"Lunes","Tuesday":"Martes","Wednesday":"Miércoles",
               "Thursday":"Jueves","Friday":"Viernes","Saturday":"Sábado","Sunday":"Domingo"}
    hoy_dia_es = DIAS_ES.get(datetime.now().strftime("%A"), hoy_dia)
    cursos_hoy = [c for c in mis_cursos if c.horario and c.horario.dia == hoy_dia_es]
    if cursos_hoy:
        tk.Label(sf, text=f"  📅  Clases de hoy ({hoy_dia_es})",
                 font=("Segoe UI", 11, "bold"), bg=C["bg"], fg=C["sidebar"]
                 ).pack(anchor="w", padx=14, pady=(14, 2))
        for c in cursos_hoy:
            ct = card(sf, C["sidebar"])
            tk.Label(ct, text=c.nombre, font=("Segoe UI", 10, "bold"),
                     bg=C["card"], fg=C["sidebar"]).pack(anchor="w")
            h = c.horario
            tk.Label(ct, text=f"🕐 {h.hora_inicio} – {h.hora_fin}  ·  🏛 {h.aula or 'Sin aula'}",
                     font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(anchor="w")


# ── Gestión de tareas ─────────────────────────────────────────────────────────
def _tab_tareas(parent, usuario, repo, ts, cs):
    wrap = tk.Frame(parent, bg=C["bg"], padx=14, pady=10)
    wrap.pack(fill="both", expand=True)
    seccion_titulo(wrap, "Mis Tareas Publicadas")

    cols = ("ID", "Título", "Asignatura", "Vence", "Entregas", "Estado")
    t, _ = tree_con_scroll(wrap, cols, [35, 220, 180, 100, 80, 100], alto=11)

    def refrescar():
        filas = []
        for tarea in ts.del_docente(usuario.email):
            asig = next((a.nombre for a in repo.asignaturas
                         if a.id == tarea.asignatura_id), "General")
            vence = tarea.fecha_limite or "–"
            n_entregas = len(tarea.entregas)
            estado = "Activa" if not tarea.fecha_limite or tarea.fecha_limite >= datetime.now().strftime("%Y-%m-%d") else "Vencida"
            filas.append((tarea.id, tarea.titulo, asig, vence, n_entregas, estado))
        refrescar_tree(t, filas)
    refrescar()

    # Acciones
    form = tk.Frame(wrap, bg=C["bg"]); form.pack(fill="x", pady=8)
    btn(form, "➕  Nueva tarea",    C["accent"],  lambda: _dlg_nueva_tarea(parent, usuario, repo, ts, refrescar),  padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🗑  Eliminar",       C["danger"],  lambda: _eliminar_tarea(t, usuario, ts, refrescar),               padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🔄  Actualizar",     C["text_sec"],refrescar,                                                        padx=10, pady=5).pack(side="left", padx=4)


def _dlg_nueva_tarea(root, usuario, repo, ts, on_done):
    v = ventana_modal(root.winfo_toplevel(), "Publicar nueva tarea", 560, 480)
    body = tk.Frame(v, bg=C["bg"], padx=20, pady=16)
    body.pack(fill="both", expand=True)

    lbl(body, "Título de la tarea: *", bold=True).pack(anchor="w")
    titulo_e = ttk.Entry(body, width=56); titulo_e.pack(fill="x", ipady=4, pady=(2, 10))

    lbl(body, "Descripción / instrucciones: *", bold=True).pack(anchor="w")
    desc_t = tk.Text(body, height=5, font=("Segoe UI", 10),
                     bg=C["white"], relief="solid", bd=1)
    desc_t.pack(fill="x", pady=(2, 10))

    fila = tk.Frame(body, bg=C["bg"]); fila.pack(fill="x", pady=(0, 10))
    lbl(fila, "Fecha límite (YYYY-MM-DD):", bold=True).pack(side="left")
    fecha_e = ttk.Entry(fila, width=16); fecha_e.pack(side="left", padx=10, ipady=3)

    lbl(body, "Vincular a asignatura (controla quién puede ver la tarea):", bold=True).pack(anchor="w")
    asig_v = tk.StringVar(value="Todas las asignaturas")
    vals = ["Todas las asignaturas"] + [f"{a.nombre}  (ID:{a.id})" for a in repo.asignaturas]
    asig_cb = ttk.Combobox(body, textvariable=asig_v, values=vals, width=54)
    asig_cb.pack(fill="x", ipady=3, pady=(2, 16))

    err_lbl = tk.Label(body, text="", fg=C["danger"], bg=C["bg"], font=("Segoe UI", 9))
    err_lbl.pack(anchor="w")

    def guardar():
        titulo = titulo_e.get().strip()
        desc   = desc_t.get("1.0", tk.END).strip()
        fecha  = fecha_e.get().strip()
        if not titulo:  err_lbl.config(text="El título es obligatorio."); return
        if not desc:    err_lbl.config(text="La descripción es obligatoria."); return
        asig_id = None
        sel = asig_v.get()
        if sel != "Todas las asignaturas":
            try: asig_id = int(sel.split("ID:")[1].rstrip(")").strip())
            except (ValueError, IndexError): pass
        ok, msg = ts.crear(titulo, desc, fecha, usuario.email, asig_id)
        if ok:
            messagebox.showinfo("✅", f"Tarea «{titulo}» publicada correctamente.")
            on_done(); v.destroy()
        else:
            err_lbl.config(text=msg)

    btn(body, "✔  Publicar tarea", C["accent"], guardar, pady=9).pack(fill="x")


def _eliminar_tarea(tree, usuario, ts, on_done):
    sel = tree.selection()
    if not sel: messagebox.showerror("Error", "Seleccione una tarea de la lista."); return
    tid = tree.item(sel[0])["values"][0]
    titulo = tree.item(sel[0])["values"][1]
    if messagebox.askyesno("Confirmar eliminación",
                           f"¿Eliminar la tarea «{titulo}»?\n\nSe perderán todas las entregas asociadas."):
        ok, msg = ts.eliminar(tid, usuario.email)
        (messagebox.showinfo if ok else messagebox.showerror)("Resultado", msg)
        if ok: on_done()


# ── Entregas ──────────────────────────────────────────────────────────────────
def _tab_entregas(parent, usuario, repo, ts):
    wrap = tk.Frame(parent, bg=C["bg"], padx=14, pady=10)
    wrap.pack(fill="both", expand=True)
    seccion_titulo(wrap, "Entregas de Estudiantes")

    # Filtro por tarea
    mis_tareas = ts.del_docente(usuario.email)
    filtro_f = tk.Frame(wrap, bg=C["bg"]); filtro_f.pack(fill="x", pady=(0, 8))
    lbl(filtro_f, "Filtrar por tarea:", bold=True).pack(side="left")
    filtro_v = tk.StringVar(value="Todas las tareas")
    filtro_vals = ["Todas las tareas"] + [t.titulo for t in mis_tareas]
    filtro_cb = ttk.Combobox(filtro_f, textvariable=filtro_v, values=filtro_vals, width=42)
    filtro_cb.pack(side="left", padx=10, ipady=3)

    cols = ("Tarea", "Estudiante", "Carrera", "Fecha de entrega", "Descripción", "Archivo")
    t, _ = tree_con_scroll(wrap, cols, [180, 160, 160, 120, 180, 120], alto=12)

    def refrescar(_=None):
        filas = []
        filtro = filtro_v.get()
        for tarea in mis_tareas:
            if filtro != "Todas las tareas" and tarea.titulo != filtro: continue
            for e in tarea.entregas:
                est = repo.usuarios.get(e.get("estudiante_email", ""))
                est_txt = est.nombre_completo() if est else e.get("estudiante_email", "")
                carrera = getattr(est, "carrera", "") if est else ""
                filas.append((tarea.titulo, est_txt, carrera,
                               e.get("fecha", ""), e.get("descripcion", ""), e.get("archivo", "")))
        refrescar_tree(t, filas)
        count = tk.Label(wrap, text=f"Total: {len(filas)} entrega(s)",
                         font=("Segoe UI", 9, "bold"), bg=C["bg"], fg=C["text_sec"])
        count.pack(anchor="e", pady=2)

    filtro_cb.bind("<<ComboboxSelected>>", refrescar)
    refrescar()
    btn(wrap, "🔄  Actualizar", C["text_sec"], refrescar, padx=8, pady=4).pack(anchor="w", pady=4)


# ── Calificaciones ────────────────────────────────────────────────────────────
def _tab_calificaciones(parent, usuario, repo, cs):
    wrap = tk.Frame(parent, bg=C["bg"], padx=14, pady=10)
    wrap.pack(fill="both", expand=True)
    seccion_titulo(wrap, "Registro de Calificaciones")

    cols = ("Estudiante", "Carrera", "Asignatura", "Nota", "Estado", "Observación")
    t, _ = tree_con_scroll(wrap, cols, [180, 160, 180, 60, 110, 180], alto=11)

    def refrescar():
        filas = []
        for c in repo.calificaciones:
            est = c.estudiante
            carrera = getattr(est, "carrera", "")
            estado = Notas.estado(c.nota)
            filas.append((est.nombre_completo(), carrera,
                           c.asignatura, f"{c.nota:.1f}", estado, c.observacion))
        refrescar_tree(t, filas)
    refrescar()

    # Formulario de nueva nota
    ttk.Separator(wrap, orient="horizontal").pack(fill="x", pady=8)
    form_lbl = tk.Label(wrap, text="Registrar nueva calificación",
                        font=("Segoe UI", 11, "bold"), bg=C["bg"], fg=C["sidebar"])
    form_lbl.pack(anchor="w", pady=(0, 6))

    form = tk.Frame(wrap, bg=C["bg"]); form.pack(fill="x")

    lbl(form, "Estudiante:", bold=True).pack(side="left")
    est_v = tk.StringVar()
    est_vals = [f"{e.nombre_completo()}  ({e.matricula})" for e in repo.estudiantes]
    ttk.Combobox(form, textvariable=est_v, values=est_vals, width=30
                 ).pack(side="left", padx=8, ipady=3)

    lbl(form, "Asignatura:", bold=True).pack(side="left")
    asig_v = tk.StringVar()
    ttk.Combobox(form, textvariable=asig_v,
                 values=[a.nombre for a in repo.asignaturas], width=22
                 ).pack(side="left", padx=8, ipady=3)

    lbl(form, "Nota (0–10):", bold=True).pack(side="left")
    nota_sb = ttk.Spinbox(form, from_=0, to=10, increment=0.1, width=7)
    nota_sb.pack(side="left", padx=8, ipady=3)

    lbl(form, "Obs.:", bold=True).pack(side="left")
    obs_e = ttk.Entry(form, width=18); obs_e.pack(side="left", padx=8, ipady=3)

    def guardar():
        sel = est_v.get()
        if not sel: messagebox.showerror("Error", "Seleccione un estudiante."); return
        if not asig_v.get(): messagebox.showerror("Error", "Seleccione una asignatura."); return
        try:
            nota = float(nota_sb.get())
            if not 0 <= nota <= 10: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La nota debe ser un número entre 0 y 10."); return
        mat = sel.split("(")[1].rstrip(")")
        est = next((e for e in repo.estudiantes if e.matricula == mat), None)
        if not est: messagebox.showerror("Error", "Estudiante no encontrado."); return
        ok, msg = cs.registrar(est.email, asig_v.get(), nota, obs_e.get().strip())
        if ok:
            messagebox.showinfo("✅", msg); refrescar()
            obs_e.delete(0, tk.END)
        else:
            messagebox.showerror("Error", msg)

    btn(form, "✔  Registrar", C["success"], guardar, padx=10, pady=5).pack(side="left", padx=8)
    btn(wrap, "🔄  Actualizar lista", C["text_sec"], refrescar, padx=8, pady=4).pack(anchor="w", pady=6)


# ── Mis cursos ────────────────────────────────────────────────────────────────
def _tab_cursos(parent, usuario, crs, repo):
    wrap = tk.Frame(parent, bg=C["bg"]); wrap.pack(fill="both", expand=True, padx=14, pady=10)
    seccion_titulo(wrap, "Mis Grupos de Nivelación")

    cursos = crs.del_docente(usuario.email)
    if not cursos:
        tk.Label(wrap, text="No tienes grupos asignados actualmente.",
                 font=("Segoe UI", 10), bg=C["bg"], fg=C["text_sec"]).pack(pady=30)
        return

    _, sf = scroll_canvas(wrap)
    COLS = [C["success"], C["sidebar"], C["accent"]]
    for i, c in enumerate(cursos):
        col = COLS[i % len(COLS)]
        ct = card(sf, col)
        tk.Label(ct, text=c.nombre, font=("Segoe UI", 12, "bold"),
                 bg=C["card"], fg=col).pack(anchor="w")
        h = c.horario
        m = c.modalidad.nombre if c.modalidad else "–"
        info = f"🕐 {h}  ·  📡 {m}  ·  🏛 {h.aula if h and h.aula else '–'}" if h else f"📡 {m}"
        tk.Label(ct, text=info, font=("Segoe UI", 9),
                 bg=C["card"], fg=C["text_sec"]).pack(anchor="w", pady=2)
        tk.Label(ct, text=f"🏫 {c.carrera or 'Todos los grupos'}  ·  📅 {c._duracion_semanas} semanas  ·  {c._total_horas} horas",
                 font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(anchor="w")

        # Estudiantes matriculados
        mats = [m for m in repo.matriculas
                if m.asignatura and m.estado == "Activa"
                and m.estudiante and getattr(m.estudiante, "carrera", "") == c.carrera]
        tk.Label(ct, text=f"👥 {len(mats)} estudiante(s) matriculados en esta carrera",
                 font=("Segoe UI", 9, "bold"), bg=C["card"], fg=col).pack(anchor="w", pady=(4, 0))


# ── Reportes ──────────────────────────────────────────────────────────────────
def _tab_reportes(parent, usuario, repo, ts):
    """Reporte de progreso de alumnos, construido con el patrón Builder.

    La UI no construye el reporte por su cuenta: delega en
    DirectorReportes, que internamente usa ReporteDocenteBuilder.
    """
    wrap = tk.Frame(parent, bg=C["bg"])
    wrap.pack(fill="both", expand=True)

    top = tk.Frame(wrap, bg=C["bg"], padx=14, pady=10)
    top.pack(fill="x")
    seccion_titulo(top, "Reporte de Progreso de Alumnos")
    lbl(top, "Generado mediante ReporteDocenteBuilder (patrón Builder)",
        size=9, color=C["text_sec"]).pack(anchor="w")

    contenido = tk.Frame(wrap, bg=C["bg"])
    contenido.pack(fill="both", expand=True)

    director = DirectorReportes(repo)

    def generar():
        for w in contenido.winfo_children():
            w.destroy()
        reporte = director.construir_reporte_docente(usuario.email)
        render_reporte(contenido, reporte, color_header=C["success"])

    btn(top, "🔄  Generar reporte", C["success"], generar, padx=10, pady=5).pack(anchor="w", pady=(6, 0))
    generar()

"""ui/panel_estudiante.py – Panel completo del estudiante de nivelación."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from ui.base import (C, btn, lbl, tree_con_scroll, refrescar_tree,
                     ventana_modal, card, scroll_canvas, seccion_titulo)
from ui.shared import panel_perfil, render_reporte
from services.academico import TareaService, CalificacionService
from services.reportes import DirectorReportes
from models import Notas


def construir(parent, usuario, repo):
    ts = TareaService(repo)
    cs = CalificacionService(repo)

    nb = ttk.Notebook(parent)
    nb.pack(fill="both", expand=True, padx=10, pady=10)

    tabs = [
        ("  🏠 Inicio  ",         lambda f: _tab_inicio(f, usuario, repo, ts, cs)),
        ("  📋 Tareas  ",         lambda f: _tab_tareas(f, usuario, ts)),
        ("  📚 Mis Cursos  ",     lambda f: _tab_cursos(f, usuario, repo)),
        ("  📊 Calificaciones  ", lambda f: _tab_notas(f, usuario, cs)),
        ("  🗓 Horarios  ",       lambda f: _tab_horarios(f, usuario, repo)),
        ("  📄 Mi Reporte  ",     lambda f: _tab_reporte(f, usuario, repo)),
        ("  👤 Mi Perfil  ",      lambda f: panel_perfil(f, usuario, repo)),
    ]
    for texto, fn in tabs:
        f = ttk.Frame(nb); nb.add(f, text=texto); fn(f)


# ── Inicio ────────────────────────────────────────────────────────────────────
def _tab_inicio(parent, usuario, repo, ts, cs):
    wrap = tk.Frame(parent, bg=C["bg"]); wrap.pack(fill="both", expand=True)
    _, sf = scroll_canvas(wrap)

    # Saludo personalizado
    hora = datetime.now().hour
    saludo = "Buenos días" if hora < 12 else ("Buenas tardes" if hora < 18 else "Buenas noches")
    bienvenida = tk.Frame(sf, bg=C["sidebar"], padx=24, pady=18)
    bienvenida.pack(fill="x", padx=12, pady=(10, 6))
    tk.Label(bienvenida, text=f"{saludo}, {usuario.nombre} 👋",
             font=("Segoe UI", 15, "bold"), bg=C["sidebar"], fg=C["white"]).pack(anchor="w")
    tk.Label(bienvenida,
             text=f"Bienvenido/a al Sistema de Nivelación  ·  {usuario.carrera}",
             font=("Segoe UI", 10), bg=C["sidebar"], fg="#9FA8DA").pack(anchor="w", pady=(2, 0))
    fecha_txt = datetime.now().strftime("%A %d de %B de %Y").capitalize()
    tk.Label(bienvenida, text=fecha_txt,
             font=("Segoe UI", 9), bg=C["sidebar"], fg="#7986CB").pack(anchor="w")

    # Resumen de estado
    pendientes = [t for t in ts.visibles(usuario.email) if not t.entregada_por(usuario.email)]
    califs = cs.del_estudiante(usuario.email)
    prom = cs.promedio_estudiante(usuario.email)
    cursos = repo.cursos_por_carrera(usuario.carrera)
    mats = repo.matriculas_activas_estudiante(usuario.email)

    stats = [
        (C["danger"] if pendientes else C["success"],
         str(len(pendientes)), "Tarea(s) pendiente(s)"),
        (C["accent"],  str(len(mats)),    "Asignatura(s) matriculadas"),
        (C["success"], str(len(cursos)),  "Grupo(s) de nivelación"),
        (C["warning"] if prom < 7 else C["success"],
         f"{prom:.1f}/10", "Promedio actual"),
    ]
    grid = tk.Frame(sf, bg=C["bg"]); grid.pack(fill="x", padx=12, pady=8)
    for i, (col, valor, label) in enumerate(stats):
        cf = tk.Frame(grid, bg=col)
        cf.grid(row=0, column=i, padx=6, pady=4, sticky="ew")
        grid.columnconfigure(i, weight=1)
        inner = tk.Frame(cf, bg=C["card"], padx=16, pady=12)
        inner.pack(fill="both", padx=2, pady=2)
        tk.Label(inner, text=valor, font=("Segoe UI", 22, "bold"),
                 bg=C["card"], fg=col).pack()
        tk.Label(inner, text=label, font=("Segoe UI", 9),
                 bg=C["card"], fg=C["text_sec"]).pack()

    # Tareas próximas a vencer
    if pendientes:
        tk.Label(sf, text="  ⚠  Tareas próximas a vencer",
                 font=("Segoe UI", 11, "bold"), bg=C["bg"], fg=C["danger"]
                 ).pack(anchor="w", padx=14, pady=(12, 2))
        COLS = [C["danger"], C["warning"], C["accent"]]
        for i, t in enumerate(pendientes[:3]):
            col = COLS[i % len(COLS)]
            ct = card(sf, col)
            fecha_txt = f"Vence: {t.fecha_limite}" if t.fecha_limite else "Sin fecha límite"
            tk.Label(ct, text=fecha_txt, font=("Segoe UI", 8, "bold"),
                     bg=C["card"], fg=col).pack(anchor="w")
            tk.Label(ct, text=t.titulo, font=("Segoe UI", 10, "bold"),
                     bg=C["card"], fg=C["text"]).pack(anchor="w", pady=(2, 0))
            tk.Label(ct, text=(t.descripcion[:100] + "…") if len(t.descripcion or "") > 100 else (t.descripcion or ""),
                     font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"],
                     wraplength=580).pack(anchor="w")

    # Calificaciones recientes
    if califs:
        tk.Label(sf, text="  📊  Últimas calificaciones",
                 font=("Segoe UI", 11, "bold"), bg=C["bg"], fg=C["sidebar"]
                 ).pack(anchor="w", padx=14, pady=(14, 2))
        for c in califs[-3:]:
            estado = Notas.estado(c.nota)
            col = C["success"] if c.esta_aprobado() else C["danger"]
            ct = card(sf, col)
            fila = tk.Frame(ct, bg=C["card"]); fila.pack(fill="x")
            tk.Label(fila, text=c.asignatura, font=("Segoe UI", 10, "bold"),
                     bg=C["card"], fg=C["text"]).pack(side="left")
            tk.Label(fila, text=f"  {c.nota:.1f} / 10  –  {estado}",
                     font=("Segoe UI", 10, "bold"), bg=C["card"], fg=col).pack(side="right")

    # Avisos
    tk.Label(sf, text="  📢  Avisos del Sistema de Nivelación",
             font=("Segoe UI", 11, "bold"), bg=C["bg"], fg=C["sidebar"]
             ).pack(anchor="w", padx=14, pady=(14, 2))
    avisos = [
        (C["sidebar2"], "Inicio del ciclo de Nivelación 2026",
         "El período académico de nivelación inició el 1 de junio de 2026. Revisa regularmente tus tareas y asistencia."),
        (C["accent"], "Tutorías disponibles",
         "El departamento de nivelación ofrece tutorías de matemáticas y lenguaje los lunes y miércoles de 12:00 a 14:00."),
    ]
    for col, titulo, desc in avisos:
        ct = card(sf, col)
        tk.Label(ct, text=titulo, font=("Segoe UI", 10, "bold"),
                 bg=C["card"], fg=col).pack(anchor="w")
        tk.Label(ct, text=desc, font=("Segoe UI", 9), bg=C["card"],
                 fg=C["text_sec"], wraplength=580).pack(anchor="w")


# ── Tareas ────────────────────────────────────────────────────────────────────
def _tab_tareas(parent, usuario, ts):
    wrap = tk.Frame(parent, bg=C["bg"]); wrap.pack(fill="both", expand=True)

    # Filtros
    filtro_frame = tk.Frame(wrap, bg=C["bg"], padx=14, pady=8)
    filtro_frame.pack(fill="x")
    tk.Label(filtro_frame, text="Mostrar:", font=("Segoe UI", 9, "bold"),
             bg=C["bg"], fg=C["text"]).pack(side="left")
    filtro_v = tk.StringVar(value="Todas")
    for opcion in ("Todas", "Pendientes", "Entregadas"):
        tk.Radiobutton(filtro_frame, text=opcion, variable=filtro_v, value=opcion,
                       bg=C["bg"], fg=C["text"], font=("Segoe UI", 9),
                       activebackground=C["bg"], command=lambda: refrescar()
                       ).pack(side="left", padx=8)

    _, sf = scroll_canvas(wrap)

    def refrescar():
        for w in sf.winfo_children(): w.destroy()
        todas = ts.visibles(usuario.email)
        filtro = filtro_v.get()
        if filtro == "Pendientes":
            mostrar = [t for t in todas if not t.entregada_por(usuario.email)]
        elif filtro == "Entregadas":
            mostrar = [t for t in todas if t.entregada_por(usuario.email)]
        else:
            mostrar = todas

        if not mostrar:
            tk.Label(sf, text="No hay tareas en esta categoría.",
                     font=("Segoe UI", 10), bg=C["bg"], fg=C["text_sec"]).pack(pady=30)
            return

        COLS_PEND = [C["accent"], C["sidebar"], C["warning"], C["sidebar2"]]
        for i, t in enumerate(mostrar):
            entregada = t.entregada_por(usuario.email)
            col = C["success"] if entregada else COLS_PEND[i % len(COLS_PEND)]
            ct = card(sf, col)

            # Cabecera
            cab = tk.Frame(ct, bg=C["card"]); cab.pack(fill="x")
            estado_lbl = "✅ Entregada" if entregada else "⏳ Pendiente"
            tk.Label(cab, text=estado_lbl, font=("Segoe UI", 8, "bold"),
                     bg=C["card"], fg=col).pack(side="left")
            if t.fecha_limite:
                tk.Label(cab, text=f"Vence: {t.fecha_limite}",
                         font=("Segoe UI", 8), bg=C["card"], fg=C["text_sec"]).pack(side="right")

            tk.Label(ct, text=t.titulo, font=("Segoe UI", 11, "bold"),
                     bg=C["card"], fg=C["text"]).pack(anchor="w", pady=(4, 2))
            if t.descripcion:
                tk.Label(ct, text=t.descripcion, font=("Segoe UI", 9),
                         bg=C["card"], fg=C["text_sec"], wraplength=580,
                         justify="left").pack(anchor="w")

            if entregada:
                entrega = next((e for e in t.entregas if e["estudiante_email"] == usuario.email), None)
                if entrega:
                    info_f = tk.Frame(ct, bg=C["bg"], padx=10, pady=6)
                    info_f.pack(fill="x", pady=(6, 0))
                    tk.Label(info_f, text=f"Entregada el {entrega['fecha']}",
                             font=("Segoe UI", 8), bg=C["bg"], fg=C["success"]).pack(anchor="w")
                    if entrega.get("archivo"):
                        tk.Label(info_f, text=f"📎 {entrega['archivo']}",
                                 font=("Segoe UI", 8), bg=C["bg"], fg=C["text_sec"]).pack(anchor="w")
            else:
                btn(ct, "⬆  Entregar tarea", col,
                    lambda tarea=t: _dlg_entregar(parent, usuario, tarea, ts, refrescar),
                    padx=10, pady=4).pack(anchor="e", pady=(6, 0))

    refrescar()


def _dlg_entregar(root, usuario, tarea, ts, on_done):
    v = ventana_modal(root.winfo_toplevel(), f"Entregar: {tarea.titulo}", 540, 400)
    body = tk.Frame(v, bg=C["bg"], padx=20, pady=16)
    body.pack(fill="both", expand=True)

    tk.Label(body, text=tarea.descripcion or "Sin descripción",
             font=("Segoe UI", 9), bg=C["bg"], fg=C["text_sec"],
             wraplength=480, justify="left").pack(anchor="w", pady=(0, 12))
    ttk.Separator(body, orient="horizontal").pack(fill="x", pady=(0, 12))

    lbl(body, "Comentarios / descripción de tu entrega: *", bold=True).pack(anchor="w")
    desc_t = tk.Text(body, height=5, font=("Segoe UI", 10),
                     bg=C["white"], relief="solid", bd=1)
    desc_t.pack(fill="x", pady=(2, 12))

    lbl(body, "Adjuntar archivo (opcional):", bold=True).pack(anchor="w")
    fila = tk.Frame(body, bg=C["bg"]); fila.pack(fill="x", pady=(2, 16))
    arch_v = tk.StringVar()
    arch_e = ttk.Entry(fila, textvariable=arch_v, width=46)
    arch_e.pack(side="left", ipady=4)
    btn(fila, "📂 Examinar", C["accent2"],
        lambda: arch_v.set(filedialog.askopenfilename()),
        padx=8, pady=3).pack(side="left", padx=8)

    err_lbl = tk.Label(body, text="", fg=C["danger"], bg=C["bg"], font=("Segoe UI", 9))
    err_lbl.pack(anchor="w")

    def guardar():
        desc = desc_t.get("1.0", tk.END).strip()
        if not desc:
            err_lbl.config(text="Por favor describe tu entrega antes de enviar."); return
        ok, msg = ts.entregar(tarea.id, usuario.email, desc, arch_v.get())
        if ok:
            messagebox.showinfo("✅ Entrega exitosa", f"Tu tarea «{tarea.titulo}» fue entregada correctamente.")
            v.destroy(); on_done()
        else:
            err_lbl.config(text=msg)

    btn(body, "✔  Confirmar y enviar entrega", C["success"], guardar, pady=9).pack(fill="x")


# ── Cursos ────────────────────────────────────────────────────────────────────
def _tab_cursos(parent, usuario, repo):
    wrap = tk.Frame(parent, bg=C["bg"]); wrap.pack(fill="both", expand=True, padx=14, pady=10)
    seccion_titulo(wrap, f"Grupos de Nivelación – {usuario.carrera}")

    cursos = repo.cursos_por_carrera(usuario.carrera)
    if not cursos:
        lbl(wrap, "No hay grupos asignados para tu carrera.",
            color=C["text_sec"]).pack(pady=20)
        return

    _, sf = scroll_canvas(wrap)
    COLS = [C["sidebar"], C["accent"], C["success"], C["sidebar2"]]
    for i, c in enumerate(cursos):
        col = COLS[i % len(COLS)]
        ct = card(sf, col)
        tk.Label(ct, text=c.nombre, font=("Segoe UI", 12, "bold"),
                 bg=C["card"], fg=col).pack(anchor="w")

        info_grid = tk.Frame(ct, bg=C["card"]); info_grid.pack(fill="x", pady=6)
        datos = []
        if c.horario: datos.append(("🕐 Horario", str(c.horario)))
        if c.horario and c.horario.aula: datos.append(("🏛 Aula", c.horario.aula))
        if c.modalidad: datos.append(("📡 Modalidad", c.modalidad.nombre))
        datos.append(("📅 Duración", f"{c._duracion_semanas} semanas · {c._total_horas} horas"))
        d_obj = repo.usuarios.get(c.docente_email or "")
        if d_obj: datos.append(("👨‍🏫 Docente", f"{d_obj.nombre_completo()} – {d_obj.especialidad}"))

        for j, (etiqueta, valor) in enumerate(datos):
            col_n = j % 2
            tk.Label(info_grid, text=f"{etiqueta}:", font=("Segoe UI", 9, "bold"),
                     bg=C["card"], fg=C["text_sec"]).grid(
                row=j//2, column=col_n*2, sticky="w", padx=(0, 6), pady=2)
            tk.Label(info_grid, text=valor, font=("Segoe UI", 9),
                     bg=C["card"], fg=C["text"]).grid(
                row=j//2, column=col_n*2+1, sticky="w", padx=(0, 20), pady=2)


# ── Calificaciones ────────────────────────────────────────────────────────────
def _tab_notas(parent, usuario, cs):
    wrap = tk.Frame(parent, bg=C["bg"]); wrap.pack(fill="both", expand=True, padx=14, pady=10)
    seccion_titulo(wrap, "Mis Calificaciones")

    califs = cs.del_estudiante(usuario.email)

    if not califs:
        tk.Label(wrap, text="Aún no tienes calificaciones registradas.",
                 font=("Segoe UI", 10), bg=C["bg"], fg=C["text_sec"]).pack(pady=30)
        return

    # Resumen promedio
    prom = cs.promedio_estudiante(usuario.email)
    col_prom = C["success"] if prom >= 7.0 else (C["warning"] if prom >= 5.0 else C["danger"])
    estado_prom = Notas.estado(prom)
    res = tk.Frame(wrap, bg=col_prom, padx=20, pady=12)
    res.pack(fill="x", pady=(0, 12))
    tk.Label(res, text=f"Promedio general: {prom:.2f} / 10  –  {estado_prom}",
             font=("Segoe UI", 13, "bold"), bg=col_prom, fg=C["white"]).pack(side="left")

    # Tabla detallada
    cols = ("Asignatura", "Nota", "Sobre 10", "Estado", "Observación")
    t, _ = tree_con_scroll(wrap, cols, [230, 60, 80, 130, 220], alto=12)

    filas = []
    for c in califs:
        estado = Notas.estado(c.nota)
        barra = "█" * int(c.nota) + "░" * (10 - int(c.nota))
        filas.append((c.asignatura, f"{c.nota:.1f}", barra, estado, c.observacion))
    refrescar_tree(t, filas)

    # Leyenda
    ley = tk.Frame(wrap, bg=C["bg"]); ley.pack(anchor="w", pady=8)
    for texto, col in [("≥ 9.0: Sobresaliente", C["success"]),
                       ("≥ 7.0: Aprobado", C["accent"]),
                       ("≥ 5.0: En recuperación", C["warning"]),
                       ("< 5.0: Reprobado", C["danger"])]:
        tk.Label(ley, text=f"  {texto}  ", bg=col, fg=C["white"],
                 font=("Segoe UI", 8), padx=6, pady=2).pack(side="left", padx=3)


# ── Horarios ──────────────────────────────────────────────────────────────────
def _tab_horarios(parent, usuario, repo):
    wrap = tk.Frame(parent, bg=C["bg"]); wrap.pack(fill="both", expand=True, padx=14, pady=10)
    seccion_titulo(wrap, "Mis Horarios de Clase")

    cursos = repo.cursos_por_carrera(usuario.carrera)
    if not cursos:
        lbl(wrap, "No hay horarios disponibles.", color=C["text_sec"]).pack(pady=20)
        return

    # Tabla de horarios
    cols = ("Grupo / Curso", "Día", "Hora", "Aula / Plataforma", "Modalidad", "Docente")
    t, _ = tree_con_scroll(wrap, cols, [220, 90, 120, 160, 100, 180], alto=10)
    filas = []
    for c in cursos:
        h = c.horario
        d_obj = repo.usuarios.get(c.docente_email or "")
        filas.append((
            c.nombre,
            h.dia if h else "–",
            f"{h.hora_inicio} – {h.hora_fin}" if h else "–",
            h.aula if h and h.aula else "–",
            c.modalidad.nombre if c.modalidad else "–",
            d_obj.nombre_completo() if d_obj else "Sin asignar"
        ))
    refrescar_tree(t, filas)

    # Horarios independientes (del coordinador)
    h_repo = [h for h in repo.horarios]
    if h_repo:
        tk.Label(wrap, text="Horarios adicionales programados",
                 font=("Segoe UI", 11, "bold"), bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", pady=(16, 6))
        cols2 = ("Actividad", "Día", "Inicio", "Fin", "Modalidad", "Lugar")
        t2, _ = tree_con_scroll(wrap, cols2, [200, 90, 80, 80, 100, 160], alto=6)
        filas2 = [(h.get("curso",""), h.get("dia",""), h.get("inicio",""),
                   h.get("fin",""), h.get("modalidad",""), h.get("aula",""))
                  for h in h_repo]
        refrescar_tree(t2, filas2)


# ── Mi Reporte ────────────────────────────────────────────────────────────────
def _tab_reporte(parent, usuario, repo):
    """Reporte de progreso individual, construido con el patrón Builder.

    Delega en DirectorReportes, que internamente usa
    ReporteEstudianteBuilder para construir el producto Reporte.
    """
    wrap = tk.Frame(parent, bg=C["bg"])
    wrap.pack(fill="both", expand=True)

    top = tk.Frame(wrap, bg=C["bg"], padx=14, pady=10)
    top.pack(fill="x")
    seccion_titulo(top, "Mi Reporte de Progreso")
    lbl(top, "Generado mediante ReporteEstudianteBuilder (patrón Builder)",
        size=9, color=C["text_sec"]).pack(anchor="w")

    contenido = tk.Frame(wrap, bg=C["bg"])
    contenido.pack(fill="both", expand=True)

    director = DirectorReportes(repo)

    def generar():
        for w in contenido.winfo_children():
            w.destroy()
        reporte = director.construir_reporte_estudiante(usuario.email)
        render_reporte(contenido, reporte, color_header=C["accent"])

    btn(top, "🔄  Generar reporte", C["accent"], generar, padx=10, pady=5).pack(anchor="w", pady=(6, 0))
    generar()

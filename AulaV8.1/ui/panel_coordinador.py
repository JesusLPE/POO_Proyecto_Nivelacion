"""ui/panel_coordinador.py – Panel del coordinador de nivelación."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from ui.base import (C, btn, lbl, tree_con_scroll, refrescar_tree,
                     ventana_modal, card, scroll_canvas, seccion_titulo,
                     DIAS, MODALIDADES)
from ui.shared import panel_perfil
from services.academico import CursoService, HorarioService, MatriculaService


def construir(parent, usuario, repo):
    cs = CursoService(repo)
    hs = HorarioService(repo)
    ms = MatriculaService(repo)

    nb = ttk.Notebook(parent)
    nb.pack(fill="both", expand=True, padx=10, pady=10)

    tabs = [
        ("  🏠 Inicio  ",          lambda f: _tab_inicio(f, repo)),
        ("  🎓 Grupos  ",          lambda f: _tab_cursos(f, repo, cs)),
        ("  🕐 Horarios  ",        lambda f: _tab_horarios(f, repo, hs)),
        ("  👨‍🏫 Docentes  ",        lambda f: _tab_docentes(f, repo, cs)),
        ("  📋 Matrículas  ",      lambda f: _tab_matriculas(f, repo, ms)),
        ("  📊 Reportes  ",        lambda f: _tab_reportes(f, repo)),
        ("  👤 Mi Perfil  ",       lambda f: panel_perfil(f, usuario, repo)),
    ]
    for texto, fn in tabs:
        f = ttk.Frame(nb); nb.add(f, text=texto); fn(f)


# ── Inicio / Dashboard ────────────────────────────────────────────────────────
def _tab_inicio(parent, repo):
    wrap = tk.Frame(parent, bg=C["bg"]); wrap.pack(fill="both", expand=True)
    _, sf = scroll_canvas(wrap)

    hdr = tk.Frame(sf, bg=C["warning"] if [m for m in repo.matriculas if m.estado=="Pendiente"] else C["sidebar2"],
                   padx=24, pady=18)
    hdr.pack(fill="x", padx=12, pady=(10, 6))
    tk.Label(hdr, text="Panel de Coordinación  –  Proceso de Nivelación",
             font=("Segoe UI", 14, "bold"), bg=hdr["bg"], fg=C["white"]).pack(anchor="w")
    tk.Label(hdr, text=f"Período académico 2026  ·  {datetime.now().strftime('%d/%m/%Y %H:%M')}",
             font=("Segoe UI", 10), bg=hdr["bg"], fg="#E8EAF6").pack(anchor="w")

    # Estadísticas generales
    sin_docente = [c for c in repo.cursos if not c.docente_email]
    sin_horario = [c for c in repo.cursos if not c.horario]
    pendientes  = [m for m in repo.matriculas if m.estado == "Pendiente"]
    activas     = [m for m in repo.matriculas if m.estado == "Activa"]

    stats = [
        (C["sidebar"],  str(len(repo.cursos)),      "Grupos activos"),
        (C["accent"],   str(len(repo.estudiantes)), "Estudiantes inscritos"),
        (C["success"],  str(len(activas)),           "Matrículas activas"),
        (C["warning"] if pendientes else C["success"],
         str(len(pendientes)), "Matrículas pendientes"),
        (C["danger"] if sin_docente else C["success"],
         str(len(sin_docente)), "Grupos sin docente"),
        (C["danger"] if sin_horario else C["success"],
         str(len(sin_horario)), "Grupos sin horario"),
    ]
    grid = tk.Frame(sf, bg=C["bg"]); grid.pack(fill="x", padx=12, pady=8)
    for i, (col, val, lbl_txt) in enumerate(stats):
        cf = tk.Frame(grid, bg=col)
        cf.grid(row=i//3, column=i%3, padx=6, pady=6, sticky="ew")
        grid.columnconfigure(i%3, weight=1)
        inner = tk.Frame(cf, bg=C["card"], padx=14, pady=12)
        inner.pack(fill="both", padx=2, pady=2)
        tk.Label(inner, text=val, font=("Segoe UI", 20, "bold"),
                 bg=C["card"], fg=col).pack()
        tk.Label(inner, text=lbl_txt, font=("Segoe UI", 9),
                 bg=C["card"], fg=C["text_sec"]).pack()

    # Alertas urgentes
    if sin_docente or pendientes:
        tk.Label(sf, text="  ⚠  Atención requerida",
                 font=("Segoe UI", 11, "bold"), bg=C["bg"], fg=C["danger"]
                 ).pack(anchor="w", padx=14, pady=(14, 2))
    if sin_docente:
        ct = card(sf, C["danger"])
        tk.Label(ct, text=f"⚠  {len(sin_docente)} grupo(s) sin docente asignado:",
                 font=("Segoe UI", 10, "bold"), bg=C["card"], fg=C["danger"]).pack(anchor="w")
        tk.Label(ct, text="  ·  " + "\n  ·  ".join(c.nombre for c in sin_docente),
                 font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(anchor="w")
    if sin_horario:
        ct = card(sf, C["warning"])
        tk.Label(ct, text=f"🕐  {len(sin_horario)} grupo(s) sin horario registrado:",
                 font=("Segoe UI", 10, "bold"), bg=C["card"], fg=C["warning"]).pack(anchor="w")
        tk.Label(ct, text="  ·  " + "\n  ·  ".join(c.nombre for c in sin_horario),
                 font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(anchor="w")
    if pendientes:
        ct = card(sf, C["warning"])
        tk.Label(ct, text=f"📋  {len(pendientes)} matrícula(s) pendiente(s) de aprobación",
                 font=("Segoe UI", 10, "bold"), bg=C["card"], fg=C["warning"]).pack(anchor="w")
        for m in pendientes[:4]:
            est = m.estudiante
            asig = m.asignatura.nombre if m.asignatura else "–"
            tk.Label(ct, text=f"  ·  {est.nombre_completo() if est else '?'}  →  {asig}",
                     font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(anchor="w")


# ── Grupos de nivelación ──────────────────────────────────────────────────────
def _tab_cursos(parent, repo, cs):
    wrap = tk.Frame(parent, bg=C["bg"], padx=12, pady=8)
    wrap.pack(fill="both", expand=True)
    seccion_titulo(wrap, "Grupos de Nivelación")

    cols = ("ID", "Grupo", "Carrera", "Docente", "Horario", "Modalidad", "Sem.", "Hs.")
    t, _ = tree_con_scroll(wrap, cols, [35, 210, 160, 180, 150, 90, 50, 50], alto=11)

    def refrescar():
        filas = []
        for c in repo.cursos:
            m  = c.modalidad.nombre if c.modalidad else "–"
            h  = str(c.horario) if c.horario else "–"
            d  = repo.usuarios.get(c.docente_email or "")
            d_txt = d.nombre_completo() if d else "⚠ Sin docente"
            filas.append((c.id, c.nombre, c.carrera or "General",
                           d_txt, h, m, c._duracion_semanas, c._total_horas))
        refrescar_tree(t, filas)
    refrescar()

    form = tk.Frame(wrap, bg=C["bg"]); form.pack(fill="x", pady=6)

    def nuevo():
        v = ventana_modal(wrap.winfo_toplevel(), "Nuevo Grupo de Nivelación", 500, 480)
        body = tk.Frame(v, bg=C["bg"], padx=20, pady=16); body.pack(fill="both", expand=True)

        campos = {}
        lbl(body, "Nombre del grupo *:", bold=True).pack(anchor="w")
        e = ttk.Entry(body, width=54); e.pack(fill="x", ipady=3, pady=(2, 8))
        campos["nombre"] = e

        lbl(body, "Carrera / Área de nivelación *:", bold=True).pack(anchor="w")
        carreras = repo.carreras_catalogo() if hasattr(repo, "carreras_catalogo") else []
        carrera_v = tk.StringVar(value=carreras[0] if carreras else "")
        ttk.Combobox(body, textvariable=carrera_v, values=carreras, state="readonly", width=52
                     ).pack(fill="x", ipady=3, pady=(2, 8))

        lbl(body, "Código del grupo (ej. A, B, C):", bold=True).pack(anchor="w")
        e = ttk.Entry(body, width=54); e.pack(fill="x", ipady=3, pady=(2, 8))
        campos["codigo"] = e

        fila = tk.Frame(body, bg=C["bg"]); fila.pack(fill="x", pady=(0, 8))
        lbl(fila, "Duración (semanas):", bold=True).pack(side="left")
        dur_e = ttk.Entry(fila, width=8); dur_e.pack(side="left", padx=8, ipady=3)
        dur_e.insert(0, "8")
        lbl(fila, "Total horas:", bold=True).pack(side="left")
        hrs_e = ttk.Entry(fila, width=8); hrs_e.pack(side="left", padx=8, ipady=3)
        hrs_e.insert(0, "256")

        lbl(body, "Modalidad:", bold=True).pack(anchor="w")
        mod_v = tk.StringVar(value="Presencial")
        ttk.Combobox(body, textvariable=mod_v, values=MODALIDADES, width=52
                     ).pack(fill="x", ipady=3, pady=(2, 8))

        lbl(body, "Docente (opcional):", bold=True).pack(anchor="w")
        d_v = tk.StringVar(value="Sin asignar")
        d_vals = ["Sin asignar"] + [f"{d.nombre_completo()}  ({d.email})" for d in repo.docentes]
        ttk.Combobox(body, textvariable=d_v, values=d_vals, width=52
                     ).pack(fill="x", ipady=3, pady=(2, 14))

        err_lbl = tk.Label(body, text="", fg=C["danger"], bg=C["bg"], font=("Segoe UI", 9))
        err_lbl.pack(anchor="w")

        def guardar():
            nombre  = campos["nombre"].get().strip()
            carrera = carrera_v.get().strip()
            if not nombre:  err_lbl.config(text="El nombre es obligatorio."); return
            if not carrera: err_lbl.config(text="La carrera es obligatoria."); return
            try: dur = int(dur_e.get()); hrs = int(hrs_e.get())
            except ValueError: err_lbl.config(text="Duración y horas deben ser números enteros."); return
            d_email = ""
            if d_v.get() != "Sin asignar":
                d_email = d_v.get().split("(")[1].rstrip(")")
            ok, msg, _ = cs.crear(nombre, carrera, dur, hrs, mod_v.get(), d_email)
            if ok:
                messagebox.showinfo("✅", msg); refrescar(); v.destroy()
            else:
                err_lbl.config(text=msg)

        btn(body, "✔  Crear grupo", C["success"], guardar, pady=9).pack(fill="x")

    def eliminar():
        sel = t.selection()
        if not sel: messagebox.showerror("Error", "Seleccione un grupo."); return
        cid   = t.item(sel[0])["values"][0]
        cnomb = t.item(sel[0])["values"][1]
        if messagebox.askyesno("Confirmar eliminación",
                               f"¿Eliminar el grupo «{cnomb}»?\nEsta acción no se puede deshacer."):
            ok, msg = cs.eliminar(cid)
            (messagebox.showinfo if ok else messagebox.showerror)("Resultado", msg)
            if ok: refrescar()

    btn(form, "➕  Nuevo grupo",  C["success"],  nuevo,    padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🗑  Eliminar",     C["danger"],   eliminar, padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🔄  Actualizar",   C["text_sec"], refrescar,padx=10, pady=5).pack(side="left", padx=4)


# ── Horarios ──────────────────────────────────────────────────────────────────
def _tab_horarios(parent, repo, hs):
    wrap = tk.Frame(parent, bg=C["bg"], padx=12, pady=8)
    wrap.pack(fill="both", expand=True)
    seccion_titulo(wrap, "Programación de Horarios")

    cols = ("ID", "Grupo / Actividad", "Día", "Hora inicio", "Hora fin", "Modalidad", "Aula / Enlace")
    t, _ = tree_con_scroll(wrap, cols, [35, 220, 100, 90, 90, 100, 160], alto=11)

    def refrescar():
        # Horarios de cursos + horarios independientes
        filas = []
        for c in repo.cursos:
            if c.horario:
                h = c.horario
                m = c.modalidad.nombre if c.modalidad else "–"
                filas.append((f"C{c.id}", c.nombre, h.dia,
                               h.hora_inicio, h.hora_fin, m, h.aula or "–"))
        for h in repo.horarios:
            filas.append((h.get("id",""), h.get("curso",""), h.get("dia",""),
                           h.get("inicio",""), h.get("fin",""),
                           h.get("modalidad",""), h.get("aula","–")))
        refrescar_tree(t, filas)
    refrescar()

    form = tk.Frame(wrap, bg=C["bg"]); form.pack(fill="x", pady=6)

    def nuevo():
        v = ventana_modal(wrap.winfo_toplevel(), "Programar Horario", 500, 440)
        body = tk.Frame(v, bg=C["bg"], padx=20, pady=16); body.pack(fill="both", expand=True)

        lbl(body, "Grupo:", bold=True).pack(anchor="w")
        c_vals = [f"{c.nombre}  (ID:{c.id})" for c in repo.cursos]
        c_v = tk.StringVar()
        ttk.Combobox(body, textvariable=c_v, values=c_vals, width=54
                     ).pack(fill="x", ipady=3, pady=(2, 8))

        lbl(body, "Día:", bold=True).pack(anchor="w")
        dia_v = tk.StringVar(value=DIAS[0])
        ttk.Combobox(body, textvariable=dia_v, values=DIAS, width=54
                     ).pack(fill="x", ipady=3, pady=(2, 8))

        fila = tk.Frame(body, bg=C["bg"]); fila.pack(fill="x", pady=(0, 8))
        lbl(fila, "Hora inicio:", bold=True).pack(side="left")
        ini_e = ttk.Entry(fila, width=10); ini_e.pack(side="left", padx=8, ipady=3)
        ini_e.insert(0, "07:30")
        lbl(fila, "Hora fin:", bold=True).pack(side="left", padx=(12, 0))
        fin_e = ttk.Entry(fila, width=10); fin_e.pack(side="left", padx=8, ipady=3)
        fin_e.insert(0, "09:30")

        lbl(body, "Modalidad:", bold=True).pack(anchor="w")
        mod_v = tk.StringVar(value="Presencial")
        ttk.Combobox(body, textvariable=mod_v, values=MODALIDADES, width=54
                     ).pack(fill="x", ipady=3, pady=(2, 8))

        lbl(body, "Aula / Plataforma virtual:", bold=True).pack(anchor="w")
        aula_e = ttk.Entry(body, width=54); aula_e.pack(fill="x", ipady=3, pady=(2, 14))

        err_lbl = tk.Label(body, text="", fg=C["danger"], bg=C["bg"], font=("Segoe UI", 9))
        err_lbl.pack(anchor="w")

        def guardar():
            sel = c_v.get()
            if not sel: err_lbl.config(text="Seleccione un grupo."); return
            if not ini_e.get().strip() or not fin_e.get().strip():
                err_lbl.config(text="Ingrese la hora de inicio y fin."); return
            try: cid = int(sel.split("ID:")[1].rstrip(")").strip())
            except (ValueError, IndexError): err_lbl.config(text="Grupo inválido."); return
            ok, msg = hs.crear(cid, dia_v.get(), ini_e.get().strip(),
                               fin_e.get().strip(), mod_v.get(), aula_e.get().strip())
            if ok:
                messagebox.showinfo("✅", msg); refrescar(); v.destroy()
            else:
                err_lbl.config(text=msg)

        btn(body, "✔  Guardar horario", C["success"], guardar, pady=9).pack(fill="x")

    def editar():
        sel = t.selection()
        if not sel: messagebox.showerror("Error", "Seleccione un horario."); return
        vals = t.item(sel[0])["values"]
        hid = vals[0]
        # Solo horarios independientes son editables (id numérico)
        if isinstance(hid, str) and hid.startswith("C"):
            messagebox.showinfo("Info", "Para editar el horario de un grupo, use la pestaña 'Grupos' y edite el grupo directamente.")
            return
        h_data = next((x for x in repo.horarios if x.get("id") == hid), None)
        if not h_data: return

        v = ventana_modal(wrap.winfo_toplevel(), "Editar Horario", 460, 380)
        body = tk.Frame(v, bg=C["bg"], padx=20, pady=16); body.pack(fill="both", expand=True)
        tk.Label(body, text=f"Editando: {h_data.get('curso','')}",
                 font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", pady=(0, 10))

        lbl(body, "Día:", bold=True).pack(anchor="w")
        dia_v = tk.StringVar(value=h_data.get("dia", DIAS[0]))
        ttk.Combobox(body, textvariable=dia_v, values=DIAS, width=50
                     ).pack(fill="x", ipady=3, pady=(2, 8))

        fila = tk.Frame(body, bg=C["bg"]); fila.pack(fill="x", pady=(0, 8))
        lbl(fila, "Inicio:", bold=True).pack(side="left")
        ini_e = ttk.Entry(fila, width=10); ini_e.pack(side="left", padx=8, ipady=3)
        ini_e.insert(0, h_data.get("inicio","07:30"))
        lbl(fila, "Fin:", bold=True).pack(side="left", padx=(12,0))
        fin_e = ttk.Entry(fila, width=10); fin_e.pack(side="left", padx=8, ipady=3)
        fin_e.insert(0, h_data.get("fin","09:30"))

        lbl(body, "Modalidad:", bold=True).pack(anchor="w")
        mod_v = tk.StringVar(value=h_data.get("modalidad", MODALIDADES[0]))
        ttk.Combobox(body, textvariable=mod_v, values=MODALIDADES, width=50
                     ).pack(fill="x", ipady=3, pady=(2, 8))

        lbl(body, "Aula / Enlace:", bold=True).pack(anchor="w")
        aula_e = ttk.Entry(body, width=50); aula_e.pack(fill="x", ipady=3, pady=(2, 14))
        aula_e.insert(0, h_data.get("aula", ""))

        def guardar():
            ok, msg = hs.editar(hid, dia_v.get(), ini_e.get().strip(),
                                fin_e.get().strip(), mod_v.get(), aula_e.get().strip())
            if ok:
                messagebox.showinfo("✅", msg); refrescar(); v.destroy()
            else:
                messagebox.showerror("Error", msg)

        btn(body, "✔  Guardar cambios", C["success"], guardar, pady=9).pack(fill="x")

    def eliminar():
        sel = t.selection()
        if not sel: messagebox.showerror("Error", "Seleccione un horario."); return
        hid = t.item(sel[0])["values"][0]
        if isinstance(hid, str) and hid.startswith("C"):
            messagebox.showinfo("Info", "Los horarios de grupo se gestionan desde la pestaña 'Grupos'.")
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar este horario?"):
            ok, msg = hs.eliminar(hid)
            (messagebox.showinfo if ok else messagebox.showerror)("Resultado", msg)
            if ok: refrescar()

    btn(form, "➕  Nuevo horario", C["success"],  nuevo,    padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "✏  Editar",        C["accent"],   editar,   padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🗑  Eliminar",      C["danger"],   eliminar, padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🔄  Actualizar",    C["text_sec"], refrescar,padx=10, pady=5).pack(side="left", padx=4)


# ── Asignación de docentes ────────────────────────────────────────────────────
def _tab_docentes(parent, repo, cs):
    wrap = tk.Frame(parent, bg=C["bg"], padx=12, pady=8)
    wrap.pack(fill="both", expand=True)
    seccion_titulo(wrap, "Asignación de Docentes a Grupos")

    cols = ("Grupo", "Carrera", "Docente actual", "Especialidad")
    t, _ = tree_con_scroll(wrap, cols, [220, 170, 200, 200], alto=11)

    def refrescar():
        filas = []
        for c in repo.cursos:
            d = repo.usuarios.get(c.docente_email or "")
            d_txt  = d.nombre_completo() if d else "⚠  Sin docente"
            d_esp  = d.especialidad if d else "–"
            filas.append((c.nombre, c.carrera or "General", d_txt, d_esp))
        refrescar_tree(t, filas)
    refrescar()

    form = tk.Frame(wrap, bg=C["bg"]); form.pack(fill="x", pady=8)
    lbl(form, "Asignar docente:", bold=True).pack(side="left", padx=(0, 8))
    d_v = tk.StringVar()
    d_vals = [f"{d.nombre_completo()}  –  {d.especialidad}  ({d.email})" for d in repo.docentes]
    ttk.Combobox(form, textvariable=d_v, values=d_vals, width=50
                 ).pack(side="left", padx=8, ipady=3)

    def asignar():
        sel = t.selection()
        if not sel: messagebox.showerror("Error", "Seleccione un grupo de la tabla."); return
        if not d_v.get(): messagebox.showerror("Error", "Seleccione un docente."); return
        cnomb = t.item(sel[0])["values"][0]
        curso = next((c for c in repo.cursos if c.nombre == cnomb), None)
        if not curso: return
        try: email = d_v.get().split("(")[1].rstrip(")")
        except IndexError: messagebox.showerror("Error", "Docente inválido."); return
        ok, msg = cs.asignar_docente(curso.id, email)
        if ok:
            messagebox.showinfo("✅", msg); refrescar()
        else:
            messagebox.showerror("Error", msg)

    btn(form, "✔  Asignar", C["success"], asignar, padx=10, pady=5).pack(side="left", padx=8)
    btn(form, "🔄  Actualizar", C["text_sec"], refrescar, padx=10, pady=5).pack(side="left", padx=4)

    # Carga horaria por docente
    ttk.Separator(wrap, orient="horizontal").pack(fill="x", pady=10)
    tk.Label(wrap, text="Carga horaria de docentes",
             font=("Segoe UI", 11, "bold"), bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", pady=(0, 6))
    cols2 = ("Docente", "Especialidad", "Grupos asignados", "Total horas")
    t2, _ = tree_con_scroll(wrap, cols2, [200, 200, 160, 120], alto=6)
    filas2 = []
    for d in repo.docentes:
        mis_grupos = [c for c in repo.cursos if c.docente_email == d.email]
        total_h = sum(c._total_horas for c in mis_grupos)
        filas2.append((d.nombre_completo(), d.especialidad, len(mis_grupos), f"{total_h} h"))
    refrescar_tree(t2, filas2)


# ── Matrículas ────────────────────────────────────────────────────────────────
def _tab_matriculas(parent, repo, ms):
    wrap = tk.Frame(parent, bg=C["bg"], padx=12, pady=8)
    wrap.pack(fill="both", expand=True)
    seccion_titulo(wrap, "Gestión de Matrículas")

    # Filtro
    fil_f = tk.Frame(wrap, bg=C["bg"]); fil_f.pack(fill="x", pady=(0, 8))
    lbl(fil_f, "Estado:", bold=True).pack(side="left")
    fil_v = tk.StringVar(value="Todos")
    for op in ("Todos", "Activa", "Pendiente", "Anulada"):
        tk.Radiobutton(fil_f, text=op, variable=fil_v, value=op,
                       bg=C["bg"], font=("Segoe UI", 9),
                       command=lambda: refrescar()).pack(side="left", padx=8)

    cols = ("ID", "Estudiante", "Carrera", "Asignatura", "Fecha", "Tipo", "Estado", "Gratuita")
    t, _ = tree_con_scroll(wrap, cols, [35, 160, 140, 170, 90, 75, 80, 70], alto=10)

    def refrescar():
        filtro = fil_v.get()
        filas = []
        for m in repo.matriculas:
            if filtro != "Todos" and m.estado != filtro: continue
            est = m.estudiante
            carrera = getattr(est, "carrera", "") if est else "–"
            filas.append((m.id, est.nombre_completo() if est else "–",
                           carrera, m.asignatura.nombre if m.asignatura else "–",
                           m.fecha, m.tipo, m.estado,
                           "Sí ✅" if m.verificarGratuidad() else "No ❌"))
        refrescar_tree(t, filas)
    refrescar()

    form = tk.Frame(wrap, bg=C["bg"]); form.pack(fill="x", pady=6)

    def aprobar():
        sel = t.selection()
        if not sel: messagebox.showerror("Error", "Seleccione una matrícula."); return
        mid = t.item(sel[0])["values"][0]
        ok, msg = ms.cambiar_estado(mid, "Activa")
        (messagebox.showinfo if ok else messagebox.showerror)("Resultado", msg)
        if ok: refrescar()

    def anular():
        sel = t.selection()
        if not sel: messagebox.showerror("Error", "Seleccione una matrícula."); return
        mid = t.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar anulación", "¿Anular esta matrícula?"):
            ok, msg = ms.cambiar_estado(mid, "Anulada")
            (messagebox.showinfo if ok else messagebox.showerror)("Resultado", msg)
            if ok: refrescar()

    def cambiar():
        sel = t.selection()
        if not sel: messagebox.showerror("Error", "Seleccione una matrícula."); return
        mid = t.item(sel[0])["values"][0]
        nuevo = simpledialog.askstring("Cambiar estado",
                                       "Nuevo estado:\n• Activa\n• Pendiente\n• Anulada")
        if nuevo:
            ok, msg = ms.cambiar_estado(mid, nuevo.strip().capitalize())
            (messagebox.showinfo if ok else messagebox.showerror)("Resultado", msg)
            if ok: refrescar()

    btn(form, "✅  Aprobar",      C["success"],  aprobar,  padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🚫  Anular",       C["danger"],   anular,   padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "✏  Cambiar estado",C["warning"],  cambiar,  padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🔄  Actualizar",   C["text_sec"], refrescar,padx=10, pady=5).pack(side="left", padx=4)


# ── Reportes ──────────────────────────────────────────────────────────────────
def _tab_reportes(parent, repo):
    wrap = tk.Frame(parent, bg=C["bg"]); wrap.pack(fill="both", expand=True)
    _, sf = scroll_canvas(wrap)

    tk.Label(sf, text="Reportes del Proceso de Nivelación",
             font=("Segoe UI", 13, "bold"), bg=C["bg"], fg=C["sidebar"]
             ).pack(anchor="w", padx=14, pady=(10, 2))
    tk.Label(sf, text=f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
             font=("Segoe UI", 9), bg=C["bg"], fg=C["text_sec"]
             ).pack(anchor="w", padx=14, pady=(0, 10))

    # Por carrera
    carreras = list({getattr(e, "carrera", "") for e in repo.estudiantes if getattr(e, "carrera","")})
    carreras.sort()
    tk.Label(sf, text="Estudiantes por carrera",
             font=("Segoe UI", 11, "bold"), bg=C["bg"], fg=C["sidebar"]
             ).pack(anchor="w", padx=14, pady=(0, 4))
    for carrera in carreras:
        ests = [e for e in repo.estudiantes if getattr(e,"carrera","") == carrera]
        mats_a = [m for m in repo.matriculas if m.estudiante and getattr(m.estudiante,"carrera","") == carrera and m.estado == "Activa"]
        col = C["sidebar"] if ests else C["text_sec"]
        ct = card(sf, col)
        fila = tk.Frame(ct, bg=C["card"]); fila.pack(fill="x")
        tk.Label(fila, text=carrera, font=("Segoe UI", 10, "bold"),
                 bg=C["card"], fg=col).pack(side="left")
        tk.Label(fila, text=f"{len(ests)} estudiante(s)  ·  {len(mats_a)} matrícula(s) activa(s)",
                 font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(side="right")

    # Por docente
    tk.Label(sf, text="Carga docente",
             font=("Segoe UI", 11, "bold"), bg=C["bg"], fg=C["sidebar"]
             ).pack(anchor="w", padx=14, pady=(14, 4))
    for d in repo.docentes:
        mis_grupos = [c for c in repo.cursos if c.docente_email == d.email]
        col = C["success"] if mis_grupos else C["danger"]
        ct = card(sf, col)
        fila = tk.Frame(ct, bg=C["card"]); fila.pack(fill="x")
        tk.Label(fila, text=d.nombre_completo(), font=("Segoe UI", 10, "bold"),
                 bg=C["card"], fg=col).pack(side="left")
        tk.Label(fila, text=f"{len(mis_grupos)} grupo(s)",
                 font=("Segoe UI", 9, "bold"), bg=C["card"], fg=col).pack(side="right")
        tk.Label(ct, text=f"Especialidad: {d.especialidad}  ·  " +
                          ("Grupos: " + ", ".join(c.nombre for c in mis_grupos) if mis_grupos else "Sin grupos asignados"),
                 font=("Segoe UI", 9), bg=C["card"], fg=C["text_sec"]).pack(anchor="w")

    # Estado de matrículas
    tk.Label(sf, text="Estado de matrículas",
             font=("Segoe UI", 11, "bold"), bg=C["bg"], fg=C["sidebar"]
             ).pack(anchor="w", padx=14, pady=(14, 4))
    estados = {"Activa": 0, "Pendiente": 0, "Anulada": 0}
    for m in repo.matriculas:
        estados[m.estado] = estados.get(m.estado, 0) + 1
    COL_EST = {"Activa": C["success"], "Pendiente": C["warning"], "Anulada": C["danger"]}
    for estado, count in estados.items():
        ct = card(sf, COL_EST.get(estado, C["text_sec"]))
        fila = tk.Frame(ct, bg=C["card"]); fila.pack(fill="x")
        tk.Label(fila, text=f"Matrículas {estado}s",
                 font=("Segoe UI", 10, "bold"), bg=C["card"],
                 fg=COL_EST.get(estado, C["text_sec"])).pack(side="left")
        tk.Label(fila, text=str(count), font=("Segoe UI", 14, "bold"),
                 bg=C["card"], fg=COL_EST.get(estado, C["text_sec"])).pack(side="right")

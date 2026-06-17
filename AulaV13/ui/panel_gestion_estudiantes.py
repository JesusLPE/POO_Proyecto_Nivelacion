"""ui/panel_gestion_estudiantes.py

Apartado de Gestión de Estudiantes, compartido por Administrador y
Coordinador con control de acceso por roles (RBAC):

- Administrador: puede CREAR, editar, reasignar curso/horario, dar de
  baja y eliminar estudiantes.
- Coordinador: puede EDITAR información existente, reasignar
  curso/horario, dar de baja (registrar retiro) — pero el botón de
  "Nuevo estudiante" se oculta para este rol.

La diferencia de permisos se resuelve con un único parámetro `puede_crear`.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from ui.base import C, btn, lbl, tree_con_scroll, refrescar_tree, ventana_modal, seccion_titulo
from ui.shared import seleccionar_carrera
from services.academico import UsuarioService, AuthService, validar_cedula_ecuatoriana


def construir_tab(parent, repo, usuario_actual, puede_crear: bool):
    """Construye el apartado de gestión de estudiantes.

    `puede_crear` controla el RBAC: True para Administrador, False
    para Coordinador (que solo edita/reasigna/da de baja).
    """
    us = UsuarioService(repo)

    wrap = tk.Frame(parent, bg=C["bg"], padx=12, pady=8)
    wrap.pack(fill="both", expand=True)
    seccion_titulo(wrap, "Gestión de Estudiantes")

    if not puede_crear:
        lbl(wrap, "Como Coordinador puede editar, reasignar curso/horario y dar de baja "
                  "a estudiantes existentes. La creación de nuevos estudiantes "
                  "está reservada al Administrador.",
            size=9, color=C["text_sec"]).pack(anchor="w", pady=(0, 8))

    cols = ("Email", "Cédula", "Nombre completo", "Matrícula", "Carrera", "Curso", "Horario", "Estado")
    t, _ = tree_con_scroll(wrap, cols, [200, 100, 160, 105, 150, 190, 125, 90], alto=12)

    def _curso_nombre(curso_id):
        c = repo.curso_por_id(curso_id)
        return c.nombre if c else "Sin asignar"

    def _horario_texto(horario_id):
        h = repo.horario_por_id(horario_id)
        if not h:
            return "Sin asignar"
        return f"{h.get('dia','')} {h.get('inicio','')}-{h.get('fin','')}"

    def refrescar():
        filas = []
        for e in repo.estudiantes:
            estado = "Activo" if e.curso_id else "Sin grupo / Baja"
            filas.append((e.email, getattr(e, "cedula", ""), e.nombre_completo(), e.matricula, e.carrera,
                           _curso_nombre(e.curso_id), _horario_texto(e.horario_id), estado))
        refrescar_tree(t, filas)
    refrescar()

    form = tk.Frame(wrap, bg=C["bg"]); form.pack(fill="x", pady=6)

    # ── Selector combinado de curso + horario ──────────────────────────────
    def _seleccionar_curso_horario(titulo_v, curso_actual=None, horario_actual=None):
        """Devuelve (curso_id, horario_id) elegidos por el usuario, o (None, None)."""
        v = ventana_modal(wrap.winfo_toplevel(), titulo_v, 480, 320)
        body = tk.Frame(v, bg=C["bg"], padx=20, pady=16); body.pack(fill="both", expand=True)

        lbl(body, "Curso / Grupo de nivelación *:", bold=True).pack(anchor="w")
        curso_vals = [f"{c.nombre}  (ID:{c.id})" for c in repo.cursos]
        curso_v = tk.StringVar()
        curso_cb = ttk.Combobox(body, textvariable=curso_v, values=curso_vals,
                                state="readonly", width=54)
        curso_cb.pack(fill="x", ipady=3, pady=(2, 10))

        lbl(body, "Horario *:", bold=True).pack(anchor="w")
        horario_v = tk.StringVar()
        horario_cb = ttk.Combobox(body, textvariable=horario_v, values=[],
                                  state="readonly", width=54)
        horario_cb.pack(fill="x", ipady=3, pady=(2, 14))

        def _actualizar_horarios(*_):
            sel = curso_v.get()
            if not sel:
                horario_cb.config(values=[]); horario_v.set(""); return
            try:
                cid = int(sel.split("ID:")[1].rstrip(")").strip())
            except (ValueError, IndexError):
                return
            hs = repo.horarios_de_curso(cid)
            vals = [f"{h.get('dia','')} {h.get('inicio','')}-{h.get('fin','')}  (ID:{h.get('id')})"
                    for h in hs]
            horario_cb.config(values=vals)
            horario_v.set(vals[0] if vals else "")

        curso_cb.bind("<<ComboboxSelected>>", _actualizar_horarios)

        # Preseleccionar valores actuales si los hay
        if curso_actual:
            preset = next((v_ for v_ in curso_vals if f"ID:{curso_actual}" in v_), "")
            curso_v.set(preset)
            _actualizar_horarios()
            if horario_actual:
                hpreset = next((v_ for v_ in horario_cb["values"] if f"ID:{horario_actual}" in v_), "")
                if hpreset:
                    horario_v.set(hpreset)

        err_lbl = tk.Label(body, text="", fg=C["danger"], bg=C["bg"], font=("Segoe UI", 9))
        err_lbl.pack(anchor="w")

        resultado = {"curso_id": None, "horario_id": None}

        def aceptar():
            sel_c = curso_v.get()
            sel_h = horario_v.get()
            if not sel_c or not sel_h:
                err_lbl.config(text="Debe seleccionar curso y horario."); return
            try:
                resultado["curso_id"] = int(sel_c.split("ID:")[1].rstrip(")").strip())
                resultado["horario_id"] = int(sel_h.split("ID:")[1].rstrip(")").strip())
            except (ValueError, IndexError):
                err_lbl.config(text="Selección inválida."); return
            v.destroy()

        btn(body, "✔  Confirmar", C["success"], aceptar, pady=8).pack(fill="x")
        v.wait_window()
        return resultado["curso_id"], resultado["horario_id"]

    # ── Crear (solo Administrador) ─────────────────────────────────────────
    def nuevo():
        v = ventana_modal(wrap.winfo_toplevel(), "Nuevo estudiante", 460, 480)
        body = tk.Frame(v, bg=C["bg"], padx=20, pady=16); body.pack(fill="both", expand=True)

        campos = {}
        for etq, key, show in [("Nombre *:", "nombre", ""), ("Apellido *:", "apellido", ""),
                                ("Cédula *:", "cedula", ""),
                                ("Correo electrónico *:", "email", ""),
                                ("Contraseña inicial *:", "pwd", "*"),
                                ("Matrícula *:", "matricula", "")]:
            lbl(body, etq, bold=True).pack(anchor="w")
            e = ttk.Entry(body, width=50, show=show)
            e.pack(fill="x", ipady=4, pady=(2, 8)); campos[key] = e

        err_lbl = tk.Label(body, text="", fg=C["danger"], bg=C["bg"], font=("Segoe UI", 9))
        err_lbl.pack(anchor="w", pady=(6, 0))

        def guardar():
            nombre   = campos["nombre"].get().strip()
            apellido = campos["apellido"].get().strip()
            cedula   = campos["cedula"].get().strip()
            email    = campos["email"].get().strip()
            pwd      = campos["pwd"].get()
            mat      = campos["matricula"].get().strip()
            if not all([nombre, apellido, cedula, email, pwd, mat]):
                err_lbl.config(text="Todos los campos son obligatorios."); return
            if not validar_cedula_ecuatoriana(cedula):
                err_lbl.config(text="Ingrese una cédula ecuatoriana válida."); return
            if not AuthService(repo).validar_email(email):
                err_lbl.config(text="El correo electrónico no es válido."); return

            car = seleccionar_carrera(wrap.winfo_toplevel(), repo)
            if not car:
                err_lbl.config(text="Debe seleccionar una carrera."); return

            curso_id, horario_id = _seleccionar_curso_horario("Asignar curso y horario")
            if curso_id is None or horario_id is None:
                err_lbl.config(text="Debe seleccionar curso y horario para continuar."); return

            ok, msg = us.crear_estudiante(nombre, apellido, email, pwd, cedula, mat, car,
                                          curso_id=curso_id, horario_id=horario_id)
            if ok:
                messagebox.showinfo("✅", msg); refrescar(); v.destroy()
            else:
                err_lbl.config(text=msg)

        btn(body, "✔  Registrar estudiante", C["success"], guardar, pady=9).pack(fill="x", pady=(10, 0))

    # ── Editar (Administrador y Coordinador) ───────────────────────────────
    def editar():
        sel = t.selection()
        if not sel: messagebox.showerror("Error", "Seleccione un estudiante."); return
        email = t.item(sel[0])["values"][0]
        est = repo.usuarios.get(email)
        if not est: return

        v = ventana_modal(wrap.winfo_toplevel(), f"Editar: {est.nombre_completo()}", 460, 410)
        body = tk.Frame(v, bg=C["bg"], padx=20, pady=16); body.pack(fill="both", expand=True)

        lbl(body, "Nombre:", bold=True).pack(anchor="w")
        nom_e = ttk.Entry(body, width=50); nom_e.insert(0, est.nombre)
        nom_e.pack(fill="x", ipady=4, pady=(2, 8))

        lbl(body, "Apellido:", bold=True).pack(anchor="w")
        ape_e = ttk.Entry(body, width=50); ape_e.insert(0, est.apellido)
        ape_e.pack(fill="x", ipady=4, pady=(2, 8))

        lbl(body, "Cédula:", bold=True).pack(anchor="w")
        ced_e = ttk.Entry(body, width=50); ced_e.insert(0, getattr(est, "cedula", ""))
        ced_e.pack(fill="x", ipady=4, pady=(2, 8))

        lbl(body, "Carrera:", bold=True).pack(anchor="w")
        car_e = ttk.Entry(body, width=50); car_e.insert(0, est.carrera)
        car_e.pack(fill="x", ipady=4, pady=(2, 8))

        lbl(body, f"Curso actual: {_curso_nombre(est.curso_id)}", size=9,
            color=C["text_sec"]).pack(anchor="w")
        lbl(body, f"Horario actual: {_horario_texto(est.horario_id)}", size=9,
            color=C["text_sec"]).pack(anchor="w", pady=(0, 8))

        err_lbl = tk.Label(body, text="", fg=C["danger"], bg=C["bg"], font=("Segoe UI", 9))
        err_lbl.pack(anchor="w")

        def reasignar():
            curso_id, horario_id = _seleccionar_curso_horario(
                "Reasignar curso y horario", est.curso_id, est.horario_id)
            if curso_id is None or horario_id is None:
                return
            ok, msg = us.editar_estudiante(est.email, curso_id=curso_id, horario_id=horario_id)
            if ok:
                messagebox.showinfo("✅", msg); refrescar(); v.destroy()
            else:
                err_lbl.config(text=msg)

        def guardar_datos():
            ok, msg = us.editar_estudiante(
                est.email, nombre=nom_e.get().strip(),
                apellido=ape_e.get().strip(), cedula=ced_e.get().strip(), carrera=car_e.get().strip())
            if ok:
                messagebox.showinfo("✅", msg); refrescar(); v.destroy()
            else:
                err_lbl.config(text=msg)

        btn(body, "🔁  Reasignar curso / horario", C["accent"], reasignar, pady=8).pack(fill="x", pady=(8, 4))
        btn(body, "✔  Guardar datos personales", C["success"], guardar_datos, pady=8).pack(fill="x")

    # ── Dar de baja (Administrador y Coordinador) ──────────────────────────
    def dar_de_baja():
        sel = t.selection()
        if not sel: messagebox.showerror("Error", "Seleccione un estudiante."); return
        email = t.item(sel[0])["values"][0]
        nombre = t.item(sel[0])["values"][2]
        if messagebox.askyesno("Confirmar baja",
                               f"¿Dar de baja a {nombre}?\n\n"
                               "Se anularán sus matrículas activas y se liberará "
                               "su curso y horario asignados."):
            ok, msg = us.dar_de_baja(email)
            (messagebox.showinfo if ok else messagebox.showerror)("Resultado", msg)
            if ok: refrescar()

    # ── Eliminar (solo Administrador) ───────────────────────────────────────
    def eliminar():
        sel = t.selection()
        if not sel: messagebox.showerror("Error", "Seleccione un estudiante."); return
        email = t.item(sel[0])["values"][0]
        nombre = t.item(sel[0])["values"][2]
        if messagebox.askyesno("Confirmar eliminación",
                               f"¿Eliminar permanentemente a {nombre} ({email})?\n"
                               "Esta acción no se puede deshacer."):
            ok, msg = us.eliminar_usuario(email, usuario_actual)
            (messagebox.showinfo if ok else messagebox.showerror)("Resultado", msg)
            if ok: refrescar()

    # RBAC: el botón de creación solo aparece para quien tiene puede_crear=True
    if puede_crear:
        btn(form, "➕  Nuevo estudiante", C["success"], nuevo, padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "✏  Editar / Reasignar", C["accent"],  editar,     padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🚫  Dar de baja",        C["warning"], dar_de_baja,padx=10, pady=5).pack(side="left", padx=4)
    if puede_crear:
        btn(form, "🗑  Eliminar", C["danger"], eliminar, padx=10, pady=5).pack(side="left", padx=4)
    btn(form, "🔄  Actualizar", C["text_sec"], refrescar, padx=10, pady=5).pack(side="left", padx=4)

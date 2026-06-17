"""ui/shared.py – Paneles compartidos por todos los roles."""
import tkinter as tk
from tkinter import ttk, messagebox
from ui.base import C, ROL_COLOR, card, scroll_canvas, tree_con_scroll, refrescar_tree


def panel_perfil(parent, usuario, repo=None, on_save=None):
    rol = usuario.obtener_rol()
    color = ROL_COLOR.get(rol, C["accent"])
    wrap = tk.Frame(parent, bg=C["bg"])
    wrap.pack(fill="both", expand=True)

    # Encabezado con avatar
    header = tk.Frame(wrap, bg=color, height=120)
    header.pack(fill="x")
    header.pack_propagate(False)
    av = tk.Frame(header, bg=C["white"], width=72, height=72)
    av.place(relx=0.5, rely=0.5, anchor="center")
    av.pack_propagate(False)
    tk.Label(av, text=(usuario.nombre[0].upper() if usuario.nombre else "?"),
             font=("Segoe UI", 28, "bold"), bg=C["white"], fg=color
             ).place(relx=0.5, rely=0.5, anchor="center")

    body = tk.Frame(wrap, bg=C["bg"], padx=40, pady=20)
    body.pack(fill="both", expand=True)

    tk.Label(body, text=usuario.nombre_completo(),
             font=("Segoe UI", 16, "bold"), bg=C["bg"], fg=C["text"]).pack(pady=(0, 2))
    badge_txt = {"estudiante": "Estudiante", "docente": "Docente",
                 "coordinador": "Coordinador", "administrador": "Administrador"}.get(rol, rol)
    tk.Label(body, text=f"  {badge_txt}  ", bg=color, fg=C["white"],
             font=("Segoe UI", 9, "bold"), padx=10, pady=3).pack(pady=(0, 16))

    # Tarjeta de datos
    card_f = tk.Frame(body, bg=C["card"], bd=1, relief="solid", padx=24, pady=16)
    card_f.pack(fill="x")

    campos = [("Correo electrónico", usuario.email),
              ("Nombre", usuario.nombre),
              ("Apellido", usuario.apellido)]
    if hasattr(usuario, "matricula"):     campos.append(("Número de matrícula", usuario.matricula))
    if hasattr(usuario, "carrera"):       campos.append(("Carrera / Programa", usuario.carrera))
    if hasattr(usuario, "especialidad"):  campos.append(("Especialidad", usuario.especialidad))

    for i, (etiqueta, valor) in enumerate(campos):
        fila = tk.Frame(card_f, bg=C["card"])
        fila.pack(fill="x", pady=4)
        if i > 0:
            ttk.Separator(card_f, orient="horizontal").pack(fill="x", pady=2)
            fila = tk.Frame(card_f, bg=C["card"])
            fila.pack(fill="x", pady=4)
        tk.Label(fila, text=etiqueta, font=("Segoe UI", 9),
                 bg=C["card"], fg=C["text_sec"], width=22, anchor="w").pack(side="left")
        tk.Label(fila, text=str(valor), font=("Segoe UI", 10, "bold"),
                 bg=C["card"], fg=C["text"]).pack(side="left", padx=8)

    # Cambiar contraseña
    tk.Label(body, text="Cambiar contraseña", font=("Segoe UI", 11, "bold"),
             bg=C["bg"], fg=C["text"]).pack(anchor="w", pady=(20, 6))
    pwd_frame = tk.Frame(body, bg=C["card"], bd=1, relief="solid", padx=20, pady=14)
    pwd_frame.pack(fill="x")

    tk.Label(pwd_frame, text="Contraseña actual:", font=("Segoe UI", 9),
             bg=C["card"], fg=C["text_sec"]).pack(anchor="w")
    actual_e = ttk.Entry(pwd_frame, show="*", width=36)
    actual_e.pack(anchor="w", ipady=3, pady=(2, 8))

    tk.Label(pwd_frame, text="Nueva contraseña:", font=("Segoe UI", 9),
             bg=C["card"], fg=C["text_sec"]).pack(anchor="w")
    nueva_e = ttk.Entry(pwd_frame, show="*", width=36)
    nueva_e.pack(anchor="w", ipady=3, pady=(2, 8))

    tk.Label(pwd_frame, text="Confirmar nueva contraseña:", font=("Segoe UI", 9),
             bg=C["card"], fg=C["text_sec"]).pack(anchor="w")
    confirm_e = ttk.Entry(pwd_frame, show="*", width=36)
    confirm_e.pack(anchor="w", ipady=3, pady=(2, 10))

    msg_lbl = tk.Label(pwd_frame, text="", font=("Segoe UI", 9),
                       bg=C["card"], fg=C["danger"])
    msg_lbl.pack(anchor="w")

    def cambiar_pwd():
        actual = actual_e.get()
        nueva = nueva_e.get()
        confirm = confirm_e.get()
        if not usuario.iniciarSesion(usuario.email, actual):
            msg_lbl.config(text="La contraseña actual es incorrecta.", fg=C["danger"]); return
        if len(nueva) < 6:
            msg_lbl.config(text="La contraseña debe tener al menos 6 caracteres.", fg=C["danger"]); return
        if nueva != confirm:
            msg_lbl.config(text="Las contraseñas no coinciden.", fg=C["danger"]); return
        # Guardar en JSON
        if repo:
            from repositories.repositorio_academico import RepositorioAcademico
            rol_u = usuario.obtener_rol()
            # Recrear objeto con nueva password
            if rol_u == "estudiante":
                from models.usuarios import Estudiante
                nuevo = Estudiante(usuario.nombre, usuario.apellido, usuario.email,
                                   nueva, usuario.matricula, usuario.carrera)
                repo.estudiantes[:] = [e if e.email != usuario.email else nuevo for e in repo.estudiantes]
                repo.usuarios[usuario.email] = nuevo
                repo.guardar_estudiantes()
            elif rol_u == "docente":
                from models.usuarios import Docente
                nuevo = Docente(usuario.nombre, usuario.apellido, usuario.email,
                                nueva, usuario.especialidad)
                repo.docentes[:] = [d if d.email != usuario.email else nuevo for d in repo.docentes]
                repo.usuarios[usuario.email] = nuevo
                repo.guardar_docentes()
        msg_lbl.config(text="✅ Contraseña actualizada correctamente.", fg=C["success"])
        actual_e.delete(0, tk.END)
        nueva_e.delete(0, tk.END)
        confirm_e.delete(0, tk.END)

    tk.Button(pwd_frame, text="Actualizar contraseña", bg=color, fg=C["white"],
              font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
              padx=12, pady=6, command=cambiar_pwd).pack(anchor="w", pady=(6, 0))


# ── Renderizado genérico del producto Reporte (patrón Builder) ────────────────
def render_reporte(parent, reporte, color_header=None):
    """Pinta un objeto `Reporte` (models.reporte.Reporte) en `parent`.

    Es deliberadamente genérico: no le importa qué builder construyó el
    reporte, solo recorre sus secciones y totales y los dibuja con los
    widgets compartidos (tarjetas, tablas con scroll).
    """
    color_header = color_header or C["sidebar"]

    wrap = tk.Frame(parent, bg=C["bg"])
    wrap.pack(fill="both", expand=True)
    _, sf = scroll_canvas(wrap)

    # Encabezado
    hdr = tk.Frame(sf, bg=color_header, padx=18, pady=14)
    hdr.pack(fill="x", padx=12, pady=(10, 6))
    tk.Label(hdr, text=reporte.titulo, font=("Segoe UI", 13, "bold"),
             bg=color_header, fg=C["white"]).pack(anchor="w")
    if reporte.subtitulo:
        tk.Label(hdr, text=reporte.subtitulo, font=("Segoe UI", 10),
                 bg=color_header, fg="#E8EAF6").pack(anchor="w")
    tk.Label(hdr, text=f"Generado: {reporte.generado_en}", font=("Segoe UI", 9),
             bg=color_header, fg="#C5CAE9").pack(anchor="w", pady=(2, 0))

    # Totales / indicadores
    if reporte.totales:
        grid = tk.Frame(sf, bg=C["bg"]); grid.pack(fill="x", padx=12, pady=6)
        cols = min(len(reporte.totales), 4)
        for i, (etiqueta, valor) in enumerate(reporte.totales):
            cf = tk.Frame(grid, bg=color_header)
            cf.grid(row=i // cols, column=i % cols, padx=6, pady=4, sticky="ew")
            grid.columnconfigure(i % cols, weight=1)
            inner = tk.Frame(cf, bg=C["card"], padx=14, pady=10)
            inner.pack(fill="both", padx=2, pady=2)
            tk.Label(inner, text=str(valor), font=("Segoe UI", 16, "bold"),
                     bg=C["card"], fg=color_header).pack()
            tk.Label(inner, text=etiqueta, font=("Segoe UI", 9),
                     bg=C["card"], fg=C["text_sec"]).pack()

    # Secciones (tablas)
    for seccion in reporte.secciones:
        tk.Label(sf, text=seccion.titulo, font=("Segoe UI", 11, "bold"),
                 bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", padx=14, pady=(12, 4))
        if seccion.filas:
            anchos = [max(90, 600 // len(seccion.columnas))] * len(seccion.columnas)
            t, _ = tree_con_scroll(sf, seccion.columnas, anchos,
                                   alto=min(max(len(seccion.filas), 1), 10))
            refrescar_tree(t, seccion.filas)
        else:
            tk.Label(sf, text="Sin datos para mostrar.", font=("Segoe UI", 9),
                     bg=C["bg"], fg=C["text_sec"]).pack(anchor="w", padx=14)
        if seccion.nota:
            tk.Label(sf, text=seccion.nota, font=("Segoe UI", 9),
                     bg=C["bg"], fg=C["text_sec"], wraplength=620,
                     justify="left").pack(anchor="w", padx=14, pady=(2, 0))

    # Pie
    if reporte.pie:
        tk.Label(sf, text=reporte.pie, font=("Segoe UI", 8),
                 bg=C["bg"], fg=C["text_sec"]).pack(anchor="w", padx=14, pady=(14, 10))


# ── Selector de carrera desde el catálogo de facultades ───────────────────────
def seleccionar_carrera(root, repo):
    """Muestra un selector de carrera usando el catálogo de facultades.

    Reutilizable desde cualquier panel que necesite asignar una carrera
    a un usuario (Administrador al crear estudiantes, etc.).
    """
    from tkinter import simpledialog
    from ui.base import ventana_modal, btn, lbl, C

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

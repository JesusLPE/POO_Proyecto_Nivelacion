"""ui/base.py – Estilos, colores y widgets reutilizables."""
import tkinter as tk
from tkinter import ttk

# ── Paleta ────────────────────────────────────────────────────────────────────
C = {
    "bg":       "#F0F4F8",
    "sidebar":  "#1A237E",
    "sidebar2": "#283593",
    "accent":   "#3949AB",
    "accent2":  "#5C6BC0",
    "success":  "#2E7D32",
    "danger":   "#C62828",
    "warning":  "#E65100",
    "white":    "#FFFFFF",
    "card":     "#FFFFFF",
    "text":     "#212121",
    "text_sec": "#546E7A",
    "border":   "#CFD8DC",
    "row_alt":  "#F5F5F5",
}

ROL_COLOR = {
    "estudiante":    "#1565C0",
    "docente":       "#2E7D32",
    "coordinador":   "#6A1B9A",
    "administrador": "#BF360C",
}

DIAS       = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
MODALIDADES = ["Presencial", "Virtual", "Híbrida"]


def aplicar_estilo():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("TFrame",         background=C["bg"])
    s.configure("TLabel",         background=C["bg"], foreground=C["text"])
    s.configure("TNotebook",      background=C["bg"])
    s.configure("TNotebook.Tab",  font=("Segoe UI", 10), padding=[12, 6])
    s.configure("Treeview",       background=C["white"], fieldbackground=C["white"],
                foreground=C["text"], rowheight=26, font=("Segoe UI", 9))
    s.configure("Treeview.Heading", background="#E8EAF6",
                foreground=C["text"], font=("Segoe UI", 9, "bold"))
    s.map("Treeview", background=[("selected", C["accent2"])])
    s.configure("TEntry",    fieldbackground=C["white"],
                foreground=C["text"], padding=5, font=("Segoe UI", 10))
    s.configure("TCombobox", fieldbackground=C["white"],
                foreground=C["text"], font=("Segoe UI", 10))
    s.configure("TSpinbox",  fieldbackground=C["white"],
                foreground=C["text"], font=("Segoe UI", 10))
    s.configure("TSeparator", background=C["border"])


# ── Widgets reutilizables ─────────────────────────────────────────────────────
def btn(parent, texto, color, comando, **kw):
    return tk.Button(parent, text=texto, bg=color, fg=C["white"],
                     font=("Segoe UI", 10, "bold"), relief="flat",
                     cursor="hand2", activebackground=color,
                     activeforeground=C["white"], command=comando, **kw)


def lbl(parent, texto, bold=False, size=10, color=None, bg=None):
    return tk.Label(parent, text=texto,
                    font=("Segoe UI", size, "bold" if bold else "normal"),
                    bg=bg or C["bg"], fg=color or C["text"])


def tree_con_scroll(parent, columnas: list, anchos: list, alto: int = 12):
    frame = tk.Frame(parent, bg=C["bg"])
    t = ttk.Treeview(frame, columns=columnas, show="headings", height=alto)
    for col, w in zip(columnas, anchos):
        t.heading(col, text=col)
        t.column(col, width=w, anchor="w")
    sb = ttk.Scrollbar(frame, orient="vertical", command=t.yview)
    t.configure(yscrollcommand=sb.set)
    t.pack(side="left", fill="both", expand=True)
    sb.pack(side="left", fill="y")
    frame.pack(fill="both", expand=True)
    # Colores alternos
    t.tag_configure("alt", background=C["row_alt"])
    return t, frame


def refrescar_tree(tree, filas: list):
    for i in tree.get_children():
        tree.delete(i)
    for idx, fila in enumerate(filas):
        tag = "alt" if idx % 2 else ""
        tree.insert("", "end", values=fila, tags=(tag,))


def ventana_modal(root, titulo: str, ancho: int = 540, alto: int = 440):
    v = tk.Toplevel(root)
    v.title(titulo)
    v.geometry(f"{ancho}x{alto}")
    v.configure(bg=C["bg"])
    v.transient(root)
    v.grab_set()
    v.resizable(True, True)
    # Header coloreado
    h = tk.Frame(v, bg=C["sidebar"], height=42)
    h.pack(fill="x")
    h.pack_propagate(False)
    tk.Label(h, text=titulo, bg=C["sidebar"], fg=C["white"],
             font=("Segoe UI", 11, "bold")).pack(side="left", padx=16, pady=10)
    return v


def formulario_campo(parent, etiqueta: str, widget_fn, **kw):
    """Dibuja label + widget en vertical."""
    tk.Label(parent, text=etiqueta, font=("Segoe UI", 9, "bold"),
             bg=C["bg"], fg=C["text"]).pack(anchor="w")
    w = widget_fn(parent, **kw)
    w.pack(fill="x", ipady=3, pady=(1, 8))
    return w


def seccion_titulo(parent, texto: str, color=None):
    tk.Label(parent, text=texto, font=("Segoe UI", 12, "bold"),
             bg=C["bg"], fg=color or C["sidebar"]).pack(anchor="w", pady=(0, 8))


def card(parent, color: str):
    outer = tk.Frame(parent, bg=color, pady=1)
    outer.pack(fill="x", pady=4, padx=8)
    inner = tk.Frame(outer, bg=C["card"], padx=14, pady=10)
    inner.pack(fill="x", padx=2)
    stripe = tk.Frame(inner, bg=color, width=5)
    stripe.pack(side="left", fill="y")
    content = tk.Frame(inner, bg=C["card"])
    content.pack(side="left", fill="both", expand=True, padx=10)
    return content


def scroll_canvas(parent):
    """Devuelve (canvas, frame_interior) con scrollbar vertical.

    El binding del mousewheel se activa SOLO cuando el puntero está
    sobre el canvas (bind en <Enter>) y se desactiva al salir (<Leave>).
    Esto evita que handlers de canvases ya destruidos sigan ejecutándose
    y lancen _tkinter.TclError al cambiar de pestaña.
    """
    canvas = tk.Canvas(parent, bg=C["bg"], highlightthickness=0)
    sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    sf = tk.Frame(canvas, bg=C["bg"])
    sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    win = canvas.create_window((0, 0), window=sf, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    def _on_mousewheel(event):
        # Guard: el canvas puede haber sido destruido entre llamadas
        try:
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    def _bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _unbind_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")

    # Activar solo mientras el puntero esté sobre este canvas
    canvas.bind("<Enter>", _bind_mousewheel)
    canvas.bind("<Leave>", _unbind_mousewheel)

    return canvas, sf

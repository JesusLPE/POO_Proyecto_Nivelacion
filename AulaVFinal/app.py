"""app.py – Sistema de Admisión del Proceso de Nivelación v12.0"""
import tkinter as tk
from tkinter import ttk, messagebox

from repositories.json_manager import JsonManager
from repositories.repositorio_academico import RepositorioAcademico
from services.academico import AuthService
from ui.base import C, ROL_COLOR, aplicar_estilo
import ui.panel_estudiante   as pe
import ui.panel_docente      as pd
import ui.panel_coordinador  as pc
import ui.panel_administrador as pa


# POO: Clase (orquestador principal de la aplicación Tkinter)
class SistemaAcademicoApp:
    """Punto de entrada. SRP: solo orquesta ventana, login y despacho de paneles."""

    # POO: Constructor
    # POO: Inyección de dependencias -> recibe "repo" ya armado (con su
    # storage) en vez de construirlo aquí dentro
    def __init__(self, repo: RepositorioAcademico):
        self.repo = repo
        self.auth = AuthService(repo)
        self.current_user = None

        self.root = tk.Tk()
        self.root.title("Sistema de Admisión – Proceso de Nivelación")
        self.root.state("zoomed")
        self.root.configure(bg=C["bg"])
        self.root.protocol("WM_DELETE_WINDOW", self._confirmar_salida)
        aplicar_estilo()
        self._show_login()

    # ── Login ─────────────────────────────────────────────────────────────────
    def _show_login(self):
        self._limpiar()

        # Panel izquierdo – identidad institucional
        left = tk.Frame(self.root, bg=C["sidebar"], width=440)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Frame(left, bg=C["sidebar"]).pack(expand=True)

        # Logo institucional simulado
        logo_f = tk.Frame(left, bg=C["accent"], width=90, height=90)
        logo_f.pack(pady=(0, 14))
        logo_f.pack_propagate(False)
        tk.Label(logo_f, text="NU", font=("Segoe UI", 28, "bold"),
                 bg=C["accent"], fg=C["white"]).place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(left, text="Uleam",
                 font=("Segoe UI", 18, "bold"), bg=C["sidebar"], fg=C["white"]).pack()
        tk.Label(left, text="Sistema de Admisión",
                 font=("Segoe UI", 12), bg=C["sidebar"], fg="#9FA8DA").pack(pady=2)
        tk.Label(left, text="Proceso de Nivelación",
                 font=("Segoe UI", 12), bg=C["sidebar"], fg="#9FA8DA").pack()

        # Separador decorativo
        sep = tk.Frame(left, bg=C["sidebar"]); sep.pack(pady=16)
        for col, w in [(C["accent2"], 80), (C["accent"], 40), (C["sidebar2"], 20)]:
            tk.Frame(sep, bg=col, width=w, height=3).pack(side="left", padx=2)

        # Información del período
        info_f = tk.Frame(left, bg=C["sidebar2"], padx=20, pady=14)
        info_f.pack(fill="x", padx=24)
        tk.Label(info_f, text="Período Académico 2026",
                 font=("Segoe UI", 10, "bold"), bg=C["sidebar2"], fg=C["white"]).pack(anchor="w")
        from datetime import datetime
        tk.Label(info_f, text=f"{datetime.now().strftime('%d/%m/%Y')}",
                 font=("Segoe UI", 9), bg=C["sidebar2"], fg="#C5CAE9").pack(anchor="w")

        # Roles disponibles
        roles_f = tk.Frame(left, bg=C["sidebar"]); roles_f.pack(pady=16)
        for rol, col in ROL_COLOR.items():
            etq = {"estudiante": "Estudiante", "docente": "Docente",
                   "coordinador": "Coordinador", "administrador": "Administrador"}.get(rol, rol)
            tk.Label(roles_f, text=f"  {etq}  ", bg=col, fg=C["white"],
                     font=("Segoe UI", 8, "bold"), padx=6, pady=3).pack(side="left", padx=2)

        tk.Frame(left, bg=C["sidebar"]).pack(expand=True)
        tk.Label(left, text="© 2026  Universidad Laica Eloy Alfaro de Manabí·",
                 font=("Segoe UI", 8), bg=C["sidebar"], fg="#5C6BC0",
                 wraplength=380, justify="center").pack(pady=12, padx=20)

        # Panel derecho – formulario
        right = tk.Frame(self.root, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True)
        form_wrap = tk.Frame(right, bg=C["bg"])
        form_wrap.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(form_wrap, text="Bienvenido",
                 font=("Segoe UI", 24, "bold"), bg=C["bg"], fg=C["sidebar"]).pack(pady=(0, 4))
        tk.Label(form_wrap, text="Ingrese sus credenciales institucionales para continuar",
                 font=("Segoe UI", 10), bg=C["bg"], fg=C["text_sec"]).pack(pady=(0, 24))

        # Campo email
        tk.Label(form_wrap, text="Correo institucional",
                 font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        self._email_e = ttk.Entry(form_wrap, width=40, font=("Segoe UI", 11))
        self._email_e.pack(ipady=5, pady=(2, 14), fill="x")

        # Campo contraseña con toggle
        tk.Label(form_wrap, text="Contraseña",
                 font=("Segoe UI", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        pwd_row = tk.Frame(form_wrap, bg=C["bg"]); pwd_row.pack(fill="x", pady=(2, 0))
        self._pwd_e = ttk.Entry(pwd_row, show="*", font=("Segoe UI", 11))
        self._pwd_e.pack(side="left", fill="x", expand=True, ipady=5)
        self._show_pwd = False
        def toggle():
            self._show_pwd = not self._show_pwd
            self._pwd_e.config(show="" if self._show_pwd else "*")
            eye.config(text="🙈" if self._show_pwd else "👁")
        eye = tk.Button(pwd_row, text="👁", bg=C["bg"], fg=C["text_sec"],
                        relief="flat", cursor="hand2",
                        font=("Segoe UI", 12), command=toggle)
        eye.pack(side="right", padx=4)

        # Error label
        self._err_lbl = tk.Label(form_wrap, text="", fg=C["danger"],
                                 font=("Segoe UI", 9), bg=C["bg"])
        self._err_lbl.pack(pady=(8, 0))

        # Botón ingresar
        login_btn = tk.Button(form_wrap, text="Ingresar al sistema  →",
                              bg=C["accent"], fg=C["white"],
                              font=("Segoe UI", 12, "bold"), relief="flat",
                              cursor="hand2", padx=20, pady=11,
                              command=self._do_login)
        login_btn.pack(fill="x", pady=(10, 0))
        login_btn.bind("<Enter>", lambda e: login_btn.config(bg=C["sidebar"]))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg=C["accent"]))

        self._pwd_e.bind("<Return>", lambda e: self._do_login())
        self._email_e.bind("<Return>", lambda e: self._pwd_e.focus())
        self._email_e.focus()


    def _do_login(self):
        email = self._email_e.get().strip()
        pwd   = self._pwd_e.get()
        self._err_lbl.config(text="")
        if not email or not pwd:
            self._err_lbl.config(text="⚠  Ingrese su correo y contraseña institucionales.")
            return
        # Depuración: mostrar información útil sin imprimir la contraseña completa
        try:
            import unicodedata
            def _norm(s: str) -> str:
                if s is None: return ""
                s2 = unicodedata.normalize("NFKD", s.strip())
                s2 = "".join(ch for ch in s2 if not unicodedata.combining(ch))
                return s2.casefold()
        except Exception:
            def _norm(s: str) -> str:
                return (s or "").strip().casefold()

        exact = email in self.repo.usuarios
        matches = [k for k in self.repo.usuarios.keys() if _norm(k) == _norm(email)]
        print(f"[DEBUG] intento login email={repr(email)} pwd_len={len(pwd)} exact_key={exact} norm_matches={matches}")
        user = self.auth.login(email, pwd)
        if user:
            self.current_user = user
            self._show_main()
        else:
            self._err_lbl.config(
                text="⚠  Credenciales incorrectas. Verifique su correo y contraseña.")
            self._pwd_e.delete(0, tk.END)
            self._pwd_e.focus()

    # ── Panel principal ───────────────────────────────────────────────────────
    def _show_main(self):
        self._limpiar()
        u     = self.current_user
        # POO: Polimorfismo -> obtener_rol() se comporta distinto según la
        # subclase real (Estudiante/Docente/Coordinador/Administrador)
        rol   = u.obtener_rol()
        color = ROL_COLOR.get(rol, C["accent"])

        # Barra superior
        topbar = tk.Frame(self.root, bg=color, height=54)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        # Logo compacto
        logo = tk.Frame(topbar, bg=C["white"], width=34, height=34)
        logo.place(x=14, rely=0.5, anchor="w")
        logo.pack_propagate(False)
        tk.Label(logo, text="UN", font=("Segoe UI", 10, "bold"),
                 bg=C["white"], fg=color).place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(topbar, text="Sistema de Admisión – Proceso de Nivelación",
                 font=("Segoe UI", 12, "bold"), bg=color, fg=C["white"]
                 ).place(x=60, rely=0.5, anchor="w")

        # Reloj
        self._reloj_lbl = tk.Label(topbar, text="", font=("Segoe UI", 9),
                                   bg=color, fg="#C5CAE9")
        self._reloj_lbl.pack(side="right", padx=14)
        self._tick()

        # Cerrar sesión
        sal = tk.Button(topbar, text="⏻  Cerrar sesión", bg=color, fg=C["white"],
                        font=("Segoe UI", 10), relief="flat", cursor="hand2",
                        activebackground=C["sidebar"], activeforeground=C["white"],
                        command=self._cerrar_sesion)
        sal.pack(side="right", padx=8, pady=10)
        sal.bind("<Enter>", lambda e: sal.config(bg=C["sidebar"]))
        sal.bind("<Leave>", lambda e: sal.config(bg=color))

        # Badge rol + usuario
        rol_txt = {"estudiante": "Estudiante", "docente": "Docente",
                   "coordinador": "Coordinador", "administrador": "Administrador"}.get(rol, rol)
        tk.Label(topbar, text=f"  {rol_txt}  ", bg=C["white"], fg=color,
                 font=("Segoe UI", 8, "bold"), padx=6, pady=2
                 ).pack(side="right", padx=4, pady=16)
        tk.Label(topbar, text=u.nombre_completo(), font=("Segoe UI", 10),
                 bg=color, fg=C["white"]).pack(side="right", padx=6)

        # Cuerpo
        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # OCP: agregar rol = una nueva entrada en el diccionario
        despacho = {
            "estudiante":    pe.construir,
            "docente":       pd.construir,
            "coordinador":   pc.construir,
            "administrador": pa.construir,
        }
        constructor = despacho.get(rol)
        if constructor:
            constructor(body, u, self.repo)

    def _tick(self):
        from datetime import datetime
        if self._reloj_lbl.winfo_exists():
            self._reloj_lbl.config(
                text=datetime.now().strftime("%H:%M:%S   %d/%m/%Y"))
            self.root.after(1000, self._tick)

    def _cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión",
                               "¿Desea cerrar su sesión?\nTodos los cambios han sido guardados.",
                               parent=self.root):
            self.current_user = None
            self._show_login()

    def _confirmar_salida(self):
        if messagebox.askyesno("Salir del sistema",
                               "¿Desea salir del sistema?\nTodos los cambios han sido guardados.",
                               parent=self.root):
            self.root.destroy()

    def _limpiar(self):
        for w in self.root.winfo_children():
            w.destroy()

    def run(self):
        self.root.mainloop()


# ── Punto de entrada ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    storage = JsonManager()                   # IRepositorio concreta
    repo    = RepositorioAcademico(storage)   # inyección de dependencia
    app     = SistemaAcademicoApp(repo)       # inyección de dependencia
    app.run()

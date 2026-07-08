hor="w")
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

        # Nota de soporte
        tk.Label(form_wrap, text="¿Problemas de acceso? Contacte al área de sistemas.",
                 font=("Segoe UI", 8), bg=C["bg"], fg=C["text_sec"]).pack(pady=(16, 0))

    def _do_login(self):
        email = self._email_e.get().strip()
        pwd   = self._pwd_e.get()
        self._err_lbl.config(text="")
        if not email or not pwd:
            self._err_lbl.config(text="⚠  Ingrese su correo y contraseña institucionales.")
            return
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

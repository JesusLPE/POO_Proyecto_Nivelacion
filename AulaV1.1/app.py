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

class SistemaAcademicoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Gestión Académica - POO")
        self.root.state("zoomed")  # Pantalla normal, no forzar fullscreen
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Datos en memoria (ahora son atributos de instancia)
        self.usuarios = {}
        self.estudiantes_lista = []
        self.docentes_lista = []
        self.asignaturas_lista = []
        self.cursos_lista = []
        self.matriculas_lista = []
        self.tareas = []
        self.entregas = []

        self.current_user = None
        self._cargar_datos_ejemplo()
        self.show_login()

    def _cargar_datos_ejemplo(self):
        """Carga usuarios y datos de prueba."""
        # Estudiantes
        est1 = Estudiante("Diocles", "Bacusoy", "diocles@gmail.com", "1234", "A001", "Ingeniería de Software")
        est2 = Estudiante("Eddy", "Vera", "eddy@gmail.com", "1234", "A002", "Administración")
        est3 = Estudiante("Josue", "Llerena", "josue@gmail.com", "1234", "A003", "Trabajo Social")
        self.estudiantes_lista = [est1, est2, est3]

        # Docentes
        doc1 = Docente("Joan", "Intriago", "joan@gmail.com", "1234", "Desarrollo Web")
        doc2 = Docente("Maria", "Gomez", "maria@gmail.com", "1234", "Matemáticas")
        self.docentes_lista = [doc1, doc2]

        # Admin y coordinador
        admin1 = Administrador("Jesus", "Palma", "jesus@gmail.com", "1234")
        coord1 = Coordinador("Jonaiker", "Perez", "jonaiker@gmail.com", "1234")

        # Registrar todos en usuarios
        for u in self.estudiantes_lista + self.docentes_lista + [admin1, coord1]:
            self.usuarios[u.email] = u

        # Asignaturas
        asig1 = Asignatura(1, "Diseño de Algoritmos", 64, 4, "Activa")
        asig2 = Asignatura(2, "Estructuras de Datos", 48, 3, "Activa")
        self.asignaturas_lista = [asig1, asig2]

        # Curso
        curso1 = Curso(1, "Desarrollo Ágil con Python", 16, 64)
        curso1.asignar_horario(Horario(1, "Lunes", "18:00", "20:00"))
        curso1.asignar_modalidad(Modalidad(1, "Virtual", "Zoom", True, "Zoom"))
        self.cursos_lista = [curso1]

        # Matrícula (corregida: ahora con atributo estudiante)
        mat1 = Matricula(1, "2025-01-10", "Ordinaria", "Activa", False, estudiante=est1)
        self.matriculas_lista.append(mat1)

    def _crear_ventana_secundaria(self, titulo, ancho=500, alto=400):
        """Método auxiliar para crear ventanas emergentes."""
        ventana = tk.Toplevel(self.root)
        ventana.title(titulo)
        ventana.geometry(f"{ancho}x{alto}")
        ventana.transient(self.root)
        ventana.grab_set()
        return ventana

    def _validar_email(self, email):
        """Validación simple de email."""
        return "@" in email and "." in email and len(email) > 5

    def _mostrar_error(self, mensaje):
        messagebox.showerror("Error", mensaje)

    def _mostrar_info(self, mensaje):
        messagebox.showinfo("Información", mensaje)

    # INICIO DE SESIÓN 
    def show_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Iniciar Sesión", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(frame, text="Email:").grid(row=1, column=0, sticky="e", pady=5)
        ttk.Label(frame, text="Contraseña:").grid(row=2, column=0, sticky="e", pady=5)

        self.email_entry = ttk.Entry(frame, width=30)
        self.pass_entry = ttk.Entry(frame, width=30, show="*")
        self.email_entry.grid(row=1, column=1, pady=5)
        self.pass_entry.grid(row=2, column=1, pady=5)

        ttk.Button(frame, text="Ingresar", command=self.do_login).grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Label(frame, text="Usuarios de prueba:", foreground="gray").grid(row=4, column=0, columnspan=2)
        ttk.Label(frame, text="Estudiante: diocles@gmail.com / 1234\nDocente: joan@gmail.com / 1234\nCoordinador: jonaiker@gmail.com / 1234\nAdmin: jesus@gmail.com / 1234",
                  foreground="blue", justify="center").grid(row=5, column=0, columnspan=2)

    def do_login(self):
        email = self.email_entry.get().strip()
        password = self.pass_entry.get()

        if not email or not password:
            self._mostrar_error("Ingrese email y contraseña")
            return

        user = self.usuarios.get(email)
        if user and user.iniciarSesion(email, password):
            self.current_user = user
            self._mostrar_info(f"Bienvenido {user.nombre}")
            self.show_main_panel()
        else:
            self._mostrar_error("Credenciales incorrectas")

    # PANEL PRINCIPAL 

    def show_main_panel(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        rol = self.current_user.obtener_rol()

        # Encabezado
        ttk.Label(self.root, text=f"Panel de {rol.capitalize()}", font=("Arial", 14)).pack(pady=10)
        ttk.Label(self.root, text=f"Bienvenido, {self.current_user.nombre} {self.current_user.apellido}").pack()

        # Contenedor principal
        if rol == "estudiante":
            self.panel_estudiante()
        elif rol == "docente":
            self.panel_docente()
        elif rol == "coordinador":
            self.panel_coordinador()
        elif rol == "administrador":
            self.panel_administrador()

        ttk.Button(self.root, text="Cerrar sesión", command=self.cerrar_sesion).pack(pady=10)

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión", "¿Está seguro de que desea salir?"):
            self.current_user = None
            self.show_login()

    # PANEL ESTUDIANTE 
    def panel_estudiante(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        frame_timeline = ttk.Frame(notebook)
        notebook.add(frame_timeline, text=" Línea de tiempo")
        self.show_timeline(frame_timeline, "estudiante")

        frame_cursos = ttk.Frame(notebook)
        notebook.add(frame_cursos, text="Cursos")
        self.show_cursos(frame_cursos)

        frame_perfil = ttk.Frame(notebook)
        notebook.add(frame_perfil, text="Mi Perfil")
        self.show_perfil(frame_perfil)

        frame_poo = ttk.Frame(notebook)
        notebook.add(frame_poo, text="Conceptos POO")
        self.show_poo_demo(frame_poo)

    # PANEL DOCENTE
    def panel_docente(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_frame = ttk.LabelFrame(main_frame, text="Línea de tiempo", padding=5)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.show_timeline(left_frame, "docente")

        right_frame = ttk.LabelFrame(main_frame, text="Acciones rápidas", padding=10)
        right_frame.pack(side="right", fill="y", padx=5, pady=5)

        ttk.Button(right_frame, text=" Registrar nota", command=self.registrar_nota, width=20).pack(pady=5)
        ttk.Button(right_frame, text=" Crear tarea", command=self.crear_tarea, width=20).pack(pady=5)
        ttk.Button(right_frame, text=" Ver entregas", command=self.ver_entregas_ventana, width=20).pack(pady=5)
        ttk.Button(right_frame, text=" Mis cursos", command=self.mis_cursos_docente, width=20).pack(pady=5)
        ttk.Button(right_frame, text=" Mi Perfil", command=lambda: self.ver_perfil_en_ventana(), width=20).pack(pady=5)
        ttk.Button(right_frame, text=" Conceptos POO", command=lambda: self.ver_poo_en_ventana(), width=20).pack(pady=5)

    def ver_perfil_en_ventana(self):
        ventana = self._crear_ventana_secundaria("Mi Perfil", 500, 400)
        self.show_perfil(ventana)

    def ver_poo_en_ventana(self):
        ventana = self._crear_ventana_secundaria("Conceptos POO", 600, 500)
        self.show_poo_demo(ventana)

    def ver_entregas_ventana(self):
        ventana = self._crear_ventana_secundaria("Entregas de estudiantes", 700, 500)
        self.show_entregas(ventana)

    # PANEL COORDINADOR
    def panel_coordinador(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        frame_timeline = ttk.Frame(notebook)
        notebook.add(frame_timeline, text="📅 Línea de tiempo")
        self.show_timeline(frame_timeline, "coordinador")

        frame_acciones = ttk.Frame(notebook)
        notebook.add(frame_acciones, text="Acciones")
        self.add_coordinador_buttons(frame_acciones)

        frame_perfil = ttk.Frame(notebook)
        notebook.add(frame_perfil, text="Mi Perfil")
        self.show_perfil(frame_perfil)

        frame_poo = ttk.Frame(notebook)
        notebook.add(frame_poo, text="Conceptos POO")
        self.show_poo_demo(frame_poo)

    def add_coordinador_buttons(self, parent):
        ttk.Button(parent, text="Asignar docente a asignatura", command=self.asignar_docente_asignatura).pack(pady=5, fill='x')
        ttk.Button(parent, text="Gestionar horarios y modalidades", command=self.gestionar_horarios).pack(pady=5, fill='x')
        ttk.Button(parent, text="Ver entregas de tareas", command=lambda: self.ver_entregas_ventana()).pack(pady=5, fill='x')

    # PANEL ADMINISTRADOR

    def panel_administrador(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        frame_timeline = ttk.Frame(notebook)
        notebook.add(frame_timeline, text="📅 Línea de tiempo")
        self.show_timeline(frame_timeline, "administrador")

        frame_acciones = ttk.Frame(notebook)
        notebook.add(frame_acciones, text="Acciones")
        self.add_admin_buttons(frame_acciones)

        frame_perfil = ttk.Frame(notebook)
        notebook.add(frame_perfil, text="Mi Perfil")
        self.show_perfil(frame_perfil)

        frame_poo = ttk.Frame(notebook)
        notebook.add(frame_poo, text="Conceptos POO")
        self.show_poo_demo(frame_poo)

    def add_admin_buttons(self, parent):
        ttk.Button(parent, text="Crear usuario", command=self.crear_usuario).pack(pady=5, fill='x')
        ttk.Button(parent, text="Eliminar usuario", command=self.eliminar_usuario).pack(pady=5, fill='x')
        ttk.Button(parent, text="Ver logs", command=self.ver_logs).pack(pady=5, fill='x')
        ttk.Button(parent, text="Gestionar asignaturas", command=self.gestionar_asignaturas).pack(pady=5, fill='x')
        ttk.Button(parent, text="Gestionar matrículas", command=self.gestionar_matriculas).pack(pady=5, fill='x')

    # FUNCIONES COMPARTIDAS

    def show_perfil(self, parent):
        user = self.current_user
        ttk.Label(parent, text="Información personal", font=("Arial", 12, "bold")).pack(pady=10)
        ttk.Label(parent, text=f"Nombre: {user.nombre}").pack(anchor="w", padx=20)
        ttk.Label(parent, text=f"Apellido: {user.apellido}").pack(anchor="w", padx=20)
        ttk.Label(parent, text=f"Email: {user.email}").pack(anchor="w", padx=20)
        ttk.Label(parent, text=f"Rol: {user.obtener_rol().capitalize()}").pack(anchor="w", padx=20)

        if hasattr(user, 'matricula'):
            ttk.Label(parent, text=f"Matrícula: {user.matricula}").pack(anchor="w", padx=20)
        if hasattr(user, 'carrera'):
            ttk.Label(parent, text=f"Carrera: {user.carrera}").pack(anchor="w", padx=20)
        if hasattr(user, 'especialidad'):
            ttk.Label(parent, text=f"Especialidad: {user.especialidad}").pack(anchor="w", padx=20)

    def show_timeline(self, parent, rol):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_width())
        canvas.configure(yscrollcommand=scrollbar.set)

        def _configure_canvas(event):
            canvas.itemconfig(1, width=event.width)
        canvas.bind("<Configure>", _configure_canvas)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        actividades = self._get_actividades(rol)
        for act in actividades:
            card = ttk.Frame(scrollable_frame, relief="solid", borderwidth=1, padding=10)
            card.pack(fill="x", pady=5, padx=5)
            ttk.Label(card, text=act["fecha"], font=("Arial", 9, "bold"), foreground="#2c3e50").pack(anchor="w")
            ttk.Label(card, text=act["titulo"], font=("Arial", 10, "bold")).pack(anchor="w", pady=(5,0))
            ttk.Label(card, text=act["descripcion"], font=("Arial", 9), foreground="#555").pack(anchor="w")
            if act.get("boton_texto") and act.get("boton_comando"):
                ttk.Button(card, text=act["boton_texto"], command=act["boton_comando"]).pack(anchor="e", pady=(5,0))

    def _get_actividades(self, rol):
        if rol == "estudiante":
            return [
                {"fecha": "Viernes, 22 de mayo de 2024 - 23:00",
                 "titulo": " Vencimiento: Proyecto Final - Diseño de Algoritmos",
                 "descripcion": "Entregar documentación y código fuente",
                 "boton_texto": "Agregar entrega", "boton_comando": self.subir_tarea},
                {"fecha": "Sábado, 23 de mayo de 2024 - 00:59",
                 "titulo": " Entrega de Avance - Estructuras de Datos",
                 "descripcion": "Implementar árboles binarios",
                 "boton_texto": "Agregar entrega", "boton_comando": self.subir_tarea},
                {"fecha": "Martes, 26 de mayo de 2024 - 21:53",
                 "titulo": " Debate: Ética en la Inteligencia Artificial",
                 "descripcion": "Foro obligatorio - Participación mínima 3 intervenciones",
                 "boton_texto": "Ver foro", "boton_comando": lambda: self._mostrar_info("Acceso al foro de debate")},
                {"fecha": "Próximos 30 días",
                 "titulo": " Calendario de exámenes",
                 "descripcion": "Consulta las fechas de parciales y finales",
                 "boton_texto": "Ver más", "boton_comando": lambda: self._mostrar_info("Exámenes: 10/06, 20/06, 30/06")}
            ]
        elif rol == "docente":
            return [
                {"fecha": "Hoy - 18:00",
                 "titulo": " Entregas por calificar",
                 "descripcion": "3 estudiantes han subido la tarea 'Algoritmos de ordenamiento'",
                 "boton_texto": "Calificar", "boton_comando": self.ver_entregas_ventana},
                {"fecha": "Mañana - 10:00",
                 "titulo": " Clase: Recursividad",
                 "descripcion": "Curso Diseño de Algoritmos - Preparar ejemplos",
                 "boton_texto": "Ver detalles", "boton_comando": lambda: self._mostrar_info("Clase virtual a las 10:00")},
                {"fecha": "2024-05-30",
                 "titulo": " Cierre de notas",
                 "descripcion": "Plazo para registrar notas del primer corte",
                 "boton_texto": "Registrar notas", "boton_comando": self.registrar_nota}
            ]
        elif rol == "coordinador":
            return [
                {"fecha": "Urgente",
                 "titulo": " Asignatura sin docente",
                 "descripcion": "Bases de Datos Avanzadas no tiene docente asignado",
                 "boton_texto": "Asignar", "boton_comando": self.asignar_docente_asignatura},
                {"fecha": "Pendiente",
                 "titulo": " Matrículas por aprobar",
                 "descripcion": "3 solicitudes de matrícula en espera",
                 "boton_texto": "Revisar", "boton_comando": self.gestionar_matriculas},
                {"fecha": "Próxima semana",
                 "titulo": " Reunión de coordinación",
                 "descripcion": "Planificación del siguiente ciclo",
                 "boton_texto": "Confirmar asistencia", "boton_comando": lambda: self._mostrar_info("Asistencia confirmada")}
            ]
        elif rol == "administrador":
            return [
                {"fecha": "2024-05-21",
                 "titulo": " Nuevo usuario registrado",
                 "descripcion": "Laura Méndez (Docente) se ha unido al sistema",
                 "boton_texto": "Ver usuarios", "boton_comando": self.manage_users},
                {"fecha": "Ayer",
                 "titulo": " Reporte de accesos generado",
                 "descripcion": "Se exportó reporte de logs del mes",
                 "boton_texto": "Descargar", "boton_comando": lambda: self._mostrar_info("Reporte descargado")},
                {"fecha": "Configuración pendiente",
                 "titulo": " Actualizar parámetros del sistema",
                 "descripcion": "Cambiar período académico",
                 "boton_texto": "Configurar", "boton_comando": self.show_config}
            ]
        return []

    def show_poo_demo(self, parent):
        texto = tk.Text(parent, wrap="word")
        texto.pack(fill="both", expand=True)
        demo = """=== DEMOSTRACIÓN DE CONCEPTOS POO ===

1. HERENCIA: Estudiante, Docente, etc. heredan de Persona.
2. POLIMORFISMO: obtener_rol() devuelve diferente según el objeto.
3. ABSTRACCIÓN: Persona y Evaluacion son abstractas.
4. ENCAPSULAMIENTO: Atributos privados __nombre, __email con propiedades.
5. PROPIEDADES: @property y @setter (ej. en Matricula).
6. SOBRECARGA: calcularPromedio(nota1, nota2, nota3=0) en Notas.
7. super(): usado en constructores de clases hijas.
8. HERENCIA MÚLTIPLE: Persona hereda de ABC e IniciarSesion.
9. INTERFACES: IniciarSesion define contrato.
10. POLIMORFISMO CON INTERFACES: iniciarSesion() implementado por Persona.
"""
        texto.insert("1.0", demo)
        texto.config(state="disabled")

    def show_cursos(self, parent):
        for curso in self.cursos_lista:
            frame = ttk.LabelFrame(parent, text=curso.nombre)
            frame.pack(fill="x", padx=10, pady=5)
            ttk.Label(frame, text=f"Horario: {curso.horario}").pack(anchor="w")
            ttk.Label(frame, text=f"Modalidad: {curso.modalidad}").pack(anchor="w")

    # ---------------------- MÉTODOS PARA ESTUDIANTE ----------------------
    def subir_tarea(self):
        ventana = self._crear_ventana_secundaria("Subir tarea", 500, 400)
        ttk.Label(ventana, text="Título:").pack(pady=5)
        titulo_entry = ttk.Entry(ventana, width=50)
        titulo_entry.pack()
        ttk.Label(ventana, text="Descripción:").pack(pady=5)
        desc_text = tk.Text(ventana, height=5, width=50)
        desc_text.pack()
        ttk.Label(ventana, text="Archivo (simulación):").pack(pady=5)
        archivo_var = tk.StringVar()
        ttk.Entry(ventana, textvariable=archivo_var, width=50).pack()
        ttk.Button(ventana, text="Seleccionar archivo", command=lambda: archivo_var.set(filedialog.askopenfilename())).pack(pady=5)

        def guardar():
            titulo = titulo_entry.get().strip()
            if not titulo:
                self._mostrar_error("El título es obligatorio")
                return
            nueva_tarea = Tarea(titulo, desc_text.get("1.0", tk.END).strip(),
                                datetime.now().strftime("%Y-%m-%d"), self.current_user.email)
            self.tareas.append(nueva_tarea)
            self.entregas.append({
                "tarea": nueva_tarea,
                "estudiante": self.current_user,
                "archivo": archivo_var.get(),
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            self._mostrar_info("Tarea subida exitosamente")
            ventana.destroy()
        ttk.Button(ventana, text="Subir", command=guardar).pack(pady=10)

    # ---------------------- MÉTODOS PARA DOCENTE ----------------------
    def registrar_nota(self):
        if not self.estudiantes_lista:
            self._mostrar_error("No hay estudiantes registrados")
            return
        ventana = self._crear_ventana_secundaria("Registrar nota", 500, 400)

        ttk.Label(ventana, text="Estudiante:").pack(pady=5)
        estudiante_var = tk.StringVar()
        valores = [f"{e.nombre} {e.apellido} ({e.matricula})" for e in self.estudiantes_lista]
        estudiante_combo = ttk.Combobox(ventana, textvariable=estudiante_var, values=valores, width=40)
        estudiante_combo.pack(pady=5)

        ttk.Label(ventana, text="Asignatura:").pack(pady=5)
        asignatura_combo = ttk.Combobox(ventana, values=[a.nombre for a in self.asignaturas_lista], width=40)
        asignatura_combo.pack(pady=5)

        ttk.Label(ventana, text="Nota (0-20):").pack(pady=5)
        nota_spinbox = ttk.Spinbox(ventana, from_=0, to=20, increment=0.1, width=10)
        nota_spinbox.pack(pady=5)

        def guardar():
            seleccion = estudiante_var.get()
            if not seleccion:
                self._mostrar_error("Seleccione un estudiante")
                return
            try:
                nota_val = float(nota_spinbox.get())
                if nota_val < 0 or nota_val > 20:
                    self._mostrar_error("La nota debe estar entre 0 y 20")
                    return
            except ValueError:
                self._mostrar_error("Ingrese un valor numérico válido para la nota")
                return

            matricula = seleccion.split("(")[-1].replace(")", "")
            estudiante = next((e for e in self.estudiantes_lista if e.matricula == matricula), None)
            if estudiante:
                calif = Calificacion(estudiante, asignatura_combo.get(), nota_val, "")
                calif.asignar_nota(self.current_user)
                self._mostrar_info(f"Nota {nota_val} registrada para {estudiante.nombre}")
                ventana.destroy()
            else:
                self._mostrar_error("Estudiante no encontrado")

        ttk.Button(ventana, text="Registrar", command=guardar).pack(pady=20)

    def crear_tarea(self):
        ventana = self._crear_ventana_secundaria("Crear tarea", 500, 400)
        ttk.Label(ventana, text="Título:").pack(pady=5)
        titulo_entry = ttk.Entry(ventana, width=50)
        titulo_entry.pack()
        ttk.Label(ventana, text="Descripción:").pack(pady=5)
        desc_text = tk.Text(ventana, height=5, width=50)
        desc_text.pack()
        ttk.Label(ventana, text="Fecha límite (YYYY-MM-DD):").pack(pady=5)
        fecha_entry = ttk.Entry(ventana, width=30)
        fecha_entry.pack()

        def guardar():
            titulo = titulo_entry.get().strip()
            if not titulo:
                self._mostrar_error("El título es obligatorio")
                return
            fecha = fecha_entry.get().strip()
            if fecha and not self._validar_fecha(fecha):
                self._mostrar_error("Formato de fecha inválido. Use YYYY-MM-DD")
                return
            tarea = Tarea(titulo, desc_text.get("1.0", tk.END).strip(), fecha, self.current_user.email)
            self.tareas.append(tarea)
            self._mostrar_info("Tarea creada")
            ventana.destroy()
        ttk.Button(ventana, text="Crear", command=guardar).pack(pady=10)

    def _validar_fecha(self, fecha_str):
        try:
            datetime.strptime(fecha_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def mis_cursos_docente(self):
        self._mostrar_info("Usted está asignado a Desarrollo Ágil con Python")

    def show_entregas(self, parent):
        tree = ttk.Treeview(parent, columns=("Tarea", "Estudiante", "Archivo", "Fecha"), show="headings")
        for col in ("Tarea", "Estudiante", "Archivo", "Fecha"):
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        for entrega in self.entregas:
            tree.insert("", "end", values=(
                entrega["tarea"].titulo,
                f"{entrega['estudiante'].nombre} {entrega['estudiante'].apellido}",
                entrega["archivo"],
                entrega["fecha"]
            ))

    # ---------------------- MÉTODOS PARA COORDINADOR ----------------------
    def asignar_docente_asignatura(self):
        if not self.docentes_lista:
            self._mostrar_error("No hay docentes registrados")
            return
        ventana = self._crear_ventana_secundaria("Asignar docente a asignatura", 400, 200)
        ttk.Label(ventana, text="Docente:").pack(pady=5)
        docente_var = tk.StringVar()
        docente_combo = ttk.Combobox(ventana, textvariable=docente_var,
                                     values=[f"{d.nombre} {d.apellido} ({d.email})" for d in self.docentes_lista])
        docente_combo.pack()
        ttk.Label(ventana, text="Asignatura:").pack(pady=5)
        asig_var = tk.StringVar()
        asig_combo = ttk.Combobox(ventana, textvariable=asig_var,
                                  values=[a.nombre for a in self.asignaturas_lista])
        asig_combo.pack()
        def asignar():
            if not docente_var.get() or not asig_var.get():
                self._mostrar_error("Seleccione docente y asignatura")
                return
            self._mostrar_info(f"Asignado {docente_var.get()} a {asig_var.get()}")
            ventana.destroy()
        ttk.Button(ventana, text="Asignar", command=asignar).pack(pady=10)

    def gestionar_horarios(self):
        ventana = self._crear_ventana_secundaria("Gestión de horarios y modalidades", 500, 300)
        for curso in self.cursos_lista:
            frame = ttk.LabelFrame(ventana, text=curso.nombre)
            frame.pack(fill="x", padx=10, pady=5)
            ttk.Label(frame, text=f"Horario actual: {curso.horario}").pack(anchor="w")
            ttk.Label(frame, text=f"Modalidad actual: {curso.modalidad}").pack(anchor="w")
            ttk.Button(frame, text="Editar horario", command=lambda c=curso: self.editar_horario(c)).pack(side="left", padx=5)
            ttk.Button(frame, text="Editar modalidad", command=lambda c=curso: self.editar_modalidad(c)).pack(side="left", padx=5)

    def editar_horario(self, curso):
        nuevo = simpledialog.askstring("Editar horario", f"Nuevo horario para {curso.nombre} (ej. Lunes 18:00-20:00):")
        if nuevo:
            partes = nuevo.split()
            if len(partes) >= 2:
                curso.asignar_horario(Horario(99, partes[0], partes[1] if len(partes)>1 else "", partes[-1]))
                self._mostrar_info(f"Horario actualizado a {nuevo}")

    def editar_modalidad(self, curso):
        nueva = simpledialog.askstring("Editar modalidad", "Nueva modalidad (Presencial/Virtual/Híbrida):")
        if nueva:
            curso.asignar_modalidad(Modalidad(99, nueva, "", True, ""))
            self._mostrar_info(f"Modalidad actualizada a {nueva}")

    def gestionar_asignaturas(self):
        ventana = self._crear_ventana_secundaria("Gestión de Asignaturas", 700, 500)
        tree = ttk.Treeview(ventana, columns=("ID", "Nombre", "Horas", "Créditos", "Estado"), show="headings")
        for col in ("ID", "Nombre", "Horas", "Créditos", "Estado"):
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        def refrescar():
            for i in tree.get_children():
                tree.delete(i)
            for a in self.asignaturas_lista:
                tree.insert("", "end", values=(a.id, a.nombre, a.horas, a.creditos, a.estado))
        refrescar()

        frame_form = ttk.Frame(ventana)
        frame_form.pack(fill="x", pady=5)
        ttk.Label(frame_form, text="Nueva:").pack(side="left")
        nombre_asi = ttk.Entry(frame_form, width=15)
        nombre_asi.pack(side="left", padx=5)
        ttk.Label(frame_form, text="Horas:").pack(side="left")
        horas_asi = ttk.Entry(frame_form, width=5)
        horas_asi.pack(side="left")
        ttk.Label(frame_form, text="Créditos:").pack(side="left")
        creditos_asi = ttk.Entry(frame_form, width=5)
        creditos_asi.pack(side="left")

        def agregar():
            nombre = nombre_asi.get().strip()
            if not nombre:
                self._mostrar_error("Ingrese el nombre de la asignatura")
                return
            try:
                horas = int(horas_asi.get())
                creditos = int(creditos_asi.get())
            except ValueError:
                self._mostrar_error("Horas y créditos deben ser números enteros")
                return
            nueva = Asignatura(len(self.asignaturas_lista)+1, nombre, horas, creditos, "Activa")
            self.asignaturas_lista.append(nueva)
            refrescar()
            self._mostrar_info("Asignatura creada")
        ttk.Button(frame_form, text="Agregar", command=agregar).pack(side="left", padx=5)

        def eliminar():
            sel = tree.selection()
            if sel:
                item = tree.item(sel[0])
                id_asi = item['values'][0]
                self.asignaturas_lista = [a for a in self.asignaturas_lista if a.id != id_asi]
                refrescar()
                self._mostrar_info("Asignatura eliminada")
        ttk.Button(ventana, text="Eliminar seleccionada", command=eliminar).pack(pady=5)

    def gestionar_matriculas(self):
        ventana = self._crear_ventana_secundaria("Gestión de Matrículas", 700, 500)
        tree = ttk.Treeview(ventana, columns=("ID", "Estudiante", "Fecha", "Tipo", "Estado"), show="headings")
        for col in ("ID", "Estudiante", "Fecha", "Tipo", "Estado"):
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        def refrescar():
            for i in tree.get_children():
                tree.delete(i)
            for m in self.matriculas_lista:
                est_nombre = f"{m.estudiante.nombre} {m.estudiante.apellido}" if m.estudiante else "N/A"
                tree.insert("", "end", values=(m.id, est_nombre, m.fecha, m.tipo, m.estado))
        refrescar()

        def cambiar_estado():
            sel = tree.selection()
            if sel:
                item = tree.item(sel[0])
                id_mat = item['values'][0]
                nuevo = simpledialog.askstring("Cambiar estado", "Nuevo estado (Activa/Anulada/Pendiente):")
                if nuevo:
                    for m in self.matriculas_lista:
                        if m.id == id_mat:
                            m.estado = nuevo
                            break
                    refrescar()
                    self._mostrar_info(f"Estado cambiado a {nuevo}")
        ttk.Button(ventana, text="Cambiar estado", command=cambiar_estado).pack(pady=5)

    # ---------------------- MÉTODOS PARA ADMINISTRADOR ----------------------
    def manage_users(self, parent=None):
        if parent is None:
            ventana = self._crear_ventana_secundaria("Usuarios", 600, 400)
            parent = ventana
        tree = ttk.Treeview(parent, columns=("Email", "Nombre", "Rol"), show="headings")
        tree.heading("Email", text="Email")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Rol", text="Rol")
        tree.pack(fill="both", expand=True)

        def refrescar():
            for i in tree.get_children():
                tree.delete(i)
            for u in self.usuarios.values():
                tree.insert("", "end", values=(u.email, f"{u.nombre} {u.apellido}", u.obtener_rol()))
        refrescar()
        ttk.Button(parent, text="Refrescar", command=refrescar).pack(pady=5)

    def crear_usuario(self):
        ventana = self._crear_ventana_secundaria("Crear usuario", 400, 450)
        ttk.Label(ventana, text="Nombre:").pack()
        nombre_e = ttk.Entry(ventana)
        nombre_e.pack()
        ttk.Label(ventana, text="Apellido:").pack()
        apellido_e = ttk.Entry(ventana)
        apellido_e.pack()
        ttk.Label(ventana, text="Email:").pack()
        email_e = ttk.Entry(ventana)
        email_e.pack()
        ttk.Label(ventana, text="Contraseña:").pack()
        pass_e = ttk.Entry(ventana, show="*")
        pass_e.pack()
        ttk.Label(ventana, text="Rol:").pack()
        rol_combo = ttk.Combobox(ventana, values=["estudiante", "docente", "coordinador", "administrador"])
        rol_combo.pack()

        def guardar():
            nombre = nombre_e.get().strip()
            apellido = apellido_e.get().strip()
            email = email_e.get().strip()
            password = pass_e.get()
            rol = rol_combo.get()

            if not all([nombre, apellido, email, password, rol]):
                self._mostrar_error("Todos los campos son obligatorios")
                return
            if not self._validar_email(email):
                self._mostrar_error("Email inválido")
                return
            if email in self.usuarios:
                self._mostrar_error("El email ya está registrado")
                return

            if rol == "estudiante":
                matricula = simpledialog.askstring("Matrícula", "Ingrese matrícula:")
                carrera = simpledialog.askstring("Carrera", "Ingrese carrera:")
                if not matricula or not carrera:
                    return
                nuevo = Estudiante(nombre, apellido, email, password, matricula, carrera)
                self.estudiantes_lista.append(nuevo)
            elif rol == "docente":
                esp = simpledialog.askstring("Especialidad", "Ingrese especialidad:")
                if not esp:
                    return
                nuevo = Docente(nombre, apellido, email, password, esp)
                self.docentes_lista.append(nuevo)
            elif rol == "coordinador":
                nuevo = Coordinador(nombre, apellido, email, password)
            else:
                nuevo = Administrador(nombre, apellido, email, password)

            self.usuarios[nuevo.email] = nuevo
            self._mostrar_info(f"Usuario {nuevo.email} creado")
            ventana.destroy()

        ttk.Button(ventana, text="Crear", command=guardar).pack(pady=10)

    def eliminar_usuario(self):
        emails = list(self.usuarios.keys())
        if not emails:
            self._mostrar_info("No hay usuarios")
            return
        seleccion = simpledialog.askstring("Eliminar usuario", f"Ingrese email a eliminar:\n{emails}")
        if seleccion and seleccion in self.usuarios:
            if self.usuarios[seleccion] == self.current_user:
                self._mostrar_error("No puede eliminarse a sí mismo")
                return
            if messagebox.askyesno("Confirmar", f"¿Eliminar usuario {seleccion}?"):
                del self.usuarios[seleccion]
                self.estudiantes_lista = [e for e in self.estudiantes_lista if e.email != seleccion]
                self.docentes_lista = [d for d in self.docentes_lista if d.email != seleccion]
                self._mostrar_info(f"Usuario {seleccion} eliminado")
        else:
            self._mostrar_error("Usuario no encontrado")

    def ver_logs(self):
        self._mostrar_info("Simulación: logs del sistema (fecha, hora, acciones)")

    def show_config(self, parent=None):
        if parent is None:
            ventana = self._crear_ventana_secundaria("Configuración", 400, 200)
            parent = ventana
        ttk.Label(parent, text="Configuración general del sistema (simulación)").pack()
        ttk.Button(parent, text="Cambiar tema", command=lambda: self._mostrar_info("Tema cambiado (simulación)")).pack(pady=5)
        ttk.Button(parent, text="Respaldar datos", command=lambda: self._mostrar_info("Respaldo simulado")).pack(pady=5)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SistemaAcademicoApp()
    app.run()
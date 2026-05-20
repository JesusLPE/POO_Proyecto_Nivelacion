import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
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
from datetime import datetime

# ---------------------------- DATOS GLOBALES EN MEMORIA ----------------------------
usuarios = {}
estudiantes_lista = []
docentes_lista = []
asignaturas_lista = []
cursos_lista = []
matriculas_lista = []
tareas = []
entregas = []

# Crear usuarios de ejemplo (materias inventadas)
est1 = Estudiante("Diocles", "Bacusoy", "diocles@gmail.com", "1234", "A001", "Ingeniería de Software")
est2 = Estudiante("Eddy", "Vera", "eddy@gmail.com", "1234", "A002", "Administración")
est3 = Estudiante("Josue", "Llerena", "josue@gmail.com", "1234", "A003", "Trabajo Social")
doc1 = Docente("Joan", "Intriago", "joan@gmail.com", "1234", "Desarrollo Web")
doc2 = Docente("Maria", "Gomez", "maria@gmail.com", "1234", "Matemáticas")
admin1 = Administrador("Jesus", "Palma", "jesus@gmail.com", "1234")
coord1 = Coordinador("Jonaiker", "Perez", "jonaiker@gmail.com", "1234")

estudiantes_lista = [est1, est2, est3]
docentes_lista = [doc1, doc2]
for u in estudiantes_lista + docentes_lista + [admin1, coord1]:
    usuarios[u.email] = u

# Asignaturas inventadas
asignatura1 = Asignatura(1, "Diseño de Algoritmos", 64, 4, "Activa")
asignatura2 = Asignatura(2, "Estructuras de Datos", 48, 3, "Activa")
asignaturas_lista = [asignatura1, asignatura2]

# Curso inventado
curso1 = Curso(1, "Desarrollo Ágil con Python", 16, 64)
curso1.asignar_horario(Horario(1, "Lunes", "18:00", "20:00"))
curso1.asignar_modalidad(Modalidad(1, "Virtual", "Zoom", True, "Zoom"))
cursos_lista = [curso1]

# Matrícula de ejemplo
mat1 = Matricula(1, "2025-01-10", "Ordinaria", "Activa", False)
mat1._Matricula__estudiante = est1
matriculas_lista.append(mat1)

# ---------------------------- CLASE PRINCIPAL ----------------------------
class SistemaAcademicoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Gestión Académica - POO")
        # Pantalla completa (opcional, presiona Escape para salir)
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        self.current_user = None
        self.show_login()

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
        email = self.email_entry.get()
        password = self.pass_entry.get()
        user = usuarios.get(email)
        if user and user.iniciarSesion(email, password):
            self.current_user = user
            messagebox.showinfo("Éxito", f"Bienvenido {user.nombre}")
            self.show_main_panel()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    def show_main_panel(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        rol = self.current_user.obtener_rol()
        
        # Encabezado
        ttk.Label(self.root, text=f"Panel de {rol.capitalize()}", font=("Arial", 14)).pack(pady=10)
        ttk.Label(self.root, text=f"Bienvenido, {self.current_user.nombre} {self.current_user.apellido}").pack()
        
        # Contenedor principal con pestañas solo para cosas no principales
        if rol == "estudiante":
            self.panel_estudiante()
        elif rol == "docente":
            self.panel_docente()
        elif rol == "coordinador":
            self.panel_coordinador()
        elif rol == "administrador":
            self.panel_administrador()
        
        ttk.Button(self.root, text="Cerrar sesión", command=self.show_login).pack(pady=10)

    # -------------------- PANEL ESTUDIANTE --------------------
    def panel_estudiante(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        frame_timeline = ttk.Frame(notebook)
        notebook.add(frame_timeline, text="📅 Línea de tiempo")
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

    # -------------------- PANEL DOCENTE (con acciones visibles) --------------------
    def panel_docente(self):
        # Usamos un Frame principal dividido en dos partes: Timeline (izquierda) y Acciones (derecha)
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Izquierda: Línea de tiempo
        left_frame = ttk.LabelFrame(main_frame, text="Línea de tiempo", padding=5)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.show_timeline(left_frame, "docente")
        
        # Derecha: Acciones rápidas
        right_frame = ttk.LabelFrame(main_frame, text="Acciones rápidas", padding=10)
        right_frame.pack(side="right", fill="y", padx=5, pady=5)
        
        ttk.Button(right_frame, text="📝 Registrar nota", command=self.registrar_nota, width=20).pack(pady=5)
        ttk.Button(right_frame, text="📄 Crear tarea", command=self.crear_tarea, width=20).pack(pady=5)
        ttk.Button(right_frame, text="📋 Ver entregas", command=self.ver_entregas_ventana, width=20).pack(pady=5)
        ttk.Button(right_frame, text="🎓 Mis cursos", command=self.mis_cursos_docente, width=20).pack(pady=5)
        ttk.Button(right_frame, text="👤 Mi Perfil", command=self.mostrar_perfil_docente, width=20).pack(pady=5)
        ttk.Button(right_frame, text="💡 Conceptos POO", command=self.mostrar_poo_docente, width=20).pack(pady=5)
    
    def ver_entregas_ventana(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Entregas de estudiantes")
        ventana.geometry("700x500")
        self.show_entregas(ventana)
    
    def mostrar_perfil_docente(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Mi Perfil")
        ventana.geometry("500x400")
        self.show_perfil(ventana)
    
    def mostrar_poo_docente(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Conceptos POO")
        ventana.geometry("600x500")
        self.show_poo_demo(ventana)
    
    # -------------------- PANEL COORDINADOR Y ADMIN (simplificados) --------------------
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

    # -------------------- PERFIL --------------------
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

    # -------------------- LÍNEA DE TIEMPO --------------------
    def show_timeline(self, parent, rol):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
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
                 "titulo": "📅 Vencimiento: Proyecto Final - Diseño de Algoritmos",
                 "descripcion": "Entregar documentación y código fuente",
                 "boton_texto": "Agregar entrega",
                 "boton_comando": self.subir_tarea},
                {"fecha": "Sábado, 23 de mayo de 2024 - 00:59",
                 "titulo": "📅 Entrega de Avance - Estructuras de Datos",
                 "descripcion": "Implementar árboles binarios",
                 "boton_texto": "Subir avance",
                 "boton_comando": self.subir_tarea},
                {"fecha": "Martes, 26 de mayo de 2024 - 21:53",
                 "titulo": "💬 Debate: Ética en la Inteligencia Artificial",
                 "descripcion": "Foro obligatorio - Participación mínima 3 intervenciones",
                 "boton_texto": "Ver foro",
                 "boton_comando": lambda: messagebox.showinfo("Foro", "Acceso al foro de debate")},
                {"fecha": "Próximos 30 días",
                 "titulo": "📌 Calendario de exámenes",
                 "descripcion": "Consulta las fechas de parciales y finales",
                 "boton_texto": "Ver más",
                 "boton_comando": lambda: messagebox.showinfo("Calendario", "Exámenes: 10/06, 20/06, 30/06")}
            ]
        elif rol == "docente":
            return [
                {"fecha": "Hoy - 18:00",
                 "titulo": "✏️ Entregas por calificar",
                 "descripcion": "5 estudiantes han subido la tarea 'Algoritmos de ordenamiento'",
                 "boton_texto": "Calificar",
                 "boton_comando": self.ver_entregas_ventana},
                {"fecha": "Mañana - 10:00",
                 "titulo": "📝 Clase: Recursividad",
                 "descripcion": "Curso Diseño de Algoritmos - Preparar ejemplos",
                 "boton_texto": "Ver detalles",
                 "boton_comando": lambda: messagebox.showinfo("Clase", "Clase virtual a las 10:00")},
                {"fecha": "2024-05-30",
                 "titulo": "📊 Cierre de notas",
                 "descripcion": "Plazo para registrar notas del primer corte",
                 "boton_texto": "Registrar notas",
                 "boton_comando": self.registrar_nota}
            ]
        elif rol == "coordinador":
            return [
                {"fecha": "Urgente",
                 "titulo": "⚠️ Asignatura sin docente",
                 "descripcion": "Bases de Datos Avanzadas no tiene docente asignado",
                 "boton_texto": "Asignar",
                 "boton_comando": self.asignar_docente_asignatura},
                {"fecha": "Pendiente",
                 "titulo": "📄 Matrículas por aprobar",
                 "descripcion": "3 solicitudes de matrícula en espera",
                 "boton_texto": "Revisar",
                 "boton_comando": self.manage_matriculas},
                {"fecha": "Próxima semana",
                 "titulo": "🗓️ Reunión de coordinación",
                 "descripcion": "Planificación del siguiente ciclo",
                 "boton_texto": "Confirmar asistencia",
                 "boton_comando": lambda: messagebox.showinfo("Reunión", "Asistencia confirmada")}
            ]
        elif rol == "administrador":
            return [
                {"fecha": "2024-05-21",
                 "titulo": "🆕 Nuevo usuario registrado",
                 "descripcion": "Laura Méndez (Docente) se ha unido al sistema",
                 "boton_texto": "Ver usuarios",
                 "boton_comando": self.manage_users},
                {"fecha": "Ayer",
                 "titulo": "📊 Reporte de accesos generado",
                 "descripcion": "Se exportó reporte de logs del mes",
                 "boton_texto": "Descargar",
                 "boton_comando": lambda: messagebox.showinfo("Reporte", "Reporte descargado")},
                {"fecha": "Configuración pendiente",
                 "titulo": "⚙️ Actualizar parámetros del sistema",
                 "descripcion": "Cambiar período académico",
                 "boton_texto": "Configurar",
                 "boton_comando": self.show_config}
            ]
        return []

    # -------------------- MÉTODOS PARA ESTUDIANTE --------------------
    def subir_tarea(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Subir tarea")
        ventana.geometry("500x400")
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
            titulo = titulo_entry.get()
            descripcion = desc_text.get("1.0", tk.END).strip()
            archivo = archivo_var.get()
            if not titulo:
                messagebox.showerror("Error", "El título es obligatorio")
                return
            nueva_tarea = Tarea(titulo, descripcion, datetime.now().strftime("%Y-%m-%d"), self.current_user.email)
            tareas.append(nueva_tarea)
            entregas.append({
                "tarea": nueva_tarea,
                "estudiante": self.current_user,
                "archivo": archivo,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            messagebox.showinfo("Éxito", "Tarea subida exitosamente")
            ventana.destroy()

        ttk.Button(ventana, text="Subir", command=guardar).pack(pady=10)

    # -------------------- MÉTODOS PARA DOCENTE --------------------
    def registrar_nota(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Registrar nota")
        ventana.geometry("500x400")
        if not estudiantes_lista:
            messagebox.showerror("Error", "No hay estudiantes registrados")
            ventana.destroy()
            return
        ttk.Label(ventana, text="Estudiante:").pack(pady=5)
        estudiante_var = tk.StringVar()
        valores = [f"{e.nombre} {e.apellido} ({e.matricula})" for e in estudiantes_lista]
        estudiante_combo = ttk.Combobox(ventana, textvariable=estudiante_var, values=valores, width=40)
        estudiante_combo.pack(pady=5)
        ttk.Label(ventana, text="Asignatura:").pack(pady=5)
        asignatura_combo = ttk.Combobox(ventana, values=[a.nombre for a in asignaturas_lista], width=40)
        asignatura_combo.pack(pady=5)
        ttk.Label(ventana, text="Nota:").pack(pady=5)
        nota_spinbox = ttk.Spinbox(ventana, from_=0, to=20, increment=0.1, width=10)
        nota_spinbox.pack(pady=5)

        def guardar():
            seleccion = estudiante_var.get()
            if not seleccion:
                messagebox.showerror("Error", "Seleccione un estudiante")
                return
            matricula = seleccion.split("(")[-1].replace(")", "")
            estudiante = next((e for e in estudiantes_lista if e.matricula == matricula), None)
            if estudiante:
                nota_val = float(nota_spinbox.get())
                calif = Calificacion(estudiante, asignatura_combo.get(), nota_val, "")
                calif.asignar_nota(self.current_user)
                messagebox.showinfo("Éxito", f"Nota {nota_val} registrada para {estudiante.nombre}")
                ventana.destroy()
            else:
                messagebox.showerror("Error", "Estudiante no encontrado")

        ttk.Button(ventana, text="Registrar", command=guardar).pack(pady=20)

    def crear_tarea(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Crear tarea")
        ventana.geometry("500x400")
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
            tarea = Tarea(titulo_entry.get(), desc_text.get("1.0", tk.END).strip(),
                          fecha_entry.get(), self.current_user.email)
            tareas.append(tarea)
            messagebox.showinfo("Éxito", "Tarea creada")
            ventana.destroy()

        ttk.Button(ventana, text="Crear", command=guardar).pack(pady=10)

    def mis_cursos_docente(self):
        messagebox.showinfo("Cursos", "Usted está asignado a Desarrollo Ágil con Python")

    def show_entregas(self, parent):
        tree = ttk.Treeview(parent, columns=("Tarea", "Estudiante", "Archivo", "Fecha"), show="headings")
        tree.heading("Tarea", text="Tarea")
        tree.heading("Estudiante", text="Estudiante")
        tree.heading("Archivo", text="Archivo")
        tree.heading("Fecha", text="Fecha")
        tree.pack(fill="both", expand=True)
        for entrega in entregas:
            tree.insert("", "end", values=(entrega["tarea"].titulo,
                                           f"{entrega['estudiante'].nombre} {entrega['estudiante'].apellido}",
                                           entrega["archivo"], entrega["fecha"]))

    # -------------------- MÉTODOS PARA COORDINADOR --------------------
    def add_coordinador_buttons(self, parent):
        ttk.Button(parent, text="Asignar docente a asignatura", command=self.asignar_docente_asignatura).pack(pady=5, fill='x')
        ttk.Button(parent, text="Gestionar horarios y modalidades", command=self.gestionar_horarios).pack(pady=5, fill='x')
        ttk.Button(parent, text="Ver entregas de tareas", command=lambda: self.show_entregas(tk.Toplevel(self.root))).pack(pady=5, fill='x')

    def asignar_docente_asignatura(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Asignar docente a asignatura")
        ttk.Label(ventana, text="Docente:").pack(pady=5)
        docente_var = tk.StringVar()
        docente_combo = ttk.Combobox(ventana, textvariable=docente_var,
                                     values=[f"{d.nombre} {d.apellido} ({d.email})" for d in docentes_lista])
        docente_combo.pack()
        ttk.Label(ventana, text="Asignatura:").pack(pady=5)
        asig_var = tk.StringVar()
        asig_combo = ttk.Combobox(ventana, textvariable=asig_var, values=[a.nombre for a in asignaturas_lista])
        asig_combo.pack()

        def asignar():
            messagebox.showinfo("Asignación", f"Asignado {docente_var.get()} a {asig_var.get()}")
            ventana.destroy()

        ttk.Button(ventana, text="Asignar", command=asignar).pack(pady=10)

    def gestionar_horarios(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Gestión de horarios y modalidades")
        for curso in cursos_lista:
            frame = ttk.LabelFrame(ventana, text=curso._nombre)
            frame.pack(fill="x", padx=10, pady=5)
            ttk.Label(frame, text=f"Horario actual: {curso._horario}").pack(anchor="w")
            ttk.Label(frame, text=f"Modalidad actual: {curso._modalidad}").pack(anchor="w")
            ttk.Button(frame, text="Editar horario", command=lambda c=curso: self.editar_horario(c)).pack(side="left", padx=5)
            ttk.Button(frame, text="Editar modalidad", command=lambda c=curso: self.editar_modalidad(c)).pack(side="left", padx=5)

    def editar_horario(self, curso):
        nuevo = simpledialog.askstring("Editar horario", f"Nuevo horario para {curso._nombre} (ej. Lunes 18:00-20:00):")
        if nuevo:
            curso.asignar_horario(Horario(99, "Nuevo", nuevo.split()[0], nuevo.split()[-1]))
            messagebox.showinfo("Actualizado", f"Horario actualizado a {nuevo}")

    def editar_modalidad(self, curso):
        nueva = simpledialog.askstring("Editar modalidad", "Nueva modalidad (Presencial/Virtual/Híbrida):")
        if nueva:
            curso.asignar_modalidad(Modalidad(99, nueva, "", True, ""))
            messagebox.showinfo("Actualizado", f"Modalidad actualizada a {nueva}")

    def manage_asignaturas(self, parent):
        tree = ttk.Treeview(parent, columns=("ID", "Nombre", "Horas", "Créditos", "Estado"), show="headings")
        for col in ("ID", "Nombre", "Horas", "Créditos", "Estado"):
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        def refrescar():
            for i in tree.get_children():
                tree.delete(i)
            for a in asignaturas_lista:
                tree.insert("", "end", values=(a.id, a.nombre, a._Asignatura__horas, a._Asignatura__creditos, a._Asignatura__estado))

        refrescar()
        frame_form = ttk.Frame(parent)
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
            if nombre_asi.get():
                nueva = Asignatura(len(asignaturas_lista)+1, nombre_asi.get(), int(horas_asi.get()), int(creditos_asi.get()), "Activa")
                asignaturas_lista.append(nueva)
                refrescar()
                messagebox.showinfo("Éxito", "Asignatura creada")

        ttk.Button(frame_form, text="Agregar", command=agregar).pack(side="left", padx=5)

        def eliminar():
            sel = tree.selection()
            if sel:
                item = tree.item(sel[0])
                id_asi = item['values'][0]
                for a in asignaturas_lista:
                    if a.id == id_asi:
                        asignaturas_lista.remove(a)
                        break
                refrescar()
                messagebox.showinfo("Eliminado", "Asignatura eliminada")

        ttk.Button(parent, text="Eliminar seleccionada", command=eliminar).pack(pady=5)

    def manage_matriculas(self, parent=None):
        if parent is None:
            ventana = tk.Toplevel(self.root)
            ventana.title("Matrículas")
            parent = ventana
        tree = ttk.Treeview(parent, columns=("ID", "Estudiante", "Fecha", "Tipo", "Estado"), show="headings")
        for col in ("ID", "Estudiante", "Fecha", "Tipo", "Estado"):
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        def refrescar():
            for i in tree.get_children():
                tree.delete(i)
            for m in matriculas_lista:
                est = getattr(m, '_Matricula__estudiante', None)
                est_nombre = f"{est.nombre} {est.apellido}" if est else "N/A"
                tree.insert("", "end", values=(m.id, est_nombre, m._Matricula__fecha, m.tipo, m.estado))

        refrescar()

        def cambiar_estado():
            sel = tree.selection()
            if sel:
                item = tree.item(sel[0])
                id_mat = item['values'][0]
                nuevo = simpledialog.askstring("Cambiar estado", "Nuevo estado (Activa/Anulada/Pendiente):")
                if nuevo:
                    for m in matriculas_lista:
                        if m.id == id_mat:
                            m.estado = nuevo
                            break
                    refrescar()
                    messagebox.showinfo("Actualizado", f"Estado cambiado a {nuevo}")

        ttk.Button(parent, text="Cambiar estado", command=cambiar_estado).pack(pady=5)

    # -------------------- MÉTODOS PARA ADMINISTRADOR --------------------
    def add_admin_buttons(self, parent):
        ttk.Button(parent, text="Crear usuario", command=self.crear_usuario).pack(pady=5, fill='x')
        ttk.Button(parent, text="Eliminar usuario", command=self.eliminar_usuario).pack(pady=5, fill='x')
        ttk.Button(parent, text="Ver logs", command=self.ver_logs).pack(pady=5, fill='x')

    def manage_users(self, parent=None):
        if parent is None:
            ventana = tk.Toplevel(self.root)
            ventana.title("Usuarios")
            parent = ventana
        tree = ttk.Treeview(parent, columns=("Email", "Nombre", "Rol"), show="headings")
        tree.heading("Email", text="Email")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Rol", text="Rol")
        tree.pack(fill="both", expand=True)

        def refrescar():
            for i in tree.get_children():
                tree.delete(i)
            for u in usuarios.values():
                tree.insert("", "end", values=(u.email, f"{u.nombre} {u.apellido}", u.obtener_rol()))

        refrescar()
        ttk.Button(parent, text="Refrescar", command=refrescar).pack(pady=5)

    def crear_usuario(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Crear usuario")
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
            rol = rol_combo.get()
            if rol == "estudiante":
                matricula = simpledialog.askstring("Matrícula", "Ingrese matrícula:")
                carrera = simpledialog.askstring("Carrera", "Ingrese carrera:")
                nuevo = Estudiante(nombre_e.get(), apellido_e.get(), email_e.get(), pass_e.get(), matricula, carrera)
                estudiantes_lista.append(nuevo)
            elif rol == "docente":
                esp = simpledialog.askstring("Especialidad", "Ingrese especialidad:")
                nuevo = Docente(nombre_e.get(), apellido_e.get(), email_e.get(), pass_e.get(), esp)
                docentes_lista.append(nuevo)
            elif rol == "coordinador":
                nuevo = Coordinador(nombre_e.get(), apellido_e.get(), email_e.get(), pass_e.get())
            else:
                nuevo = Administrador(nombre_e.get(), apellido_e.get(), email_e.get(), pass_e.get())
            usuarios[nuevo.email] = nuevo
            messagebox.showinfo("Creado", f"Usuario {nuevo.email} creado")
            ventana.destroy()

        ttk.Button(ventana, text="Crear", command=guardar).pack(pady=10)

    def eliminar_usuario(self):
        emails = list(usuarios.keys())
        if not emails:
            messagebox.showinfo("Info", "No hay usuarios")
            return
        seleccion = simpledialog.askstring("Eliminar usuario", f"Ingrese email a eliminar:\n{emails}")
        if seleccion and seleccion in usuarios:
            if usuarios[seleccion] == self.current_user:
                messagebox.showerror("Error", "No puede eliminarse a sí mismo")
                return
            del usuarios[seleccion]
            global estudiantes_lista, docentes_lista
            estudiantes_lista = [e for e in estudiantes_lista if e.email != seleccion]
            docentes_lista = [d for d in docentes_lista if d.email != seleccion]
            messagebox.showinfo("Eliminado", f"Usuario {seleccion} eliminado")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")

    def ver_logs(self):
        messagebox.showinfo("Logs", "Simulación: logs del sistema (fecha, hora, acciones)")

    def show_config(self, parent=None):
        if parent is None:
            ventana = tk.Toplevel(self.root)
            parent = ventana
        ttk.Label(parent, text="Configuración general del sistema (simulación)").pack()
        ttk.Button(parent, text="Cambiar tema", command=lambda: messagebox.showinfo("Tema", "Tema cambiado (simulación)")).pack()
        ttk.Button(parent, text="Respaldar datos", command=lambda: messagebox.showinfo("Respaldo", "Respaldo simulado")).pack()

    # -------------------- DEMOSTRACIÓN POO --------------------
    def show_poo_demo(self, parent):
        texto = tk.Text(parent, wrap="word")
        texto.pack(fill="both", expand=True)
        demo = """=== DEMOSTRACIÓN DE CONCEPTOS POO ===

1. HERENCIA: Estudiante, Docente, etc. heredan de Persona.
2. POLIMORFISMO: obtener_rol() devuelve diferente según el objeto.
3. ABSTRACCIÓN: Persona y Evaluacion son abstractas.
4. ENCAPSULAMIENTO: Atributos privados __nombre, __email.
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
        for curso in cursos_lista:
            frame = ttk.LabelFrame(parent, text=curso._nombre)
            frame.pack(fill="x", padx=10, pady=5)
            ttk.Label(frame, text=f"Horario: {curso._horario}").pack(anchor="w")
            ttk.Label(frame, text=f"Modalidad: {curso._modalidad}").pack(anchor="w")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SistemaAcademicoApp()
    app.run()
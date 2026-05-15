from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models.estudiante import Estudiante
from models.docente import Docente
from models.administrador import Administrador
from models.coordinador import Coordinador
from models.tarea import Tarea
from models.curso import Curso, Horario, Modalidad
import os
from functools import wraps

# Inicializamos la aplicación Flask y la clave secreta usada por sesión.
app = Flask(__name__)
app.secret_key = 'clave_para_fase1'

# Configuración de Flask-Login para manejar la autenticación.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Ruta a la que redirige cuando no está autenticado.

# --------------------------------------------------
# DATOS SIMULADOS EN MEMORIA
# --------------------------------------------------
usuarios = {}

# Creamos usuarios de ejemplo para simular el sistema de autenticación.
est1 = Estudiante("Diocles", "Bacusoy", "diocles@gmail.com", "1234", "A001", "ISF")
est2 = Estudiante("Eddy", "Vera", "eddy@gmail.com", "1234", "A002", "Administración")
est3 = Estudiante("Josue", "Llerena", "josue@gmail.com", "1234", "A003", "Trabajo Social")
doc1 = Docente("Joan", "Intriago", "joan@gmail.com", "1234", "POO")
admin1 = Administrador("Jesus", "Palma", "jesus@gmail.com", "1234")
coord1 = Coordinador("Jonaiker", "Perez", "jonaiker@gmail.com", "1234")

# Guardamos los usuarios en el diccionario usando el email como clave.
for u in [est1, est2, est3, doc1, admin1, coord1]:
    usuarios[u.email] = u

# Definimos un curso de ejemplo con horario y modalidad.
curso1 = Curso(1, "POO con Python", 16, 64)
curso1.asignar_horario(Horario(1, "Lunes", "18:00", "20:00"))
curso1.asignar_modalidad(Modalidad(1, "Virtual", "Zoom", True, "Zoom"))
cursos = [curso1]

# Definimos una tarea de ejemplo solo para mostrar en la interfaz.
tarea_ejemplo = Tarea("Proyecto POO", "Implementar sistema académico", "2026-06-15", doc1.email)
tareas = [tarea_ejemplo]

# --------------------------------------------------
# DECORADOR DE ROLES
# --------------------------------------------------
# Este decorador envuelve rutas para que solo usuarios con ciertos roles
# puedan acceder a ellas. Además maneja el "modo estudiante" simulado.
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated(*args, **kwargs):
            if session.get('modo_estudiante_activo') and current_user.obtener_rol() != 'estudiante':
                # En vista de estudiante, roles no estudiantes solo pueden acceder a rutas válidas para estudiantes.
                if 'estudiante' in roles:
                    return f(*args, **kwargs)
                else:
                    flash("No tienes permiso en modo estudiante", "danger")
                    return redirect(url_for('index'))
            else:
                # Validación normal con el rol real del usuario.
                if current_user.obtener_rol() not in roles:
                    flash("Acceso denegado", "danger")
                    return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# --------------------------------------------------
# LOGIN MANAGER
# --------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    # Flask-Login pide esta función para recuperar el usuario desde el identificador guardado en sesión.
    return usuarios.get(user_id)

# --------------------------------------------------
# RUTAS DE AUTENTICACIÓN
# --------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Muestra el formulario de inicio de sesión y procesa el login.
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = usuarios.get(email)

        if user and user.get_password() == password:
            login_user(user)
            session.pop('modo_estudiante_activo', None)
            flash(f"Bienvenido {user.nombre}", "success")
            return redirect(url_for('index'))
        else:
            flash("Credenciales incorrectas", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Cierra la sesión activa y vuelve al login.
    logout_user()
    session.pop('modo_estudiante_activo', None)
    return redirect(url_for('login'))

# --------------------------------------------------
# RUTA PRINCIPAL
# --------------------------------------------------
@app.route('/')
@login_required
def index():
    # Calcula si se muestra la vista normal o la vista de estudiante simulada.
    modo_estudiante = session.get('modo_estudiante_activo', False)
    rol_real = current_user.obtener_rol()
    rol_vista = 'estudiante' if modo_estudiante and rol_real != 'estudiante' else rol_real

    # Contenido simulado para fase 1.
    tareas_disponibles = tareas if rol_vista == 'estudiante' else tareas
    mis_entregas = []

    return render_template('index.html',
                           usuario=current_user,
                           rol_vista=rol_vista,
                           modo_estudiante_activo=modo_estudiante,
                           tareas=tareas_disponibles,
                           mis_entregas=mis_entregas,
                           cursos=cursos)

# --------------------------------------------------
# PERFIL
# --------------------------------------------------
@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        # Solo el coordinador puede modificar datos (simulación)
        if current_user.obtener_rol() == 'coordinador':
            # Simulación: solo mostramos un mensaje
            nuevo_nombre = request.form.get('nombre')
            nuevo_apellido = request.form.get('apellido')
            nuevo_email = request.form.get('email')
            nueva_carrera = request.form.get('carrera')
            flash(f"[FASE 1] Simulación: Coordinador actualizaría los datos de {current_user.nombre} a {nuevo_nombre} {nuevo_apellido}.", "info")
        else:
            flash("No tienes permiso para modificar este perfil.", "danger")
        return redirect(url_for('perfil'))
    return render_template('perfil.html', usuario=current_user)
# --------------------------------------------------
# SUBIR TAREA
# --------------------------------------------------
@app.route('/subir_tarea', methods=['GET', 'POST'])
@role_required('estudiante')
def subir_tarea():
    modo_estudiante = session.get('modo_estudiante_activo', False)
    rol_real = current_user.obtener_rol()
    rol_vista = 'estudiante' if modo_estudiante and rol_real != 'estudiante' else rol_real

    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form.get('descripcion', '')
        archivo = request.files.get('archivo')
        if archivo:
            flash(f"[FASE 1] Tarea '{titulo}' recibida. {archivo.filename}.", "info")
        else:
            flash("Debe seleccionar un archivo", "danger")
        return redirect(url_for('subir_tarea'))

    return render_template('subir_tarea.html',
                           modo_estudiante_activo=modo_estudiante,
                           rol_vista=rol_vista)

# --------------------------------------------------
# MIS TAREAS
# --------------------------------------------------
@app.route('/mis_tareas')
@role_required('estudiante')
def mis_tareas():
    modo_estudiante = session.get('modo_estudiante_activo', False)
    rol_real = current_user.obtener_rol()
    rol_vista = 'estudiante' if modo_estudiante and rol_real != 'estudiante' else rol_real

    tareas_vacias = []
    flash("Las tareas se guardarán en la fase 2.", "info")
    return render_template('mis_tareas.html', 
                           tareas=tareas_vacias,
                           modo_estudiante_activo=modo_estudiante,
                           rol_vista=rol_vista)

# --------------------------------------------------
# CAMBIAR MODO ESTUDIANTE
# --------------------------------------------------
@app.route('/cambiar_modo')
@login_required
def cambiar_modo():
    # Permite alternar el modo de vista de estudiante para roles administrativos.
    if current_user.obtener_rol() != 'estudiante':
        if session.get('modo_estudiante_activo', False):
            session['modo_estudiante_activo'] = False
            flash("Modo estudiante desactivado", "info")
        else:
            session['modo_estudiante_activo'] = True
            flash("Modo estudiante activado. Ahora ves la plataforma como un estudiante (simulación).", "info")
    else:
        flash("Los estudiantes no pueden cambiar de modo", "warning")
    return redirect(url_for('index'))

# --------------------------------------------------
# VER ENTREGAS
# --------------------------------------------------
@app.route('/ver_entregas')
@role_required('docente', 'coordinador', 'administrador')
def ver_entregas():
    if session.get('modo_estudiante_activo'):
        flash("Desactive el modo estudiante para ver entregas", "warning")
        return redirect(url_for('index'))
    # Simulación: aún no existen entregas reales en esta fase.
    entregas = []
    flash("En fase 2 se mostrarán las tareas subidas por estudiantes.", "info")
    return render_template('lista_tareas.html', entregas=entregas)

# --------------------------------------------------
# ELIMINAR TAREA
# --------------------------------------------------
@app.route('/eliminar_tarea/<int:indice>')
@role_required('estudiante')
def eliminar_tarea(indice):
    # Esta ruta existe como placeholder; la eliminación real llegará en fase 2.
    flash("Eliminación de tareas no disponible en fase 1. Se implementará en la fase 2.", "warning")
    return redirect(url_for('mis_tareas'))

# --------------------------------------------------
# REGISTRAR NOTA
# --------------------------------------------------
@app.route('/registrar_nota', methods=['GET', 'POST'])
@role_required('docente', 'coordinador')
def registrar_nota():
    if request.method == 'POST':
        matricula = request.form['matricula']
        asignatura = request.form['asignatura']
        nota = float(request.form['nota'])
        # Buscamos un estudiante en memoria para mostrar la simulación.
        estudiante = next((e for e in usuarios.values() if hasattr(e, 'matricula') and e.matricula == matricula), None)
        if estudiante:
            flash(f"[FASE 1] Simulando registro de nota {nota} para {estudiante.nombre} en {asignatura}. En fase 2 se guardará.", "info")
        else:
            flash("Estudiante no encontrado", "danger")
        return redirect(url_for('index'))
    estudiantes = [u for u in usuarios.values() if hasattr(u, 'matricula')]
    return render_template('notas.html', estudiantes=estudiantes)

if __name__ == '__main__':
    app.run(debug=True)
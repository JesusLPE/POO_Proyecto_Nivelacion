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

app = Flask(__name__)
app.secret_key = 'clave_para_fase1'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ---------- BASE DE DATOS EN MEMORIA (SOLO PARA LOGIN Y ROLES) ----------
usuarios = {}

# Usuarios de ejemplo (sin funcionalidad real)
est1 = Estudiante("Diocles", "Bacusoy", "diocles@mail.com", "1234", "A001", "Ingeniería")
est2 = Estudiante("Eddy", "Vera", "eddy@mail.com", "1234", "A002", "Administración")
doc1 = Docente("Joan", "Intriago", "joan@mail.com", "1234", "POO")
admin1 = Administrador("Leonel", "Palma", "leonel@mail.com", "1234")
coord1 = Coordinador("Jonaiker", "Perez", "jonaiker@mail.com", "1234")

for u in [est1, est2, doc1, admin1, coord1]:
    usuarios[u.email] = u

# Algunos cursos de ejemplo (solo estructura)
curso1 = Curso(1, "POO con Python", 16, 64)
curso1.asignar_horario(Horario(1, "Lunes", "18:00", "20:00"))
curso1.asignar_modalidad(Modalidad(1, "Virtual", "Zoom", True, "Zoom"))
cursos = [curso1]

# Tarea de ejemplo (solo para mostrar en la vista, sin funcionalidad de entrega real)
tarea_ejemplo = Tarea("Proyecto POO", "Implementar sistema académico", "2026-06-15", doc1.email)
tareas = [tarea_ejemplo]

# ---------- DECORADOR DE ROLES ----------
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated(*args, **kwargs):
            if session.get('modo_estudiante_activo') and current_user.obtener_rol() != 'estudiante':
                if 'estudiante' in roles:
                    return f(*args, **kwargs)
                else:
                    flash("No tienes permiso en modo estudiante", "danger")
                    return redirect(url_for('index'))
            else:
                if current_user.obtener_rol() not in roles:
                    flash("Acceso denegado", "danger")
                    return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated
    return decorator

@login_manager.user_loader
def load_user(user_id):
    return usuarios.get(user_id)

# ---------- RUTAS DE AUTENTICACIÓN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = usuarios.get(email)
        if user and user._password == password:
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
    logout_user()
    session.pop('modo_estudiante_activo', None)
    return redirect(url_for('login'))

# ---------- RUTA PRINCIPAL ----------
@app.route('/')
@login_required
def index():
    modo_estudiante = session.get('modo_estudiante_activo', False)
    rol_real = current_user.obtener_rol()
    rol_vista = 'estudiante' if modo_estudiante and rol_real != 'estudiante' else rol_real

    # Datos simulados para la vista
    tareas_disponibles = tareas if rol_vista == 'estudiante' else tareas
    mis_entregas = []  # En fase 1 no se guardan entregas reales

    return render_template('index.html',
                           usuario=current_user,
                           rol_vista=rol_vista,
                           modo_estudiante_activo=modo_estudiante,
                           tareas=tareas_disponibles,
                           mis_entregas=mis_entregas,
                           cursos=cursos)

# ---------- PERFIL (solo estudiantes pueden modificar, pero sin guardado real) ----------
@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        if current_user.obtener_rol() == 'estudiante':
            # Solo simulamos la actualización
            nuevo_nombre = request.form['nombre']
            nueva_carrera = request.form['carrera']
            flash(f"[FASE 1] Se recibió la solicitud de actualizar perfil a {nuevo_nombre} - {nueva_carrera}. En fase 2 se guardará.", "info")
        else:
            flash("Solo los estudiantes pueden modificar su perfil", "warning")
        return redirect(url_for('perfil'))
    return render_template('perfil.html', usuario=current_user)

# ---------- SUBIR TAREA (solo simulación) ----------
@app.route('/subir_tarea', methods=['GET', 'POST'])
@role_required('estudiante')
def subir_tarea():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form.get('descripcion', '')
        archivo = request.files.get('archivo')
        if archivo:
            flash(f"[FASE 1] Tarea '{titulo}' recibida. {archivo.filename}.", "info")
        else:
            flash("Debe seleccionar un archivo", "danger")
        return redirect(url_for('subir_tarea'))
    return render_template('subir_tarea.html')

# ---------- MIS TAREAS (solo muestra que la interacción está prevista) ----------
@app.route('/mis_tareas')
@role_required('estudiante')
def mis_tareas():
    # En fase 1, no hay tareas guardadas realmente, solo mostramos un mensaje
    tareas_vacias = []
    flash("Las tareas se guardarán en la fase 2.", "info")
    return render_template('mis_tareas.html', tareas=tareas_vacias)

# ---------- CAMBIAR MODO ESTUDIANTE ----------
@app.route('/cambiar_modo')
@login_required
def cambiar_modo():
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

# ---------- VER ENTREGAS (SOLO DOCENTE, simulada) ----------
@app.route('/ver_entregas')
@role_required('docente', 'coordinador', 'administrador')
def ver_entregas():
    if session.get('modo_estudiante_activo'):
        flash("Desactive el modo estudiante para ver entregas", "warning")
        return redirect(url_for('index'))
    # Simulación: no hay entregas reales en fase 1
    entregas = []
    flash("En fase 2 se mostrarán las tareas subidas por estudiantes.", "info")
    return render_template('lista_tareas.html', entregas=entregas)

# ---------- ELIMINAR TAREA (no implementado en fase 1) ----------
@app.route('/eliminar_tarea/<int:indice>')
@role_required('estudiante')
def eliminar_tarea(indice):
    flash("Eliminación de tareas no disponible en fase 1. Se implementará en la fase 2.", "warning")
    return redirect(url_for('mis_tareas'))

# ---------- REGISTRAR NOTA (solo simulación) ----------
@app.route('/registrar_nota', methods=['GET', 'POST'])
@role_required('docente', 'coordinador')
def registrar_nota():
    if request.method == 'POST':
        matricula = request.form['matricula']
        asignatura = request.form['asignatura']
        nota = float(request.form['nota'])
        # Buscar estudiante (solo para mostrar simulación)
        estudiante = next((e for e in usuarios.values() if hasattr(e, 'matricula') and e.matricula == matricula), None)
        if estudiante:
            flash(f"[FASE 1] Simulando registro de nota {nota} para {estudiante.nombre} en {asignatura}. En fase 2 se guardará.", "info")
        else:
            flash("Estudiante no encontrado", "danger")
        return redirect(url_for('index'))
    # Lista de estudiantes para el select (solo los que tienen matrícula)
    estudiantes = [u for u in usuarios.values() if hasattr(u, 'matricula')]
    return render_template('notas.html', estudiantes=estudiantes)

if __name__ == '__main__':
    app.run(debug=True)
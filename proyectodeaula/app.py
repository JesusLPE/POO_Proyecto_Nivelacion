from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models.estudiante import Estudiante
from models.docente import Docente
from models.administrador import Administrador
from models.coordinador import Coordinador
from models.tarea import Tarea
import os

app = Flask(__name__)
app.secret_key = 'clave_super_secreta'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Base de datos en memoria (diccionarios)
usuarios = {}       # email -> objeto usuario
tareas = []         # lista de objetos Tarea

# Cargar usuarios de ejemplo
est1 = Estudiante("Diocles", "Bacusoy", "diocles@mail.com", "1234", "A001", "Ingeniería")
est2 = Estudiante("Eddy", "Vera", "eddy@mail.com", "1234", "A002", "Administración")
doc1 = Docente("Joan", "Intriago", "joan@mail.com", "1234", "POO")
admin1 = Administrador("Leonel", "Palma", "leonel@mail.com", "1234")
coord1 = Coordinador("Jonaiker", "Perez", "javier@mail.com", "1234")

for u in [est1, est2, doc1, admin1, coord1]:
    usuarios[u.email] = u

# Tarea de ejemplo
tarea_ejemplo = Tarea("Proyecto POO", "Implementar sistema de gestión académica", "2026-06-15", doc1.email)
tareas.append(tarea_ejemplo)

@login_manager.user_loader
def load_user(user_id):
    return usuarios.get(user_id)

# Decorador para roles
def role_required(*roles):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated(*args, **kwargs):
            # Verificar modo estudiante: si el usuario tiene activado modo_estudiante,
            # entonces se le muestra la vista de estudiante aunque sea docente.
            if session.get('modo_estudiante_activo') and current_user.obtener_rol() != 'estudiante':
                # Permitir acceso a rutas de estudiante
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = usuarios.get(email)
        if user and user._password == password:
            login_user(user)
            # Limpiar modo estudiante al iniciar sesión
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

@app.route('/')
@login_required
def index():
    # Verificar modo estudiante
    modo_estudiante = session.get('modo_estudiante_activo', False)
    rol_real = current_user.obtener_rol()
    rol_vista = 'estudiante' if modo_estudiante and rol_real != 'estudiante' else rol_real

    # Obtener tareas según el rol de vista
    if rol_vista == 'estudiante':
        # Mostrar tareas disponibles y las entregas del estudiante
        tareas_disponibles = tareas
        mis_entregas = [entrega for t in tareas for entrega in t.entregas if entrega['estudiante_email'] == current_user.email]
    elif rol_vista == 'docente':
        tareas_disponibles = tareas
        mis_entregas = None
    else:
        tareas_disponibles = tareas
        mis_entregas = None

    return render_template('index.html',
                           usuario=current_user,
                           rol_vista=rol_vista,
                           modo_estudiante_activo=modo_estudiante,
                           tareas=tareas_disponibles,
                           mis_entregas=mis_entregas if rol_vista == 'estudiante' else None)

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    # Solo el estudiante puede modificar su perfil; otros roles solo ven (o pueden editar campos comunes)
    if request.method == 'POST':
        if current_user.obtener_rol() == 'estudiante':
            # Actualizar datos del estudiante
            current_user.nombre = request.form['nombre']
            current_user.apellido = request.form['apellido']
            current_user.carrera = request.form['carrera']
            flash("Perfil actualizado", "success")
        else:
            flash("Solo los estudiantes pueden modificar su perfil desde aquí", "warning")
        return redirect(url_for('perfil'))

    return render_template('perfil.html', usuario=current_user)

@app.route('/subir_tarea', methods=['GET', 'POST'])
@role_required('estudiante')
def subir_tarea():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form.get('descripcion', '')
        # Simulamos archivo subido
        archivo = request.files.get('archivo')
        if archivo:
            filename = archivo.filename
            # Guardar en disco simulado (omitimos por brevedad)
            current_user.subir_tarea(titulo, filename, '2026-06-20')
            flash("Tarea subida correctamente", "success")
        else:
            flash("Debe seleccionar un archivo", "danger")
        return redirect(url_for('subir_tarea'))
    return render_template('subir_tarea.html')

@app.route('/mis_tareas')
@role_required('estudiante')
def mis_tareas():
    return render_template('mis_tareas.html', tareas=current_user.tareas_subidas)

@app.route('/cambiar_modo')
@login_required
def cambiar_modo():
    # Solo docentes, coordinadores y administradores pueden cambiar al modo estudiante
    if current_user.obtener_rol() != 'estudiante':
        if session.get('modo_estudiante_activo', False):
            session['modo_estudiante_activo'] = False
            flash("Modo estudiante desactivado", "info")
        else:
            session['modo_estudiante_activo'] = True
            flash("Modo estudiante activado. Ahora ves la plataforma como un estudiante.", "info")
    else:
        flash("Los estudiantes no pueden cambiar de modo", "warning")
    return redirect(url_for('index'))

# Ruta para docentes: ver todas las entregas de estudiantes
@app.route('/ver_entregas')
@role_required('docente', 'coordinador', 'administrador')
def ver_entregas():
    # Si está en modo estudiante, redirigir a index o mostrar advertencia
    if session.get('modo_estudiante_activo'):
        flash("Desactive el modo estudiante para ver entregas", "warning")
        return redirect(url_for('index'))
    todas_entregas = []
    for tarea in tareas:
        for entrega in tarea.entregas:
            estudiante = usuarios.get(entrega['estudiante_email'])
            todas_entregas.append({
                "tarea_titulo": tarea.titulo,
                "estudiante_nombre": estudiante.nombre if estudiante else "desconocido",
                "archivo": entrega['archivo'],
                "fecha": entrega['fecha']
            })
    return render_template('lista_tareas.html', entregas=todas_entregas)

@app.route('/eliminar_tarea/<int:indice>')
@role_required('estudiante')
def eliminar_tarea(indice):
    if 0 <= indice < len(current_user.tareas_subidas):
        eliminada = current_user.tareas_subidas.pop(indice)
        flash(f"Tarea '{eliminada['titulo']}' eliminada", "success")
    else:
        flash("Tarea no encontrada", "danger")
    return redirect(url_for('mis_tareas'))

if __name__ == '__main__':
    app.run(debug=True)
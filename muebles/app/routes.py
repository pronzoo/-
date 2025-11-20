from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.init_db import get_all_users, get_user_by_email
from app.init_db import bcrypt

main = Blueprint("main", __name__)

# Ruta de inicio
@main.route('/')
def index():
    return render_template("index.html")

# Ruta de login
@main.route('/login', methods=["GET", "POST"])
def login():
    # 🚫 Si ya está logueado, no tiene sentido mostrar el form
    if "user_id" in session:
        flash("Ya iniciaste sesión.", "info")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = get_user_by_email(email)

        if user and bcrypt.check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["nombre"]
            flash("Login exitoso", "success")
            # ✅ Ahora lo mandamos al index
            return redirect(url_for("main.index"))
        else:
            flash("Email o contraseña incorrectos", "danger")
            return render_template("form.html")

    # GET: muestro el form solo si no está logueado (ya lo controlamos arriba)
    return render_template("form.html")

# Ruta de logout
@main.route('/logout')
def logout():
    session.clear()  # Limpiar la sesión
    flash("Has cerrado sesión exitosamente", "info")
    return redirect(url_for("main.login"))  # Redirige al login

# Ruta de productos
@main.route('/productos')
def productos():
    return render_template("muebles.html")

# Ruta de contacto
@main.route('/contacto')
def contacto():
    return render_template("contacto.html")

# Ruta de home
@main.route('/home')
def home():
    # Verificamos si el usuario está logueado antes de acceder a la página
    if "user_id" not in session:
        flash("Debes iniciar sesión para ver esta página", "warning")
        return redirect(url_for("main.login"))
    
    usuarios = get_all_users()  # Obtener usuarios de la base de datos
    return render_template("usuarios.html", usuarios=usuarios)

# Ruta para ver usuarios desde la base de datos
@main.route('/usuariosBD')
def usuariosBD():
    # Aquí obtenemos todos los usuarios de la base de datos
    usuarios = get_all_users()
    return render_template("usuarios.html", usuarios=usuarios)

# Ruta de submit de formulario
@main.route('/submit', methods=['POST'])
def submit():
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    return render_template('index.html')

# app/__init__.py
import os
from flask import Flask
from dotenv import load_dotenv

from app.init_db import bcrypt, init_db  # bcrypt y función para inicializar la DB

def create_app():
    # Cargar variables de entorno desde .env
    load_dotenv()

    app = Flask(__name__)

    # Secret key necesaria para session y flash
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "mi_clave_secreta")

    # Inicializar bcrypt con la app
    bcrypt.init_app(app)

    # Inicializar la base de datos si no existe
    init_db()

    # Registrar blueprints de la aplicación principal
    from app.routes import main
    app.register_blueprint(main)

    from app.users.routes import users
    app.register_blueprint(users, url_prefix="/users")

    # Registrar blueprint de autenticación con Google
    from app.auth.routes import auth
    app.register_blueprint(auth)  # Tiene url_prefix="/auth" dentro del blueprint

    return app

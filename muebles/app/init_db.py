# app/init_db.py
import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()  # Inicializamos bcrypt

DB_NAME = 'deconlinee.db'

# ----------------- FUNCIONES DE CONEXIÓN -----------------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Esto nos permite acceder a los resultados por nombre de columna
    return conn

# ----------------- USUARIOS -----------------
def get_all_users():
    """Obtiene todos los usuarios de la base de datos."""
    conn = get_db_connection()
    usuarios = conn.execute("SELECT * FROM usuarios").fetchall()
    conn.close()
    return usuarios

def get_user_by_email(email):
    """Obtiene un usuario por su email."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Obtiene un usuario por su ID."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def create_user(nombre, email, password, rol):
    """Crea un nuevo usuario en la base de datos."""
    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)",
        (nombre, email, hashed_pw, rol)
    )
    conn.commit()
    conn.close()

# ----------------- PRODUCTOS -----------------
def get_all_products():
    """Obtiene todos los productos de la base de datos."""
    conn = get_db_connection()
    productos = conn.execute("SELECT * FROM productos").fetchall()
    conn.close()
    return productos

# ----------------- INICIALIZACIÓN DB -----------------
def init_db():
    """Inicializa la base de datos con tablas si no existen."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabla usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    ''')

    # Crear admin con contraseña encriptada
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", ("inge@gmail.com",))
    if cursor.fetchone() is None:
        admin_hash = bcrypt.generate_password_hash("thomasito10").decode("utf-8")
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)",
            ("Inge", "inge@gmail.com", admin_hash, "admin")
        )

    # Tabla productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            tipo TEXT NOT NULL,
            precio REAL NOT NULL,
            descripcion TEXT,
            stock INTEGER DEFAULT 0
        )
    ''')

    productos = [
        {"titulo": "sillon de oficina", "tipo": "sillon", "precio": 800000, "descripcion": "Sillon comodo calidad premium"},
        {"titulo": "silla de playa", "tipo": "silla", "precio": 250000, "descripcion": "Silla ideal para la playa"},
        {"titulo": "sillon de living", "tipo": "sillon", "precio": 1000000, "descripcion": "Sillon ideal para la familia"}
    ]

    for prod in productos:
        cursor.execute("SELECT * FROM productos WHERE titulo = ?", (prod["titulo"],))
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO productos (titulo, tipo, precio, descripcion) VALUES (?, ?, ?, ?)",
                (prod["titulo"], prod["tipo"], prod["precio"], prod["descripcion"])
            )

    # Tabla ventas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 1,
            total REAL NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente")

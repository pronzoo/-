# app/auth/routes.py

import os
import requests

from flask import (
    Blueprint,
    redirect,
    request,
    session,
    url_for,
    flash,
)

from dotenv import load_dotenv

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests

# Cargar variables de entorno (.env)
load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# En desarrollo, permitir HTTP (NO usar esto en producción)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Blueprint de autenticación
auth = Blueprint("auth", __name__, url_prefix="/auth")


def _get_flow(state: str | None = None) -> Flow:
    """
    Crea y devuelve un objeto Flow configurado con nuestro client_id y client_secret.

    Coincide con lo que pide Google y con la redirect_uri del PPT:
    http://127.0.0.1:5000/auth/callback
    """
    redirect_uri = "http://127.0.0.1:5000/auth/callback"

    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }

    scopes = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]

    flow = Flow.from_client_config(
        client_config,
        scopes=scopes,
        state=state,
    )
    flow.redirect_uri = redirect_uri
    return flow


# Paso 2 - Ruta de Login (inicio del flujo OAuth)
@auth.route("/login")
def login_google():
    """
    Inicia el flujo de autenticación con Google.
    Redirige a la pantalla de login de Google.
    """
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        flash("Faltan configurar GOOGLE_CLIENT_ID o GOOGLE_CLIENT_SECRET en el .env", "danger")
        return redirect(url_for("main.login"))

    flow = _get_flow()

    # authorization_url: URL a la que redirigimos al usuario
    # state: token aleatorio para prevenir ataques CSRF
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",  # fuerza a elegir cuenta (útil en demos)
    )

    # Guardamos el state en la sesión
    session["oauth_state"] = state

    return redirect(authorization_url)


# Paso 3 - Ruta de Callback (Google redirige acá)
@auth.route("/callback")
def callback():
    """
    Recibe la respuesta de Google, intercambia el 'code' por un token,
    valida el ID Token y guarda los datos del usuario en la sesión.
    """
    state = session.get("oauth_state")

    if state is None:
        flash("La sesión de autenticación ha expirado. Por favor, intenta de nuevo.", "warning")
        return redirect(url_for("main.login"))

    # Recreamos el flow con el mismo state
    flow = _get_flow(state=state)

    # URL completa con el "code" que mandó Google
    authorization_response = request.url

    # Intercambiamos el código por tokens (access_token, id_token, etc.)
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    # Verificación del ID Token
    request_session = requests.Session()
    token_request = google.auth.transport.requests.Request(session=request_session)

    try:
        id_info = id_token.verify_oauth2_token(
            credentials._id_token,
            token_request,
            GOOGLE_CLIENT_ID,
        )
    except Exception:
        flash("Error al verificar el token de Google. Intenta nuevamente.", "danger")
        return redirect(url_for("main.login"))

    # Datos básicos del usuario de Google
    google_user_id = id_info.get("sub")       # ID único de Google
    name = id_info.get("name")
    email = id_info.get("email")
    picture = id_info.get("picture")

    # Guardamos en la sesión para que /home detecte que está logueado
    # IMPORTANTE: tu /home solo chequea que exista session["user_id"]
    # así que usamos este ID de Google.
    session["user_id"] = google_user_id
    session["user_name"] = name
    session["user_email"] = email
    session["user_picture"] = picture
    session["is_google_auth"] = True

    flash("Inicio de sesión con Google exitoso.", "success")
    
    return redirect(url_for("main.index"))

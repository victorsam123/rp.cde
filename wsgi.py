from dotenv import load_dotenv
from cde_deployment import validar_configuracion_cde

load_dotenv()
validar_configuracion_cde()

from app import app

app.config["SESSION_COOKIE_NAME"] = "rp_cde_session"

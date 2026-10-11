import os


def validar_configuracion_cde(environ=None):
    env = os.environ if environ is None else environ
    if env.get("CDE_DEPLOYMENT") != "1" and not env.get("RAILWAY_ENVIRONMENT_ID"):
        return
    required = ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD", "SECRET_KEY", "ADMIN_PASSWORD")
    missing = [name for name in required if not env.get(name)]
    if missing:
        raise RuntimeError("Configuracion de Ciudad del Este incompleta: " + ", ".join(missing))
    if env.get("MUNICIPALITY_ID") != "ciudad_del_este":
        raise RuntimeError("El despliegue requiere MUNICIPALITY_ID=ciudad_del_este.")
    if env["DB_NAME"] != "rp_cde":
        raise RuntimeError("Ciudad del Este requiere su base independiente DB_NAME=rp_cde.")
    if len(env["SECRET_KEY"]) < 32 or env["SECRET_KEY"].startswith("REEMPLAZAR"):
        raise RuntimeError("Configure una SECRET_KEY propia de al menos 32 caracteres.")
    if env["ADMIN_PASSWORD"] == "Admin@2026!" or env["ADMIN_PASSWORD"].startswith("REEMPLAZAR"):
        raise RuntimeError("Configure una ADMIN_PASSWORD propia para Ciudad del Este.")
    if env.get("SESSION_COOKIE_SECURE") != "1":
        raise RuntimeError("El despliegue HTTPS requiere SESSION_COOKIE_SECURE=1.")

"""Integration checks on a newly created local database, never on the configured one."""
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import sys
from html.parser import HTMLParser
from contextlib import redirect_stdout
from itertools import count
from unittest.mock import patch

import psycopg2
from psycopg2 import sql
from dotenv import dotenv_values
from jinja2 import FileSystemLoader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
STATE = ROOT / ".qa/session.json"
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=")


class ContractParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.controls = []
        self.forms = []
        self.links = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form":
            self.forms.append(tuple(attrs.get(key, "") for key in ("method", "action", "enctype", "onsubmit")))
        if tag in ("input", "select", "textarea", "option"):
            keys = ("id", "name", "type", "required", "accept", "min", "max", "maxlength", "value")
            self.controls.append((tag, tuple(attrs.get(key) if key != "value" or attrs.get("name") != "csrf_token" else "TOKEN" for key in keys)))
        if tag == "a" and attrs.get("href", "").startswith("/") and not attrs["href"].startswith("/static/"):
            self.links.add(attrs["href"])


def local_config():
    values = dotenv_values(ROOT / ".env")
    if values.get("DB_HOST") not in ("localhost", "127.0.0.1", "::1"):
        raise RuntimeError("These checks require local PostgreSQL, not a remote database.")
    return values


def initialize(create):
    values = local_config()
    if create:
        state = {"database": "rp_cde_qa_" + secrets.token_hex(5), "password": secrets.token_urlsafe(24)}
        connection = psycopg2.connect(host=values["DB_HOST"], port=values.get("DB_PORT", "5432"),
                                      user=values["DB_USER"], password=values["DB_PASSWORD"], dbname="postgres")
        try:
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(state["database"])))
        finally:
            connection.close()
        STATE.parent.mkdir(exist_ok=True)
        STATE.write_text(json.dumps(state), encoding="utf-8")
    else:
        state = json.loads(STATE.read_text(encoding="utf-8"))
    if not re.fullmatch(r"rp_cde_qa_[0-9a-f]{10}", state["database"]):
        raise RuntimeError("Not an isolated QA database.")
    os.environ.update({key: str(value) for key, value in values.items() if value is not None})
    os.environ.update(DB_NAME=state["database"], ADMIN_PASSWORD=state["password"],
                      SECRET_KEY=secrets.token_hex(32), SESSION_COOKIE_SECURE="0", CDE_DEPLOYMENT="0")
    import app as module
    app = module.app
    app.config.update(TESTING=True, TEMPLATES_AUTO_RELOAD=True, SESSION_COOKIE_NAME="rp_cde_qa_session")
    public = ROOT / ".qa/public"
    shutil.copytree(ROOT / "static", public, dirs_exist_ok=True, ignore=shutil.ignore_patterns("uploads"))
    (public / "uploads").mkdir(exist_ok=True)
    app.static_folder = str(public)
    app.config["UPLOAD_FOLDER"] = str(public / "uploads")
    return module, state


def exercise(module, state, template_dir):
    app = module.app
    app.jinja_loader = FileSystemLoader(str(template_dir))
    app.jinja_env.cache.clear()
    connection = module.obtener_conexion()
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE reportes, logs_cambios RESTART IDENTITY")
        cursor.execute("DELETE FROM usuarios WHERE usuario <> 'admin'")
        cursor.execute("SELECT setval(pg_get_serial_sequence('usuarios', 'id'), (SELECT MAX(id) FROM usuarios))")
    connection.commit()
    connection.close()
    pages = {}
    checks = []
    client = app.test_client()

    def get(path):
        response = client.get(path)
        assert response.status_code == 200, (path, response.status_code)
        if response.mimetype == "text/html":
            pages[path] = response.get_data(as_text=True)
        return response

    def post(path, data=None):
        with client.session_transaction() as session:
            has_token = bool(session.get("csrf_token"))
        if not has_token:
            client.get("/ciudadano")
        with client.session_transaction() as session:
            token = session["csrf_token"]
        return client.post(path, data={"csrf_token": token, **(data or {})})

    get("/ciudadano")
    get("/login")
    assert client.get("/admin").status_code == 302
    assert client.post("/crear_reporte", data={}).status_code == 400
    checks.append("Acceso publico, proteccion administrativa y CSRF")
    assert post("/crear_reporte", {}).status_code == 302
    assert module.contar_total_reportes() == 0
    sample = {"nombre": "Ciudadano de prueba CDE", "telefono": "0981123456", "correo": "prueba@example.com",
              "tipo": module.CATALOGO_TIPOS_POR_PRIORIDAD[0]["opciones"][0], "descripcion": "Incidencia de prueba aislada.",
              "ubicacion": "Centro de Ciudad del Este", "mapa_url": "https://www.google.com/maps?q=-25.509,-54.611"}
    for change in ({"telefono": "abc"}, {"correo": "invalido"}, {"descripcion": "x" * 2001},
                   {"mapa_url": "https://www.google.com/maps?q=-25.563,-54.611"}):
        assert post("/crear_reporte", {**sample, **change}).status_code == 302
        assert module.contar_total_reportes() == 0
    assert post("/crear_reporte", {**sample, "foto_problema": (io.BytesIO(b"bad"), "bad.exe")}).status_code == 302
    assert module.contar_total_reportes() == 0
    assert post("/crear_reporte", {**sample, "foto_problema": (io.BytesIO(b"x" * (6 * 1024 * 1024)), "grande.png")}).status_code == 413
    assert module.contar_total_reportes() == 0
    checks.append("Campos obligatorios, telefono, correo, longitud, geocerca y formato de foto")
    sequence = count(1)
    with patch.object(module, "generar_codigo_reporte", side_effect=lambda: f"REP-ABCD{next(sequence):04d}"):
        response = post("/crear_reporte", {**sample, "foto_problema": (io.BytesIO(PNG), "prueba.png")})
        assert response.status_code == 302 and response.location.endswith("/confirmacion/1")
        for index in range(2, 25):
            tipo = module.CATALOGO_TIPOS_POR_PRIORIDAD[index % len(module.CATALOGO_TIPOS_POR_PRIORIDAD)]["opciones"][0]
            assert post("/crear_reporte", {**sample, "nombre": f"Ciudadano de prueba {index:02d}", "tipo": tipo}).status_code == 302
    get("/confirmacion/1")
    report = module.obtener_reporte_por_id(1)
    assert get("/static/" + report["foto_problema"]).data == PNG
    pdf = get("/descargar_comprobante/1")
    assert pdf.data.startswith(b"%PDF")
    assert get("/api/buscar_reporte?id=REP-ABCD0001").json["exito"]
    assert client.get("/api/buscar_reporte?id=invalid").status_code == 400
    checks.append("Registro persistido, foto visible, seguimiento y comprobante PDF")
    assert post("/login", {"usuario": "admin", "clave": "incorrecta"}).location.endswith("/login")
    response = post("/login", {"usuario": "admin", "clave": state["password"]})
    assert response.location.endswith("/admin")
    get("/admin")
    get("/reportes")
    get("/reportes?pagina=2")
    get("/reportes?estado=Pendiente&busqueda=prueba&ordenar_por=nombre&direccion=asc")
    get("/reportes_pendientes")
    get("/reportes_realizados")
    get("/reporte/1")
    assert post("/cambiar_estado/1", {"estado": "Realizado"}).status_code == 302
    assert module.obtener_reporte_por_id(1)["estado"] == "Realizado"
    assert post("/guardar_observacion/1", {"observacion_admin": "Verificacion aislada CDE"}).status_code == 302
    assert module.obtener_reporte_por_id(1)["observacion_admin"] == "Verificacion aislada CDE"
    assert post("/subir_foto_solucion/1", {"foto_solucion": (io.BytesIO(PNG), "solucion.png")}).status_code == 302
    assert get("/static/" + module.obtener_reporte_por_id(1)["foto_solucion"]).data == PNG
    get("/reporte/1")
    get("/reportes_realizados")
    get("/estadisticas")
    for path in ("/admin/exportar/todos", "/admin/exportar/pendientes", "/admin/exportar/realizados",
                 "/admin/exportar/estadisticas", "/reportes/exportar/pdf", "/reporte/1/pdf"):
        assert get(path).data.startswith(b"%PDF"), path
    checks.append("Login, dashboard, filtros, paginacion, detalle, estado, observacion, solucion, estadisticas y 6 exportaciones PDF")
    get("/usuarios_admin")
    get("/crear_usuario_admin")
    fields = {"nombre": "Usuario CDE QA", "usuario": "cde_qa", "password": "QA-password-123",
              "confirmar_password": "QA-password-123", "rol": "admin"}
    assert post("/crear_usuario_admin", fields).location.endswith("/usuarios_admin")
    user = module.buscar_usuario_por_nombre("cde_qa")
    assert user
    assert post("/crear_usuario_admin", fields).location.endswith("/crear_usuario_admin")
    get(f"/editar_usuario_admin/{user['id']}")
    assert post(f"/editar_usuario_admin/{user['id']}", {"nombre": "Usuario CDE editado", "usuario": "cde_qa", "rol": "admin", "activo": "1"}).status_code == 302
    assert module.buscar_usuario_por_nombre("cde_qa")["nombre"] == "Usuario CDE editado"
    get("/cambiar_clave")
    assert client.get("/logout").location.endswith("/login")
    get("/login")
    post("/login", {"usuario": "cde_qa", "clave": fields["password"]})
    assert post("/cambiar_clave", {"clave_actual": fields["password"], "nueva_clave": "QA-nueva-456", "confirmar_nueva": "QA-nueva-456"}).status_code == 302
    client.get("/logout")
    get("/login")
    assert post("/login", {"usuario": "cde_qa", "clave": "QA-nueva-456"}).location.endswith("/admin")
    client.get("/logout")
    get("/login")
    post("/login", {"usuario": "admin", "clave": state["password"]})
    assert post(f"/eliminar_usuario_admin/{user['id']}").status_code == 302
    assert module.buscar_usuario_por_nombre("cde_qa") is None
    checks.append("Alta, duplicados, edicion, cambio de clave, nuevo login, eliminacion y logout")
    return pages, checks


def validate_contracts(before, after):
    differences = []
    for path, html in before.items():
        left, right = ContractParser(), ContractParser()
        left.feed(html)
        right.feed(after[path])
        assert left.forms == right.forms, ("Forms changed", path)
        assert left.controls == right.controls, ("Controls changed", path)
        assert left.links <= right.links, ("Actions removed", path, left.links - right.links)
        if html != after[path]:
            differences.append(path)
    return differences


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--baseline", action="store_true")
    parser.add_argument("--port", type=int, default=5003)
    args = parser.parse_args()
    if args.serve:
        module, state = initialize(False)
        if args.baseline:
            module.app.jinja_loader = FileSystemLoader(str(ROOT / ".qa/before/templates"))
        module.app.config["TESTING"] = False
        module.app.run(host="127.0.0.1", port=args.port, debug=False)
    else:
        has_baseline = (ROOT / ".qa/before/templates").exists()
        with redirect_stdout(io.StringIO()):
            module, state = initialize(not STATE.exists())
            before, checks_before = exercise(module, state, ROOT / ".qa/before/templates") if has_baseline else ({}, [])
            after, checks_after = exercise(module, state, ROOT / "templates")
        for path, snapshot in ((ROOT / "app.py", ROOT / ".qa/before/app.py"),
                               (ROOT / "static/ciudad_del_este_boundary.geojson", ROOT / ".qa/before/ciudad_del_este_boundary.geojson")):
            if has_baseline:
                assert hashlib.sha256(path.read_bytes()).digest() == hashlib.sha256(snapshot.read_bytes()).digest(), path
        changed = validate_contracts(before, after)
        palette_before = set()
        for path in (ROOT / ".qa/before/templates").glob("*.html"):
            palette_before.update(value.lower() for value in re.findall(r"#[0-9a-fA-F]{3,8}\b", path.read_text(encoding="utf-8-sig")))
        palette_after = set(value.lower() for value in re.findall(r"#[0-9a-fA-F]{3,8}\b", (ROOT / "static/css/cde-institucional.css").read_text()))
        if has_baseline:
            assert palette_after <= palette_before, palette_after - palette_before
        for name in ("ciudadano.html", "login.html"):
            pattern = r"<script\b[^>]*>.*?</script>"
            if has_baseline:
                assert re.findall(pattern, (ROOT / "templates" / name).read_text(encoding="utf-8"), re.S) == re.findall(pattern, (ROOT / ".qa/before/templates" / name).read_text(encoding="utf-8-sig"), re.S), name
        result = {"database": state["database"], "checks_before": checks_before, "checks_after": checks_after,
                  "rendered_pages": len(after), "redesigned_pages": changed, "baseline_compared": has_baseline,
                  "backend_unchanged": True if has_baseline else None, "geofence_unchanged": True if has_baseline else None,
                  "palette_preserved": True if has_baseline else None, "form_contracts_preserved": True if has_baseline else None}
        (ROOT / ".qa/regression-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        inventory = {"routes": [{"path": str(rule), "endpoint": rule.endpoint, "methods": sorted(rule.methods - {'HEAD', 'OPTIONS'})}
                                for rule in module.app.url_map.iter_rules()], "forms_and_fields": {}}
        for route, html in after.items():
            contract = ContractParser()
            contract.feed(html)
            inventory["forms_and_fields"][route] = {"forms": contract.forms, "fields": contract.controls, "action_links": sorted(contract.links)}
        (ROOT / "docs").mkdir(exist_ok=True)
        (ROOT / "docs/INVENTARIO_CDE.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(result, indent=2))

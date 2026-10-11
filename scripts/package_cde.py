from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "RP_CDE_REDISENO_VISUAL_PROFESIONAL.zip"
TOP_LEVEL = ("app.py", "wsgi.py", "cde_deployment.py", "requirements.txt", "Procfile",
             "railway.toml", "Dockerfile", ".dockerignore", ".gitignore", ".env.cde.example")


def project_files():
    for name in TOP_LEVEL:
        yield ROOT / name
    for folder in ("templates", "static", "tests", "docs", "scripts"):
        for path in sorted((ROOT / folder).rglob("*")):
            relative = path.relative_to(ROOT)
            if not path.is_file() or "__pycache__" in relative.parts:
                continue
            if relative.parts[:2] == ("static", "uploads"):
                continue
            if path.suffix in (".pyc", ".log", ".zip"):
                continue
            yield path


if __name__ == "__main__":
    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in project_files():
            archive.write(path, path.relative_to(ROOT).as_posix())
    with ZipFile(OUTPUT) as archive:
        names = archive.namelist()
        assert archive.testzip() is None
        assert ".env" not in names
        assert ".env.cde.example" in names
        assert "railway.toml" in names
        assert not any(name.startswith((".qa/", ".runtime/", ".git/", "static/uploads/")) for name in names)
        print(f"ZIP verificado: {OUTPUT.name}; {len(names)} archivos; {OUTPUT.stat().st_size} bytes; sin credenciales ni fotografias de ciudadanos.")

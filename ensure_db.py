"""Crea la base DB_NAME si no existe (idempotente). Se ejecuta antes de gunicorn."""
import os
import sys

import psycopg2
from psycopg2 import sql


def main():
    name = os.environ.get("DB_NAME")
    if not name or not os.environ.get("DB_HOST"):
        return
    conn = None
    for admin_db in ("postgres", "railway"):
        try:
            conn = psycopg2.connect(
                host=os.environ["DB_HOST"],
                port=int(os.environ.get("DB_PORT", "5432")),
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
                dbname=admin_db,
                connect_timeout=10,
            )
            break
        except psycopg2.OperationalError as exc:
            print(f"ensure_db: no se pudo abrir {admin_db}: {exc}", file=sys.stderr)
    if conn is None:
        sys.exit(1)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,))
        if cur.fetchone():
            print(f"ensure_db: {name} ya existe")
        else:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
            print(f"ensure_db: {name} creada")
    conn.close()


if __name__ == "__main__":
    main()

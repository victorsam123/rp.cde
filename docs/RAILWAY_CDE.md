# Despliegue independiente de Ciudad del Este

La configuracion entregada pertenece a esta copia. No vincularla al proyecto, al servicio PostgreSQL, al volumen ni a las credenciales de Presidente Franco.

## Proyecto y servicios

1. Crear un proyecto Railway independiente, por ejemplo `RP-CDE`, con un servicio web `rp-cde-web` y un servicio PostgreSQL `postgres-cde` nuevos.
2. En el PostgreSQL nuevo, crear la base `rp_cde`. Ejecutar `CREATE DATABASE rp_cde;` exclusivamente en ese servicio nuevo. Cambiar el nombre de una variable no crea una base sobre un volumen existente.
3. Conectar el servicio web a este repositorio/copia. Usar el Dockerfile incluido y el comando de inicio de `railway.toml`. No cambiar la configuracion del servicio de Presidente Franco.
4. Crear un volumen exclusivo de Ciudad del Este y montarlo en `/app/static/uploads` para conservar las fotografias entre despliegues.

## Variables del servicio web

| Variable | Valor/origen |
| --- | --- |
| `MUNICIPALITY_ID` | `ciudad_del_este` |
| `CDE_DEPLOYMENT` | `1` |
| `DB_HOST` | `${{postgres-cde.PGHOST}}` del PostgreSQL nuevo |
| `DB_PORT` | `${{postgres-cde.PGPORT}}` |
| `DB_USER` | `${{postgres-cde.PGUSER}}` |
| `DB_PASSWORD` | `${{postgres-cde.PGPASSWORD}}` |
| `DB_NAME` | `rp_cde`, previamente creada en el PostgreSQL nuevo |
| `SECRET_KEY` | Clave aleatoria nueva, exclusiva de CDE, de al menos 32 caracteres |
| `ADMIN_PASSWORD` | Password inicial propia; no reutilizar la de otra municipalidad |
| `SESSION_COOKIE_SECURE` | `1` |
| `FLASK_DEBUG` | `0` |
| `PORT` | La asigna Railway; no fijar un puerto local |

El archivo `.env.cde.example` contiene solamente una plantilla sin credenciales. El `.env` local existente no se modifico ni se incluye en la entrega. La aplicacion conserva el uso de `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` y `DB_NAME`; no se cambio la conexion PostgreSQL de `app.py`.

## Comprobacion antes de arrancar

`wsgi.py` valida la configuracion mediante `cde_deployment.py` antes de importar `app.py`. En Railway, o con `CDE_DEPLOYMENT=1`, rechaza otra identidad municipal, una base distinta de `rp_cde`, variables ausentes, secretos predeterminados y cookies sin HTTPS. El nombre de cookie queda en `rp_cde_session`.

Esta comprobacion reduce errores de configuracion, pero no demuestra por si sola que el servicio o las credenciales sean exclusivos: la separacion efectiva requiere el proyecto y el PostgreSQL nuevos. El mismo nombre de base en otro servidor tampoco prueba aislamiento. Verificar las referencias desde el panel de Railway.

El arranque original inicializa tablas, crea el administrador inicial y puede normalizar reportes existentes. Por eso debe apuntar a la base CDE nueva desde el primer despliegue.

El healthcheck `/ciudadano` comprueba que la aplicacion responde; no sustituye una prueba de conexion y registro en PostgreSQL. Usar un solo worker evita ejecutar simultaneamente la inicializacion original desde multiples procesos.

## Validacion del despliegue

Comprobar el dominio HTTPS propio, el login, un reporte de prueba dentro de CDE, sus fotografias, el seguimiento, un cambio de estado y un PDF. Confirmar que el reporte no aparece en Presidente Franco y que sus usuarios no acceden a CDE. No copiar datos o backups de Presidente Franco como inicializacion de esta version.

Los proyectos Railway y las bases remotas no se crearon ni modificaron durante este trabajo. La entrega prepara la configuracion; el aislamiento remoto debe verificarse al desplegar.

## Referencias

- [PostgreSQL y variables de conexion](https://docs.railway.com/databases/postgresql).
- [Red privada y aislamiento por entorno](https://docs.railway.com/networking/private-networking).
- [Configuracion de despliegue](https://docs.railway.com/config-as-code/reference).

La documentacion consultada indica que Config as Code esta deprecado y que los archivos existentes siguen funcionando para servicios legacy hasta el 1 de diciembre de 2026. Para un servicio nuevo, confirmar en Railway el mecanismo vigente o definir los mismos ajustes de Docker, inicio, healthcheck y reinicio desde el panel. El Dockerfile no depende del constructor Nixpacks.

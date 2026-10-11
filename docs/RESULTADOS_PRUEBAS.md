# Resultados de verificacion

Fecha: 11 de octubre de 2026.

## Entorno y comparacion

Flask y PostgreSQL locales, con una base nueva `rp_cde_qa_*` y fotografias sinteticas en un directorio exclusivo de pruebas. Se ejecuto el mismo recorrido con las plantillas anteriores y con las nuevas. Los datos originales y las credenciales del `.env` no se modificaron.

La comparacion abarca 15 respuestas HTML: ciudadano, login, confirmacion, dashboard, reportes, segunda pagina, filtros/ordenacion, pendientes, realizados, detalle, estadisticas, usuarios, alta, edicion y cambio de clave.

Se verificaron por hash `app.py` y el poligono: sin modificaciones durante el rediseno. Los scripts de ciudadano y login permanecen iguales. Los metodos y acciones de formularios, sus campos y restricciones, los valores de las opciones y los enlaces funcionales se conservaron. La hoja nueva no introduce valores HEX ajenos a la paleta anterior.

## Funcionalidad ejecutada

| Prueba | Resultado |
| --- | --- |
| Acceso ciudadano y login | HTTP 200 |
| Acceso administrativo sin sesion | Redireccion al login |
| POST sin CSRF | HTTP 400 |
| Campos obligatorios, telefono, correo y longitud | Rechazo sin crear reportes |
| Coordenadas externas a CDE | Rechazo sin crear reportes |
| Foto con extension no permitida | Rechazo sin crear reportes |
| Archivo superior al limite de 5 MB | HTTP 413 |
| Registro de reporte con foto y Google Maps | Persistido en la base de prueba |
| Confirmacion, foto del problema y seguimiento por codigo | Correctos |
| Comprobante PDF ciudadano | Generado; cabecera `%PDF` verificada |
| Login incorrecto y correcto, logout | Correctos |
| Dashboard, pendientes, realizados y detalle | HTTP 200 |
| Filtros, ordenacion y pagina 2 | HTTP 200; contratos de controles/enlaces conservados |
| Cambio de estado, observacion y foto de solucion | Persistidos y recuperados correctamente |
| Estadisticas | HTTP 200 con datos de prueba |
| Seis exportaciones PDF administrativas | Generadas; cabecera `%PDF` verificada |
| Alta, prevencion de usuario duplicado y edicion | Correctas |
| Cambio de clave y posterior login con la clave nueva | Correctos |
| Eliminacion del usuario de prueba | Correcta |

Cinco pruebas unitarias verifican coordenadas dentro/fuera, datos invalidos, borde del distrito, rechazo de envio directo externo y el GeoJSON publicado. Otras siete pruebas verifican la configuracion independiente de CDE, incluyendo rechazo de otra base, otra municipalidad, variables incompletas y secretos predeterminados.

La prueba JavaScript de la geocerca confirma siete ubicaciones y un punto del limite. Ambas validaciones, navegador y servidor, aceptan los puntos CDE y rechazan los puntos probados en Presidente Franco, Hernandarias, Minga Guazu y Foz do Iguacu.

## Navegador

Playwright con Microsoft Edge en modo headless. Se generaron 62 capturas de las versiones anterior y nueva, en 1440, 390 y 320 px. Las capturas seleccionadas de la version nueva estan en `capturas/`.

Se ejecutaron en navegador las pestanas de registro y seguimiento, consulta de codigo, validacion HTML obligatoria, GPS simulado dentro/fuera, error de login, mostrar/ocultar password, login correcto, alta/eliminacion de usuario y logout. En el nuevo diseno se comprobo el menu movil y su cierre mediante Escape. Las dos fotografias del detalle cargaron correctamente.

No hubo errores JavaScript. El nuevo diseno no presenta desbordamiento horizontal de pagina en los tamanos probados. Las tablas y graficos anchos mantienen desplazamiento dentro de su contenedor. El anterior dashboard desbordaba hasta 780 px en movil; el nuevo ajuste corrige ese problema.

En las capturas anteriores se bloqueo la fotografia externa de Unsplash y se proporciono la misma fuente Poppins desde archivos locales para evitar demoras externas. La comparacion visual del login anterior no incluye esa fotografia. La version nueva no utiliza esa fotografia y carga Poppins e iconos desde archivos del proyecto.

## Limites

- GPS comprobado con coordenadas simuladas del navegador; no se probo un telefono fisico ni el permiso de ubicacion del sistema operativo.
- Las imagenes de prueba son PNG sinteticos. No se utilizaron fotografias ni datos de ciudadanos reales.
- Se verifico que los PDF se generan, pero no se revisaron visualmente todas sus paginas. Su implementacion no se modifico.
- Las pruebas administrativas usan el rol admin. No se certifica una auditoria integral de permisos para todos los perfiles.
- No se ejecuto una imagen Docker: el equipo no dispone del comando Docker. La sintaxis TOML y Python se comprueban localmente.
- No se desplego en Railway, no se crearon servicios remotos y no se verifico el aislamiento frente al despliegue real de Presidente Franco. Los pasos estan en `RAILWAY_CDE.md`.
- WhatsApp conserva los enlaces existentes; no se enviaron mensajes a ciudadanos.

## Reproduccion

En un entorno Python con `requirements.txt`, configurar un PostgreSQL local con permiso para crear una base nueva y ejecutar `python tests/verify_redesign.py`. El script rechaza servidores remotos y solo limpia sus tablas en una base con nombre `rp_cde_qa_*`. Mantiene esa base local para inspeccion. Nunca usa la base configurada originalmente como destino de las pruebas.

La entrega no incluye la copia previa de las plantillas. Sin esa copia, el script ejecuta el recorrido actual e indica `baseline_compared=false`; el resultado comparativo de este trabajo queda registrado en este documento. Ejecutar las pruebas unitarias con `python tests/run_checks.py`, que configura la base aislada antes de importar la aplicacion. La geocerca JavaScript se verifica con `node tests/test_geocerca.cjs`.

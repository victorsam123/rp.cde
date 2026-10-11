# Entrega del rediseno visual de Ciudad del Este

## Cambios visuales

- Ciudadano: encabezado institucional, titulo Reporte Ciudadano / Ciudad del Este, formulario principal a la izquierda y contexto municipal a la derecha. Datos del ciudadano, incidencia/ubicacion y evidencia tienen secciones separadas. Las pestanas de registro y seguimiento conservan sus eventos originales.
- Login: una sola columna centrada con identidad municipal y acceso administrativo; sustituye la composicion anterior en dos paneles sobre una fotografia externa.
- Administracion: barra lateral clara, navegacion agrupada, pagina activa identificada y encabezado con contexto municipal. El menu movil cuenta con cierre, fondo y tecla Escape.
- Dashboard: indicadores generales primero, indicadores ejecutivos despues, tabla de actividad y accesos en una columna lateral. Se eliminan los paneles flotantes y las tarjetas anidadas.
- Reportes y usuarios: filtros alineados, tablas compactas, filas con separacion clara y acciones existentes. Las tablas anchas se desplazan dentro de su contenedor en movil.
- Detalle: identificacion, ciudadano e incidencia diferenciados, fotografias completas y formularios administrativos separados por divisores.
- Estadisticas: indicadores, barras, distribucion por estado y lecturas ejecutivas con jerarquia tipografica uniforme y estructura adaptable.
- Creacion/edicion de usuarios, cambio de clave y confirmacion: formularios y comprobante integrados al mismo sistema visual.

Se conserva la paleta anterior, incluyendo todos los colores de estados, prioridades, botones y graficos. Los nuevos estilos reutilizan exclusivamente valores HEX existentes. Poppins se conserva y se incluye localmente, con licencia; Lucide se incluye como sprite local y con su licencia.

## Archivos

- Plantillas: `base.html`, `ciudadano.html`, `login.html`, `confirmacion.html`, `admin.html`, `reportes.html`, `reportes_pendientes.html`, `reportes_realizados.html`, `detalle_reporte.html`, `estadisticas.html`, `usuarios_admin.html`, `crear_usuario.html`, `editar_usuario.html`, `cambiar_clave.html` y el nuevo parcial `_cde_icons.html`.
- Recursos: `static/css/cde-institucional.css`, `static/cde-icons.svg`, `static/LUCIDE-LICENSE.txt`, las cinco fuentes Poppins y su licencia en `static/fonts`.
- Configuracion CDE: `railway.toml`, `Dockerfile`, `.dockerignore`, `.env.cde.example`, `cde_deployment.py` y `wsgi.py`.
- Pruebas y documentacion: `tests/verify_redesign.py`, `tests/test_cde_deployment.py`, los tests de geocerca existentes, los documentos de entrega y el inventario generado.
- `.gitignore`: exclusion de herramientas de prueba, dependencias locales y registros.

## Proteccion funcional

Durante este rediseno no se modifico `app.py`, la geocerca, las rutas, las consultas, el esquema, la autenticacion ni las operaciones de reportes. La comprobacion SHA-256 compara `app.py` y el GeoJSON contra la copia anterior al rediseno.

Se comparan los formularios HTML renderizados: metodos, destinos, enctype, campos, identificadores, tipos, valores, restricciones y enlaces de acciones. Los scripts de ciudadano y login se comparan sin cambios. Solo el menu administrativo incorpora comportamiento visual para abrir/cerrar el panel movil.

Las diferencias de presentacion en textos con escapes Unicode se limitan al texto visible: el valor original del selector de estados se conserva. La deteccion comparativa permitio corregir una sustitucion accidental de ese atributo antes de la entrega.

La configuracion adicional responde al pedido de independencia municipal. La validacion previa de WSGI y el nombre de cookie no cambian el sistema de autenticacion ni la conexion de `app.py`. La configuracion Railway, las variables y el almacenamiento exclusivo se documentan en `RAILWAY_CDE.md`.

## Pruebas

Ver `RESULTADOS_PRUEBAS.md` para resultados ejecutados, condiciones y limites. Las pruebas funcionales usan una base nueva local `rp_cde_qa_*` y un directorio de fotografias de prueba separados. Ningun reporte ni usuario de la base configurada originalmente se usa como dato de prueba.

El inventario de rutas, formularios y campos se entrega en `INVENTARIO_CDE.json`. Los contratos comparados se mantuvieron iguales antes y despues del rediseno.

## Ejecucion local

Instalar `requirements.txt` en un entorno Python propio y configurar `.env` con un PostgreSQL exclusivo de CDE. Para HTTP local, usar `CDE_DEPLOYMENT=0` y `SESSION_COOKIE_SECURE=0`. Ejecutar `python app.py` para la vista local o usar `wsgi:app` con un servidor WSGI compatible.

El ZIP no contiene credenciales, fotografias de ciudadanos, dependencias de herramientas locales, registros ni datos de base de datos. El directorio `static/uploads` se crea al iniciar. Las pruebas de ubicacion usan coordenadas simuladas; la verificacion en telefonos reales queda pendiente.

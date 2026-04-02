# Especificación del Módulo: Profesionales (Junami 2.0)

## 1. Objetivo del Módulo
Gestionar el equipo de profesionales, configuración del sistema (obras sociales) y copias de seguridad. Extraer la lógica de `app.py` y crear un Blueprint en `rutas/profesionales.py`.

## 2. Rutas a migrar
* `GET/POST /profesionales` - Directorio del equipo y creación de nuevos profesionales.
* `POST /profesional/editar/<int:id>` - Edición de datos y foto de perfil.
* `GET /profesional/<int:id>` - Ficha individual del profesional.
* `POST /profesional/asignar_paciente` - Asignación rápida de pacientes.
* `GET/POST /configuracion` - Ajustes del sistema y actualización del perfil propio.
* `GET /configuracion/backup` - Generación y descarga del archivo ZIP de respaldo.

## 3. Reglas de Negocio
* **Restricciones:** Usuarios con `jerarquia == 'Auxiliar'` no pueden acceder a `/profesionales` ni `/configuracion`. Si intentan entrar, redirigir a `dashboard_personal_bp.dashboard2`.
* **Fotos de Perfil:** Guardar usando `secure_filename` con la nomenclatura `profesional_{id}.{ext}`. Si el usuario actualiza su propio perfil, hay que actualizar también `session['usuario_actual']` para que el cambio se vea en el momento.
* **Obras Sociales:** La ruta de configuración maneja un campo `action` para agregar (`add_os`) o eliminar (`delete_os`) obras sociales en `parametros.json`.
* **Backups:** La ruta `/configuracion/backup` debe crear un ZIP en memoria (`io.BytesIO()`) con las carpetas `datos` y `static/uploads`, y devolverlo usando `send_file`.
* **Dependencias:** Importar `cargar_datos` desde `utils.py`.

## 4. app.py
* Eliminar las funciones originales del archivo principal.
* Registrar el Blueprint `profesionales_bp`.
* Asegurar mediante `app.add_url_rule` que los enlaces del frontend (`url_for('profesionales')` y `url_for('configuracion')`) sigan funcionando.
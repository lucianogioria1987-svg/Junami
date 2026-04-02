# Especificación del Módulo: Configuración y Backups (Junami 2.0)

## 1. Objetivo del Módulo
Separar la lógica de ajustes del sistema y copias de seguridad, dándole su propio espacio independiente. Extraer estas rutas (actualmente en `rutas/profesionales.py` o `app.py`) hacia un nuevo Blueprint en `rutas/configuracion.py`.

## 2. Rutas y Endpoints a migrar
* `GET/POST /configuracion` - Panel de ajustes del sistema (obras sociales, parámetros).
* `GET /configuracion/backup` - Generación y descarga del archivo ZIP de la base de datos.

## 3. Reglas de Negocio Estrictas
* **Restricción Crítica:** El acceso a configuración es exclusivo. Si `session['usuario_actual']['jerarquia'] == 'Auxiliar'`, denegar acceso y redirigir a `dashboard_personal_bp.dashboard2`.
* **Manejo del Backup:** Mantener la lógica intacta usando `io.BytesIO()` y `zipfile.ZipFile` para empaquetar las carpetas `datos` y `static/uploads`, devolviendo el archivo con `send_file`.
* **Edición de Parámetros:** La lógica de agregar o eliminar obras sociales (u otros parámetros de `parametros.json`) se maneja aquí.
* **Dependencias:** Importar `cargar_datos` u otras utilidades necesarias desde `utils.py`.

## 4. Integración en el Sistema
* **Limpieza:** Eliminar estas funciones del archivo donde se encuentren actualmente (probablemente `rutas/profesionales.py`).
* **app.py:** Registrar el nuevo Blueprint `configuracion_bp`.
* Asegurar mediante `app.add_url_rule` que los enlaces visuales del frontend (`url_for('configuracion')`) sigan resolviendo perfectamente.
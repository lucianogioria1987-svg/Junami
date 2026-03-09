# Especificación del Módulo: Reportes y Estadísticas (Junami 2.0)

## 1. Objetivo del Módulo
Extraer toda la lógica de cálculo, filtrado y renderizado de métricas de la clínica. Encapsular esta lógica en un Flask Blueprint dentro del archivo `rutas/reportes.py`.

## 2. Rutas y Endpoints a migrar
* `GET/POST /reportes` - Renderiza la pantalla principal de estadísticas y procesa los filtros por rango de fechas u otros parámetros.

## 3. Reglas de Negocio Estrictas (Business Logic)

### 3.1. Restricción de Seguridad por Rol
* Al igual que en el Dashboard General, la información estadística global es confidencial. 
* Si el `session['usuario_actual']` tiene `jerarquia == 'Auxiliar'`, se le debe denegar el acceso y redirigir automáticamente a `dashboard_personal_bp.dashboard2`.

### 3.2. Carga y Procesamiento de Datos
* Importar la función `cargar_datos` desde `utils.py`.
* Leer los archivos base necesarios (típicamente `pacientes.json`, `sesiones.json` y `profesionales.json`).
* Mantener intacta la lógica matemática original que genera los contadores (ej: pacientes activos vs. inactivos, cantidad de turnos por estado, distribución por obras sociales o diagnósticos).
* Si la ruta recibe parámetros `POST` (ejemplo: filtrado por mes o rango de fechas), aplicar los filtros a las listas antes de calcular los totales.

## 4. Integración en app.py (Frontend)
* No realizar modificaciones en la plantilla `reportes.html` (o el nombre que tenga el HTML original).
* Eliminar la función original `reportes()` (o similar) de `app.py`.
* Registrar el Blueprint `reportes_bp`.
* CRÍTICO: Asegurar mediante un alias (`app.add_url_rule`) que cualquier llamada en el frontend a `url_for('reportes')` siga funcionando sin romperse para no afectar el menú de navegación.
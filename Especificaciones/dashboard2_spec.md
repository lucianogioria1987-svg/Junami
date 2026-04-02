# Especificación del Módulo: Dashboard Personal (Junami 2.0)

## 1. Objetivo del Módulo
Aislar el panel de control individual de los profesionales (conocido como `dashboard2`). Toda la lógica debe encapsularse en un Blueprint llamado `dashboard_personal_bp` dentro del archivo `rutas/dashboard_personal.py`.

## 2. Rutas y Endpoints a migrar
* `GET /dashboard2` - Función `dashboard2()`

## 3. Reglas de Negocio Estrictas (Business Logic)
* **Validación de Sesión:** Si el usuario no está en sesión, redirigir a `login`.
* **Procesamiento de Turnos:**
  * Leer `sesiones.json`. Filtrar únicamente los turnos que coincidan con el día actual Y donde el `profesional_nombre` sea el del usuario logueado.
  * Por defecto, el `estado_turno` visual en esta vista es 'Confirmado'.
* **Procesamiento de Pacientes y Equipo:**
  * `mis_pacientes`: Filtrar de `pacientes.json` aquellos que tienen al usuario en su lista de `profesionales`.
  * `mi_equipo`: Si el usuario actual tiene `jerarquia == 'Titular'`, buscar en `profesionales.json` a quienes lo tengan definido como `supervisor`.
* **Procesamiento de Recordatorios:**
  * Leer `recordatorios.json`, filtrar los del usuario actual y ordenarlos por `fecha_iso` y `hora`.
* **Dependencias:** Importar `cargar_datos` y `obtener_mapa_fotos_pacientes` desde `utils.py`. Importar `datetime` de la librería estándar.

## 4. Integración en app.py
* Eliminar por completo la función `dashboard2` del archivo `app.py`.
* Registrar el Blueprint `dashboard_personal_bp`.
* Asegurar (mediante alias o nombrado correcto) que todas las plantillas que llaman a `url_for('dashboard2')` sigan funcionando perfectamente.
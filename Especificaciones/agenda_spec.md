# Especificación del Módulo: Agenda y Turnos (Junami 2.0)

## 1. Objetivo del Módulo
Gestionar el calendario de sesiones, asignación de consultorios y estados de los turnos de la clínica. Desacoplar la lógica actual de `app.py` y encapsularla en un Flask Blueprint dentro de `rutas/agenda.py`.

## 2. Rutas y Endpoints a migrar
* `GET /agenda` - Renderiza la vista principal del calendario/agenda (`agenda.html`).
* `POST /agenda` - Procesa la creación manual de un nuevo turno general.
* `GET /turno/cambiar_estado/<int:id>/<string:nuevo_estado>` - Actualiza el estado de un turno específico (ej: Confirmado, Cancelado, Asistió) y redirige.

## 3. Reglas de Negocio Estrictas (Business Logic)

### 3.1. Carga de Contexto para la Vista
La ruta `GET /agenda` necesita procesar múltiples fuentes de datos antes de renderizar:
* Leer `pacientes.json`, `sesiones.json` y `profesionales.json`.
* Utilizar los helpers `obtener_mapa_fotos_pacientes` y `obtener_mapa_fotos_profesionales` (ahora en `utils.py`) para inyectar visualmente las fotos en cada tarjeta de sesión.
* Inyectar el ID del profesional leyendo desde el mapa de profesionales.

### 3.2. Creación de un Nuevo Turno (POST /agenda)
Al crear un turno, se deben garantizar las siguientes claves en el nuevo objeto JSON que se guardará en `sesiones.json`:
* `id`: Autoincremental.
* `id_paciente`: Obtenido del formulario (int).
* `nombre_paciente`: Extraído buscando el id_paciente en la lista de pacientes (Fallback: "Desconocido").
* `dias`: Lista de días seleccionados (request.form.getlist).
* `hora`, `tipo`, `consultorio`: Directo del formulario.
* `profesional_nombre` y `profesional_especialidad`: Se toman del `session['usuario_actual']` de quien está logueado creando el turno.
* `estado_turno`: Por defecto debe ser `"Confirmado"`.

### 3.3. Cambio de Estado Rápido
La ruta `/turno/cambiar_estado...` busca el turno por ID en `sesiones.json`, actualiza la clave `estado_turno` con el string recibido por URL, guarda el archivo, y DEBE redirigir a `dashboard2` (el panel personal del profesional).

## 4. UI/UX (Frontend)
No se deben realizar modificaciones en `agenda.html`. Asegurar mediante `app.add_url_rule` (en `app.py`) o configurando correctamente el Blueprint que los `url_for('agenda')` o `url_for('cambiar_estado_turno')` de las plantillas HTML sigan funcionando sin romperse.
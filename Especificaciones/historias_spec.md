# Especificación del Módulo: Historias Clínicas (Junami 2.0)

## 1. Objetivo del Módulo
Gestionar la visualización y carga de evoluciones clínicas de los pacientes en la vista dedicada. Desacoplar la lógica actual de `app.py` y encapsularla en un Flask Blueprint dentro de `rutas/historias.py`.

## 2. Rutas y Endpoints a migrar
* `GET/POST /historias` - Renderiza la pantalla principal de historias clínicas y procesa la carga de nuevas notas.

## 3. Reglas de Negocio Estrictas (Business Logic)

### 3.1. Restricción de Seguridad por Rol
* Al ingresar, se debe verificar el rol del usuario logueado.
* Si el usuario tiene `jerarquia == 'Auxiliar'` Y no viene con un parámetro `id_paciente` en la URL (`request.args.get('id_paciente')`), se le debe denegar el acceso global y redirigir a `dashboard2`.

### 3.2. Carga de Contexto (GET)
* Leer `pacientes.json`, `historias.json` y `profesionales.json`.
* Utilizar el helper `obtener_mapa_fotos_profesionales` (importado de `utils.py`) para tener disponibles las fotos del staff.
* Si hay un `id_paciente` seleccionado:
  1. Buscar los datos de ese paciente específico.
  2. Filtrar el historial correspondiente a ese ID.
  3. Invertir la lista (`reverse()`) para mostrar lo más reciente arriba.
  4. Inyectar la `foto_profesional` en cada registro del historial.

### 3.3. Creación de Nuevo Registro (POST)
Al enviar una nueva evolución desde esta pantalla, el sistema debe:
* Calcular el nuevo `id` autoincremental para `historias.json`.
* Registrar el `id_paciente` y el texto de la `nota` recibidos del formulario.
* Inyectar automáticamente el nombre del `profesional` que está en sesión.
* Inyectar la fecha actual en formato `DD/MM/YYYY` y la hora en formato `HH:MM`.
* Guardar en el JSON y redirigir a la misma ruta `historias` manteniendo el parámetro URL `id_paciente` para que la pantalla recargue mostrando el nuevo registro.

## 4. Integración en app.py (Frontend)
* No realizar modificaciones en la plantilla `historias.html`.
* Eliminar la función original de `app.py`.
* Registrar el Blueprint `historias_bp`.
* Asegurar mediante un alias (`app.add_url_rule`) que cualquier llamada en el frontend a `url_for('historias')` siga funcionando sin romperse.
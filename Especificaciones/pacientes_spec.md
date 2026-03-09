# Especificación del Módulo: Pacientes (Junami 2.0)

## 1. Objetivo del Módulo
Gestionar el ciclo de vida de los pacientes activos. Extraer toda la lógica de `app.py` y crear un Blueprint independiente en `rutas/pacientes.py`. Se deben utilizar los helpers globales ahora ubicados en `utils.py`.

## 2. Rutas y Endpoints a migrar
* `GET /pacientes` - Listado general de pacientes activos.
* `GET/POST /pacientes/nuevo` - Creación manual de un paciente.
* `GET /paciente/<int:id>` - Ficha integral del paciente (`ficha_paciente.html`).
* `GET/POST /paciente/editar/<int:id>` - Edición de datos del legajo.
* `POST /paciente/subir_archivo` - Subida de documentos a la historia.
* `GET /paciente/estado/<int:id>` - Toggle activo/inactivo (Soft delete).
* `POST /paciente/asignar_turno/<int:id>` - Asignación rápida de turnos.
* `POST /paciente/guardar_plan/<int:id>` - Actualización de objetivos y plan anual.
* `POST /paciente/actualizar_equipo/<int:id>` - Gestión de profesionales a cargo.
* `POST /paciente/guardar_evolucion/<int:id>` - Registro diario de sesiones.

## 3. Reglas de Negocio Estrictas (Business Logic)

### 3.1. Retención de Estado Visual (State Loss Prevention) - CRÍTICO
Para mejorar la UX, todas las rutas `POST` que modifiquen datos dentro de la ficha de un paciente, DEBEN redirigir al perfil del paciente adjuntando el parámetro URL `tab` correspondiente. 
* `/paciente/editar/...` -> `redirect(url_for('pacientes_bp.perfil_paciente', id=id, tab='clinica'))`
* `/paciente/subir_archivo` -> `redirect(url_for('pacientes_bp.perfil_paciente', id=id, tab='docs'))`
* `/paciente/guardar_plan/...` -> `redirect(url_for('pacientes_bp.perfil_paciente', id=id, tab='plan'))`
* `/paciente/actualizar_equipo/...` -> `redirect(url_for('pacientes_bp.perfil_paciente', id=id, tab='clinica'))`
* `/paciente/guardar_evolucion/...` -> `redirect(url_for('pacientes_bp.perfil_paciente', id=id, tab='evoluciones'))`

*(Nota para el agente: Adapta el nombre de la función `url_for` según cómo nombres el Blueprint, asegurando que el parámetro `tab` se envíe siempre).*

### 3.2. Gestión de Archivos (Uploads)
* **Fotos de Perfil:** Al crear o editar, se guardan como `paciente_{id}.ext`.
* **Documentación:** Al subir en `/subir_archivo`, el formato de nombre debe ser estricto: `{tipo_documento}_{id_paciente}_{YYYYMMDDHHMMSS}.ext` utilizando la fecha actual. Los datos del archivo se apendean a la lista `archivos_adjuntos` dentro de `pacientes.json`.

### 3.3. Evoluciones Clínicas
La ruta `guardar_evolucion` no guarda en `pacientes.json`, sino que inserta un nuevo objeto en `historias.json` vinculado al `id_paciente`. Debe inyectar automáticamente la fecha (`DD/MM/YYYY`) y hora actual (`HH:MM`), junto con el nombre del `profesional` (tomado de la sesión actual).

## 4. UI/UX (Frontend)
No se deben realizar modificaciones en las plantillas HTML (como `ficha_paciente.html`) durante esta refactorización. Mantener los enlaces compatibles con la configuración de enrutamiento.
# Especificación del Módulo: Admisiones (Junami 2.0)

## 1. Objetivo del Módulo
Gestionar el ingreso de posibles pacientes a la clínica. Este módulo debe ser desacoplado del archivo monolítico `app.py` y convertido en un Flask Blueprint (ej: `routes/admisiones.py` o `modulos/admisiones.py`).

## 2. Rutas y Endpoints a migrar
El Blueprint debe manejar las siguientes rutas exactas para no romper la navegación actual:
* `GET /admisiones` - Renderiza el listado histórico de admisiones (`admisiones.html`). Ordenado por ID descendente.
* `POST /admisiones` - Crea una nueva solicitud de admisión desde un formulario tipo Wizard.
* `GET /admision/<int:id>` - Renderiza la ficha individual del candidato (`ficha_admision.html`).
* `POST /admision/<int:id>` - Procesa la edición del candidato o la subida rápida de la entrevista.
* `GET /admision/alta/<int:id>` - Aprueba al candidato, lo migra a `pacientes.json` y cambia su estado.
* `GET /admision/borrar/<int:id>` - Elimina el registro de `admisiones.json`.
* `GET /admision/imprimir/<int:id>` - Renderiza la vista de impresión (`imprimir_admision.html`).

## 3. Reglas de Negocio Estrictas (Business Logic)

### 3.1. Procesamiento de Fechas
Todas las fechas que ingresan desde formularios HTML (`YYYY-MM-DD`) deben guardarse en el JSON en formato latino (`DD/MM/YYYY`). Al enviarlas de vuelta al HTML, deben ser transformadas mediante el filtro `fecha_input`. (Se deben seguir usando los helpers globales de `app.py`).

### 3.2. Gestión de Archivos Adjuntos (Uploads)
Los archivos subidos deben usar `secure_filename` y guardarse en `app.config['UPLOAD_FOLDER']` con prefijos específicos según su tipo:
* Informes Diagnósticos (Múltiples): `diag_{id}_{filename}`
* Informes Previos (Múltiples): `previo_{id}_{filename}`
* Informe Escolar (Múltiples): `escolar_{id}_{filename}`
* Orden Médica / Derivación (Único): `derivacion_{id}_{filename}`
* Informe de Entrevista (Único): `entrevista_{id}_{filename}`

### 3.3. El "Escudo de Edición" (Ruta POST /admision/<id>)
La vista de perfil tiene dos formularios diferentes apuntando a la misma ruta. El código Python DEBE verificar la existencia del campo clave:
* `if 'nombre' in request.form:` -> Significa que es una edición completa. Procesa todos los textos, fechas y archivos múltiples.
* `else:` -> Significa que es una subida rápida de entrevista. Omite los campos de texto para evitar vaciar el JSON, procesando ÚNICAMENTE el archivo de entrevista.

### 3.4. Regla de Transición: "Dar de Alta"
Al llamar a `/admision/alta/<id>`:
1. Se debe buscar al candidato en `admisiones.json`.
2. Se genera un nuevo ID secuencial para `pacientes.json`.
3. Se copian TODOS los datos exactos del candidato hacia el nuevo paciente (incluyendo las listas de archivos `informe_diagnostico`, `archivo_informes_previos`, etc.).
4. El paciente nuevo recibe el atributo `"activo": True`.
5. IMPORTANTE: La admisión original NO SE BORRA. Solo se actualiza su campo `"estado": "Procesada"`.

## 4. UI/UX (Frontend)
* Mantener estrictamente el diseño actual basado en Tailwind CSS.
* No modificar los IDs de los botones ni el código JavaScript a menos que se solicite en una iteración futura.
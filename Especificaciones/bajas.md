# Especificación del Módulo: Bajas (Junami 2.0)
# 1. Objetivo del Módulo
Centralizar la gestión de pacientes que deben ser removidos del sistema activo. El proceso debe ser controlado y permitir una visualización previa antes de la eliminación definitiva de los datos y archivos asociados.

# 2. Componentes de Interfaz (UI/UX)
2.1. Navegación (Sidebar)
Se debe agregar un ítem de menú en el Sidebar izquierdo debajo de la sección de "Pacientes".

Etiqueta: Bajas

Ícono: fas fa-user-minus o fas fa-trash-alt.

Estilo: Debe heredar las clases de Tailwind de los otros botones (hover, active y espaciado).

2.2. Plantilla Principal (bajas.html)
La vista debe presentar un listado o buscador para identificar al paciente que se desea dar de baja.

Debe contener una tabla con: ID, Nombre y Apellido, DNI, Área y un botón de acción Gestionar Baja.

# 3. Rutas y Endpoints (Paso 1)
El módulo se integrará inicialmente con las siguientes rutas básicas:

GET /bajas - Renderiza la vista principal del módulo con la lista de pacientes candidatos a baja.

GET /bajas/historial - (Opcional Futuro) Para ver pacientes que ya fueron dados de baja.

# 4. Reglas de Negocio Estrictas (Business Logic)
Acceso Restringido: Solo los usuarios con jerarquia == "Titular" podrán visualizar y operar esta solapa. El botón de "Bajas" no debe renderizarse para el rol Auxiliar.

Integridad de Datos: En esta primera etapa, la ruta solo debe mostrar la información. La lógica de borrado físico de archivos en uploads/ y la eliminación de nodos en los archivos JSON se definirá en la Fase 2 de esta especificación.

# 5. Preparación Técnica
El endpoint en app.py debe apuntar inicialmente a una plantilla limpia que mantenga el layout base de la aplicación (header y sidebar intactos).

# Implementación de Sistema Dual de Bajas (Pacientes y Profesionales)
Esta actualización transformará el módulo de Bajas en un centro unificado de desvinculaciones, permitiendo alternar sin recargas entre el listado de Pacientes y el nuevo listado de Profesionales, manteniendo intacta la estética y seguridad actual.

Cambios Propuestos
Módulo Backend
Se actualizará el controlador para suministrar ambos listados y orquestar el borrado dinámico de ambas bases de datos.

[MODIFY] rutas/bajas.py
Visualización:
Importar e inyectar también los datos de data/profesionales.json dentro del modelo que alimenta a la vista.
Eliminación Segura:
Actualizar la lógica para recibir un nuevo parámetro tipo desde el modal.
Generar un ruteador semántico internamente:
Si tipo == 'paciente', extraer id, filtrar pacientes.json y guardar.
Si tipo == 'profesional', extraer id, filtrar profesionales.json y guardar.
Mantener los mismos sistemas de control por Consola (print) incluyendo la trazabilidad del tipo de usuario eliminado.
Módulo Frontend (Interfaz de Usuario)
Se creará un ecosistema visual en forma de Tabs interactivos ocultando y revelando elementos al instante y centralizando el uso del Modal de Baja para ambas entidades.

[MODIFY] plantillas/bajas.html
Barra de Navegación (Tabs):
Implementar un grupo de botones Toggle bajo el título: "Listado de Pacientes" y "Bajas Profesionales". Aplicar colores dinámicos: el activo usará bg-slate-800 para mantener la elegancia solicitada, y bg-slate-100 o transparente para el inactivo.
Tablas Independientes:
Envolver la tabla actual en <div id="contenedorPacientes">.
Construir <div id="contenedorProfesionales" class="hidden"> con la misma estética pero presentando los campos: ID, Nombre, Especialidad y Matrícula.
Modernización del Modal / JS:
Agregar un input hidden llamado tipo a la estructura del modal enviando su valor en el formulario.
Actualizar los botones rojos de baja sumando data-tipo="paciente" y data-tipo="profesional" según corresponda al contexto.
Modificar el controlador JS de apertura de modal para inyectar este "tipo" en el form oculto y modificar la leyenda de advertencia dinámicamente ("Confirmar Baja de Paciente: [X]" vs "...de Profesional: [Y]").
User Review Required
WARNING

La lógica de borrado físico re-escribirá el archivo profesionales.json. Los profesionales dados de baja no irán a una tabla paralela de archivados, se eliminarán directamente del JSON original (al igual que ya se hace con los pacientes). ¿Está correcto este flujo directo?

Verification Plan
Manual Verification
Iniciar la app, acceder a Bajas siendo Titular.
Accionar los botones Toggle de la parte superior, validando la transición instantánea entre ambas tablas de listados.
Presionar 'Gestionar Baja' en un Paciente: observar si el modal indica 'Paciente' y verificar eliminación en pacientes.json.
Presionar 'Gestionar Baja' en un Profesional: observar si el modal indica 'Profesional' y verificar en consola de Python y en profesionales.json su desaparición efectiva.
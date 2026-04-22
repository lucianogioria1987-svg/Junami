# Especificación de Roles y Permisos: Auxiliares (Junami 2.0)

# 1. Objetivo de la Segmentación
Definir las restricciones y alcances operativos del rol Auxiliar frente al rol Titular (Profesional) dentro de la ficha del paciente. El objetivo es permitir la carga operativa diaria (evoluciones) pero restringir la gestión administrativa y la toma de decisiones estratégicas.

# 2. Identificación de Jerarquía
El sistema debe validar el tipo de usuario antes de renderizar la vista /paciente/<id> o procesar sus peticiones:

Titular: session['usuario_actual']['jerarquia'] == "Titular".

Auxiliar: session['usuario_actual']['jerarquia'] == "Auxiliar".

# 3. Reglas de Interfaz (Frontend)
En la plantilla ficha_paciente.html, se deben aplicar condicionales Jinja2 para modificar el DOM según el rol:

3.1. Elementos Inhabilitados para el Auxiliar (Ocultar/No renderizar)
Acciones de Cabecera: Botón Asignar Horario, Botón Imprimir Carátula y enlace de Editar Legajo.

Documentación y Reportes: Botón Imprimir Historial y botón Imprimir Planificación.

Gestión de Archivos: Formulario de subida de archivos/estudios médicos.

Gestión de Equipo: Botón de asignación de profesionales al staff del paciente.

3.2. El "Escudo de Estrategia" (Solo Lectura)
En la solapa de Planificación, si el usuario es Auxiliar:

Se debe envolver el contenido en un <fieldset disabled="disabled">.

Los campos Plan Anual, Objetivos Mensuales y Sugerencias deben ser visibles pero no editables.

El botón Guardar Cambios de esta sección no debe renderizarse.

# 4. Reglas de Negocio Estrictas (Excepción Operativa)
4.1. Habilitación de Registro Diario
A diferencia de la Planificación, la sección de Asistencia y Evoluciones debe ser interactiva para el Auxiliar:

El formulario de "Nueva Evolución" DEBE estar habilitado (sin atributo disabled).

El botón Guardar Registro DEBE estar visible y funcional.

El historial de evoluciones previas debe ser visible en modo lectura (comportamiento estándar).

4.2. Validación de Seguridad (Backend)
Las rutas POST relacionadas con la modificación de la Planificación o Datos del Legajo deben verificar la jerarquía en el servidor. Si un Auxiliar intenta forzar un envío a estas rutas, el sistema debe rebotar la petición con un flash de error y no modificar el JSON.

# 5. UI/UX
No utilizar filtros de escala de grises (grayscale) dentro de la ficha del paciente para no entorpecer la legibilidad de la historia clínica.

Mantener la estética de Tailwind CSS, asegurando que los campos deshabilitados mantengan un contraste suficiente para ser leídos cómodamente.
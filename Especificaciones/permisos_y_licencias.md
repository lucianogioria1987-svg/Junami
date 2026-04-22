# Especificación del Módulo: Permisos y Licencias (Junami 3.0)
# 1. Objetivo del Módulo
Implementar un sistema de Feature Flags (Banderas de Funcionalidad) que permita habilitar o deshabilitar módulos del sistema (Áreas Terapéuticas y Facturación) de forma dinámica. Este sistema permite que el software funcione como un modelo SaaS, donde cada clínica "activa" solo los servicios contratados.

# 2. Arquitectura de Control (La Fuente de Verdad)
Los permisos no están harcodeados en el HTML, sino que dependen de un archivo de configuración centralizado:

datos/config_clinica.json - Contiene el estado de activación de cada módulo.

Estructura del JSON de Control:
JSON
{
  "licencia_activa": {
    "psicologia": true,
    "terapia_ocupacional": true,
    "fonoaudiologia": false,
    "psicopedagogia": false,
    "facturacion": false
  }
}

# 3. Reglas de Negocio Estrictas (Business Logic)
3.1. Carga Dinámica de Configuración
El motor de Flask debe cargar el archivo config_clinica.json en cada petición relevante (o mediante un context_processor de Jinja2) para asegurar que los cambios en el JSON impacten inmediatamente sin reiniciar el servidor.

3.2. Bloqueo de Rutas (Backend Security)
Si un usuario intenta acceder manualmente a una URL de un módulo inhabilitado (ej: /facturacion), el servidor DEBE:

Verificar el flag en el JSON.

Si es false, abortar la petición y redirigir a una vista de "Módulo no Contratado" o lanzar un error 403 Forbidden.

3.3. Consistencia de Datos en "Profesionales"
Al deshabilitar un área (ej: Psicopedagogía), el sistema debe:

Mantener los datos existentes en los JSON de staff y pacientes (no se borra nada).

Impedir el acceso a la gestión de profesionales de esa área específica.

# 4. UI/UX y Comportamiento Visual (Frontend)
4.1. El "Efecto Candado" (Cards de Áreas)
Cuando un módulo en licencia_activa es false, se deben aplicar las siguientes reglas visuales a las Cards de la sección Profesionales:

Filtro CSS: grayscale(100%) (Escala de grises completa).

Opacidad: 0.6 para denotar estado inactivo/bloqueado.

Cursor: not-allowed.

Pointer Events: none para evitar que el usuario pueda hacer clic en el botón de "Ingresar".

Iconografía: Superponer un icono de candado (🔒) o un badge de "Bloqueado" en la esquina superior de la Card.

4.2. Menú Lateral y Navegación
La pestaña de Facturación en el sidebar debe mostrar un icono de candado al lado del texto y estar deshabilitada si su flag es false.

# 5. Casos de Prueba (Criterios de QA)
CP-01: Cambiar el flag de un área a false y verificar que la Card se torne gris automáticamente.

CP-02: Verificar que un clic sobre una Card bloqueada no dispare ninguna acción ni redirección.

CP-03: Intentar forzar la entrada a una ruta bloqueada por URL y confirmar que el Backend impide el renderizado.
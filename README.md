# 🚀 Junami 3.0 - Versión Base (Estabilización de Datos y Dashboards)

Esta rama representa el **Checkpoint de Estabilidad** del ecosistema Junami. Tras una fase intensiva de ingeniería de datos y control de calidad (QA), hemos consolidado una arquitectura de persistencia que garantiza la integridad de la información clínica y la precisión en las métricas de negocio.

En esta versión, el sistema no solo es funcional, sino que es **"Data-Resilient"**, capaz de manejar flujos de trabajo reales con una carga de datos simulada de alta fidelidad.

---

## 🏗️ Ingeniería de Datos y Persistencia

El corazón de esta versión radica en la reestructuración profunda de los archivos JSON para eliminar inconsistencias y fugas de información:

* **120 Pacientes Activos Certificados:** Generación de un set de datos de prueba con vinculación lógica total. Cada paciente posee un historial médico, estado administrativo y asignación terapéutica real.
* **Doble Clave de Compatibilidad de Estado:** Implementación de un sistema de estados híbrido (`"estado": "Activo"` para UI y `"activo": true` para lógica booleana), eliminando los errores de conteo en los dashboards.
* **Mapeo de Staff Dinámico:** Los pacientes cuentan con un diccionario `staff_fijo` que vincula IDs de profesionales de múltiples especialidades (Psicología, TO, Fono, Psicopedagogía), permitiendo una trazabilidad de 360°.

---

## ✨ Mejoras en Dashboards (Business Intelligence)

Se han refinado los motores de búsqueda y filtrado de Flask para ofrecer una experiencia personalizada según el rol del usuario:

* **Dashboard Personal (Vista Profesional):** Implementación de lógica de filtrado selectivo. El sistema identifica al profesional logueado y recorre la base de datos para mostrar únicamente "Mis Pacientes Activos", cruzando la sesión del usuario con el `staff_fijo` de cada legajo.
* **Sincronización de Métricas:** Los contadores de turnos, pacientes y profesionales ahora reflejan la realidad exacta de los archivos de datos, garantizando que el Dashboard General y el Personal mantengan coherencia total.

---

## 🧠 Arquitectura QA-Driven (Estadío Base)

Para alcanzar este nivel de estabilidad, aplicamos técnicas de "Blindaje de Datos":

* **Validación de Claves Críticas:** Inclusión de campos como `contacto_tutor` y `diagnostico` en el motor de generación para evitar celdas vacías o errores de renderizado en el Frontend.
* **Prevención de KeyErrors:** Refuerzo de las rutas en Flask para manejar diccionarios de asignación complejos, asegurando que el servidor nunca caiga ante datos incompletos.
* **Triple Blindaje de Estado:** Los pacientes están protegidos contra filtros de visibilidad erróneos, asegurando que la población activa sea siempre la correcta para las pruebas de estrés del sistema.

---

## ⚙️ Configuración del Entorno de Datos

Si necesitas regenerar la base de datos estabilizada en tu entorno local, sigue el flujo de ejecución de los scripts maestros:

1.  **`generar_1_profesionales.py`**: Crea el cuerpo médico base (24 profesionales distribuidos por especialidad).
2.  **`generar_2_pacientes.py`**: Genera los 120 pacientes con el "Triple Blindaje de Estado" y asignación de staff.
3.  **`generar_3_otros_modulos.py`**: Sincroniza las historias clínicas, pagos y recordatorios con los IDs generados previamente.

> **Nota:** Esta rama debe mantenerse como referencia de estabilidad para futuras implementaciones de módulos de facturación avanzada o historias clínicas dinámicas.

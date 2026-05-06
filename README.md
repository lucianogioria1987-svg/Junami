# 🏥 Junami 3.0 - Manual de Operaciones Integral
**Rama Principal de Estabilidad:** `RevisionBase`
**Arquitectura:** Flask (Python) + Tailwind CSS + Vanilla JS + JSON Storage

## 🚀 1. Descripción de la Versión
Esta rama representa el **Checkpoint de Estabilidad** del ecosistema Junami. Tras una fase intensiva de ingeniería de datos y control de calidad (QA), hemos consolidado una arquitectura capaz de manejar flujos de trabajo reales con una carga de datos de alta fidelidad.

---

## 🏗️ 2. Ingeniería de Datos y Persistencia
El sistema utiliza una reestructuración profunda de archivos JSON para eliminar inconsistencias:
* **120 Pacientes Activos Certificados**: Cada registro posee historial médico y vinculación lógica total.
* **Triple Blindaje de Estado**: Implementación de estados híbridos (`"estado": "Activo"` y `"activo": true`) para eliminar errores de conteo.
* **Mapeo de Staff Dinámico**: Los pacientes cuentan con un diccionario `staff_fijo` que vincula múltiples especialidades.
* **Silos JSON**: Separación física de datos operativos (`pacientes.json`) de los históricos (`bajas_pacientes.json`) para garantizar velocidad y escalabilidad.

---

## 🖥️ 3. Dashboards & Business Intelligence
Refinamiento de motores de búsqueda para ofrecer una experiencia personalizada por rol:
* **Dashboard Personal**: Filtra selectivamente "Mis Pacientes Activos" cruzando la sesión del profesional con el staff asignado.
* **Sincronización de Métricas**: Los contadores de turnos y profesionales reflejan la realidad exacta de los archivos de datos.

---

## 💬 4. Módulo de Mensajería Avanzada
Sistema de comunicación diseñado para no interrumpir el flujo médico:
* **Interfaz Draggable**: El modal de lectura permite arrastre dinámico mediante el encabezado para no tapar datos de fondo.
* **Menciones Inteligentes (@)**: Vinculación automática entre el mensaje y la ficha técnica del paciente mencionado.
* **Multitarea Real**: Capacidad de navegar por solapas del paciente sin cerrar el mensaje abierto.

---

## 📑 5. Gestión Clínica y UX
* **Legajos Electrónicos**: Fichas estructuradas en pestañas (Datos, Clínica, Planificación, Evoluciones) con navegación asíncrona.
* **Prevención de Conflictos**: Panel informativo que muestra la agenda externa del paciente antes de asignar turnos fijos.
* **Módulo Otras Terapias**: Soporte para registrar especialidades y profesionales externos al equipo de Junami.

---

## ⚙️ 6. Configuración del Entorno de Datos
Para regenerar la base de datos estabilizada, ejecutar en orden:
1. `generar_1_profesionales.py`: Crea el cuerpo médico base.
2. `generar_2_pacientes.py`: Genera los 120 pacientes con triple blindaje.
3. `generar_3_otros_modulos.py`: Sincroniza historias clínicas y registros.

---

## 🧪 7. Automatización y QA
El entorno está preparado para pruebas de integración de punta a punta:
* **Playwright**: Para automatizar flujos de alta de pacientes y envío de mensajes.
* **Desacoplamiento Estructural**: Separación de rutas en Blueprints de Flask para facilitar la detección de bugs.

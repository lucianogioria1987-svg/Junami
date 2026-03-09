🚀 Junami - Sistema de Gestión Terapéutica (SaaS)

🌿 Novedad de la Rama (mejoras-temporales): Refactorización Modular
El sistema evolucionó de un diseño monolítico a una arquitectura 100% modular basada en Blueprints de Flask. La lógica se separó en 10 submódulos (Pacientes, Admisiones, Agenda, etc.) centralizados en app.py, garantizando un mantenimiento ágil y evitando errores en cadena.

🛠️ Stack Tecnológico

Backend: Python 3.x, Flask (Arquitectura Modular)
Frontend: HTML5, JavaScript (Vanilla), Tailwind CSS (Mobile First)
Base de Datos: Persistencia de datos ultraligera basada en archivos JSON (NoSQL), optimizada para máxima portabilidad y despliegues rápidos sin dependencias de servidores SQL externos.
Control de Versiones: Git / GitHub

✨ Módulos Principales (Features Core)

📥 Embudo de Admisiones Digital: Sistema de buzón de entrada para nuevos pacientes. Permite la carga de datos demográficos, familiares, escolares y subida de archivos adjuntos (órdenes médicas, informes previos). Transición automatizada de "Candidato" a "Paciente Activo".
🗂️ Legajos Clínicos (Historias Electrónicas): Fichas de pacientes estructuradas en sistema de pestañas nativo (Datos, Clínica, Planificación, Evoluciones). Protegidas contra inconsistencias de datos.
📅 Agenda Inteligente: Gestión y visualización visual de turnos diarios. Panel de control con filtros rápidos por paciente o profesional.
🏢 Entorno "White-Label" (Marca Blanca B2B): Implementación avanzada de manejo de sesiones temporales que permite a potenciales clínicas clientes probar una demo del software personalizada en tiempo real con su propio nombre y logotipo.
📊 Dashboard Operativo: Métricas clave en tiempo real (KPIs de pacientes activos, turnos de hoy y profesionales registrados).

🧠 Arquitectura QA-Driven (Calidad desde el Diseño)

Este proyecto fue desarrollado combinando mejores prácticas de Ingeniería de Software con una fuerte mentalidad de Control de Calidad (QA):
Desacoplamiento Estructural: Separación de rutas y lógica en módulos independientes para facilitar la detección de bugs.
Blindaje de Diccionarios: Uso extensivo de métodos seguros de extracción de datos (.get()) en el backend y filtros en Jinja2 para evitar crashes de servidor por datos nulos o claves faltantes.
Manejo Seguro de Archivos: Guardado de datos estructurado garantizando la correcta codificación (ensure_ascii=False) para caracteres especiales y médicos.
UI/UX a prueba de fallos: Modales e interacciones de usuario construidas con Vanilla JS para minimizar dependencias de librerías de terceros, garantizando transiciones de estado estables.

⚙️ Instalación y Ejecución Local

Si deseas correr este proyecto en tu entorno local:
Clonar el repositorio:git clone https://github.com/TU-USUARIO/junami-teo.git cd junami-teo
git checkout mejoras-temporales

#Crear y activar un entorno virtual (Recomendado) python -m venv venv
En Windows:

venv\Scripts\activate
En Mac/Linux:

source venv/bin/activate
#Instalar dependencias pip install Flask
(Agrega otras dependencias si creaste un requirements.txt)

#Ejecutar la aplicación python app.py
#El sistema estará disponible en http://127.0.0.1:5000/

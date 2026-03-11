# 🚀 Junami - Rama: `nuevas-funcionalidades`

## 📝 Descripción General
Esta rama (originalmente nacida como `mejora-visual`) evolucionó para incorporar lógica de negocio crítica y mejoras sustanciales en la Experiencia de Usuario (UX). El enfoque principal es la prevención de conflictos de agenda y la ampliación del legajo clínico del paciente.

## ✨ Nuevas Funcionalidades Implementadas

### 1. Módulo "Otras Terapias" (Terapias Externas)
* **Backend:** Se actualizó la estructura de la base de datos (JSON) para soportar un array de diccionarios bajo la clave `"otras_terapias"`.
* **Edición de Legajo:** Se agregó una sección dinámica en el formulario de paciente que permite cargar múltiples terapias externas (Especialidad, Profesional y Horario).
* **Visualización:** La solapa "Clínica y Equipo" ahora diferencia claramente entre los **Profesionales Tratantes** (internos de Junami) y el **Equipo Terapéutico (Otras Áreas)**.

### 2. Prevención de Conflictos en Agenda (UX)
Se transformó el formulario de asignación de turnos en una herramienta de prevención de superposiciones:
* **Modal Ficha de Paciente:** Se insertó un panel informativo de solo lectura (Renderizado vía Jinja) que muestra la agenda externa del paciente antes de asignarle un horario fijo.
* **Vista General de Agenda:** Se implementó lógica con JavaScript nativo para que, al seleccionar un paciente del `<select>`, el panel lea dinámicamente sus terapias externas y muestre las alertas en tiempo real sin recargar la página.

### 3. Simulador de Datos (Mock Data)
* El script `simular_pacientes.py` fue reescrito para soportar la nueva estructura 2.0.
* Actualmente, el **100% de los pacientes simulados** (140 registros) reciben aleatoriamente entre 1 y 2 terapias externas con especialidades, días y horarios ficticios para poder estresar y probar las alertas de prevención en la agenda.

## 🛠️ Tecnologías Utilizadas
* **Backend:** Python, Flask, JSON (Base de datos temporal).
* **Frontend:** HTML, Tailwind CSS, Flowbite (Estilos de paneles de alerta).
* **Lógica Dinámica:** Jinja2 (Renderizado en servidor) y JavaScript Vanilla (DOM manipulation para la agenda).

---
*Nota de Arquitectura: Esta rama se mantiene separada de `mejoras-temporales` como medida de seguridad hasta finalizar las pruebas de QA de los paneles de prevención de turnos.*

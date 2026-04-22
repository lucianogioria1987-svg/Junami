import os

filepath = r"c:\Users\lucia\OneDrive\Escritorio\Junami 3.0\plantillas\bajas.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Insert Tabs before the white container
div_flex1 = '<div class="flex-1 overflow-y-auto p-8">'
tabs_html = """<div class="flex-1 overflow-y-auto p-8">
                <!-- TABS -->
                <div class="mb-4 flex gap-2">
                    <button id="tabPacientes" type="button" class="px-5 py-2 font-bold rounded-lg bg-slate-800 text-white transition shadow-sm border border-slate-800">Listado de Pacientes</button>
                    <button id="tabProfesionales" type="button" class="px-5 py-2 font-bold rounded-lg bg-transparent hover:bg-slate-200 text-slate-700 transition border border-transparent">Bajas Profesionales</button>
                </div>
"""
content = content.replace(div_flex1, tabs_html)

# 2. Add data-tipo="paciente" to existing btn-baja
btn_baja_old = 'data-id="{{ paciente.id }}" data-nombre="{{ paciente.nombre }}">'
btn_baja_new = 'data-id="{{ paciente.id }}" data-nombre="{{ paciente.nombre }}" data-tipo="paciente">'
content = content.replace(btn_baja_old, btn_baja_new)

# 3. Wrap table and add Profesionales table
table_div_start = '<div class="overflow-x-auto">'
new_table_divs = """<div id="contenedorPacientes" class="overflow-x-auto block">"""
content = content.replace(table_div_start, new_table_divs)

# Then find end of current table to inject new table
end_table = """                        </table>
                    </div>"""
profesionales_table = """                        </table>
                    </div>
                    
                    <!-- TABLA PROFESIONALES -->
                    <div id="contenedorProfesionales" class="overflow-x-auto hidden">
                        <table class="w-full text-left border-collapse" id="tablaProfesionales">
                            <thead>
                                <tr class="text-xs font-semibold tracking-wide text-white uppercase border-b bg-slate-800">
                                    <th class="px-6 py-4 rounded-tl-lg">ID</th>
                                    <th class="px-6 py-4">Nombre Completo</th>
                                    <th class="px-6 py-4">Especialidad</th>
                                    <th class="px-6 py-4">Matrícula</th>
                                    <th class="px-6 py-4 text-center rounded-tr-lg">Acción</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                {% for profesional in profesionales %}
                                <tr class="hover:bg-slate-50 transition border-b border-slate-100 items-center">
                                    <td class="px-6 py-4 text-sm font-medium text-slate-500">#{{ profesional.id }}</td>
                                    <td class="px-6 py-4">
                                        <div class="flex items-center gap-3">
                                            {% if profesional.foto %}
                                            <img src="{{ url_for('static', filename='uploads/' + profesional.foto) }}" class="w-10 h-10 rounded-full object-cover border border-gray-200 shadow-sm">
                                            {% else %}
                                            <div class="w-10 h-10 rounded-full bg-slate-200 text-slate-600 flex items-center justify-center font-bold text-lg shadow-sm">
                                                {{ profesional.nombre[0] }}
                                            </div>
                                            {% endif %}
                                            <div class="font-semibold text-gray-700">{{ profesional.nombre }}</div>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4">
                                        <span class="px-3 py-1 bg-blue-50 text-blue-700 text-xs font-bold rounded-full border border-blue-100 shadow-sm">{{ profesional.especialidad if profesional.especialidad else 'Sin especialidad' }}</span>
                                    </td>
                                    <td class="px-6 py-4 text-sm font-medium text-slate-600">{{ profesional.matricula if profesional.matricula else 'Sin Matrícula' }}</td>
                                    <td class="px-6 py-4 text-center">
                                        <button type="button" class="btn-baja bg-red-600 hover:bg-red-700 text-white text-sm font-bold py-2 px-5 rounded shadow-sm hover:shadow-md transition flex items-center justify-center gap-2 mx-auto" data-id="{{ profesional.id }}" data-nombre="{{ profesional.nombre }}" data-tipo="profesional">
                                            <i class="fas fa-trash-alt"></i> Gestionar Baja
                                        </button>
                                    </td>
                                </tr>
                                {% else %}
                                <tr>
                                    <td colspan="5" class="px-6 py-12 text-center text-slate-500">No hay profesionales registrados.</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>"""
content = content.replace(end_table, profesionales_table)

# 4. Modify modal to have inputTipo and adapt abrirModalBaja to read it
old_input = '<input type="hidden" name="paciente_id" id="inputPacienteId">'
new_input = """<input type="hidden" name="paciente_id" id="inputPacienteId">\n                <input type="hidden" name="tipo" id="inputTipo" value="paciente">"""
content = content.replace(old_input, new_input)

old_abrir = "function abrirModalBaja(id, nombre) {"
new_abrir = """function abrirModalBaja(id, nombre, tipo) {
            document.getElementById('inputTipo').value = tipo;
            let label = tipo === 'profesional' ? 'Profesional' : 'Paciente';"""
content = content.replace(old_abrir, new_abrir)

old_title_set = "document.getElementById('modalTitle').innerText = 'Confirmar Baja Definitiva de ' + nombre;"
new_title_set = "document.getElementById('modalTitle').innerText = 'Confirmar Baja Definitiva de ' + label + ': ' + nombre;"
content = content.replace(old_title_set, new_title_set)

old_btn_listener = """let btnNombre = this.getAttribute('data-nombre');
                    abrirModalBaja(btnId, btnNombre);"""
new_btn_listener = """let btnNombre = this.getAttribute('data-nombre');
                    let btnTipo = this.getAttribute('data-tipo');
                    abrirModalBaja(btnId, btnNombre, btnTipo);"""
content = content.replace(old_btn_listener, new_btn_listener)

# 5. Add logic for tabs at end of script
tabs_script = """
        // Logging Tabs UI
        const tabPacientes = document.getElementById('tabPacientes');
        const tabProfesionales = document.getElementById('tabProfesionales');
        const contenedorPacientes = document.getElementById('contenedorPacientes');
        const contenedorProfesionales = document.getElementById('contenedorProfesionales');

        tabPacientes.addEventListener('click', () => {
            tabPacientes.className = "px-5 py-2 font-bold rounded-lg bg-slate-800 text-white transition shadow-sm border border-slate-800";
            tabProfesionales.className = "px-5 py-2 font-bold rounded-lg bg-transparent hover:bg-slate-200 text-slate-700 transition border border-transparent";
            contenedorPacientes.classList.remove('hidden');
            contenedorPacientes.classList.add('block');
            contenedorProfesionales.classList.add('hidden');
            contenedorProfesionales.classList.remove('block');
        });

        tabProfesionales.addEventListener('click', () => {
            tabProfesionales.className = "px-5 py-2 font-bold rounded-lg bg-slate-800 text-white transition shadow-sm border border-slate-800";
            tabPacientes.className = "px-5 py-2 font-bold rounded-lg bg-transparent hover:bg-slate-200 text-slate-700 transition border border-transparent";
            contenedorProfesionales.classList.remove('hidden');
            contenedorProfesionales.classList.add('block');
            contenedorPacientes.classList.add('hidden');
            contenedorPacientes.classList.remove('block');
        });
"""
content = content.replace("</script>", tabs_script + "\n    </script>")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Plantilla Bajas HTML actualizada con éxito.")

import re

file_path = r'c:\Users\lucia\OneDrive\Escritorio\Junami 3.0\plantillas\mensajeria.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Archivar button to Enviados
enviados_ver_btn_pattern = r'<button onclick="abrirModalLectura\(\{\{ msg\.id \}\}, \'\{\{ msg\.receptor_nombre\|escape \}\}\', \'\{\{ msg\.fecha \}\}\', \'\{\{ msg\.asunto\|escape \}\}\', \'\{\{ msg\.mensaje\|escape \}\}\', true, \'Enviado\'\)" class="inline-flex items-center px-3 py-1\.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-emerald-500 hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors">\s*<i class="fas fa-eye mr-2"></i> Ver\s*</button>'

enviados_botones_repl = """<div class="flex justify-center gap-2">
                                            <button onclick="abrirModalLectura({{ msg.id }}, '{{ msg.receptor_nombre|escape }}', '{{ msg.fecha }}', '{{ msg.asunto|escape }}', '{{ msg.mensaje|escape }}', true, 'Enviado')" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-emerald-500 hover:bg-emerald-600 transition-colors">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                            <button onclick="archivarMensaje({{ msg.id }})" class="inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors" title="Archivar">
                                                <i class="fas fa-archive"></i>
                                            </button>
                                        </div>"""
content = re.sub(enviados_ver_btn_pattern, enviados_botones_repl, content)

# 2. Add Archivar button to Historial
historial_botones_pattern = r'<div class="flex justify-center gap-2">\s*<button onclick="abrirModalLectura\(\{\{ msg\.id \}\}, \'\{\{ msg\.emisor_nombre\|escape \}\}\', \'\{\{ msg\.fecha \}\}\', \'\{\{ msg\.asunto\|escape \}\}\', \'\{\{ msg\.mensaje\|escape \}\}\', true, \'Recibido\'\)" class="inline-flex items-center px-3 py-1\.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors">\s*<i class="fas fa-eye"></i>\s*</button>\s*<button onclick="borrarMensaje\(\{\{ msg\.id \}\}\)" class="inline-flex items-center px-3 py-1\.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-red-400 hover:bg-red-500 transition-colors">\s*<i class="fas fa-trash-alt mr-2"></i> Borrar\s*</button>\s*</div>'

historial_botones_repl = """<div class="flex justify-center gap-2">
                                            <button onclick="abrirModalLectura({{ msg.id }}, '{{ msg.emisor_nombre|escape }}', '{{ msg.fecha }}', '{{ msg.asunto|escape }}', '{{ msg.mensaje|escape }}', true, 'Recibido')" class="inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                            <button onclick="archivarMensaje({{ msg.id }})" class="inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors" title="Archivar">
                                                <i class="fas fa-archive"></i>
                                            </button>
                                            <button onclick="borrarMensaje({{ msg.id }})" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-red-400 hover:bg-red-500 transition-colors" title="Borrar">
                                                <i class="fas fa-trash-alt"></i>
                                            </button>
                                        </div>"""
content = re.sub(historial_botones_pattern, historial_botones_repl, content)

# 3. Add the Archivados HTML block
archivados_html = """
                <!-- ARCHIVADOS -->
                <details class="group bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden mt-8 mb-8">
                    <summary class="px-6 py-4 bg-gray-50 text-gray-600 font-bold cursor-pointer hover:bg-gray-100 transition-colors flex items-center justify-between list-none">
                        <span class="flex items-center"><i class="fas fa-archive mr-2"></i> Mensajes Archivados</span>
                        <i class="fas fa-chevron-down transform group-open:rotate-180 transition-transform"></i>
                    </summary>
                    <div class="overflow-x-auto border-t border-gray-200">
                        <table class="w-full text-left border-collapse">
                            <thead class="bg-gray-50 text-xs text-gray-500 uppercase border-b border-gray-200">
                                <tr>
                                    <th class="px-6 py-4 font-bold text-gray-600">Origen</th>
                                    <th class="px-6 py-4 font-bold text-gray-600">Fecha</th>
                                    <th class="px-6 py-4 font-bold text-gray-600">Contacto</th>
                                    <th class="px-6 py-4 font-bold text-gray-600">Asunto</th>
                                    <th class="px-6 py-4 font-bold text-gray-600 text-center">Acciones</th>
                                </tr>
                            </thead>
                            <tbody id="tbody-archivados" class="divide-y divide-gray-100">
                                {% for msg in archivados %}
                                {% set otro_nombre = msg.emisor_nombre if msg.origen == 'Entrante' else msg.receptor_nombre %}
                                {% set otra_foto = msg.emisor_foto if msg.origen == 'Entrante' else msg.receptor_foto %}
                                {% set otras_iniciales = msg.emisor_iniciales if msg.origen == 'Entrante' else msg.receptor_iniciales %}
                                
                                <tr class="hover:bg-gray-50 text-gray-400 transition-colors bg-white font-medium opacity-80" id="fila-msg-{{ msg.id }}" data-origen="{{ msg.origen }}">
                                    <td class="px-6 py-4">
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-gray-200 text-gray-600 shadow-sm" id="badge-origen-{{ msg.id }}">
                                            {{ msg.origen }}
                                        </span>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm">{{ msg.fecha }}</td>
                                    <td class="px-6 py-4">
                                        <div class="flex items-center gap-3">
                                            {% if otra_foto %}
                                            <img src="{{ url_for('static', filename='uploads/' + otra_foto) }}" class="w-8 h-8 rounded-full object-cover border border-gray-200 grayscale">
                                            {% else %}
                                            <div class="w-8 h-8 rounded-full bg-gray-200 text-gray-500 flex items-center justify-center font-bold text-xs">{{ otras_iniciales }}</div>
                                            {% endif %}
                                            <span class="text-sm">{{ otro_nombre }}</span>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 text-sm">{{ msg.asunto }} {% if msg.tiene_adjunto %} <i class="fas fa-paperclip text-emerald-500 ml-2" title="Contiene archivo adjunto"></i>{% endif %}</td>
                                    <td class="px-6 py-4 text-center">
                                        <div class="flex justify-center gap-2">
                                            <button onclick="abrirModalLectura({{ msg.id }}, '{{ otro_nombre|escape }}', '{{ msg.fecha }}', '{{ msg.asunto|escape }}', '{{ msg.mensaje|escape }}', true, '{% if msg.origen == "Entrante" %}Recibido{% else %}Enviado{% endif %}')" class="inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-500 bg-white hover:bg-gray-50 transition-colors" title="Ver">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                            <button onclick="desarchivarMensaje({{ msg.id }})" class="inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-emerald-600 bg-white hover:bg-emerald-50 transition-colors" title="Desarchivar">
                                                <i class="fas fa-box-open"></i>
                                            </button>
                                            <button onclick="borrarMensaje({{ msg.id }})" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-red-400 hover:bg-red-500 transition-colors" title="Borrar">
                                                <i class="fas fa-trash-alt"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                {% else %}
                                <tr id="tr-archivados-vacio">
                                    <td colspan="5" class="px-6 py-10 text-center text-gray-400">
                                        <div class="flex flex-col items-center justify-center">
                                            <div class="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mb-3 text-gray-300">
                                                <i class="fas fa-archive text-xl"></i>
                                            </div>
                                            <p class="text-md font-medium text-gray-500">No hay mensajes archivados</p>
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </details>
"""
# Insert Archivados table right after Historial table
# Look for: </main>
main_end_pattern = r'            </main>'
content = content.replace(main_end_pattern, archivados_html + '\n            </main>')

# 4. Add JavaScript for Archivar, Desarchivar, and update moverFila
js_functions = """
        function archivarMensaje(id) {
            fetch(`/mensajeria/archivar/${id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            }).then(res => res.json()).then(data => {
                if(data.success) {
                    moverFila(id, 'Archivados');
                } else {
                    alert("Error al archivar.");
                }
            });
        }

        function desarchivarMensaje(id) {
            fetch(`/mensajeria/desarchivar/${id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            }).then(res => res.json()).then(data => {
                if(data.success) {
                    let fila = document.getElementById(`fila-msg-${id}`) || document.getElementById(`fila-enviado-${id}`);
                    if(!fila) return;
                    let origen = fila.getAttribute('data-origen') || 'Saliente';
                    
                    if(origen === 'Entrante') {
                        moverFila(id, 'Historial');
                    } else {
                        moverFila(id, 'Enviados');
                    }
                } else {
                    alert("Error al desarchivar.");
                }
            });
        }
"""

content = content.replace('function borrarMensaje(id) {', js_functions + '\n        function borrarMensaje(id) {')

# Modify moverFila to handle "Archivados" and restoring
old_mover_fila = """function moverFila(id, destino) {
            let fila = document.getElementById(`fila-msg-${id}`);
            if(!fila) fila = document.getElementById(`fila-enviado-${id}`);"""

new_mover_fila = """function moverFila(id, destino) {
            let fila = document.getElementById(`fila-msg-${id}`);
            if(!fila) fila = document.getElementById(`fila-enviado-${id}`);
            if(!fila) return;
            
            // Remove empty rows message if any
            let emptyRows = ['tr-archivados-vacio'];
            emptyRows.forEach(eid => { let el = document.getElementById(eid); if(el) el.style.display = 'none'; });

            let htmlFila = '';
            // Determine Origen currently for storing when archiving
            let currentOrigen = fila.getAttribute('data-origen');
            if(!currentOrigen) {
                // Determine by tbody
                if(fila.parentElement.id === 'tbody-enviados') currentOrigen = 'Saliente';
                else currentOrigen = 'Entrante';
                fila.setAttribute('data-origen', currentOrigen);
            }
"""
content = content.replace(old_mover_fila, new_mover_fila)

# Now add logic for handling 'Archivados' inside moverFila
# Look for: } else if (destino === 'Enviados') { ... }
mover_fila_body = r"\} else if \(destino === 'Enviados'\) \{(.*?)\}\n        \}"
mover_fila_match = re.search(mover_fila_body, content, re.DOTALL)
if mover_fila_match:
    archivados_logic = """} else if (destino === 'Archivados') {
                let badge = fila.querySelector('td:first-child span');
                if(badge) {
                    badge.className = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-gray-200 text-gray-600 shadow-sm";
                    badge.innerText = currentOrigen;
                }
                fila.className = "hover:bg-gray-50 text-gray-400 transition-colors bg-white font-medium opacity-80";
                
                // Hacer las imagenes blanco y negro
                let img = fila.querySelector('img');
                if(img) img.classList.add('grayscale');
                
                document.getElementById('tbody-archivados').prepend(fila);
                
                let tdAcciones = fila.querySelector('td:last-child');
                let btnVer = tdAcciones.querySelector('button[title="Ver"]') || tdAcciones.querySelector('button');
                let onclickStr = btnVer ? btnVer.getAttribute('onclick') : '';
                
                tdAcciones.innerHTML = `
                    <div class="flex justify-center gap-2">
                        <button onclick="${onclickStr}" class="inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-500 bg-white hover:bg-gray-50 transition-colors" title="Ver">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button onclick="desarchivarMensaje(${id})" class="inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-emerald-600 bg-white hover:bg-emerald-50 transition-colors" title="Desarchivar">
                            <i class="fas fa-box-open"></i>
                        </button>
                        <button onclick="borrarMensaje(${id})" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-red-400 hover:bg-red-500 transition-colors" title="Borrar">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                `;
            }"""
    # Also we need to fix Historial and Enviados moving to reinstate colored badges
    content = content.replace("} else if (destino === 'Enviados') {", "} else if (destino === 'Enviados') {")
    # Replace the closing brace of Enviados block with the Archivados block + the closing brace
    content = content.replace("            }\n        }\n\n        function validarTamanioAdjunto", "            }\n            " + archivados_logic + "\n        }\n\n        function validarTamanioAdjunto")

# Fix Historial block to include "Archivar" button and remove grayscale if restoring
historial_block = r"// De Nuevos a Historial.*?</tr>`;" # Actually it doesn't have </tr>
# We just need to make sure that in `destino === 'Historial'` and `destino === 'Enviados'` we remove `grayscale` from the image
grayscale_fix = """// Remover grayscale por si viene de Archivados
                let img = fila.querySelector('img');
                if(img) img.classList.remove('grayscale');
                fila.classList.remove('opacity-80', 'text-gray-400');"""

content = content.replace("// Mover a tbody-historial", grayscale_fix + "\n                // Mover a tbody-historial")
content = content.replace("document.getElementById('tbody-enviados').prepend(fila);", grayscale_fix + "\n                document.getElementById('tbody-enviados').prepend(fila);")

# Add Archivar to Historial's rebuilt buttons in moverFila
old_historial_btns = """<div class="flex justify-center gap-2">
                        <button onclick="${onclickStr}" class="inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button onclick="borrarMensaje(${id})" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-red-400 hover:bg-red-500 transition-colors">
                            <i class="fas fa-trash-alt mr-2"></i> Borrar
                        </button>
                    </div>"""
new_historial_btns = """<div class="flex justify-center gap-2">
                        <button onclick="${onclickStr}" class="inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button onclick="archivarMensaje(${id})" class="inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors" title="Archivar">
                            <i class="fas fa-archive"></i>
                        </button>
                        <button onclick="borrarMensaje(${id})" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-red-400 hover:bg-red-500 transition-colors" title="Borrar">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>"""
content = content.replace(old_historial_btns, new_historial_btns)

# Add Archivar to Enviados's rebuilt buttons in moverFila
old_enviados_btns = """<button onclick="${onclickStr}" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-emerald-500 hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors">
                        <i class="fas fa-eye mr-2"></i> Ver
                    </button>"""
new_enviados_btns = """<div class="flex justify-center gap-2">
                        <button onclick="${onclickStr}" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-emerald-500 hover:bg-emerald-600 transition-colors">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button onclick="archivarMensaje(${id})" class="inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors" title="Archivar">
                            <i class="fas fa-archive"></i>
                        </button>
                    </div>"""
content = content.replace(old_enviados_btns, new_enviados_btns)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("UI actualizada para el Archivador")

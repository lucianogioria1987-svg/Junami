import re

file_path = r'c:\Users\lucia\OneDrive\Escritorio\Junami 3.0\plantillas\mensajeria.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Reemplazar Header rojo por emerald
content = content.replace('border-b border-red-50', 'border-b border-emerald-50')
content = content.replace('bg-red-50 text-red-500', 'bg-emerald-50 text-emerald-500')

# 2. Reemplazar flash messages verde a emerald por si acaso, aunque ya era green
content = content.replace('bg-green-50', 'bg-emerald-50')
content = content.replace('text-green-700', 'text-emerald-700')
content = content.replace('border-green-500', 'border-emerald-500')
content = content.replace('text-green-500', 'text-emerald-500')
content = content.replace('hover:text-green-700', 'hover:text-emerald-700')

# 3. Reemplazar la tabla actual
tabla_vieja_pattern = r'<div class="bg-white rounded-2xl shadow-sm border border-red-50 overflow-hidden">.*?</div>\s*</div>\s*</main>'

tabla_nueva = """
                {% set mensajes_nuevos = mensajes | selectattr('leido', 'equalto', False) | list %}
                {% set mensajes_historial = mensajes | selectattr('leido', 'equalto', True) | list %}

                <h2 class="text-lg font-bold text-gray-800 mb-4">Mensajes Nuevos</h2>
                <div class="bg-white rounded-2xl shadow-sm border border-emerald-50 overflow-hidden mb-8">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse">
                            <thead class="bg-gradient-to-r from-emerald-50 to-white text-xs text-gray-500 uppercase border-b border-emerald-100">
                                <tr>
                                    <th class="px-6 py-4 font-bold text-emerald-800">Estado</th>
                                    <th class="px-6 py-4 font-bold text-emerald-800">Fecha</th>
                                    <th class="px-6 py-4 font-bold text-emerald-800">Emisor</th>
                                    <th class="px-6 py-4 font-bold text-emerald-800">Asunto</th>
                                    <th class="px-6 py-4 font-bold text-emerald-800 text-center">Acciones</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-50">
                                {% for msg in mensajes_nuevos %}
                                <tr class="hover:bg-emerald-50/30 transition-colors bg-emerald-50/50 font-semibold" id="fila-msg-{{ msg.id }}">
                                    <td class="px-6 py-4">
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 shadow-sm" id="badge-{{ msg.id }}">
                                            Nuevo
                                        </span>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm">{{ msg.fecha }}</td>
                                    <td class="px-6 py-4">
                                        <div class="flex items-center gap-3">
                                            {% if msg.emisor_foto %}
                                            <img src="{{ url_for('static', filename='uploads/' + msg.emisor_foto) }}" class="w-8 h-8 rounded-full object-cover border border-emerald-100">
                                            {% else %}
                                            <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center font-bold text-xs">{{ msg.emisor_iniciales }}</div>
                                            {% endif %}
                                            <span class="text-sm text-gray-700">{{ msg.emisor_nombre }}</span>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 text-sm text-gray-800">{{ msg.asunto }}</td>
                                    <td class="px-6 py-4 text-center">
                                        <button onclick="abrirModalLectura({{ msg.id }}, '{{ msg.emisor_nombre|escape }}', '{{ msg.fecha }}', '{{ msg.asunto|escape }}', '{{ msg.mensaje|escape }}', false)" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-emerald-500 hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors">
                                            <i class="fas fa-envelope-open-text mr-2"></i> Leer
                                        </button>
                                    </td>
                                </tr>
                                {% else %}
                                <tr>
                                    <td colspan="5" class="px-6 py-10 text-center text-gray-400">
                                        <div class="flex flex-col items-center justify-center">
                                            <div class="w-12 h-12 bg-emerald-50 rounded-full flex items-center justify-center mb-3 text-emerald-300">
                                                <i class="fas fa-inbox text-xl"></i>
                                            </div>
                                            <p class="text-md font-medium text-gray-500">No hay mensajes nuevos</p>
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>

                <h2 class="text-lg font-bold text-gray-800 mb-4">Historial de Mensajes</h2>
                <div class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse">
                            <thead class="bg-gray-50 text-xs text-gray-500 uppercase border-b border-gray-200">
                                <tr>
                                    <th class="px-6 py-4 font-bold text-gray-600">Estado</th>
                                    <th class="px-6 py-4 font-bold text-gray-600">Fecha</th>
                                    <th class="px-6 py-4 font-bold text-gray-600">Emisor</th>
                                    <th class="px-6 py-4 font-bold text-gray-600">Asunto</th>
                                    <th class="px-6 py-4 font-bold text-gray-600 text-center">Acciones</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                {% for msg in mensajes_historial %}
                                <tr class="hover:bg-gray-50 transition-colors text-gray-500" id="fila-msg-{{ msg.id }}">
                                    <td class="px-6 py-4">
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500">
                                            Leído
                                        </span>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm">{{ msg.fecha }}</td>
                                    <td class="px-6 py-4">
                                        <div class="flex items-center gap-3">
                                            {% if msg.emisor_foto %}
                                            <img src="{{ url_for('static', filename='uploads/' + msg.emisor_foto) }}" class="w-8 h-8 rounded-full object-cover border border-gray-200 grayscale opacity-80">
                                            {% else %}
                                            <div class="w-8 h-8 rounded-full bg-gray-100 text-gray-500 flex items-center justify-center font-bold text-xs">{{ msg.emisor_iniciales }}</div>
                                            {% endif %}
                                            <span class="text-sm text-gray-600">{{ msg.emisor_nombre }}</span>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 text-sm text-gray-600">{{ msg.asunto }}</td>
                                    <td class="px-6 py-4 text-center">
                                        <div class="flex justify-center gap-2">
                                            <button onclick="abrirModalLectura({{ msg.id }}, '{{ msg.emisor_nombre|escape }}', '{{ msg.fecha }}', '{{ msg.asunto|escape }}', '{{ msg.mensaje|escape }}', true)" class="inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                            <button onclick="borrarMensaje({{ msg.id }})" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-red-400 hover:bg-red-500 transition-colors">
                                                <i class="fas fa-trash-alt mr-2"></i> Borrar
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                {% else %}
                                <tr>
                                    <td colspan="5" class="px-6 py-10 text-center text-gray-400">
                                        <p class="text-sm font-medium">No hay mensajes en el historial.</p>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>
"""

content = re.sub(tabla_vieja_pattern, tabla_nueva, content, flags=re.DOTALL)

# 4. Cambiar colores del MODAL LECTURA (red a emerald)
# Partimos por MODAL LECTURA y cambiamos todo hasta el fin del div
partes = content.split('<!-- MODAL LECTURA -->')
if len(partes) > 1:
    modal_lectura = partes[1].split('<!-- El Modal de Enviar Mensaje')[0]
    # Reemplazamos en modal_lectura
    modal_lectura = modal_lectura.replace('border-red-50', 'border-emerald-50')
    modal_lectura = modal_lectura.replace('from-red-50', 'from-emerald-50')
    modal_lectura = modal_lectura.replace('text-red-800', 'text-emerald-800')
    modal_lectura = modal_lectura.replace('text-red-500', 'text-emerald-500')
    modal_lectura = modal_lectura.replace('hover:text-red-500', 'hover:text-emerald-500')
    modal_lectura = modal_lectura.replace('bg-red-50/30', 'bg-emerald-50/30')
    modal_lectura = modal_lectura.replace('border-red-50', 'border-emerald-50')
    modal_lectura = modal_lectura.replace('hover:text-red-600', 'hover:text-emerald-600')
    
    # Reconstruimos
    content = partes[0] + '<!-- MODAL LECTURA -->' + modal_lectura + '<!-- El Modal de Enviar Mensaje' + partes[1].split('<!-- El Modal de Enviar Mensaje', 1)[1]

# 5. Agregar la función borrarMensaje
js_borrar = """
        function borrarMensaje(id) {
            if(confirm("¿Estás seguro de eliminar este mensaje? Esta acción no se puede deshacer.")) {
                fetch(`/mensajeria/borrar/${id}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                }).then(res => res.json()).then(data => {
                    if(data.success) {
                        let fila = document.getElementById(`fila-msg-${id}`);
                        if(fila) {
                            fila.style.display = 'none';
                        }
                    } else {
                        alert("Error: " + (data.error || "No se pudo eliminar"));
                    }
                });
            }
        }
"""
if 'function borrarMensaje' not in content:
    content = content.replace('function cerrarModalLectura() {', js_borrar + '\n        function cerrarModalLectura() {')

# Asegurar que en modalLectura (al clickear) para historial también marque si hiciera falta, pero leido_previo=true no hace fetch. Y eso es lo correcto!
# Sin embargo, los mensajes del historial al marcarlos leidos en la vista de nuevos se pasarían a historial sin refrescar.
# Ya que está con JS nativo, al marcar leído el JS actual dice `fila.classList.remove... fila.classList.add...`.
# Lo ideal es que al refrescar la página ya aparezcan en Historial. Como funciona como bandeja, eso es correcto!

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("¡Plantilla mensajeria.html actualizada!")

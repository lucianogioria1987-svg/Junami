import re

file_path = r'c:\Users\lucia\OneDrive\Escritorio\Junami 3.0\plantillas\mensajeria.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the Historial section to inject the Mensajes Enviados section right before it
historial_pattern = r'<h2 class="text-lg font-bold text-gray-800 mb-4">Historial de Mensajes</h2>'

mensajes_enviados_html = """
                <h2 class="text-lg font-bold text-gray-800 mb-4">Mensajes Enviados</h2>
                <div class="bg-white rounded-2xl shadow-sm border border-emerald-50 overflow-hidden mb-8">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse">
                            <thead class="bg-gradient-to-r from-emerald-50 to-white text-xs text-gray-500 uppercase border-b border-emerald-100">
                                <tr>
                                    <th class="px-6 py-4 font-bold text-emerald-800">Estado</th>
                                    <th class="px-6 py-4 font-bold text-emerald-800">Fecha</th>
                                    <th class="px-6 py-4 font-bold text-emerald-800">Receptor</th>
                                    <th class="px-6 py-4 font-bold text-emerald-800">Asunto</th>
                                    <th class="px-6 py-4 font-bold text-emerald-800 text-center">Acciones</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-50">
                                {% for msg in mensajes_enviados %}
                                <tr class="hover:bg-emerald-50/30 transition-colors bg-white font-medium" id="fila-enviado-{{ msg.id }}">
                                    <td class="px-6 py-4">
                                        {% if not msg.leido %}
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-700 shadow-sm">
                                            Pendiente
                                        </span>
                                        {% else %}
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">
                                            Leído
                                        </span>
                                        {% endif %}
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm">{{ msg.fecha }}</td>
                                    <td class="px-6 py-4">
                                        <div class="flex items-center gap-3">
                                            {% if msg.receptor_foto %}
                                            <img src="{{ url_for('static', filename='uploads/' + msg.receptor_foto) }}" class="w-8 h-8 rounded-full object-cover border border-emerald-100">
                                            {% else %}
                                            <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center font-bold text-xs">{{ msg.receptor_iniciales }}</div>
                                            {% endif %}
                                            <span class="text-sm text-gray-700">{{ msg.receptor_nombre }}</span>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 text-sm text-gray-800">{{ msg.asunto }}</td>
                                    <td class="px-6 py-4 text-center">
                                        <button onclick="abrirModalLectura({{ msg.id }}, '{{ msg.receptor_nombre|escape }}', '{{ msg.fecha }}', '{{ msg.asunto|escape }}', '{{ msg.mensaje|escape }}', true, 'Enviado')" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-emerald-500 hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors">
                                            <i class="fas fa-eye mr-2"></i> Ver
                                        </button>
                                    </td>
                                </tr>
                                {% else %}
                                <tr>
                                    <td colspan="5" class="px-6 py-10 text-center text-gray-400">
                                        <div class="flex flex-col items-center justify-center">
                                            <div class="w-12 h-12 bg-emerald-50 rounded-full flex items-center justify-center mb-3 text-emerald-300">
                                                <i class="fas fa-paper-plane text-xl"></i>
                                            </div>
                                            <p class="text-md font-medium text-gray-500">No has enviado mensajes</p>
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>

                <h2 class="text-lg font-bold text-gray-800 mb-4">Historial de Mensajes</h2>"""

if 'Mensajes Enviados' not in content:
    content = content.replace(historial_pattern, mensajes_enviados_html)

# Now update the JS parameters in Mensajes Nuevos and Historial
content = content.replace(
    "abrirModalLectura({{ msg.id }}, '{{ msg.emisor_nombre|escape }}', '{{ msg.fecha }}', '{{ msg.asunto|escape }}', '{{ msg.mensaje|escape }}', false)",
    "abrirModalLectura({{ msg.id }}, '{{ msg.emisor_nombre|escape }}', '{{ msg.fecha }}', '{{ msg.asunto|escape }}', '{{ msg.mensaje|escape }}', false, 'Recibido')"
)

content = content.replace(
    "abrirModalLectura({{ msg.id }}, '{{ msg.emisor_nombre|escape }}', '{{ msg.fecha }}', '{{ msg.asunto|escape }}', '{{ msg.mensaje|escape }}', true)",
    "abrirModalLectura({{ msg.id }}, '{{ msg.emisor_nombre|escape }}', '{{ msg.fecha }}', '{{ msg.asunto|escape }}', '{{ msg.mensaje|escape }}', true, 'Recibido')"
)

# Now update the JS function definition
js_function_old = "function abrirModalLectura(id, emisor, fecha, asunto, mensaje, leido_previo) {"
js_function_new = """function abrirModalLectura(id, emisor, fecha, asunto, mensaje, leido_previo, tipo) {
            if (tipo === 'Enviado') {
                document.getElementById('lecturaEmisor').innerText = "Para: " + emisor;
            } else {
                document.getElementById('lecturaEmisor').innerText = "De: " + emisor;
            }"""

content = content.replace(
    "function abrirModalLectura(id, emisor, fecha, asunto, mensaje, leido_previo) {\n            document.getElementById('lecturaEmisor').innerText = emisor;",
    js_function_new
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("¡Plantilla mensajeria.html actualizada con Enviados!")

import re

file_path = r'c:\Users\lucia\OneDrive\Escritorio\Junami 3.0\plantillas\mensajeria.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update modalLectura HTML to include the reply form and a scrollable message area
new_modal_html = """    <!-- MODAL LECTURA -->
    <div id="modalLectura" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4 transition-opacity duration-300 opacity-0">
        <div class="bg-white rounded-2xl w-full max-w-2xl shadow-2xl transform transition-transform duration-300 scale-95 flex flex-col max-h-[90vh]" id="modalLecturaContent">
            <div class="px-6 py-4 border-b border-emerald-50 flex justify-between items-center bg-gradient-to-r from-emerald-50 to-white rounded-t-2xl shrink-0">
                <h3 class="font-bold text-emerald-800 flex items-center"><svg class="w-5 h-5 mr-2 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg> <span id="lecturaEmisor">Recado</span></h3>
                <button onclick="cerrarModalLectura()" class="text-gray-400 hover:text-emerald-500 transition-colors bg-white rounded-full p-1"><i class="fas fa-times"></i></button>
            </div>
            <div class="px-8 py-4 border-b border-gray-100 shrink-0">
                <h2 class="text-xl font-bold text-gray-800" id="lecturaAsunto">Asunto</h2>
            </div>
            
            <div class="p-8 overflow-y-auto flex-1 bg-slate-50" id="lecturaMensaje">
                <!-- Hilo de mensajes renderizado por JS -->
            </div>
            
            <div class="px-6 py-4 bg-white border-t border-gray-100 rounded-b-2xl shrink-0">
                <form id="formResponder" action="" method="POST" class="flex flex-col gap-3">
                    <textarea name="respuesta" required rows="2" class="w-full border-gray-200 rounded-xl shadow-sm focus:border-emerald-500 focus:ring-emerald-500 text-sm p-3" placeholder="Escribir una respuesta..."></textarea>
                    <div class="flex justify-end gap-2">
                        <button type="button" onclick="cerrarModalLectura()" class="px-5 py-2 border border-gray-200 text-gray-600 rounded-lg font-bold text-sm hover:bg-gray-50 transition-colors shadow-sm">Cerrar</button>
                        <button type="submit" class="px-5 py-2 bg-emerald-500 text-white rounded-lg font-bold text-sm hover:bg-emerald-600 transition-colors shadow-sm flex items-center">
                            <i class="fas fa-paper-plane mr-2"></i> Responder
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>"""

# Replace the old modal
modal_pattern = r'<!-- MODAL LECTURA -->.*?</div>\s*</div>\s*</div>'
content = re.sub(modal_pattern, new_modal_html, content, flags=re.DOTALL)

# 2. Inject MI_ID
mi_id_script = "<script>\n        const MI_ID = {{ profesional.id }};\n"
content = content.replace("<script>\n        function abrirModalLectura", mi_id_script + "        function abrirModalLectura")

# 3. Update abrirModalLectura JS
new_abrir_modal = """function abrirModalLectura(id, emisor, fecha, asunto, mensaje, leido_previo, tipo) {
            if (tipo === 'Enviado') {
                document.getElementById('lecturaEmisor').innerText = "Para: " + emisor;
            } else {
                document.getElementById('lecturaEmisor').innerText = "De: " + emisor;
            }
            document.getElementById('lecturaAsunto').innerText = asunto;
            
            // Set form action
            document.getElementById('formResponder').action = `/mensajeria/responder/${id}`;
            
            const msgContainer = document.getElementById('lecturaMensaje');
            msgContainer.innerHTML = '<div class="text-center text-gray-400 py-4"><i class="fas fa-spinner fa-spin text-2xl"></i></div>';
            
            const modal = document.getElementById('modalLectura');
            const content = document.getElementById('modalLecturaContent');
            modal.classList.remove('hidden');
            void modal.offsetWidth; // force reflow
            modal.classList.remove('opacity-0');
            content.classList.remove('scale-95');
            content.classList.add('scale-100');

            // Fetch hilo
            fetch(`/mensajeria/hilo/${id}`).then(res => res.json()).then(data => {
                if(data.success) {
                    let html = '';
                    data.hilo.forEach(item => {
                        let es_mio = item.emisor_id === MI_ID;
                        html += `
                            <div class="mb-6 flex ${es_mio ? 'justify-end' : 'justify-start'}">
                                <div class="max-w-[85%]">
                                    <div class="flex items-center gap-2 mb-1 ${es_mio ? 'justify-end' : 'justify-start'}">
                                        <span class="text-[11px] font-bold text-gray-500">${es_mio ? 'Tú' : item.emisor_nombre}</span>
                                        <span class="text-[10px] text-gray-400">${item.fecha}</span>
                                    </div>
                                    <div class="p-4 rounded-2xl shadow-sm text-sm ${es_mio ? 'bg-emerald-500 text-white rounded-tr-none' : 'bg-white text-gray-700 border border-gray-100 rounded-tl-none'} whitespace-pre-wrap leading-relaxed">${item.texto}</div>
                                </div>
                            </div>
                        `;
                    });
                    msgContainer.innerHTML = html;
                    msgContainer.scrollTop = msgContainer.scrollHeight;
                } else {
                    msgContainer.innerHTML = '<div class="text-center text-red-400 py-4">Error al cargar el hilo.</div>';
                }
            });

            if (!leido_previo && tipo !== 'Enviado') {
                // Hacer petición POST silenciosa para marcar leído
                fetch(`/mensajeria/leer/${id}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                }).then(res => res.json()).then(data => {
                    if (data.success) {
                        let badge = document.getElementById(`badge-${id}`);
                        if(badge) {
                            badge.className = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500";
                            badge.innerText = "Leído";
                        }
                        let fila = document.getElementById(`fila-msg-${id}`);
                        if(fila) {
                            fila.classList.remove('bg-emerald-50/50', 'font-semibold');
                            fila.classList.add('text-gray-500');
                        }
                        let badgeGlobal = document.getElementById('badgeGlobalSide');
                        if (badgeGlobal) {
                            let current = parseInt(badgeGlobal.innerText);
                            if (current > 1) {
                                badgeGlobal.innerText = current - 1;
                            } else {
                                badgeGlobal.remove();
                            }
                        }
                    }
                });
            }
        }"""

js_pattern = r'function abrirModalLectura\(id, emisor, fecha, asunto, mensaje, leido_previo, tipo\) \{.*?\}\n\n        \n        function borrarMensaje'
content = re.sub(js_pattern, new_abrir_modal + '\n\n        \n        function borrarMensaje', content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Modal de lectura actualizado para soportar hilos y respuestas.")

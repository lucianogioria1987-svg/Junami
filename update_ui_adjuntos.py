import re

file_path = r'c:\Users\lucia\OneDrive\Escritorio\Junami 3.0\plantillas\mensajeria.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update modalNuevoMensaje form
# We need to add enctype="multipart/form-data" and the file input
nuevo_form_pattern = r'<form action="{{ url_for\(\'mensajeria_bp\.enviar\'\) }}" method="POST" class="p-6">'
nuevo_form_repl = '<form action="{{ url_for(\'mensajeria_bp.enviar\') }}" method="POST" enctype="multipart/form-data" class="p-6" onsubmit="return validarTamanioAdjunto(this)">'
content = content.replace(nuevo_form_pattern, nuevo_form_repl)

# Add the file input to modalNuevoMensaje before the submit buttons
submit_buttons_pattern = r'<div class="flex justify-end gap-3 pt-2 border-t border-gray-50">'
file_input_html = """
                <div class="mb-6">
                    <label class="block text-sm font-bold text-gray-700 mb-2">Adjunto (Opcional, Max 10MB)</label>
                    <input type="file" name="adjunto" accept=".pdf,.docx,.xlsx,.jpg,.png" class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 transition-colors">
                </div>
                """
content = content.replace(submit_buttons_pattern, file_input_html + submit_buttons_pattern)

# 2. Update modalLectura reply form
# Find the textarea in formResponder
textarea_pattern = r'<textarea name="respuesta" required rows="2" class="w-full border-gray-200 rounded-xl shadow-sm focus:border-emerald-500 focus:ring-emerald-500 text-sm p-3" placeholder="Escribir una respuesta..."></textarea>'
reply_file_input_html = """<textarea name="respuesta" required rows="2" class="w-full border-gray-200 rounded-xl shadow-sm focus:border-emerald-500 focus:ring-emerald-500 text-sm p-3" placeholder="Escribir una respuesta..."></textarea>
                    <div class="flex items-center mt-2 mb-2">
                        <label class="text-sm font-bold text-gray-600 mr-3">Adjuntar:</label>
                        <input type="file" name="adjunto" accept=".pdf,.docx,.xlsx,.jpg,.png" class="text-sm text-gray-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-bold file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200 transition-colors cursor-pointer">
                    </div>"""
content = content.replace(textarea_pattern, reply_file_input_html)

# 3. Update JavaScript to handle sizes, FormData, and UI
js_pattern = r'function enviarRespuesta\(e\) \{.*?\}\);(.*?)        \}'
js_match = re.search(js_pattern, content, re.DOTALL)

# Let's replace the entire enviarRespuesta logic
old_enviarRespuesta = """        function enviarRespuesta(e) {
            e.preventDefault();
            let form = e.target;
            let respuesta = form.querySelector('textarea[name="respuesta"]').value;
            let id = currentModalId;
            
            // UI instantánea en el modal
            let msgContainer = document.getElementById('lecturaMensaje');
            let nuevaBurbuja = `
                <div class="mb-6 flex justify-end">
                    <div class="max-w-[85%]">
                        <div class="flex items-center gap-2 mb-1 justify-end">
                            <span class="text-[11px] font-bold text-gray-500">Tú</span>
                            <span class="text-[10px] text-gray-400">Ahora</span>
                        </div>
                        <div class="p-4 rounded-2xl shadow-sm text-sm bg-emerald-500 text-white rounded-tr-none whitespace-pre-wrap leading-relaxed opacity-50 transition-opacity duration-300" id="msg-temp-${id}">${respuesta}</div>
                    </div>
                </div>
            `;
            msgContainer.insertAdjacentHTML('beforeend', nuevaBurbuja);
            msgContainer.scrollTop = msgContainer.scrollHeight;
            form.querySelector('textarea[name="respuesta"]').value = '';
            
            fetch(`/mensajeria/responder/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ respuesta: respuesta })
            }).then(res => res.json()).then(data => {
                if (data.success) {
                    document.getElementById(`msg-temp-${id}`).classList.remove('opacity-50');
                    
                    // Mover la fila a Enviados
                    moverFila(id, 'Enviados');
                    currentModalTipo = 'Enviado'; // Actualizar estado modal
                } else {
                    alert('Error al enviar: ' + data.error);
                    document.getElementById(`msg-temp-${id}`).parentElement.parentElement.remove();
                }
            });
        }"""

new_enviarRespuesta = """        function validarTamanioAdjunto(form) {
            const input = form.querySelector('input[type="file"]');
            if (input && input.files.length > 0) {
                const fileSize = input.files[0].size / 1024 / 1024; // MB
                if (fileSize > 10) {
                    alert('El archivo supera el límite de 10MB.');
                    return false;
                }
            }
            return true;
        }

        function enviarRespuesta(e) {
            e.preventDefault();
            let form = e.target;
            
            if (!validarTamanioAdjunto(form)) return;
            
            let respuesta = form.querySelector('textarea[name="respuesta"]').value;
            let fileInput = form.querySelector('input[type="file"]');
            let hasFile = fileInput && fileInput.files.length > 0;
            let id = currentModalId;
            
            let formData = new FormData(form);
            
            // UI instantánea en el modal
            let msgContainer = document.getElementById('lecturaMensaje');
            let archivoDiv = hasFile ? `<div class="mt-3 pt-3 border-t border-emerald-400 border-opacity-30"><span class="flex items-center text-xs font-bold text-emerald-100"><i class="fas fa-paperclip mr-2"></i> Enviando adjunto...</span></div>` : '';
            
            let nuevaBurbuja = `
                <div class="mb-6 flex justify-end">
                    <div class="max-w-[85%]">
                        <div class="flex items-center gap-2 mb-1 justify-end">
                            <span class="text-[11px] font-bold text-gray-500">Tú</span>
                            <span class="text-[10px] text-gray-400">Ahora</span>
                        </div>
                        <div class="p-4 rounded-2xl shadow-sm text-sm bg-emerald-500 text-white rounded-tr-none whitespace-pre-wrap leading-relaxed opacity-50 transition-opacity duration-300" id="msg-temp-${id}">${respuesta}${archivoDiv}</div>
                    </div>
                </div>
            `;
            msgContainer.insertAdjacentHTML('beforeend', nuevaBurbuja);
            msgContainer.scrollTop = msgContainer.scrollHeight;
            
            // Disable form while submitting
            let btnSubmit = form.querySelector('button[type="submit"]');
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Enviando';
            
            fetch(`/mensajeria/responder/${id}`, {
                method: 'POST',
                body: formData
            }).then(res => res.json()).then(data => {
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = '<i class="fas fa-paper-plane mr-2"></i> Responder';
                form.querySelector('textarea[name="respuesta"]').value = '';
                if(fileInput) fileInput.value = ''; // clear file
                
                if (data.success) {
                    let tempMsg = document.getElementById(`msg-temp-${id}`);
                    tempMsg.classList.remove('opacity-50');
                    if (data.adjunto) {
                        tempMsg.innerHTML = tempMsg.innerHTML.replace('Enviando adjunto...', `Adjunto guardado: ${data.adjunto.nombre_original}`);
                    }
                    
                    moverFila(id, 'Enviados');
                    currentModalTipo = 'Enviado';
                    
                    // Asegurarnos de recargar la burbuja si quisieramos, pero así sirve
                } else {
                    alert('Error al enviar: ' + data.error);
                    document.getElementById(`msg-temp-${id}`).parentElement.parentElement.remove();
                }
            }).catch(err => {
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = '<i class="fas fa-paper-plane mr-2"></i> Responder';
                alert('Error de conexión.');
            });
        }"""
        
content = content.replace(old_enviarRespuesta, new_enviarRespuesta)

# 4. Update the bubble rendering in abrirModalLectura to show the attachment
old_bubble = """<div class="p-4 rounded-2xl shadow-sm text-sm ${es_mio ? 'bg-emerald-500 text-white rounded-tr-none' : 'bg-white text-gray-700 border border-gray-100 rounded-tl-none'} whitespace-pre-wrap leading-relaxed">${item.texto}</div>"""
new_bubble = """<div class="p-4 rounded-2xl shadow-sm text-sm ${es_mio ? 'bg-emerald-500 text-white rounded-tr-none' : 'bg-white text-gray-700 border border-gray-100 rounded-tl-none'} whitespace-pre-wrap leading-relaxed">
                                        ${item.texto}
                                        ${item.adjunto ? `<div class="mt-3 pt-3 border-t ${es_mio ? 'border-emerald-400 border-opacity-30' : 'border-gray-100'}"><a href="/static/${item.adjunto.ruta}" target="_blank" class="inline-flex items-center px-3 py-1.5 text-xs font-bold rounded-lg ${es_mio ? 'bg-emerald-600 hover:bg-emerald-700 text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'} transition-colors"><i class="fas fa-paperclip mr-2"></i> ${item.adjunto.nombre_original}</a></div>` : ''}
                                    </div>"""
content = content.replace(old_bubble, new_bubble)

# 5. Add Paperclip icon in the Inbox tables next to Asunto
# Find `{{ msg.asunto }}` and replace with `{{ msg.asunto }} {% if msg.tiene_adjunto %} <i class="fas fa-paperclip text-emerald-500 ml-2" title="Contiene archivo adjunto"></i>{% endif %}`
content = content.replace('{{ msg.asunto }}</td>', '{{ msg.asunto }} {% if msg.tiene_adjunto %} <i class="fas fa-paperclip text-emerald-500 ml-2" title="Contiene archivo adjunto"></i>{% endif %}</td>')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("HTML modificado para soportar archivos adjuntos y tamaño máximo de 10MB.")

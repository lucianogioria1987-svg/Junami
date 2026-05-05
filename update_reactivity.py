import re

file_path = r'c:\Users\lucia\OneDrive\Escritorio\Junami 3.0\plantillas\mensajeria.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Añadir IDs a los tbodys si no los tienen
content = content.replace('<tbody class="divide-y divide-gray-50">', '<tbody id="tbody-nuevos" class="divide-y divide-gray-50">', 1)
content = content.replace('<tbody class="divide-y divide-gray-50">', '<tbody id="tbody-enviados" class="divide-y divide-gray-50">', 1)
content = content.replace('<tbody class="divide-y divide-gray-100">', '<tbody id="tbody-historial" class="divide-y divide-gray-100">', 1)

# 2. Reemplazar el <form id="formResponder"> con un event listener de submit para AJAX
# Currently it is:
# <form id="formResponder" action="" method="POST" class="flex flex-col gap-3">
form_pattern = r'<form id="formResponder" action="" method="POST" class="flex flex-col gap-3">'
content = content.replace(form_pattern, '<form id="formResponder" onsubmit="enviarRespuesta(event)" class="flex flex-col gap-3">')

# 3. Añadir el script de Reactividad en la etiqueta <script> existente
js_reactividad = """
        let currentModalId = null;
        let currentModalTipo = null;
        let currentModalLeidoPrevio = false;

        function moverFila(id, destino) {
            let fila = document.getElementById(`fila-msg-${id}`);
            if(!fila) fila = document.getElementById(`fila-enviado-${id}`);
            if(!fila) return;
            
            let htmlFila = '';
            // Clonar o reconstruir botones según destino
            if (destino === 'Historial') {
                // De Nuevos a Historial
                let badge = fila.querySelector('td:first-child span');
                if(badge) {
                    badge.className = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500";
                    badge.innerText = "Leído";
                }
                fila.classList.remove('bg-emerald-50/50', 'font-semibold', 'bg-white');
                fila.classList.add('hover:bg-gray-50', 'text-gray-500');
                
                // Mover a tbody-historial
                document.getElementById('tbody-historial').prepend(fila);
                
                // Reconstruir botones a Ver y Borrar
                let tdAcciones = fila.querySelector('td:last-child');
                // Extraer variables para no romper el onclick
                let btn = tdAcciones.querySelector('button');
                let onclickStr = btn.getAttribute('onclick');
                // onclickStr = abrirModalLectura(2, 'Dr. ...', '', 'Asunto', '', false, 'Recibido')
                // Cambiar false a true
                onclickStr = onclickStr.replace(', false,', ', true,');
                
                tdAcciones.innerHTML = `
                    <div class="flex justify-center gap-2">
                        <button onclick="${onclickStr}" class="inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button onclick="borrarMensaje(${id})" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-red-400 hover:bg-red-500 transition-colors">
                            <i class="fas fa-trash-alt mr-2"></i> Borrar
                        </button>
                    </div>
                `;
            } else if (destino === 'Enviados') {
                // De Historial o Nuevos a Enviados (al responder)
                let badge = fila.querySelector('td:first-child span');
                if(badge) {
                    badge.className = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-700 shadow-sm";
                    badge.innerText = "Pendiente";
                }
                fila.classList.remove('bg-emerald-50/50', 'font-semibold', 'text-gray-500', 'hover:bg-gray-50');
                fila.classList.add('hover:bg-emerald-50/30', 'bg-white', 'font-medium', 'text-gray-700');
                
                document.getElementById('tbody-enviados').prepend(fila);
                
                let tdAcciones = fila.querySelector('td:last-child');
                let onclickStr = '';
                let btn = tdAcciones.querySelector('button');
                if(btn) {
                    onclickStr = btn.getAttribute('onclick');
                    onclickStr = onclickStr.replace("'Recibido'", "'Enviado'");
                    onclickStr = onclickStr.replace("false,", "true,");
                }
                
                tdAcciones.innerHTML = `
                    <button onclick="${onclickStr}" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-emerald-500 hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors">
                        <i class="fas fa-eye mr-2"></i> Ver
                    </button>
                `;
            }
        }

        function enviarRespuesta(e) {
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
        }
"""

content = content.replace("const MI_ID = {{ profesional.id }};", "const MI_ID = {{ profesional.id }};\n" + js_reactividad)

# 4. Modificar abrirModalLectura para usar variables globales y quitar peticion de leer, ahora leer ocurre al CERRAR
old_abrir = "function abrirModalLectura(id, emisor, fecha, asunto, mensaje, leido_previo, tipo) {"
new_abrir = """function abrirModalLectura(id, emisor, fecha, asunto, mensaje, leido_previo, tipo) {
            currentModalId = id;
            currentModalTipo = tipo;
            currentModalLeidoPrevio = leido_previo;
"""
content = content.replace(old_abrir, new_abrir)

# Eliminar el fetch de leer de abrirModalLectura
fetch_leer_pattern = r'if \(!leido_previo && tipo !== \'Enviado\'\) \{.*?\}\);\n            \}'
content = re.sub(fetch_leer_pattern, '', content, flags=re.DOTALL)

# Poner fetch leer en cerrarModalLectura()
old_cerrar = "function cerrarModalLectura() {"
new_cerrar = """function cerrarModalLectura() {
            if (!currentModalLeidoPrevio && currentModalTipo !== 'Enviado') {
                // Hacer petición POST silenciosa para marcar leído
                fetch(`/mensajeria/leer/${currentModalId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                }).then(res => res.json()).then(data => {
                    if (data.success) {
                        moverFila(currentModalId, 'Historial');
                        
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
"""
content = content.replace(old_cerrar, new_cerrar)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("JS modificado para Reactividad 100% Sin F5.")

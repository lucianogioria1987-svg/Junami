

        const MI_ID = {{ profesional.id }};

        let currentModalId = null;
        let currentModalTipo = null;
        let currentModalLeidoPrevio = false;

        function moverFila(id, destino) {
            let fila = document.getElementById(`fila-msg-${id}`);
            if(!fila) fila = document.getElementById(`fila-enviado-${id}`);
            if(!fila) return;
            
            // Remove empty rows message if any
            let emptyRows = [];
            emptyRows.forEach(eid => { let el = document.getElementById(eid); if(el) el.style.display = 'none'; });

            // Determine Origen currently for storing when archiving
            let currentOrigen = fila.getAttribute('data-origen');
            if(!currentOrigen) {
                // Determine by tbody
                if(fila.parentElement.id === 'tbody-enviados') currentOrigen = 'Saliente';
                else currentOrigen = 'Entrante';
                fila.setAttribute('data-origen', currentOrigen);
            }

            if(!fila) return;
            
            // Declarar variables comunes una sola vez para evitar conflictos de scope
            let badge = fila.querySelector('td:first-child span');
            let img = fila.querySelector('img');
            let tdAcciones = fila.querySelector('td:last-child');
            
            // Clonar o reconstruir botones según destino
            if (destino === 'Historial') {
                // De Nuevos a Historial
                if(badge) {
                    badge.className = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500";
                    badge.innerText = "Leído";
                }
                fila.classList.remove('bg-emerald-50/50', 'font-semibold', 'bg-white');
                fila.classList.add('hover:bg-gray-50', 'text-gray-500');
                
                // Mover a tbody-historial
                document.getElementById('tbody-historial').prepend(fila);
                
                // Extract data attributes from existing ver button
                let btnVerHist = tdAcciones.querySelector('.btn-ver') || tdAcciones.querySelector('button');
                let dEmisor = btnVerHist ? btnVerHist.getAttribute('data-emisor') : '';
                let dFecha = btnVerHist ? btnVerHist.getAttribute('data-fecha') : '';
                let dAsunto = btnVerHist ? btnVerHist.getAttribute('data-asunto') : '';
                
                tdAcciones.innerHTML = `
                    <div class="flex justify-center gap-2">
                        <button class="btn-ver inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors" data-id="${id}" data-emisor="${dEmisor}" data-fecha="${dFecha}" data-asunto="${dAsunto}" data-leido="true" data-tipo="Recibido">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-borrar inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-red-400 hover:bg-red-500 transition-colors" title="Borrar" data-id="${id}">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                `;
            } else if (destino === 'Enviados') {
                // De Historial o Nuevos a Enviados (al responder)
                if(badge) {
                    badge.className = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-700 shadow-sm";
                    badge.innerText = "Pendiente";
                }
                fila.classList.remove('bg-emerald-50/50', 'font-semibold', 'text-gray-500', 'hover:bg-gray-50');
                fila.classList.add('hover:bg-emerald-50/30', 'bg-white', 'font-medium', 'text-gray-700');
                
                document.getElementById('tbody-enviados').prepend(fila);
                
                let btnVerEnv = tdAcciones.querySelector('.btn-ver') || tdAcciones.querySelector('button');
                let eEmisor = btnVerEnv ? btnVerEnv.getAttribute('data-emisor') : '';
                let eFecha = btnVerEnv ? btnVerEnv.getAttribute('data-fecha') : '';
                let eAsunto = btnVerEnv ? btnVerEnv.getAttribute('data-asunto') : '';
                
                tdAcciones.innerHTML = `
                    <div class="flex justify-center gap-2">
                        <button class="btn-ver inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-emerald-500 hover:bg-emerald-600 transition-colors" data-id="${id}" data-emisor="${eEmisor}" data-fecha="${eFecha}" data-asunto="${eAsunto}" data-leido="true" data-tipo="Enviado">
                            <i class="fas fa-eye"></i>
                        </button>
                        </div>
                `;
            }function validarTamanioAdjunto(form) {
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
        }

        function abrirModalLectura(id, emisor, fecha, asunto, mensaje, leido_previo, tipo) {
            currentModalId = id;
            currentModalTipo = tipo;
            currentModalLeidoPrevio = leido_previo;

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
                                    <div class="p-4 rounded-2xl shadow-sm text-sm ${es_mio ? 'bg-emerald-500 text-white rounded-tr-none' : 'bg-white text-gray-700 border border-gray-100 rounded-tl-none'} whitespace-pre-wrap leading-relaxed">
                                        ${item.texto}
                                        ${item.adjunto ? `<div class="mt-3 pt-3 border-t ${es_mio ? 'border-emerald-400 border-opacity-30' : 'border-gray-100'}"><a href="/static/${item.adjunto.ruta}" target="_blank" class="inline-flex items-center px-3 py-1.5 text-xs font-bold rounded-lg ${es_mio ? 'bg-emerald-600 hover:bg-emerald-700 text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'} transition-colors"><i class="fas fa-paperclip mr-2"></i> ${item.adjunto.nombre_original}</a></div>` : ''}
                                    </div>
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

            
        }

        
        
        `, {
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

        `, {
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

        function cerrarModalLectura() {
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

            const modal = document.getElementById('modalLectura');
            const content = document.getElementById('modalLecturaContent');
            modal.classList.add('opacity-0');
            content.classList.remove('scale-100');
            content.classList.add('scale-95');
            setTimeout(() => {
                modal.classList.add('hidden');
            }, 300);
        }
    

        function abrirModalNuevoMensaje() {
            const modal = document.getElementById('modalNuevoMensaje');
            if(!modal) return;
            const content = document.getElementById('modalNuevoMensajeContent');
            modal.classList.remove('hidden');
            void modal.offsetWidth; // force reflow
            modal.classList.remove('opacity-0');
            content.classList.remove('translate-y-full', 'sm:translate-y-10');
            content.classList.add('translate-y-0');
        }
        function cerrarModalNuevoMensaje() {
            const modal = document.getElementById('modalNuevoMensaje');
            if(!modal) return;
            const content = document.getElementById('modalNuevoMensajeContent');
            modal.classList.add('opacity-0');
            content.classList.remove('translate-y-0');
            content.classList.add('translate-y-full', 'sm:translate-y-10');
            setTimeout(() => {
                modal.classList.add('hidden');
            }, 300);
        }
    
        document.addEventListener('DOMContentLoaded', function() {
    console.log("Botones encontrados: ", document.querySelectorAll('.btn-ver').length);
    // DELEGACION DE EVENTOS GLOBAL
        document.addEventListener('click', function(e) {
            let btnVer = e.target.closest('.btn-ver');
            if(btnVer) {
                let id = btnVer.getAttribute('data-id');
                let emisor = btnVer.getAttribute('data-emisor');
                let fecha = btnVer.getAttribute('data-fecha');
                let asunto = btnVer.getAttribute('data-asunto');
                let leido = btnVer.getAttribute('data-leido') === 'true';
                let tipo = btnVer.getAttribute('data-tipo');
                abrirModalLectura(id, emisor, fecha, asunto, null, leido, tipo);
                return;
            }
            
            let btnBorrar = e.target.closest('.btn-borrar');
            if(btnBorrar) {
                borrarMensaje(btnBorrar.getAttribute('data-id'));
                return;
            }
        });
});


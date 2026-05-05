import os
import glob
import re

PLANTILLAS_DIR = os.path.join(os.path.dirname(__file__), 'plantillas')

INYECCION_SIDEBAR = """
                <p class="px-6 text-xs font-semibold text-gray-400 uppercase tracking-wider mt-6 mb-2">Mensajería</p>
                <a href="{{ url_for('mensajeria_bp.inbox') }}"
                    class="flex items-center px-6 py-3 transition-all group {{ 'text-red-700 bg-red-50 border-r-4 border-red-600 font-bold' if request.blueprint == 'mensajeria_bp' else 'text-gray-500 hover:text-red-600 hover:bg-slate-50' }}">
                    <svg class="w-5 h-5 mr-3 {{ 'text-red-600' if request.blueprint == 'mensajeria_bp' else 'group-hover:text-red-500 transition' }}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                    Buzón
                    {% if mensajes_sin_leer > 0 %}
                    <span class="ml-auto bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-sm" id="badgeGlobalSide">{{ mensajes_sin_leer }}</span>
                    {% endif %}
                </a>
                <div class="px-6 py-3">
                    <button onclick="abrirModalNuevoMensaje()" class="w-full bg-red-50 text-red-600 border border-red-100 hover:bg-red-600 hover:text-white transition-colors rounded-lg py-2 text-sm font-bold flex items-center justify-center shadow-sm">
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg> Redactar Mensaje
                    </button>
                </div>
            </nav>
            <div class="p-4 border-t border-gray-100">"""

INYECCION_MODAL = """
    <!-- MODAL NUEVO MENSAJE (GLOBAL) -->
    <div id="modalNuevoMensaje" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 hidden flex items-end justify-center sm:items-center p-4 transition-opacity duration-300 opacity-0">
        <div class="bg-white rounded-t-2xl sm:rounded-2xl w-full max-w-lg shadow-2xl transform transition-transform duration-300 translate-y-full sm:translate-y-10" id="modalNuevoMensajeContent">
            <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50 rounded-t-2xl sm:rounded-t-2xl">
                <h3 class="font-bold text-gray-800 flex items-center"><svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg> Nuevo Recado</h3>
                <button onclick="cerrarModalNuevoMensaje()" class="text-gray-400 hover:text-red-500 transition-colors bg-white rounded-full p-1"><i class="fas fa-times"></i></button>
            </div>
            <form action="{{ url_for('mensajeria_bp.enviar') }}" method="POST" class="p-6">
                <div class="mb-4">
                    <label class="block text-sm font-bold text-gray-700 mb-2">Destinatario</label>
                    <select name="receptor_id" required class="w-full border-gray-200 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm">
                        <option value="">Seleccione un profesional...</option>
                        {% for p in lista_profesionales_global %}
                        <option value="{{ p.id }}">{{ p.nombre }} ({{ p.rol }})</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-bold text-gray-700 mb-2">Asunto</label>
                    <input type="text" name="asunto" required class="w-full border-gray-200 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm" placeholder="Breve descripción...">
                </div>
                <div class="mb-6">
                    <label class="block text-sm font-bold text-gray-700 mb-2">Mensaje</label>
                    <textarea name="mensaje" required rows="4" class="w-full border-gray-200 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm" placeholder="Escriba su recado aquí..."></textarea>
                </div>
                <div class="flex justify-end gap-3 pt-2 border-t border-gray-50">
                    <button type="button" onclick="cerrarModalNuevoMensaje()" class="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg font-bold text-sm hover:bg-gray-50 transition-colors shadow-sm">Cancelar</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg font-bold text-sm hover:bg-blue-700 transition-colors shadow-sm flex items-center"><svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg> Enviar Recado</button>
                </div>
            </form>
        </div>
    </div>

    <script>
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
    </script>
</body>"""

def update_templates():
    html_files = glob.glob(os.path.join(PLANTILLAS_DIR, '*.html'))
    for file in html_files:
        if 'imprimir_' in file or 'login.html' in file:
            continue
            
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        modified = False
        
        # 1. Inyectar en el sidebar
        if 'Buzón de Recados' not in content and 'mensajeria_bp.inbox' not in content:
            # Buscar el cierre del nav y el inicio de la zona del perfil
            pattern = re.compile(r'</nav>\s*<div\s+class="p-4\s+border-t\s+border-gray-100">')
            if pattern.search(content):
                content = pattern.sub(INYECCION_SIDEBAR, content)
                modified = True
                
        # 2. Inyectar modal
        if 'id="modalNuevoMensaje"' not in content:
            # Insertar justo antes del cierre del body
            content = content.replace('</body>', INYECCION_MODAL)
            modified = True
            
        if modified:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Actualizado: {os.path.basename(file)}")

if __name__ == "__main__":
    update_templates()

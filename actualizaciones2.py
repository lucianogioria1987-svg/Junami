import os
import glob

PLANTILLAS_DIR = os.path.join(os.path.dirname(__file__), 'plantillas')

def update_templates():
    html_files = glob.glob(os.path.join(PLANTILLAS_DIR, '*.html'))
    for file in html_files:
        if 'imprimir_' in file or 'login.html' in file:
            continue
            
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        modified = False
        
        # 1. Cambiar colores de Buzón y Redactar Mensaje
        # Partimos el string donde empieza Mensajería para solo reemplazar ahí
        marker = '<p class="px-6 text-xs font-semibold text-gray-400 uppercase tracking-wider mt-6 mb-2">Mensajería</p>'
        if marker in content:
            partes = content.split(marker)
            if len(partes) == 2:
                # La parte 1 es desde Mensajería hasta el final
                # Partimos de nuevo por <div class="p-4 border-t border-gray-100"> que es donde termina el nav
                subpartes = partes[1].split('</nav>')
                if len(subpartes) >= 2:
                    bloque = subpartes[0]
                    
                    bloque = bloque.replace('text-red-700', 'text-emerald-700')
                    bloque = bloque.replace('bg-red-50', 'bg-emerald-50')
                    bloque = bloque.replace('border-red-600', 'border-emerald-600')
                    bloque = bloque.replace('hover:text-red-600', 'hover:text-emerald-600')
                    bloque = bloque.replace('text-red-600', 'text-emerald-600')
                    bloque = bloque.replace('group-hover:text-red-500', 'group-hover:text-emerald-500')
                    bloque = bloque.replace('bg-red-500', 'bg-emerald-500')
                    bloque = bloque.replace('border-red-100', 'border-emerald-100')
                    bloque = bloque.replace('hover:bg-red-600', 'hover:bg-emerald-600')
                    
                    subpartes[0] = bloque
                    partes[1] = '</nav>'.join(subpartes)
                    new_content = marker.join(partes)
                    if new_content != content:
                        content = new_content
                        modified = True

        # 2. Reparación del Sidebar (Principal)
        nav_tag = '<nav class="flex-1 py-6 space-y-1 overflow-y-auto">'
        p_tag = '<p class="px-6 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Principal</p>'
        if nav_tag in content:
            if p_tag not in content:
                # Puede ser que el p_tag original tuviera otro espaciado, veamos si está "Principal</p>"
                if "Principal</p>" not in content:
                    content = content.replace(
                        nav_tag,
                        nav_tag + '\n                ' + p_tag
                    )
                    modified = True

        # 3. Rediseño del Modal
        old_modal_start1 = 'class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 hidden flex items-end justify-center sm:items-center p-4 transition-opacity duration-300 opacity-0"'
        new_modal_start1 = 'class="fixed bottom-0 right-0 sm:bottom-6 sm:right-6 z-[100] hidden w-full sm:w-[450px] transition-opacity duration-300 opacity-0"'
        
        if old_modal_start1 in content:
            content = content.replace(old_modal_start1, new_modal_start1)
            modified = True
            
        old_modal_content1 = 'class="bg-white rounded-t-2xl sm:rounded-2xl w-full max-w-lg shadow-2xl transform transition-transform duration-300 translate-y-full sm:translate-y-10"'
        new_modal_content1 = 'class="bg-white rounded-t-2xl sm:rounded-2xl w-full shadow-[0_10px_50px_-12px_rgba(0,0,0,0.4)] border border-gray-100 transform transition-transform duration-300 translate-y-full sm:translate-y-10"'
        
        if old_modal_content1 in content:
            content = content.replace(old_modal_content1, new_modal_content1)
            modified = True

        if modified:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Actualizado: {os.path.basename(file)}")

if __name__ == "__main__":
    update_templates()

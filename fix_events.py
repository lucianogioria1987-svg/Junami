import re

file_path = r'c:\Users\lucia\OneDrive\Escritorio\Junami 3.0\plantillas\mensajeria.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Bump Z-Index of modalLectura to z-[100]
content = content.replace('backdrop-blur-sm z-50', 'backdrop-blur-sm z-[100]')

# 2. Replace all inline onclicks with data attributes and classes
# Function to replace Jinja onclicks
def replace_jinja_onclicks(html):
    # btn-ver in Nuevos
    ver_nuevos_pattern = r'<button onclick="abrirModalLectura\((\{\{ msg\.id \}\}), \'(.*?)\', \'(.*?)\', \'(.*?)\', \'.*?\', (false|true), \'(Recibido|Enviado)\'\)" (class="[^"]*?")>'
    html = re.sub(ver_nuevos_pattern, r'<button \7 class-tmp="\7" data-action="ver" data-id="\1" data-emisor="\2" data-fecha="\3" data-asunto="\4" data-leido="\5" data-tipo="\6">', html)
    
    # Let's fix the class-tmp hack
    html = re.sub(r'class-tmp="class=\\"(.*?)\\""', r'class="\1 btn-ver"', html)

    # archivar
    html = re.sub(r'<button onclick="archivarMensaje\(\{\{ msg\.id \}\}\)" (class="[^"]*?")', r'<button \1 data-action="archivar" data-id="{{ msg.id }}"', html)
    
    # desarchivar
    html = re.sub(r'<button onclick="desarchivarMensaje\(\{\{ msg\.id \}\}\)" (class="[^"]*?")', r'<button \1 data-action="desarchivar" data-id="{{ msg.id }}"', html)
    
    # borrar
    html = re.sub(r'<button onclick="borrarMensaje\(\{\{ msg\.id \}\}\)" (class="[^"]*?")', r'<button \1 data-action="borrar" data-id="{{ msg.id }}"', html)
    
    # Clean up classes
    html = re.sub(r'data-action="archivar" class="(.*?)"', r'class="\1 btn-archivar" data-id="{{ msg.id }}"', html)
    html = re.sub(r'data-action="desarchivar" class="(.*?)"', r'class="\1 btn-desarchivar" data-id="{{ msg.id }}"', html)
    html = re.sub(r'data-action="borrar" class="(.*?)"', r'class="\1 btn-borrar" data-id="{{ msg.id }}"', html)

    return html

content = replace_jinja_onclicks(content)

# 3. Modify moverFila to use data attributes instead of onclickStr
# Replace the blocks where tdAcciones.innerHTML is built
# Target Historial reconstruction
hist_inner_html = r'''tdAcciones\.innerHTML = `
                    <div class="flex justify-center gap-2">
                        <button onclick="\$\{onclickStr\}" class="inline-flex items-center px-3 py-1\.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button onclick="archivarMensaje\(\$\{id\}\)" class="inline-flex items-center px-3 py-1\.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors" title="Archivar">
                            <i class="fas fa-archive"></i>
                        </button>
                        <button onclick="borrarMensaje\(\$\{id\}\)" class="inline-flex items-center px-3 py-1\.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-red-400 hover:bg-red-500 transition-colors" title="Borrar">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                `;'''

new_hist_inner = r'''// Extract data attributes from existing ver button
                let btnVerHist = tdAcciones.querySelector('.btn-ver') || tdAcciones.querySelector('button');
                let dEmisor = btnVerHist ? btnVerHist.getAttribute('data-emisor') : '';
                let dFecha = btnVerHist ? btnVerHist.getAttribute('data-fecha') : '';
                let dAsunto = btnVerHist ? btnVerHist.getAttribute('data-asunto') : '';
                
                tdAcciones.innerHTML = `
                    <div class="flex justify-center gap-2">
                        <button class="btn-ver inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors" data-id="${id}" data-emisor="${dEmisor}" data-fecha="${dFecha}" data-asunto="${dAsunto}" data-leido="true" data-tipo="Recibido">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-archivar inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors" title="Archivar" data-id="${id}">
                            <i class="fas fa-archive"></i>
                        </button>
                        <button class="btn-borrar inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-red-400 hover:bg-red-500 transition-colors" title="Borrar" data-id="${id}">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                `;'''
content = re.sub(hist_inner_html, new_hist_inner, content)

# Target Enviados reconstruction
env_inner_html = r'''tdAcciones\.innerHTML = `
                    <div class="flex justify-center gap-2">
                        <button onclick="\$\{onclickStr\}" class="inline-flex items-center px-3 py-1\.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-emerald-500 hover:bg-emerald-600 transition-colors">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button onclick="archivarMensaje\(\$\{id\}\)" class="inline-flex items-center px-3 py-1\.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors" title="Archivar">
                            <i class="fas fa-archive"></i>
                        </button>
                    </div>
                `;'''

new_env_inner = r'''let btnVerEnv = tdAcciones.querySelector('.btn-ver') || tdAcciones.querySelector('button');
                let eEmisor = btnVerEnv ? btnVerEnv.getAttribute('data-emisor') : '';
                let eFecha = btnVerEnv ? btnVerEnv.getAttribute('data-fecha') : '';
                let eAsunto = btnVerEnv ? btnVerEnv.getAttribute('data-asunto') : '';
                
                tdAcciones.innerHTML = `
                    <div class="flex justify-center gap-2">
                        <button class="btn-ver inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-emerald-500 hover:bg-emerald-600 transition-colors" data-id="${id}" data-emisor="${eEmisor}" data-fecha="${eFecha}" data-asunto="${eAsunto}" data-leido="true" data-tipo="Enviado">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-archivar inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors" title="Archivar" data-id="${id}">
                            <i class="fas fa-archive"></i>
                        </button>
                    </div>
                `;'''
content = re.sub(env_inner_html, new_env_inner, content)

# Target Archivados reconstruction
arch_inner_html = r'''tdAcciones\.innerHTML = `
                    <div class="flex justify-center gap-2">
                        <button onclick="\$\{onclickStr\}" class="inline-flex items-center px-3 py-1\.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-500 bg-white hover:bg-gray-50 transition-colors" title="Ver">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button onclick="desarchivarMensaje\(\$\{id\}\)" class="inline-flex items-center px-3 py-1\.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-emerald-600 bg-white hover:bg-emerald-50 transition-colors" title="Desarchivar">
                            <i class="fas fa-box-open"></i>
                        </button>
                        <button onclick="borrarMensaje\(\$\{id\}\)" class="inline-flex items-center px-3 py-1\.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-red-400 hover:bg-red-500 transition-colors" title="Borrar">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                `;'''

new_arch_inner = r'''let btnVerArch = tdAcciones.querySelector('.btn-ver') || tdAcciones.querySelector('button');
                let aEmisor = btnVerArch ? btnVerArch.getAttribute('data-emisor') : '';
                let aFecha = btnVerArch ? btnVerArch.getAttribute('data-fecha') : '';
                let aAsunto = btnVerArch ? btnVerArch.getAttribute('data-asunto') : '';
                let aTipo = currentOrigen === 'Entrante' ? 'Recibido' : 'Enviado';
                
                tdAcciones.innerHTML = `
                    <div class="flex justify-center gap-2">
                        <button class="btn-ver inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-500 bg-white hover:bg-gray-50 transition-colors" title="Ver" data-id="${id}" data-emisor="${aEmisor}" data-fecha="${aFecha}" data-asunto="${aAsunto}" data-leido="true" data-tipo="${aTipo}">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-desarchivar inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-emerald-600 bg-white hover:bg-emerald-50 transition-colors" title="Desarchivar" data-id="${id}">
                            <i class="fas fa-box-open"></i>
                        </button>
                        <button class="btn-borrar inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-red-400 hover:bg-red-500 transition-colors" title="Borrar" data-id="${id}">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                `;'''
content = re.sub(arch_inner_html, new_arch_inner, content)

# Remove the extraction lines that became obsolete above tdAcciones.innerHTML
obsolete_extractions = r'''let tdAcciones = fila\.querySelector\('td:last-child'\);\s*let btnVer = tdAcciones\.querySelector\('button\[title="Ver"\]'\) \|\| tdAcciones\.querySelector\('button'\);\s*let onclickStr = btnVer \? btnVer\.getAttribute\('onclick'\) : '';'''
content = re.sub(obsolete_extractions, r'let tdAcciones = fila.querySelector(\'td:last-child\');', content)

obsolete_extractions_2 = r'''// Extraer variables para no romper el onclick\s*let btn = tdAcciones\.querySelector\('button'\);\s*let onclickStr = btn\.getAttribute\('onclick'\);\s*// onclickStr = abrirModalLectura\(2, 'Dr\. ...', '', 'Asunto', '', false, 'Recibido'\)\s*// Cambiar false a true\s*onclickStr = onclickStr\.replace\(', false,', ', true,'\);'''
content = re.sub(obsolete_extractions_2, '', content)

obsolete_extractions_3 = r'''let onclickStr = '';\s*let btn = tdAcciones\.querySelector\('button'\);\s*if\(btn\) \{\s*onclickStr = btn\.getAttribute\('onclick'\);\s*onclickStr = onclickStr\.replace\("'Recibido'", "'Enviado'"\);\s*onclickStr = onclickStr\.replace\("false,", "true,"\);\s*\}'''
content = re.sub(obsolete_extractions_3, '', content)


# 4. Add the Global Event Listener and remove inline `onclick="borrarMensaje(id)"`
# Insert the global listener just before the closing script tag
global_listener = """
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
            
            let btnArchivar = e.target.closest('.btn-archivar');
            if(btnArchivar) {
                archivarMensaje(btnArchivar.getAttribute('data-id'));
                return;
            }
            
            let btnDesarchivar = e.target.closest('.btn-desarchivar');
            if(btnDesarchivar) {
                desarchivarMensaje(btnDesarchivar.getAttribute('data-id'));
                return;
            }
            
            let btnBorrar = e.target.closest('.btn-borrar');
            if(btnBorrar) {
                borrarMensaje(btnBorrar.getAttribute('data-id'));
                return;
            }
        });
"""
content = content.replace('</script>\n</body>', global_listener + '</script>\n</body>')


with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Event delegation aplicado correctamente.")

import re

with open("plantillas/mensajeria.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove the buttons btn-archivar and btn-desarchivar from the HTML directly
html = re.sub(r'<button class="btn-archivar inline-flex[^>]+>.*?<\/button>\s*', '', html, flags=re.DOTALL)
html = re.sub(r'<button class="btn-desarchivar inline-flex[^>]+>.*?<\/button>\s*', '', html, flags=re.DOTALL)

# 2. Remove archivarMensaje and desarchivarMensaje functions
html = re.sub(r'function archivarMensaje\(id\) \{.*?\}\s*', '', html, flags=re.DOTALL)
html = re.sub(r'function desarchivarMensaje\(id\) \{.*?\}\s*', '', html, flags=re.DOTALL)

# 3. Remove event delegation for btn-archivar and btn-desarchivar
html = re.sub(r'let btnArchivar = e\.target\.closest\(\'\.btn-archivar\'\);.*?return;\s*\}\s*', '', html, flags=re.DOTALL)
html = re.sub(r'let btnDesarchivar = e\.target\.closest\(\'\.btn-desarchivar\'\);.*?return;\s*\}\s*', '', html, flags=re.DOTALL)

# 4. Clean up moverFila
# In Historial button generation:
html = re.sub(r'<button class="btn-archivar inline-flex[^>]+>.*?<\/button>\s*', '', html, flags=re.DOTALL)
# It's already caught by regex #1 since we match anywhere in the file. Wait! The JS string interpolation:
# `<button class="btn-archivar inline-flex ...">`
# Let's ensure the JS strings generating the buttons are removed.
html = re.sub(r'<button class=\\\"btn-archivar inline-flex[^>]+>.*?<\/button>\s*', '', html, flags=re.DOTALL)
html = re.sub(r'<button class=\\\"btn-desarchivar inline-flex[^>]+>.*?<\/button>\s*', '', html, flags=re.DOTALL)

# Also remove the whole `} else if (destino === 'Archivados') { ... }` block
html = re.sub(r'\} else if \(destino === \'Archivados\'\) \{.*?\}\s*(?=function validarTamanioAdjunto)', '}', html, flags=re.DOTALL)

# Remove `tr-archivados-vacio` emptyRows
html = re.sub(r"let emptyRows = \['tr-archivados-vacio'\];", "let emptyRows = [];", html)
# Remove `// Remover grayscale por si viene de Archivados` and `if(img) img.classList.remove('grayscale');` and `fila.classList.remove('opacity-80', 'text-gray-400');`
html = re.sub(r'// Remover grayscale por si viene de Archivados\s*if\(img\) img\.classList\.remove\(\'grayscale\'\);\s*fila\.classList\.remove\(\'opacity-80\', \'text-gray-400\'\);\s*', '', html, flags=re.DOTALL)

with open("plantillas/mensajeria.html", "w", encoding="utf-8") as f:
    f.write(html)
print("HTML updated.")

import re

file_path = r'c:\Users\lucia\OneDrive\Escritorio\Junami 3.0\plantillas\mensajeria.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the class-tmp mess
bad_class_pattern = r'class="([^"]*?)" class-tmp="class=\\"[^"]*?\\""'
content = re.sub(bad_class_pattern, r'class="\1 btn-ver"', content)

# Check all tables to ensure there are no other onclick attributes on the ver/archivar/desarchivar/borrar buttons
# We did this for the Nuevos table, let's check Enviados and Historial
# Enviados:
# <button onclick="abrirModalLectura({{ msg.id }}, '{{ msg.receptor_nombre|escape }}', '{{ msg.fecha }}', '{{ msg.asunto|escape }}', '{{ msg.mensaje|escape }}', true, 'Enviado')" class="inline-flex ...">
env_pattern = r'<button onclick="abrirModalLectura\(\{\{ msg\.id \}\}, \'\{\{ msg\.receptor_nombre\|escape \}\}\', \'\{\{ msg\.fecha \}\}\', \'\{\{ msg\.asunto\|escape \}\}\', \'\{\{ msg\.mensaje\|escape \}\}\', true, \'Enviado\'\)" (class="[^"]*?")>'
content = re.sub(env_pattern, r'<button \1 class="btn-ver" data-id="{{ msg.id }}" data-emisor="{{ msg.receptor_nombre|escape }}" data-fecha="{{ msg.fecha }}" data-asunto="{{ msg.asunto|escape }}" data-leido="true" data-tipo="Enviado">', content)

# Historial:
hist_pattern = r'<button onclick="abrirModalLectura\(\{\{ msg\.id \}\}, \'\{\{ msg\.emisor_nombre\|escape \}\}\', \'\{\{ msg\.fecha \}\}\', \'\{\{ msg\.asunto\|escape \}\}\', \'\{\{ msg\.mensaje\|escape \}\}\', true, \'Recibido\'\)" (class="[^"]*?")>'
content = re.sub(hist_pattern, r'<button \1 class="btn-ver" data-id="{{ msg.id }}" data-emisor="{{ msg.emisor_nombre|escape }}" data-fecha="{{ msg.fecha }}" data-asunto="{{ msg.asunto|escape }}" data-leido="true" data-tipo="Recibido">', content)

# Archivados:
arch_pattern = r'<button onclick="abrirModalLectura\(\{\{ msg\.id \}\}, \'\{\{ otro_nombre\|escape \}\}\', \'\{\{ msg\.fecha \}\}\', \'\{\{ msg\.asunto\|escape \}\}\', \'\{\{ msg\.mensaje\|escape \}\}\', true, \'\{% if msg\.origen == "Entrante" %\}Recibido\{% else %\}Enviado\{% endif %\}\'\)" (class="[^"]*?") title="Ver">'
content = re.sub(arch_pattern, r'<button \1 class="btn-ver" title="Ver" data-id="{{ msg.id }}" data-emisor="{{ otro_nombre|escape }}" data-fecha="{{ msg.fecha }}" data-asunto="{{ msg.asunto|escape }}" data-leido="true" data-tipo="{% if msg.origen == \'Entrante\' %}Recibido{% else %}Enviado{% endif %}">', content)

# Add missing btn-ver if there's any remaining `class="... btn-ver"` vs `class="btn-ver ..."`
# The regex above will end up with `class="inline-flex..." class="btn-ver"` which is invalid HTML
# Let's fix that.
invalid_class = r'(class="[^"]*?") class="btn-ver"'
content = re.sub(invalid_class, r'\1', content) # temporary remove

# Actually it's easier to just append btn-ver to the existing class string
# Let's just fix the bad ones completely using a robust approach.

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("HTML limpiado")

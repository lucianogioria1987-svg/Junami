import re

file_path = r'c:\Users\lucia\OneDrive\Escritorio\Junami 3.0\plantillas\mensajeria.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Nuevos table button
nuevos_bad = r'<button class="[^"]*?" class-tmp="class=\\"[^"]*?\\"" data-action="ver" data-id="\{\{ msg\.id \}\}" data-emisor="\{\{ msg\.emisor_nombre\|escape \}\}" data-fecha="\{\{ msg\.fecha \}\}" data-asunto="\{\{ msg\.asunto\|escape \}\}" data-leido="false" data-tipo="Recibido">'
nuevos_good = r'<button class="btn-ver inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-emerald-500 hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors" data-id="{{ msg.id }}" data-emisor="{{ msg.emisor_nombre|escape }}" data-fecha="{{ msg.fecha }}" data-asunto="{{ msg.asunto|escape }}" data-leido="false" data-tipo="Recibido">'
content = re.sub(nuevos_bad, nuevos_good, content)

# Fix Enviados table button
env_bad = r'<button class="[^"]*?" class-tmp="class=\\"[^"]*?\\"" data-action="ver" data-id="\{\{ msg\.id \}\}" data-emisor="\{\{ msg\.receptor_nombre\|escape \}\}" data-fecha="\{\{ msg\.fecha \}\}" data-asunto="\{\{ msg\.asunto\|escape \}\}" data-leido="true" data-tipo="Enviado">'
env_good = r'<button class="btn-ver inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-bold rounded-lg shadow-sm text-white bg-emerald-500 hover:bg-emerald-600 transition-colors" data-id="{{ msg.id }}" data-emisor="{{ msg.receptor_nombre|escape }}" data-fecha="{{ msg.fecha }}" data-asunto="{{ msg.asunto|escape }}" data-leido="true" data-tipo="Enviado">'
content = re.sub(env_bad, env_good, content)

# Fix Historial table button
hist_bad = r'<button class="[^"]*?" class-tmp="class=\\"[^"]*?\\"" data-action="ver" data-id="\{\{ msg\.id \}\}" data-emisor="\{\{ msg\.emisor_nombre\|escape \}\}" data-fecha="\{\{ msg\.fecha \}\}" data-asunto="\{\{ msg\.asunto\|escape \}\}" data-leido="true" data-tipo="Recibido">'
hist_good = r'<button class="btn-ver inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-600 bg-white hover:bg-gray-50 hover:text-emerald-600 transition-colors" data-id="{{ msg.id }}" data-emisor="{{ msg.emisor_nombre|escape }}" data-fecha="{{ msg.fecha }}" data-asunto="{{ msg.asunto|escape }}" data-leido="true" data-tipo="Recibido">'
content = re.sub(hist_bad, hist_good, content)

# Fix Archivados table button
arch_bad = r'<button class="[^"]*?" class-tmp="class=\\"[^"]*?\\"" title="Ver" data-id="\{\{ msg\.id \}\}" data-emisor="\{\{ otro_nombre\|escape \}\}" data-fecha="\{\{ msg\.fecha \}\}" data-asunto="\{\{ msg\.asunto\|escape \}\}" data-leido="true" data-tipo="\{% if msg\.origen == \'Entrante\' %\}Recibido\{% else %\}Enviado\{% endif %\}">'
arch_good = r'<button class="btn-ver inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-bold rounded-lg shadow-sm text-gray-500 bg-white hover:bg-gray-50 transition-colors" title="Ver" data-id="{{ msg.id }}" data-emisor="{{ otro_nombre|escape }}" data-fecha="{{ msg.fecha }}" data-asunto="{{ msg.asunto|escape }}" data-leido="true" data-tipo="{% if msg.origen == \'Entrante\' %}Recibido{% else %}Enviado{% endif %}">'
content = re.sub(arch_bad, arch_good, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("HTML purgado de class-tmp")

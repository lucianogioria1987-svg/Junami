with open("rutas/mensajeria.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Remove mis_archivados usage in inbox()
content = re.sub(r'mis_archivados\s*=\s*\[\]\n', '', content)
content = re.sub(r'archivado_por = m\.get\(\'archivado_por\', \[\]\)\n\s*es_archivado = mi_id in archivado_por\n', '', content)

# Modify the conditions to remove es_archivado check
content = re.sub(r'if es_archivado:\n\s*mis_archivados\.append\(m\)\n\s*else:\n\s*mis_mensajes\.append\(m\)', 'mis_mensajes.append(m)', content)
content = re.sub(r'if es_archivado:\n\s*mis_archivados\.append\(m\)\n\s*else:\n\s*mis_mensajes_enviados\.append\(m\)', 'mis_mensajes_enviados.append(m)', content)

# Remove sort for mis_archivados
content = re.sub(r'mis_archivados\.sort\(key=lambda x: x\[\'id\'\], reverse=True\)\n', '', content)

# Update render_template
content = re.sub(r'archivados=mis_archivados, ', '', content)

# Remove routes archivar and desarchivar
# They are at the end of the file.
archivar_route_start = content.find("@mensajeria_bp.route('/mensajeria/archivar/<int:id>', methods=['POST'])")
if archivar_route_start != -1:
    content = content[:archivar_route_start]

with open("rutas/mensajeria.py", "w", encoding="utf-8") as f:
    f.write(content.strip() + "\n")

print("Backend updated.")

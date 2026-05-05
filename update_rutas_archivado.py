import re

file_path = r'c:\Users\lucia\OneDrive\Escritorio\Junami 3.0\rutas\mensajeria.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update inbox()
old_inbox_pattern = r'# Filtrar mis mensajes recibidos.*?return render_template\(\'mensajeria\.html\', mensajes=mis_mensajes, mensajes_enviados=mis_mensajes_enviados, profesional=session\[\'usuario_actual\'\]\)'

new_inbox = """mis_mensajes = []
    mis_mensajes_enviados = []
    mis_archivados = []

    for m in mensajes:
        archivado_por = m.get('archivado_por', [])
        es_archivado = mi_id in archivado_por
        m['tiene_adjunto'] = 'adjunto' in m or any('adjunto' in r for r in m.get('respuestas', []))
        
        if m['ultimo_receptor_id'] == mi_id:
            emisor = mapa_profesionales.get(m['ultimo_emisor_id'], {})
            m['emisor_nombre'] = emisor.get('nombre', 'Usuario Desconocido')
            m['emisor_iniciales'] = emisor.get('iniciales', '??')
            m['emisor_foto'] = emisor.get('foto')
            m['origen'] = 'Entrante'
            if es_archivado:
                mis_archivados.append(m)
            else:
                mis_mensajes.append(m)
        elif m['ultimo_emisor_id'] == mi_id:
            receptor = mapa_profesionales.get(m['ultimo_receptor_id'], {})
            m['receptor_nombre'] = receptor.get('nombre', 'Usuario Desconocido')
            m['receptor_iniciales'] = receptor.get('iniciales', '??')
            m['receptor_foto'] = receptor.get('foto')
            m['origen'] = 'Saliente'
            if es_archivado:
                mis_archivados.append(m)
            else:
                mis_mensajes_enviados.append(m)

    mis_mensajes.sort(key=lambda x: x['id'], reverse=True)
    mis_mensajes_enviados.sort(key=lambda x: x['id'], reverse=True)
    mis_archivados.sort(key=lambda x: x['id'], reverse=True)
    
    return render_template('mensajeria.html', mensajes=mis_mensajes, mensajes_enviados=mis_mensajes_enviados, archivados=mis_archivados, profesional=session['usuario_actual'])"""

content = re.sub(old_inbox_pattern, new_inbox, content, flags=re.DOTALL)

# 2. Add archivar and desarchivar routes at the end
rutas_archivado = """
@mensajeria_bp.route('/mensajeria/archivar/<int:id>', methods=['POST'])
def archivar(id):
    if 'usuario_actual' not in session:
        return jsonify({"success": False, "error": "No autenticado"}), 401
        
    mensajes = cargar_datos('mensajeria.json')
    mi_id = session['usuario_actual']['id']
    
    for m in mensajes:
        if m['id'] == id:
            if 'archivado_por' not in m:
                m['archivado_por'] = []
            if mi_id not in m['archivado_por']:
                m['archivado_por'].append(mi_id)
            guardar_mensajes(mensajes)
            return jsonify({"success": True})
            
    return jsonify({"success": False, "error": "Mensaje no encontrado"}), 404

@mensajeria_bp.route('/mensajeria/desarchivar/<int:id>', methods=['POST'])
def desarchivar(id):
    if 'usuario_actual' not in session:
        return jsonify({"success": False, "error": "No autenticado"}), 401
        
    mensajes = cargar_datos('mensajeria.json')
    mi_id = session['usuario_actual']['id']
    
    for m in mensajes:
        if m['id'] == id:
            if 'archivado_por' in m and mi_id in m['archivado_por']:
                m['archivado_por'].remove(mi_id)
            guardar_mensajes(mensajes)
            return jsonify({"success": True})
            
    return jsonify({"success": False, "error": "Mensaje no encontrado"}), 404
"""
content += rutas_archivado

# Also, when answering (responder), if the message was archived, should we unarchive it?
# WhatsApp typically unarchives a thread if you get a new message in it!
# For the receiver, if it was archived, it should unarchive. 
# "saltará como Nuevo" -> If it's Nuevo, it shouldn't be in Archivados.
responder_pattern = r'm\[\'leido\'\] = False'
responder_repl = """m['leido'] = False
            # Desarchivar para el receptor (así le salta en Nuevos)
            # El receptor de esta respuesta es el emisor de la original o el que no es mi_id
            if 'archivado_por' in m:
                # Quitamos de archivados a todos excepto a mi_id (yo lo dejé en enviados, o capaz tmb se desarchiva para mí)
                # Mejor lo vaciamos, así revive para ambos.
                m['archivado_por'] = []"""
content = content.replace(responder_pattern, responder_repl)

# Remove the 'tiene_adjunto' loop from inbox that we added in the previous script, since we moved it into the main loop
old_tiene_adjunto_loop = r'    for m in mensajes:\n        m\[\'tiene_adjunto\'\] = \'adjunto\' in m or any\(\'adjunto\' in r for r in m\.get\(\'respuestas\', \[\]\)\)\s*'
content = re.sub(old_tiene_adjunto_loop, '', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("rutas/mensajeria.py actualizada para soportar archivado personal.")

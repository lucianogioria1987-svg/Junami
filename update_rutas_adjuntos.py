import re

file_path = r'c:\Users\lucia\OneDrive\Escritorio\Junami 3.0\rutas\mensajeria.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add imports
if 'import time' not in content:
    content = content.replace('import os', 'import os\nimport time\nfrom werkzeug.utils import secure_filename')

# 2. Add config and allowed extensions checking function
config_str = """
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'jpg', 'png'}
UPLOAD_FOLDER_MENSAJERIA = os.path.join('static', 'adjuntos_mensajeria')
os.makedirs(UPLOAD_FOLDER_MENSAJERIA, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

"""
if 'ALLOWED_EXTENSIONS' not in content:
    content = content.replace('mensajeria_bp = Blueprint(\'mensajeria_bp\', __name__)', 'mensajeria_bp = Blueprint(\'mensajeria_bp\', __name__)\n' + config_str)

# 3. Update enviar()
enviar_pattern = r'def enviar\(\):(.*?)mensajes\.append\(nuevo_mensaje\)'
enviar_match = re.search(enviar_pattern, content, re.DOTALL)
if enviar_match:
    enviar_body = enviar_match.group(1)
    
    # We replace the new_message creation to handle the file
    nuevo_mensaje_str = """
    adjunto_info = None
    if 'adjunto' in request.files:
        file = request.files['adjunto']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{int(time.time())}_{filename}"
            file.save(os.path.join(UPLOAD_FOLDER_MENSAJERIA, unique_filename))
            adjunto_info = {"nombre_original": filename, "ruta": f"adjuntos_mensajeria/{unique_filename}"}
    
    nuevo_mensaje = {
        "id": nuevo_id,
        "emisor_id": emisor_id,
        "receptor_id": receptor_id,
        "fecha": datetime.now().strftime('%d/%m/%Y %H:%M'),
        "asunto": asunto,
        "mensaje": texto_mensaje,
        "leido": False,
        "respuestas": []
    }
    if adjunto_info:
        nuevo_mensaje['adjunto'] = adjunto_info
    
    mensajes.append(nuevo_mensaje)"""
    
    # Careful substitution inside enviar
    content = re.sub(r'    nuevo_mensaje = \{.*?\n    \}\n    \n    mensajes\.append\(nuevo_mensaje\)', nuevo_mensaje_str, content, flags=re.DOTALL)

# 4. Update responder()
responder_pattern = r'def responder\(id\):.*?return jsonify\(\{"success": False, "error": "Mensaje no encontrado"\}\), 404'
new_responder = """def responder(id):
    if 'usuario_actual' not in session:
        return jsonify({"success": False, "error": "No autenticado"}), 401
        
    mensajes = cargar_datos('mensajeria.json')
    mi_id = session['usuario_actual']['id']
    
    # Leer texto
    texto_respuesta = request.form.get('respuesta')
    if not texto_respuesta and request.is_json:
        texto_respuesta = request.json.get('respuesta')
        
    adjunto_info = None
    if 'adjunto' in request.files:
        file = request.files['adjunto']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{int(time.time())}_{filename}"
            file.save(os.path.join(UPLOAD_FOLDER_MENSAJERIA, unique_filename))
            adjunto_info = {"nombre_original": filename, "ruta": f"adjuntos_mensajeria/{unique_filename}"}
    
    for m in mensajes:
        if m['id'] == id:
            if 'respuestas' not in m:
                m['respuestas'] = []
                
            nueva_resp = {
                "emisor_id": mi_id,
                "texto": texto_respuesta,
                "fecha": datetime.now().strftime('%d/%m/%Y %H:%M')
            }
            if adjunto_info:
                nueva_resp['adjunto'] = adjunto_info
                
            m['respuestas'].append(nueva_resp)
            m['leido'] = False
            
            guardar_mensajes(mensajes)
            
            # Devolver adjunto info para UI si se guardó
            return jsonify({"success": True, "adjunto": adjunto_info})
            
    return jsonify({"success": False, "error": "Mensaje no encontrado"}), 404"""

content = re.sub(responder_pattern, new_responder, content, flags=re.DOTALL)

# 5. Update hilo()
hilo_pattern = r'hilo_completo\.append\(\{(.*?)\}\)'
# We want to extract adjunto from original message and answers
hilo_orig_repl = r'''hilo_completo.append({
                "emisor_id": m['emisor_id'],
                "emisor_nombre": emisor_orig.get('nombre', 'Usuario Desconocido'),
                "fecha": m['fecha'],
                "texto": m['mensaje'],
                "adjunto": m.get('adjunto')
            })'''
content = content.replace('''hilo_completo.append({
                "emisor_id": m['emisor_id'],
                "emisor_nombre": emisor_orig.get('nombre', 'Usuario Desconocido'),
                "fecha": m['fecha'],
                "texto": m['mensaje']
            })''', hilo_orig_repl)

hilo_resp_repl = r'''hilo_completo.append({
                    "emisor_id": r['emisor_id'],
                    "emisor_nombre": emisor_resp.get('nombre', 'Usuario Desconocido'),
                    "fecha": r['fecha'],
                    "texto": r['texto'],
                    "adjunto": r.get('adjunto')
                })'''
content = content.replace('''hilo_completo.append({
                    "emisor_id": r['emisor_id'],
                    "emisor_nombre": emisor_resp.get('nombre', 'Usuario Desconocido'),
                    "fecha": r['fecha'],
                    "texto": r['texto']
                })''', hilo_resp_repl)


# 6. Update inbox() to mark messages with attachment
inbox_pattern = r'm\[\'receptor_foto\'\] = receptor\.get\(\'foto\'\)'
inbox_repl = r'''m['receptor_foto'] = receptor.get('foto')
        
    for m in mensajes:
        m['tiene_adjunto'] = 'adjunto' in m or any('adjunto' in r for r in m.get('respuestas', []))'''
if 'm[\'tiene_adjunto\']' not in content:
    content = content.replace("m['receptor_foto'] = receptor.get('foto')", inbox_repl)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("rutas/mensajeria.py actualizadas para soportar adjuntos.")

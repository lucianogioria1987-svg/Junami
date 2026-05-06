from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
import json
import os
import time
import re 
import html
from werkzeug.utils import secure_filename
from datetime import datetime
from utils import cargar_datos

mensajeria_bp = Blueprint('mensajeria_bp', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'jpg', 'png'}
UPLOAD_FOLDER_MENSAJERIA = os.path.join('static', 'adjuntos_mensajeria')
os.makedirs(UPLOAD_FOLDER_MENSAJERIA, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def procesar_menciones(texto, tag_a_paciente):
    menciones_encontradas = {}
    if not texto: return "", []
    texto_esc = html.escape(str(texto))
    
    def reemplazar(match):
        nombre = match.group(1)
        id_pac = match.group(2)
        menciones_encontradas[id_pac] = nombre
        return f'<a href="javascript:void(0)" onclick="cargarVistaPaciente(\'{id_pac}\')" class="text-blue-600 font-bold hover:underline"><i class="fas fa-user-medical mr-1"></i> @{nombre}</a>'

    texto_procesado = re.sub(r'@([^#]+)#([a-zA-Z0-9_-]+)', reemplazar, texto_esc)
    return texto_procesado, list(menciones_encontradas.values())

def guardar_mensajes(mensajes):
    ruta = os.path.join('datos', 'mensajeria.json')
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(mensajes, f, indent=4, ensure_ascii=False)

@mensajeria_bp.route('/mensajeria')
def inbox():
    if 'usuario_actual' not in session:
        return redirect(url_for('dashboard_loguin_bp.login'))
    
    mi_id = session['usuario_actual']['id']
    mensajes = cargar_datos('mensajeria.json')
    profesionales = cargar_datos('profesionales.json')
    pacientes = cargar_datos('pacientes.json')
    
    tag_a_paciente = { ("@" + "".join(p.get('nombre', '').split())).lower(): p for p in pacientes if p.get('nombre') }
    mapa_profesionales = {p['id']: p for p in profesionales}
    
    mis_mensajes = []
    mis_mensajes_enviados = []
    
    for m in mensajes:
        resp = m.get('respuestas', [])
        ultimo_emisor_id = resp[-1]['emisor_id'] if resp else m['emisor_id']
        ultimo_receptor_id = m['receptor_id'] if ultimo_emisor_id == m['emisor_id'] else m['emisor_id']
        
        m['tiene_adjunto'] = 'adjunto' in m or any('adjunto' in r for r in resp)
        _, m_menc = procesar_menciones(m['mensaje'], tag_a_paciente)
        t_menc = list(m_menc)
        for r in resp:
            _, r_menc = procesar_menciones(r.get('texto', ''), tag_a_paciente)
            t_menc.extend(r_menc)
        m['menciones'] = list(set(t_menc))
        
        if ultimo_receptor_id == mi_id:
            emisor = mapa_profesionales.get(ultimo_emisor_id, {})
            m['emisor_nombre'] = emisor.get('nombre', 'Usuario')
            m['emisor_iniciales'] = emisor.get('iniciales', '??')
            m['emisor_foto'] = emisor.get('foto')
            mis_mensajes.append(m)
        elif ultimo_emisor_id == mi_id:
            receptor = mapa_profesionales.get(ultimo_receptor_id, {})
            m['receptor_nombre'] = receptor.get('nombre', 'Usuario')
            m['receptor_iniciales'] = receptor.get('iniciales', '??')
            m['receptor_foto'] = receptor.get('foto')
            mis_mensajes_enviados.append(m)

    mis_mensajes.sort(key=lambda x: x['id'], reverse=True)
    mis_mensajes_enviados.sort(key=lambda x: x['id'], reverse=True)
    return render_template('mensajeria.html', mensajes=mis_mensajes, mensajes_enviados=mis_mensajes_enviados, profesional=session['usuario_actual'])

@mensajeria_bp.route('/mensajeria/enviar', methods=['POST'])
def enviar():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    mensajes = cargar_datos('mensajeria.json')
    mi_id = session['usuario_actual']['id']
    
    adjunto_info = None
    if 'adjunto' in request.files:
        file = request.files['adjunto']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{int(time.time())}_{filename}"
            file.save(os.path.join(UPLOAD_FOLDER_MENSAJERIA, unique_filename))
            adjunto_info = {"nombre_original": filename, "ruta": f"adjuntos_mensajeria/{unique_filename}"}

    nuevo_id = max([m['id'] for m in mensajes], default=0) + 1
    nuevo_mensaje = {
        "id": nuevo_id,
        "emisor_id": mi_id,
        "receptor_id": int(request.form.get('receptor_id')),
        "asunto": request.form.get('asunto'),
        "mensaje": request.form.get('mensaje'),
        "fecha": datetime.now().strftime('%d/%m/%Y %H:%M'),
        "leido": False,
        "respuestas": []
    }
    if adjunto_info: nuevo_mensaje['adjunto'] = adjunto_info
    
    mensajes.append(nuevo_mensaje)
    guardar_mensajes(mensajes)
    flash("Mensaje enviado con éxito")
    return redirect(url_for('mensajeria_bp.inbox'))

@mensajeria_bp.route('/mensajeria/leer/<int:id>', methods=['POST'])
def leer(id):
    mensajes = cargar_datos('mensajeria.json')
    for m in mensajes:
        if m['id'] == id:
            m['leido'] = True
            break
    guardar_mensajes(mensajes)
    return jsonify({"success": True})

@mensajeria_bp.route('/mensajeria/borrar/<int:id>', methods=['POST'])
def borrar(id):
    mensajes = cargar_datos('mensajeria.json')
    mensajes = [m for m in mensajes if m['id'] != id]
    guardar_mensajes(mensajes)
    return jsonify({"success": True})

@mensajeria_bp.route('/mensajeria/hilo/<int:id>')
def obtener_hilo(id):
    mensajes = cargar_datos('mensajeria.json')
    profesionales = cargar_datos('profesionales.json')
    pacientes = cargar_datos('pacientes.json')
    mapa_profesionales = {p['id']: p for p in profesionales}
    tag_a_paciente = { ("@" + "".join(p.get('nombre', '').split())).lower(): p for p in pacientes if p.get('nombre') }

    for m in mensajes:
        if m['id'] == id:
            hilo = []
            # Mensaje original
            txt_m, _ = procesar_menciones(m['mensaje'], tag_a_paciente)
            hilo.append({
                "emisor_id": m['emisor_id'],
                "emisor_nombre": mapa_profesionales.get(m['emisor_id'], {}).get('nombre', 'Usuario'),
                "texto": txt_m,
                "fecha": m['fecha'],
                "adjunto": m.get('adjunto')
            })
            # Respuestas
            for r in m.get('respuestas', []):
                txt_r, _ = procesar_menciones(r['texto'], tag_a_paciente)
                hilo.append({
                    "emisor_id": r['emisor_id'],
                    "emisor_nombre": mapa_profesionales.get(r['emisor_id'], {}).get('nombre', 'Usuario'),
                    "texto": txt_r,
                    "fecha": r['fecha'],
                    "adjunto": r.get('adjunto')
                })
            return jsonify({"success": True, "hilo": hilo})
    return jsonify({"success": False})

@mensajeria_bp.route('/mensajeria/responder/<int:id>', methods=['POST'])
def responder(id):
    if 'usuario_actual' not in session: return jsonify({"success": False})
    mensajes = cargar_datos('mensajeria.json')
    mi_id = session['usuario_actual']['id']
    texto = request.json.get('respuesta') if request.is_json else request.form.get('respuesta')

    for m in mensajes:
        if m['id'] == id:
            m.setdefault('respuestas', []).append({
                "emisor_id": mi_id,
                "texto": texto,
                "fecha": datetime.now().strftime('%d/%m/%Y %H:%M')
            })
            m['leido'] = False
            guardar_mensajes(mensajes)
            return jsonify({"success": True})
    return jsonify({"success": False})
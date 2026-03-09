from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, current_app
import json
import os
import io
import zipfile
from werkzeug.utils import secure_filename
from datetime import datetime
from utils import cargar_datos

configuracion_bp = Blueprint('configuracion_bp', __name__)

@configuracion_bp.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    
    # Restricción de Auxiliar para Configuración
    profesional = session['usuario_actual']
    if profesional.get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard_personal_bp.dashboard2'))
    
    profesionales = cargar_datos('profesionales.json')
    parametros = cargar_datos('parametros.json') or {"obras_sociales": ["Particular"]}
    
    if request.method == 'POST':
        if request.form.get('action') == 'update_profile':
            for p in profesionales:
                if p['id'] == session['usuario_actual']['id']:
                    p.update({k: request.form[k] for k in ['nombre', 'usuario', 'contrasena']})
                    p['iniciales'] = request.form['iniciales'].upper()
                    if 'foto_perfil' in request.files and request.files['foto_perfil'].filename != '':
                        nom = secure_filename(f"profesional_{p['id']}.{request.files['foto_perfil'].filename.split('.')[-1]}")
                        request.files['foto_perfil'].save(os.path.join(current_app.config['UPLOAD_FOLDER'], nom))
                        p['foto'] = nom
                    session['usuario_actual'] = p
                    break
            with open(os.path.join('datos', 'profesionales.json'), 'w', encoding='utf-8') as f: json.dump(profesionales, f, indent=4, ensure_ascii=False)
        elif request.form.get('action') == 'add_os':
            parametros['obras_sociales'].append(request.form['nueva_os'])
            with open(os.path.join('datos', 'parametros.json'), 'w', encoding='utf-8') as f: json.dump(parametros, f, indent=4, ensure_ascii=False)
        elif request.form.get('action') == 'delete_os':
            parametros['obras_sociales'].remove(request.form['os_name'])
            with open(os.path.join('datos', 'parametros.json'), 'w', encoding='utf-8') as f: json.dump(parametros, f, indent=4, ensure_ascii=False)
    return render_template('configuracion.html', profesional=session['usuario_actual'], lista_profesionales=profesionales, parametros=parametros)

@configuracion_bp.route('/configuracion/nuevo_profesional', methods=['POST'])
def nuevo_prof_desde_config():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    lista = cargar_datos('profesionales.json')
    nid = 1 if not lista else lista[-1]['id'] + 1
    foto = None
    if 'foto_perfil' in request.files and request.files['foto_perfil'].filename != '':
        foto = secure_filename(f"profesional_{nid}.{request.files['foto_perfil'].filename.split('.')[-1]}")
        request.files['foto_perfil'].save(os.path.join(current_app.config['UPLOAD_FOLDER'], foto))
    
    lista.append({
        "id": nid, "nombre": request.form['nombre'], "usuario": request.form['usuario'], "contrasena": request.form['contrasena'], "rol": request.form['rol'],
        "iniciales": request.form['iniciales'].upper(), "foto": foto, "jerarquia": request.form.get('jerarquia', 'Titular'), "supervisor": request.form.get('supervisor'),
        "dni": request.form.get('dni',''), "edad": request.form.get('edad',''), "domicilio": request.form.get('domicilio',''), "universidad": request.form.get('universidad',''), "telefono": request.form.get('telefono',''), "email": request.form.get('email',''), "matricula": request.form.get('matricula','')
    })
    with open(os.path.join('datos', 'profesionales.json'), 'w', encoding='utf-8') as f: json.dump(lista, f, indent=4, ensure_ascii=False)
    return redirect(url_for('configuracion'))

@configuracion_bp.route('/configuracion/backup')
def descargar_backup():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for folder in ['datos', 'static/uploads']:
            if os.path.exists(folder):
                for root, dirs, files in os.walk(folder):
                    for file in files: zip_file.write(os.path.join(root, file), os.path.join(folder, file))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Backup_Junami_{datetime.now().strftime('%d-%m-%Y')}.zip", mimetype='application/zip')

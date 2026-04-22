from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from utils import cargar_datos, procesar_fecha

admisiones_bp = Blueprint('admisiones_bp', __name__)

@admisiones_bp.route('/admisiones', methods=['GET', 'POST'])
def admisiones():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    profesional_actual = session['usuario_actual']
    if profesional_actual.get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard_personal_bp.dashboard2'))

    lista_admisiones = cargar_datos('admisiones.json')
    lista_profesionales = cargar_datos('profesionales.json')
    parametros = cargar_datos('parametros.json') or {"obras_sociales": ["Particular", "OSDE"]}

    if request.method == 'POST':
        nuevo_id = 1 if not lista_admisiones else lista_admisiones[-1]['id'] + 1
        
        lista_diagnosticos = []
        if 'archivo_diagnostico' in request.files:
            archivos = request.files.getlist('archivo_diagnostico')
            for f in archivos:
                if f.filename != '':
                    nombre = secure_filename(f"diag_{nuevo_id}_{f.filename}")
                    f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], nombre))
                    lista_diagnosticos.append(nombre)
        
        lista_informes_previos = []
        if 'archivo_informes_previos' in request.files:
            archivos = request.files.getlist('archivo_informes_previos')
            for f in archivos:
                if f.filename != '':
                    nombre = secure_filename(f"previo_{nuevo_id}_{f.filename}")
                    f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], nombre))
                    lista_informes_previos.append(nombre)
        
        lista_informes_escolares = []
        if 'archivo_informe_escolar' in request.files:
            archivos = request.files.getlist('archivo_informe_escolar')
            for f in archivos:
                if f.filename != '':
                    nombre = secure_filename(f"escolar_{nuevo_id}_{f.filename}")
                    f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], nombre))
                    lista_informes_escolares.append(nombre)

        nueva_admision = {
            "id": nuevo_id, "estado": "Recibidos", 
            "fecha_solicitud": datetime.now().strftime("%d/%m/%Y"),
            "fecha_entrevista": procesar_fecha(request.form.get('fecha_entrevista', '')),
            "fecha_nacimiento": procesar_fecha(request.form.get('fecha_nacimiento', '')),
            "hora_entrevista": request.form.get('hora_entrevista', ''),
            "nombre": request.form['nombre'], 
            "dni": request.form.get('dni', ''), 
            "edad": request.form['edad'], 
            "domicilio": request.form.get('domicilio', ''), 
            "obra_social": request.form.get('obra_social', 'Particular'),
            
            "nombre_madre": request.form.get('nombre_madre', ''), 
            "tel_madre": request.form.get('tel_madre', ''), 
            "domicilio_madre": request.form.get('domicilio_madre', ''), 
            "nombre_padre": request.form.get('nombre_padre', ''), 
            "tel_padre": request.form.get('tel_padre', ''), 
            "domicilio_padre": request.form.get('domicilio_padre', ''), 
            "estado_padres": request.form.get('estado_padres', 'Conviven'),
            "vive_con": request.form.get('vive_con', ''),
            "hermanos": request.form.get('hermanos', ''),
            "email": request.form.get('email', ''),

            "escuela_nombre": request.form.get('escuela_nombre', ''), 
            "escuela_grado": request.form.get('escuela_grado', ''), 
            "escuela_turno": request.form.get('escuela_turno', ''),
            "escuela_apoyo_nombre": request.form.get('escuela_apoyo_nombre', ''), 
            "informe_escolar": lista_informes_escolares,
            
            "tiene_terapias_previas": request.form.get('tiene_terapias_previas', 'No'), 
            "terapias_previas_desc": request.form.get('terapias_previas_desc', ''), 
            "archivo_informes_previos": lista_informes_previos, 

            "motivo_consulta": request.form.get('motivo_consulta', ''), 
            "medico_cabecera": request.form.get('medico_cabecera', ''), 
            "neurologo": request.form.get('neurologo', ''),
            "informe_diagnostico": lista_diagnosticos, 

            "profesional_admision": request.form['profesional_admision'], 
            "prioridad": request.form.get('prioridad', 'Media'), 
            "disponibilidad_preferencia": request.form.get('disponibilidad_preferencia', ''),
            "equipo_sugerido": [], "informe_derivacion": None, "informe_entrevista": None
        }
        lista_admisiones.append(nueva_admision)
        with open(os.path.join('datos', 'admisiones.json'), 'w', encoding='utf-8') as f: json.dump(lista_admisiones, f, indent=4, ensure_ascii=False)
        return redirect(url_for('admisiones_bp.admisiones'))
    
    lista_admisiones.sort(key=lambda x: x['id'], reverse=True)
    return render_template('admisiones.html', profesional=profesional_actual, candidatos=lista_admisiones, profesionales=lista_profesionales, obras_sociales=parametros['obras_sociales'])

@admisiones_bp.route('/admision/<int:id>', methods=['GET', 'POST'])
def perfil_admision(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    admisiones = cargar_datos('admisiones.json')
    candidato = next((a for a in admisiones if a['id'] == id), None)
    if not candidato: return redirect(url_for('admisiones_bp.admisiones'))
    
    if request.method == 'POST':
        if 'nombre' in request.form:
            campos = ['nombre','dni','edad','domicilio','obra_social',
                      'nombre_padre','tel_padre','domicilio_padre',
                      'nombre_madre','tel_madre','domicilio_madre',
                      'estado_padres','vive_con','hermanos',
                      'email','escuela_nombre','escuela_grado','escuela_turno',
                      'escuela_apoyo_nombre',
                      'tiene_terapias_previas', 'terapias_previas_desc',
                      'motivo_consulta','medico_cabecera','neurologo',
                      'profesional_admision','prioridad','disponibilidad_preferencia','hora_entrevista']
            
            for c in campos:
                if c in request.form: candidato[c] = request.form[c]
                
            candidato['fecha_entrevista'] = procesar_fecha(request.form.get('fecha_entrevista', ''))
            candidato['fecha_nacimiento'] = procesar_fecha(request.form.get('fecha_nacimiento', ''))
            
            def procesar_archivos_multiples(campo_form, campo_json, prefijo):
                if campo_form in request.files:
                    archivos = request.files.getlist(campo_form)
                    if campo_json not in candidato or not isinstance(candidato[campo_json], list):
                        candidato[campo_json] = [] if not isinstance(candidato.get(campo_json), str) else [candidato[campo_json]]
                    
                    for f in archivos:
                        if f.filename != '':
                            nom = secure_filename(f"{prefijo}_{id}_{f.filename}")
                            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], nom))
                            candidato[campo_json].append(nom)

            procesar_archivos_multiples('archivo_diagnostico', 'informe_diagnostico', 'diag')
            procesar_archivos_multiples('archivo_informes_previos', 'archivo_informes_previos', 'previo')
            procesar_archivos_multiples('archivo_informe_escolar', 'informe_escolar', 'escolar')
            
            if 'archivo_derivacion' in request.files and request.files['archivo_derivacion'].filename != '':
                nom = secure_filename(f"derivacion_{id}_{request.files['archivo_derivacion'].filename}")
                request.files['archivo_derivacion'].save(os.path.join(current_app.config['UPLOAD_FOLDER'], nom))
                candidato['informe_derivacion'] = nom

        if 'archivo_entrevista' in request.files and request.files['archivo_entrevista'].filename != '':
            nom = secure_filename(f"entrevista_{id}_{request.files['archivo_entrevista'].filename}")
            request.files['archivo_entrevista'].save(os.path.join(current_app.config['UPLOAD_FOLDER'], nom))
            candidato['informe_entrevista'] = nom

        with open(os.path.join('datos', 'admisiones.json'), 'w', encoding='utf-8') as f: 
            json.dump(admisiones, f, indent=4, ensure_ascii=False)
            
        return redirect(url_for('admisiones_bp.admisiones'))

    return render_template('ficha_admision.html', candidato=candidato)

@admisiones_bp.route('/admision/alta/<int:id>')
def alta_admision(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    admisiones = cargar_datos('admisiones.json')
    pacientes = [p for p in cargar_datos('pacientes.json') if p.get('activo', True)]
    candidato = next((a for a in admisiones if a['id'] == id), None)
    if not candidato: return redirect(url_for('admisiones_bp.admisiones'))
    
    nuevo_id_pac = 1 if not pacientes else max(p['id'] for p in pacientes) + 1
    
    nuevo_paciente = {
        "id": nuevo_id_pac, 
        "activo": True,
        "nombre": candidato.get('nombre'), 
        "dni": candidato.get('dni'), 
        "fecha_nacimiento": candidato.get('fecha_nacimiento'),
        "edad": candidato.get('edad'), 
        "domicilio": candidato.get('domicilio'), 
        "obra_social": candidato.get('obra_social'),
        "nombre_madre": candidato.get('nombre_madre'), 
        "tel_madre": candidato.get('tel_madre'),
        "domicilio_madre": candidato.get('domicilio_madre'),
        "nombre_padre": candidato.get('nombre_padre'), 
        "tel_padre": candidato.get('tel_padre'),
        "domicilio_padre": candidato.get('domicilio_padre'),
        "estado_padres": candidato.get('estado_padres'),
        "vive_con": candidato.get('vive_con'),
        "hermanos": candidato.get('hermanos'),
        "email": candidato.get('email'),
        "escuela_nombre": candidato.get('escuela_nombre'), 
        "escuela_grado": candidato.get('escuela_grado'), 
        "escuela_turno": candidato.get('escuela_turno'),
        "escuela_apoyo_nombre": candidato.get('escuela_apoyo_nombre'),
        "diagnostico": candidato.get('motivo_consulta'), 
        "medico_cabecera": candidato.get('medico_cabecera'), 
        "neurologo": candidato.get('neurologo'),
        "tiene_terapias_previas": candidato.get('tiene_terapias_previas'),
        "terapias_previas_desc": candidato.get('terapias_previas_desc'),
        "informe_diagnostico": candidato.get('informe_diagnostico', []),
        "archivo_informes_previos": candidato.get('archivo_informes_previos', []),
        "informe_escolar": candidato.get('informe_escolar', []),
        "informe_derivacion": candidato.get('informe_derivacion'),
        "disponibilidad_registro": candidato.get('disponibilidad_preferencia'),
        "profesionales": [], 
        "plan_anual": "", 
        "objetivos_mensuales": "", 
        "sugerencias_hogar": "", 
        "archivos_adjuntos": [], 
        "foto": None,
        "informe": candidato.get('informe_derivacion') 
    }
    
    pacientes.append(nuevo_paciente)
    with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f: json.dump(pacientes, f, indent=4, ensure_ascii=False)
    
    candidato['estado'] = 'Procesada'
    with open(os.path.join('datos', 'admisiones.json'), 'w', encoding='utf-8') as f: json.dump(admisiones, f, indent=4, ensure_ascii=False)
        
    return redirect(url_for('admisiones_bp.admisiones'))

@admisiones_bp.route('/admision/borrar/<int:id>')
def borrar_admision(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    admisiones = cargar_datos('admisiones.json')
    admisiones = [a for a in admisiones if a['id'] != id]
    with open(os.path.join('datos', 'admisiones.json'), 'w', encoding='utf-8') as f: json.dump(admisiones, f, indent=4, ensure_ascii=False)
    return redirect(url_for('admisiones_bp.admisiones'))

@admisiones_bp.route('/admision/imprimir/<int:id>')
def imprimir_admision(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    admisiones = cargar_datos('admisiones.json')
    candidato = next((a for a in admisiones if a['id'] == id), None)
    if not candidato: return "Admisión no encontrada"
    return render_template('imprimir_admision.html', adm=candidato)

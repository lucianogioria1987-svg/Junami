from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from utils import cargar_datos, obtener_mapa_fotos_pacientes, obtener_mapa_fotos_profesionales, procesar_fecha

pacientes_bp = Blueprint('pacientes_bp', __name__)

@pacientes_bp.route('/pacientes')
def pacientes():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    profesional = session['usuario_actual']
    if profesional.get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard_personal_bp.dashboard2'))

    lista_pacientes = cargar_datos('pacientes.json')
    lista_sesiones = cargar_datos('sesiones.json')
    lista_profesionales = cargar_datos('profesionales.json')
    
    for paciente in lista_pacientes:
        agendas = [s for s in lista_sesiones if s['id_paciente'] == paciente['id']]
        if agendas:
            txts = []
            for ag in agendas: 
                dias = ", ".join(ag['dias'])
                txts.append(f"{dias} {ag['hora']}hs ({ag['profesional_especialidad']})")
            paciente['info_agenda'] = " | ".join(txts)
        else: 
            paciente['info_agenda'] = "Sin asignar"
            
    return render_template('pacientes.html', profesional=profesional, pacientes=lista_pacientes, profesionales_disponibles=lista_profesionales)

@pacientes_bp.route('/paciente/<int:id>')
def perfil_paciente(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    profesional = session['usuario_actual']
    
    lista_pacientes = cargar_datos('pacientes.json')
    paciente = next((p for p in lista_pacientes if p['id'] == id), None)
    if not paciente: return redirect(url_for('dashboard_personal_bp.dashboard2'))

    if profesional.get('jerarquia') == 'Auxiliar':
        if profesional['nombre'] not in paciente.get('profesionales', []):
            return redirect(url_for('dashboard_personal_bp.dashboard2'))

    historias = cargar_datos('historias.json')
    profesionales = cargar_datos('profesionales.json')
    sesiones = cargar_datos('sesiones.json')
    
    historial = [h for h in historias if h['id_paciente'] == id]
    historial.reverse()
    mapa_fotos_prof = obtener_mapa_fotos_profesionales(profesionales)
    for h in historial: h['foto_profesional'] = mapa_fotos_prof.get(h['profesional'])
    
    equipo = [p for p in profesionales if 'profesionales' in paciente and p['nombre'] in paciente['profesionales']]
    turnos_paciente = [s for s in sesiones if s['id_paciente'] == id]
    turnos_paciente.sort(key=lambda x: (x['dias'][0], x['hora']))
    
    return render_template('ficha_paciente.html', 
                           profesional=profesional, 
                           paciente=paciente, 
                           historial=historial, 
                           equipo=equipo, 
                           turnos=turnos_paciente, 
                           profesionales=profesionales)

@pacientes_bp.route('/paciente/editar/<int:id>', methods=['GET', 'POST'])
def editar_paciente(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    lista_pacientes = cargar_datos('pacientes.json')
    profesionales = cargar_datos('profesionales.json')
    parametros = cargar_datos('parametros.json') or {"obras_sociales": ["Particular"]}

    paciente_encontrado = next((p for p in lista_pacientes if p['id'] == id), None)
    if not paciente_encontrado: return redirect(url_for('pacientes_bp.pacientes'))

    if request.method == 'GET':
        return render_template('editar_paciente.html', paciente=paciente_encontrado, profesionales=profesionales, obras_sociales=parametros.get('obras_sociales', []))

    if request.method == 'POST':
        for p in lista_pacientes:
            if p['id'] == id:
                campos = ['nombre','dni','edad','domicilio','obra_social','nombre_padre','tel_padre','nombre_madre','tel_madre','escuela_nombre','escuela_grado','escuela_turno','diagnostico','medico_cabecera','neurologo','plan_anual','objetivos_mensuales','sugerencias_hogar']
                p.update({k: request.form[k] for k in campos if k in request.form})
                
                p['fecha_nacimiento'] = procesar_fecha(request.form.get('fecha_nacimiento', ''))
                p['profesionales'] = request.form.getlist('profesionales')
                
                esp = request.form.getlist('especialidad[]')
                prof = request.form.getlist('profesional[]')
                hor = request.form.getlist('horario[]')

                if 'foto_perfil' in request.files and request.files['foto_perfil'].filename != '':
                    nom = secure_filename(f"paciente_{id}.{request.files['foto_perfil'].filename.split('.')[-1]}")
                    request.files['foto_perfil'].save(os.path.join(current_app.config['UPLOAD_FOLDER'], nom))
                    p['foto'] = nom
                break
        with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f: json.dump(lista_pacientes, f, indent=4, ensure_ascii=False)
        return redirect(url_for('pacientes_bp.perfil_paciente', id=id, tab='clinica'))

@pacientes_bp.route('/paciente/subir_archivo', methods=['POST'])
def subir_archivo_paciente():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    id_paciente = int(request.form['id_paciente'])
    if 'archivo' in request.files and request.files['archivo'].filename != '':
        archivo = request.files['archivo']
        nom = secure_filename(f"{request.form.get('tipo_documento', 'Doc')}_{id_paciente}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{archivo.filename.split('.')[-1]}")
        archivo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], nom))
        lista_pacientes = cargar_datos('pacientes.json')
        for p in lista_pacientes:
            if p['id'] == id_paciente:
                p.setdefault('archivos_adjuntos', []).append({"nombre_archivo": nom, "nombre_original": archivo.filename, "tipo": request.form.get('tipo_documento'), "fecha": datetime.now().strftime("%d/%m/%Y")})
                break
        with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f: json.dump(lista_pacientes, f, indent=4, ensure_ascii=False)
    return redirect(url_for('pacientes_bp.perfil_paciente', id=id_paciente, tab='docs'))

@pacientes_bp.route('/paciente/estado/<int:id>')
def toggle_estado_paciente(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    lista = cargar_datos('pacientes.json')
    for p in lista:
        if p['id'] == id: p['activo'] = not p.get('activo', True); break
    with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f: json.dump(lista, f, indent=4, ensure_ascii=False)
    return redirect(url_for('pacientes_bp.pacientes'))

@pacientes_bp.route('/pacientes/nuevo', methods=['GET', 'POST'])
def crear_paciente():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    profesionales = cargar_datos('profesionales.json')
    if request.method == 'POST':
        lista_pacientes = cargar_datos('pacientes.json')
        nuevo_id = 1 if not lista_pacientes else max(p['id'] for p in lista_pacientes) + 1
        nuevo_paciente = {
            "id": nuevo_id, "activo": True,
            "nombre": request.form['nombre'], 
            "dni": request.form.get('dni', ''), 
            "fecha_nacimiento": procesar_fecha(request.form.get('fecha_nacimiento', '')), 
            "edad": request.form['edad'], "domicilio": request.form.get('domicilio', ''), "obra_social": request.form.get('obra_social', 'Particular'),
            "nombre_padre": request.form.get('nombre_padre', ''), "tel_padre": request.form.get('tel_padre', ''), "nombre_madre": request.form.get('nombre_madre', ''), "tel_madre": request.form.get('tel_madre', ''),
            "escuela_nombre": request.form.get('escuela_nombre', ''), "escuela_grado": request.form.get('escuela_grado', ''), "escuela_turno": request.form.get('escuela_turno', ''),
            "diagnostico": request.form['diagnostico'], "medico_cabecera": request.form.get('medico_cabecera', ''), "neurologo": request.form.get('neurologo', ''),
            "profesionales": request.form.getlist('profesionales'),
            "plan_anual": "", "objetivos_mensuales": "", "sugerencias_hogar": "", "archivos_adjuntos": [], "foto": None
        }
        if 'foto_perfil' in request.files and request.files['foto_perfil'].filename != '':
            nom = secure_filename(f"paciente_{nuevo_id}.{request.files['foto_perfil'].filename.split('.')[-1]}")
            request.files['foto_perfil'].save(os.path.join(current_app.config['UPLOAD_FOLDER'], nom))
            nuevo_paciente['foto'] = nom
        lista_pacientes.append(nuevo_paciente)
        with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f: json.dump(lista_pacientes, f, indent=4, ensure_ascii=False)
        return redirect(url_for('pacientes_bp.pacientes'))
    return render_template('nuevo_paciente.html', profesionales=profesionales)

@pacientes_bp.route('/paciente/asignar_turno/<int:id>', methods=['POST'])
def asignar_turno(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    
    lista_pacientes = cargar_datos('pacientes.json')
    paciente = next((p for p in lista_pacientes if p['id'] == id), None)
    
    if paciente:
        nuevo_turno = {
            "fecha": procesar_fecha(request.form.get('fecha')),
            "hora": request.form.get('hora'),
            "profesional": request.form.get('profesional'),
            "tipo": request.form.get('tipo')
        }
        if 'turnos_programados' not in paciente:
            paciente['turnos_programados'] = []
        paciente['turnos_programados'].append(nuevo_turno)
        
        with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f:
            json.dump(lista_pacientes, f, indent=4, ensure_ascii=False)
            
    return redirect(url_for('pacientes_bp.perfil_paciente', id=id, tab='clinica'))

@pacientes_bp.route('/paciente/guardar_plan/<int:id>', methods=['POST'])
def guardar_planificacion(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    
    lista_pacientes = cargar_datos('pacientes.json')
    paciente = next((p for p in lista_pacientes if p['id'] == id), None)
    
    if paciente:
        paciente['plan_anual'] = request.form.get('plan_anual', '')
        paciente['objetivos_mensuales'] = request.form.get('objetivos_mensuales', '')
        paciente['sugerencias_hogar'] = request.form.get('sugerencias_hogar', '')
        
        with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f:
            json.dump(lista_pacientes, f, indent=4, ensure_ascii=False)
            
    return redirect(url_for('pacientes_bp.perfil_paciente', id=id, tab='plan'))

@pacientes_bp.route('/paciente/actualizar_equipo/<int:id>', methods=['POST'])
def actualizar_equipo(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    
    lista_pacientes = cargar_datos('pacientes.json')
    paciente = next((p for p in lista_pacientes if p['id'] == id), None)
    
    if paciente:
        paciente['profesionales'] = request.form.getlist('profesionales')
        with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f:
            json.dump(lista_pacientes, f, indent=4, ensure_ascii=False)
            
    return redirect(url_for('pacientes_bp.perfil_paciente', id=id, tab='clinica'))

@pacientes_bp.route('/paciente/guardar_evolucion/<int:id>', methods=['POST'])
def guardar_evolucion_paciente(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    profesional = session['usuario_actual']
    
    historias = cargar_datos('historias.json')
    nuevo_id = 1 if not historias else max(h['id'] for h in historias) + 1
    
    nueva_historia = {
        "id": nuevo_id,
        "id_paciente": id,
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "hora": datetime.now().strftime("%H:%M"),
        "profesional": profesional['nombre'],
        "nota": request.form.get('nota', '')
    }
    
    historias.append(nueva_historia)
    with open(os.path.join('datos', 'historias.json'), 'w', encoding='utf-8') as f:
        json.dump(historias, f, indent=4, ensure_ascii=False)
        
    return redirect(url_for('pacientes_bp.perfil_paciente', id=id, tab='evoluciones'))

@pacientes_bp.route('/paciente/imprimir/<int:id>/<string:seccion>')
def imprimir_seccion(id, seccion):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    p = next((x for x in cargar_datos('pacientes.json') if x['id'] == id), None)
    if not p: return "Error"
    
    data = p if seccion == 'datos' else {}
    if seccion == 'planificacion': data = {k: p.get(k,'') for k in ['plan_anual','objetivos_mensuales','sugerencias_hogar']}
    elif seccion == 'evoluciones': data = [h for h in cargar_datos('historias.json') if h['id_paciente']==id][::-1]
    
    return render_template('imprimir_seccion.html', paciente=p, seccion=seccion, titulo=seccion.capitalize(), datos=data, fecha_impresion=datetime.now().strftime("%d/%m/%Y"))

@pacientes_bp.route('/paciente/asignar_horario/<int:id>', methods=['POST'])
def asignar_horario_fijo(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    
    sesiones = cargar_datos('sesiones.json')
    pacientes = cargar_datos('pacientes.json')
    profesionales = cargar_datos('profesionales.json') 
    
    paciente = next((p for p in pacientes if p['id'] == id), None)
    
    if paciente:
        nuevo_id_sesion = 1 if not sesiones else max(s['id'] for s in sesiones) + 1
        
        nombre_prof = request.form.get('profesional')
        prof_obj = next((p for p in profesionales if p['nombre'] == nombre_prof), None)
        
        # BLINDAJE 1: Si no tiene especialidad, ponemos "T.O" por defecto para que no rompa
        especialidad = prof_obj.get('especialidad', 'T.O') if prof_obj else "T.O"

        # Guardamos la sesión con las CLAVES EXACTAS que pide agenda.html
        nueva_sesion = {
            "id": nuevo_id_sesion,
            "id_paciente": id,
            "nombre_paciente": paciente['nombre'], 
            "profesional_nombre": nombre_prof, 
            "profesional_especialidad": especialidad,
            "dias": request.form.getlist('dias'),
            "hora": request.form.get('hora'),
            "consultorio": request.form.get('consultorio'),
            "tipo": request.form.get('tipo')
        }
        
        sesiones.append(nueva_sesion)
        
        with open(os.path.join('datos', 'sesiones.json'), 'w', encoding='utf-8') as f:
            json.dump(sesiones, f, indent=4, ensure_ascii=False)
            
    # ARQUITECTURA: Lo redirigimos a la solapa clínica luego de asignar el horario
    return redirect(url_for('pacientes_bp.perfil_paciente', id=id, tab='clinica'))

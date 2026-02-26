from flask import Flask, render_template, request, redirect, url_for, session, send_file
import json
import os
import zipfile
import io
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__, template_folder='plantillas')
app.secret_key = 'nidus_clave_secreta_segura'

# Configuración de carpeta para subir archivos
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- HELPER: Cargar JSON ---
def cargar_datos(nombre_archivo):
    ruta = os.path.join('datos', nombre_archivo)
    try:
        with open(ruta, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []

# --- HELPER: Mapas de Fotos ---
def obtener_mapa_fotos_pacientes(pacientes):
    return {p['id']: p.get('foto') for p in pacientes}

def obtener_mapa_fotos_profesionales(profesionales):
    return {p['nombre']: p.get('foto') for p in profesionales}

# --- LÓGICA DE FECHAS (GLOBAL PARA TODO EL SISTEMA) ---

@app.template_filter('fecha_input')
def fecha_input_filter(fecha_str):
    """
    Filtro para HTML: Transforma '31/12/2025' (JSON) -> '2025-12-31' (Input HTML)
    Uso en HTML: value="{{ fecha | fecha_input }}"
    """
    if not fecha_str: return ''
    try:
        return datetime.strptime(fecha_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    except:
        return fecha_str 

def procesar_fecha(fecha_ymd):
    """
    Función Backend: Transforma '2025-12-31' (Input HTML) -> '31/12/2025' (JSON)
    """
    if not fecha_ymd: return ""
    try:
        return datetime.strptime(fecha_ymd, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        return fecha_ymd

# ==========================================
# 1. LOGIN Y DASHBOARD (Rutas Principales)
# ==========================================

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario_input = request.form['usuario']
        password_input = request.form['contrasena']
        profesionales = cargar_datos('profesionales.json')
        
        usuario_encontrado = next((p for p in profesionales if p['usuario'] == usuario_input and p['contrasena'] == password_input), None)
        
        if usuario_encontrado:
            session['usuario_actual'] = usuario_encontrado
            return redirect(url_for('dashboard2')) 
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """ DASHBOARD GENERAL: Muestra estadísticas de TODA la clínica """
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    profesional = session['usuario_actual']
    
    # Si es Auxiliar, no debería ver el general, lo mandamos al personal
    if profesional.get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard2'))
    
    pacientes = cargar_datos('pacientes.json')
    todas_sesiones = cargar_datos('sesiones.json')
    lista_profesionales = cargar_datos('profesionales.json')
    
    mapa_ids_prof = {p['nombre']: p['id'] for p in lista_profesionales}
    mapa_fotos_pac = obtener_mapa_fotos_pacientes(pacientes)
    mapa_fotos_prof = obtener_mapa_fotos_profesionales(lista_profesionales)
    
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia_hoy_texto = dias_semana[datetime.now().weekday()]
    
    # Filtrar turnos de HOY (de todos los profesionales)
    turnos_hoy = []
    for s in todas_sesiones:
        if dia_hoy_texto in s['dias']:
            turno_display = s.copy()
            turno_display.setdefault('estado_turno', 'Pendiente')
            turno_display['profesional_id'] = mapa_ids_prof.get(s['profesional_nombre'])
            turno_display['foto_paciente'] = mapa_fotos_pac.get(s['id_paciente'])
            turno_display['foto_profesional'] = mapa_fotos_prof.get(s['profesional_nombre'])
            turnos_hoy.append(turno_display)
    
    turnos_hoy.sort(key=lambda x: x['hora'])
    
    stats = {
        "pacientes": len(pacientes), 
        "turnos_hoy": len(turnos_hoy),
        "profesionales": len(lista_profesionales)
    }
    
    return render_template('dashboard.html', profesional=profesional, stats=stats, sesiones=turnos_hoy, dia_hoy=dia_hoy_texto)

@app.route('/dashboard2')
def dashboard2():
    """ DASHBOARD PERSONAL: Muestra solo LO MÍO """
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    profesional = session['usuario_actual']
    
    pacientes = cargar_datos('pacientes.json')
    todas_sesiones = cargar_datos('sesiones.json')
    lista_profesionales = cargar_datos('profesionales.json')
    recordatorios = cargar_datos('recordatorios.json')
    
    mapa_ids_prof = {p['nombre']: p['id'] for p in lista_profesionales}
    mapa_fotos_pac = obtener_mapa_fotos_pacientes(pacientes)
    
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia_hoy_texto = dias_semana[datetime.now().weekday()]
    
    # Mis turnos de hoy
    mis_turnos_hoy = []
    for s in todas_sesiones:
        if dia_hoy_texto in s['dias'] and s['profesional_nombre'] == profesional['nombre']:
            turno_display = s.copy()
            turno_display.setdefault('estado_turno', 'Confirmado')
            turno_display['profesional_id'] = mapa_ids_prof.get(s['profesional_nombre'])
            turno_display['foto_paciente'] = mapa_fotos_pac.get(s['id_paciente'])
            mis_turnos_hoy.append(turno_display)
    mis_turnos_hoy.sort(key=lambda x: x['hora'])

    # Mis pacientes asignados
    mis_pacientes = [p for p in pacientes if 'profesionales' in p and profesional['nombre'] in p['profesionales']]
    
    # Mi equipo (si soy titular)
    mi_equipo = []
    if profesional.get('jerarquia') == 'Titular':
        mi_equipo = [p for p in lista_profesionales if p.get('supervisor') == profesional['nombre']]

    # Mis recordatorios
    mis_recordatorios = [r for r in recordatorios if r['usuario'] == profesional['usuario']]
    mis_recordatorios.sort(key=lambda x: (x.get('fecha_iso', ''), x.get('hora', '')))

    stats = {"pacientes": len(mis_pacientes), "turnos_hoy": len(mis_turnos_hoy), "equipo": len(mi_equipo)}
    
    return render_template('dashboard2.html', profesional=profesional, stats=stats, sesiones=mis_turnos_hoy, mis_pacientes=mis_pacientes, mi_equipo=mi_equipo, recordatorios=mis_recordatorios, dia_hoy=dia_hoy_texto)

@app.route('/logout')
def logout():
    session.pop('usuario_actual', None)
    return redirect(url_for('login'))

# ==========================================
# 2. GESTIÓN DE PACIENTES (Fechas Corregidas)
# ==========================================

# --- BLOQUE DE PACIENTES COMPLETO Y CORREGIDO ---

@app.route('/pacientes')
def pacientes():
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    profesional = session['usuario_actual']
    if profesional.get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard2'))

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

@app.route('/paciente/<int:id>')
def perfil_paciente(id):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    profesional = session['usuario_actual']
    
    pacientes = cargar_datos('pacientes.json')
    paciente = next((p for p in pacientes if p['id'] == id), None)
    if not paciente: return redirect(url_for('dashboard2'))

    if profesional.get('jerarquia') == 'Auxiliar':
        if profesional['nombre'] not in paciente.get('profesionales', []):
            return redirect(url_for('dashboard2'))

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
    
    # SE AGREGA 'profesionales=profesionales' PARA EL MODAL DE TURNOS
    return render_template('ficha_paciente.html', 
                           profesional=profesional, 
                           paciente=paciente, 
                           historial=historial, 
                           equipo=equipo, 
                           turnos=turnos_paciente, 
                           profesionales=profesionales)

@app.route('/paciente/editar/<int:id>', methods=['GET', 'POST'])
def editar_paciente(id):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    pacientes = cargar_datos('pacientes.json')
    profesionales = cargar_datos('profesionales.json')
    parametros = cargar_datos('parametros.json') or {"obras_sociales": ["Particular"]}

    paciente_encontrado = next((p for p in pacientes if p['id'] == id), None)
    if not paciente_encontrado: return redirect(url_for('pacientes'))

    if request.method == 'GET':
        return render_template('editar_paciente.html', paciente=paciente_encontrado, profesionales=profesionales, obras_sociales=parametros.get('obras_sociales', []))

    if request.method == 'POST':
        for p in pacientes:
            if p['id'] == id:
                campos = ['nombre','dni','edad','domicilio','obra_social','nombre_padre','tel_padre','nombre_madre','tel_madre','escuela_nombre','escuela_grado','escuela_turno','diagnostico','medico_cabecera','neurologo','plan_anual','objetivos_mensuales','sugerencias_hogar']
                p.update({k: request.form[k] for k in campos if k in request.form})
                
                p['fecha_nacimiento'] = procesar_fecha(request.form.get('fecha_nacimiento', ''))
                
                p['profesionales'] = request.form.getlist('profesionales')
                if 'foto_perfil' in request.files and request.files['foto_perfil'].filename != '':
                    nom = secure_filename(f"paciente_{id}.{request.files['foto_perfil'].filename.split('.')[-1]}")
                    request.files['foto_perfil'].save(os.path.join(app.config['UPLOAD_FOLDER'], nom))
                    p['foto'] = nom
                break
        with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f: json.dump(pacientes, f, indent=4, ensure_ascii=False)
        return redirect(url_for('perfil_paciente', id=id))

@app.route('/paciente/subir_archivo', methods=['POST'])
def subir_archivo_paciente():
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    id_paciente = int(request.form['id_paciente'])
    if 'archivo' in request.files and request.files['archivo'].filename != '':
        archivo = request.files['archivo']
        nom = secure_filename(f"{request.form.get('tipo_documento', 'Doc')}_{id_paciente}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{archivo.filename.split('.')[-1]}")
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nom))
        pacientes = cargar_datos('pacientes.json')
        for p in pacientes:
            if p['id'] == id_paciente:
                p.setdefault('archivos_adjuntos', []).append({"nombre_archivo": nom, "nombre_original": archivo.filename, "tipo": request.form.get('tipo_documento'), "fecha": datetime.now().strftime("%d/%m/%Y")})
                break
        with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f: json.dump(pacientes, f, indent=4, ensure_ascii=False)
    return redirect(url_for('perfil_paciente', id=id_paciente))

@app.route('/paciente/estado/<int:id>')
def toggle_estado_paciente(id):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    lista = cargar_datos('pacientes.json')
    for p in lista:
        if p['id'] == id: p['activo'] = not p.get('activo', True); break
    with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f: json.dump(lista, f, indent=4, ensure_ascii=False)
    return redirect(url_for('pacientes'))

@app.route('/pacientes/nuevo', methods=['GET', 'POST'])
def crear_paciente():
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    profesionales = cargar_datos('profesionales.json')
    if request.method == 'POST':
        pacientes = cargar_datos('pacientes.json')
        nuevo_id = 1 if not pacientes else max(p['id'] for p in pacientes) + 1
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
            request.files['foto_perfil'].save(os.path.join(app.config['UPLOAD_FOLDER'], nom))
            nuevo_paciente['foto'] = nom
        pacientes.append(nuevo_paciente)
        with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f: json.dump(pacientes, f, indent=4, ensure_ascii=False)
        return redirect(url_for('pacientes'))
    return render_template('nuevo_paciente.html', profesionales=profesionales)

# --- NUEVA FUNCIÓN: ASIGNAR TURNO ---
@app.route('/paciente/asignar_turno/<int:id>', methods=['POST'])
def asignar_turno(id):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    
    pacientes = cargar_datos('pacientes.json')
    paciente = next((p for p in pacientes if p['id'] == id), None)
    
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
            json.dump(pacientes, f, indent=4, ensure_ascii=False)
            
    return redirect(url_for('perfil_paciente', id=id))

# --- GUARDAR PLANIFICACIÓN ---
@app.route('/paciente/guardar_plan/<int:id>', methods=['POST'])
def guardar_planificacion(id):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    
    pacientes = cargar_datos('pacientes.json')
    paciente = next((p for p in pacientes if p['id'] == id), None)
    
    if paciente:
        paciente['plan_anual'] = request.form.get('plan_anual', '')
        paciente['objetivos_mensuales'] = request.form.get('objetivos_mensuales', '')
        paciente['sugerencias_hogar'] = request.form.get('sugerencias_hogar', '')
        
        with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f:
            json.dump(pacientes, f, indent=4, ensure_ascii=False)
            
    return redirect(url_for('perfil_paciente', id=id))

# ==========================================
# 3. ADMISIONES (LISTA ÚNICA + FECHAS OK + EDICIÓN MODAL)
# ==========================================

# --- RUTAS DE ADMISIONES (ACTUALIZADO) ---

@app.route('/admisiones', methods=['GET', 'POST'])
def admisiones():
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    profesional_actual = session['usuario_actual']
    if profesional_actual.get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard2'))

    lista_admisiones = cargar_datos('admisiones.json')
    lista_profesionales = cargar_datos('profesionales.json')
    parametros = cargar_datos('parametros.json') or {"obras_sociales": ["Particular", "OSDE"]}

    if request.method == 'POST':
        nuevo_id = 1 if not lista_admisiones else lista_admisiones[-1]['id'] + 1
        
        # 1. Informe Diagnóstico (MULTIPLE)
        lista_diagnosticos = []
        if 'archivo_diagnostico' in request.files:
            archivos = request.files.getlist('archivo_diagnostico')
            for f in archivos:
                if f.filename != '':
                    nombre = secure_filename(f"diag_{nuevo_id}_{f.filename}")
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre))
                    lista_diagnosticos.append(nombre)
        
        # 2. Informes Previos (MULTIPLE)
        lista_informes_previos = []
        if 'archivo_informes_previos' in request.files:
            archivos = request.files.getlist('archivo_informes_previos')
            for f in archivos:
                if f.filename != '':
                    nombre = secure_filename(f"previo_{nuevo_id}_{f.filename}")
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre))
                    lista_informes_previos.append(nombre)
        
        # 3. Informe Escolar / AT (MULTIPLE)
        lista_informes_escolares = []
        if 'archivo_informe_escolar' in request.files:
            archivos = request.files.getlist('archivo_informe_escolar')
            for f in archivos:
                if f.filename != '':
                    nombre = secure_filename(f"escolar_{nuevo_id}_{f.filename}")
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre))
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
            
            # FAMILIA
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

            # CLÍNICA Y ESCOLARIDAD
            "escuela_nombre": request.form.get('escuela_nombre', ''), 
            "escuela_grado": request.form.get('escuela_grado', ''), 
            "escuela_turno": request.form.get('escuela_turno', ''),
            "escuela_apoyo_nombre": request.form.get('escuela_apoyo_nombre', ''), 
            "informe_escolar": lista_informes_escolares, # LISTA
            
            "tiene_terapias_previas": request.form.get('tiene_terapias_previas', 'No'), 
            "terapias_previas_desc": request.form.get('terapias_previas_desc', ''), 
            "archivo_informes_previos": lista_informes_previos, # LISTA

            "motivo_consulta": request.form.get('motivo_consulta', ''), 
            "medico_cabecera": request.form.get('medico_cabecera', ''), 
            "neurologo": request.form.get('neurologo', ''),
            "informe_diagnostico": lista_diagnosticos, # LISTA

            "profesional_admision": request.form['profesional_admision'], 
            "prioridad": request.form.get('prioridad', 'Media'), 
            "disponibilidad_preferencia": request.form.get('disponibilidad_preferencia', ''),
            "equipo_sugerido": [], "informe_derivacion": None, "informe_entrevista": None
        }
        lista_admisiones.append(nueva_admision)
        with open(os.path.join('datos', 'admisiones.json'), 'w', encoding='utf-8') as f: json.dump(lista_admisiones, f, indent=4, ensure_ascii=False)
        return redirect(url_for('admisiones'))
    
    lista_admisiones.sort(key=lambda x: x['id'], reverse=True)
    return render_template('admisiones.html', profesional=profesional_actual, candidatos=lista_admisiones, profesionales=lista_profesionales, obras_sociales=parametros['obras_sociales'])

@app.route('/admision/<int:id>', methods=['GET', 'POST'])
def perfil_admision(id):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    admisiones = cargar_datos('admisiones.json')
    candidato = next((a for a in admisiones if a['id'] == id), None)
    if not candidato: return redirect(url_for('admisiones'))
    
    if request.method == 'POST':
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
        
        # --- CARGA MÚLTIPLE EN EDICIÓN ---
        def procesar_archivos_multiples(campo_form, campo_json, prefijo):
            if campo_form in request.files:
                archivos = request.files.getlist(campo_form)
                # Inicializar como lista si no existe o si es string viejo
                if campo_json not in candidato or not isinstance(candidato[campo_json], list):
                    candidato[campo_json] = [] if not isinstance(candidato.get(campo_json), str) else [candidato[campo_json]]
                
                for f in archivos:
                    if f.filename != '':
                        nom = secure_filename(f"{prefijo}_{id}_{f.filename}")
                        f.save(os.path.join(app.config['UPLOAD_FOLDER'], nom))
                        candidato[campo_json].append(nom)

        procesar_archivos_multiples('archivo_diagnostico', 'informe_diagnostico', 'diag')
        procesar_archivos_multiples('archivo_informes_previos', 'archivo_informes_previos', 'previo')
        procesar_archivos_multiples('archivo_informe_escolar', 'informe_escolar', 'escolar')
        
        # Archivos únicos
        if 'archivo_derivacion' in request.files and request.files['archivo_derivacion'].filename != '':
            nom = secure_filename(f"derivacion_{id}_{request.files['archivo_derivacion'].filename}")
            request.files['archivo_derivacion'].save(os.path.join(app.config['UPLOAD_FOLDER'], nom))
            candidato['informe_derivacion'] = nom

        if 'archivo_entrevista' in request.files and request.files['archivo_entrevista'].filename != '':
            nom = secure_filename(f"entrevista_{id}_{request.files['archivo_entrevista'].filename}")
            request.files['archivo_entrevista'].save(os.path.join(app.config['UPLOAD_FOLDER'], nom))
            candidato['informe_entrevista'] = nom

        with open(os.path.join('datos', 'admisiones.json'), 'w', encoding='utf-8') as f: json.dump(admisiones, f, indent=4, ensure_ascii=False)
        return redirect(url_for('admisiones'))

    return render_template('ficha_admision.html', candidato=candidato)

@app.route('/admision/alta/<int:id>')
def alta_admision(id):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    admisiones = cargar_datos('admisiones.json')
    pacientes = cargar_datos('pacientes.json')
    candidato = next((a for a in admisiones if a['id'] == id), None)
    if not candidato: return redirect(url_for('admisiones'))
    
    nuevo_id_pac = 1 if not pacientes else max(p['id'] for p in pacientes) + 1
    
    # CREAR PACIENTE CON TODOS LOS DATOS COPIADOS
    nuevo_paciente = {
        "id": nuevo_id_pac, 
        "activo": True,
        
        # Datos Básicos
        "nombre": candidato.get('nombre'), 
        "dni": candidato.get('dni'), 
        "fecha_nacimiento": candidato.get('fecha_nacimiento'),
        "edad": candidato.get('edad'), 
        "domicilio": candidato.get('domicilio'), 
        "obra_social": candidato.get('obra_social'),
        
        # Datos Familia (NUEVOS CAMPOS AGREGADOS)
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
        
        # Datos Clínica y Escolar (NUEVOS CAMPOS AGREGADOS)
        "escuela_nombre": candidato.get('escuela_nombre'), 
        "escuela_grado": candidato.get('escuela_grado'), 
        "escuela_turno": candidato.get('escuela_turno'),
        "escuela_apoyo_nombre": candidato.get('escuela_apoyo_nombre'),
        
        "diagnostico": candidato.get('motivo_consulta'), 
        "medico_cabecera": candidato.get('medico_cabecera'), 
        "neurologo": candidato.get('neurologo'),
        "tiene_terapias_previas": candidato.get('tiene_terapias_previas'),
        "terapias_previas_desc": candidato.get('terapias_previas_desc'),
        
        # Archivos (COPIAR LISTAS COMPLETAS)
        "informe_diagnostico": candidato.get('informe_diagnostico', []),
        "archivo_informes_previos": candidato.get('archivo_informes_previos', []),
        "informe_escolar": candidato.get('informe_escolar', []),
        "informe_derivacion": candidato.get('informe_derivacion'),
        
        # Campos de sistema (Vacíos por ahora)
        "disponibilidad_registro": candidato.get('disponibilidad_preferencia'),
        "profesionales": [], 
        "plan_anual": "", 
        "objetivos_mensuales": "", 
        "sugerencias_hogar": "", 
        "archivos_adjuntos": [], # Lista para futuros archivos subidos desde Pacientes
        "foto": None,
        "informe": candidato.get('informe_derivacion') # Legacy support
    }
    
    pacientes.append(nuevo_paciente)
    with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f: json.dump(pacientes, f, indent=4, ensure_ascii=False)
    
    # NO BORRAR ADMISION -> CAMBIAR ESTADO
    candidato['estado'] = 'Procesada'
    with open(os.path.join('datos', 'admisiones.json'), 'w', encoding='utf-8') as f: json.dump(admisiones, f, indent=4, ensure_ascii=False)
        
    return redirect(url_for('admisiones')) # Volver a admisiones para seguir trabajando

@app.route('/admision/borrar/<int:id>')
def borrar_admision(id):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    admisiones = cargar_datos('admisiones.json')
    # Filtrar la admisión a borrar
    admisiones = [a for a in admisiones if a['id'] != id]
    with open(os.path.join('datos', 'admisiones.json'), 'w', encoding='utf-8') as f: json.dump(admisiones, f, indent=4, ensure_ascii=False)
    return redirect(url_for('admisiones'))

@app.route('/admision/imprimir/<int:id>')
def imprimir_admision(id):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    admisiones = cargar_datos('admisiones.json')
    candidato = next((a for a in admisiones if a['id'] == id), None)
    if not candidato: return "Admisión no encontrada"
    return render_template('imprimir_admision.html', adm=candidato)

# ==========================================
# 4. AGENDA Y TURNOS
# ==========================================

@app.route('/agenda', methods=['GET', 'POST'])
def agenda():
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    profesional = session['usuario_actual']
    if profesional.get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard2'))

    pacientes = cargar_datos('pacientes.json')
    sesiones = cargar_datos('sesiones.json')
    lista_profesionales = cargar_datos('profesionales.json')
    
    mapa_fotos_pac = obtener_mapa_fotos_pacientes(pacientes)
    mapa_fotos_prof = obtener_mapa_fotos_profesionales(lista_profesionales)
    mapa_ids_prof = {p['nombre']: p['id'] for p in lista_profesionales}
    
    for s in sesiones:
        s['foto_paciente'] = mapa_fotos_pac.get(s['id_paciente'])
        s['foto_profesional'] = mapa_fotos_prof.get(s['profesional_nombre'])
        s['profesional_id'] = mapa_ids_prof.get(s['profesional_nombre'])
        
    if request.method == 'POST':
        id_paciente = int(request.form['id_paciente'])
        dias = request.form.getlist('dias_semana')
        hora = request.form['hora']
        
        nombre_p = next((p['nombre'] for p in pacientes if p['id'] == id_paciente), "Desconocido")
        nid = 1 if not sesiones else sesiones[-1]['id'] + 1
        nueva = {
            "id": nid, "id_paciente": id_paciente, "nombre_paciente": nombre_p,
            "dias": dias, "hora": hora, "tipo": request.form['tipo'],
            "consultorio": request.form['consultorio'],
            "profesional_nombre": profesional['nombre'], "profesional_especialidad": profesional['rol'], "estado_turno": "Confirmado"
        }
        sesiones.append(nueva)
        with open(os.path.join('datos', 'sesiones.json'), 'w', encoding='utf-8') as f:
            json.dump(sesiones, f, indent=4, ensure_ascii=False)
        return redirect(url_for('agenda'))
                
    return render_template('agenda.html', profesional=profesional, turnos=sesiones, pacientes=pacientes)

@app.route('/turno/cambiar_estado/<int:id>/<string:nuevo_estado>')
def cambiar_estado_turno(id, nuevo_estado):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    sesiones = cargar_datos('sesiones.json')
    for s in sesiones:
        if s['id'] == id: s['estado_turno'] = nuevo_estado; break
    with open(os.path.join('datos', 'sesiones.json'), 'w', encoding='utf-8') as f: json.dump(sesiones, f, indent=4, ensure_ascii=False)
    return redirect(url_for('dashboard2'))

# ==========================================
# 5. HISTORIAS CLINICAS
# ==========================================

@app.route('/historias', methods=['GET', 'POST'])
def historias():
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    profesional = session['usuario_actual']
    
    if profesional.get('jerarquia') == 'Auxiliar' and not request.args.get('id_paciente'):
         return redirect(url_for('dashboard2'))

    pacientes = cargar_datos('pacientes.json')
    historias = cargar_datos('historias.json')
    lista_profesionales = cargar_datos('profesionales.json')
    mapa_fotos_prof = obtener_mapa_fotos_profesionales(lista_profesionales)
    
    id_sel = request.args.get('id_paciente')
    paciente_actual = None
    historial_paciente = []
    
    if id_sel:
        try:
            id_sel = int(id_sel)
            paciente_actual = next((p for p in pacientes if p['id'] == id_sel), None)
            historial_paciente = [h for h in historias if h['id_paciente'] == id_sel]
            historial_paciente.reverse()
            for h in historial_paciente: h['foto_profesional'] = mapa_fotos_prof.get(h['profesional'])
        except: pass
        
    if request.method == 'POST':
        id_p = int(request.form['id_paciente'])
        nid = 1 if not historias else historias[-1]['id'] + 1
        ahora = datetime.now()
        nueva = {
            "id": nid, "id_paciente": id_p, "profesional": profesional['nombre'],
            "nota": request.form['nota'], "fecha": ahora.strftime("%d/%m/%Y"), 
            "hora": ahora.strftime("%H:%M")
        }
        historias.append(nueva)
        with open(os.path.join('datos', 'historias.json'), 'w', encoding='utf-8') as f:
            json.dump(historias, f, indent=4, ensure_ascii=False)
        return redirect(url_for('historias', id_paciente=id_p))
        
    return render_template('historias.html', profesional=profesional, pacientes=pacientes, paciente_actual=paciente_actual, historial=historial_paciente)

# ==========================================
# 6. REPORTES
# ==========================================

@app.route('/reportes')
def reportes():
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    if session['usuario_actual'].get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard2'))

    pacientes = cargar_datos('pacientes.json')
    sesiones = cargar_datos('sesiones.json')
    pagos = cargar_datos('pagos.json') 
    
    total_p = len(pacientes)
    conteo_diag = {}
    for p in pacientes: 
        d = p['diagnostico']
        conteo_diag[d] = conteo_diag.get(d, 0) + 1
    diag_freq = max(conteo_diag, key=conteo_diag.get) if conteo_diag else "N/A"
    
    conteo_tipo = {}
    for s in sesiones: 
        t = s.get('tipo', 'Individual')
        conteo_tipo[t] = conteo_tipo.get(t, 0) + 1

    stats_os = {}
    for pago in pagos:
        os_nombre = pago['obra_social']
        if os_nombre != 'Particular':
            if os_nombre not in stats_os: stats_os[os_nombre] = {"total_monto": 0, "total_demora": 0, "cantidad": 0}
            stats_os[os_nombre]["total_monto"] += pago['monto']
            stats_os[os_nombre]["total_demora"] += pago['dias_demora']
            stats_os[os_nombre]["cantidad"] += 1
    
    reporte_financiero = []
    for nombre, datos in stats_os.items():
        if datos["cantidad"] > 0:
            reporte_financiero.append({
                "nombre": nombre,
                "promedio_pago": int(datos["total_monto"] / datos["cantidad"]),
                "promedio_demora": int(datos["total_demora"] / datos["cantidad"]),
                "cantidad_pagos": datos["cantidad"]
            })
    reporte_financiero.sort(key=lambda x: x['promedio_demora'], reverse=True)

    data = {"total_pacientes": len(pacientes), "diag_frecuente": diag_freq, "desglose_diag": conteo_diag, "total_sesiones": len(sesiones), "desglose_tipos": conteo_tipo, "financiero": reporte_financiero}
    return render_template('reportes.html', profesional=session['usuario_actual'], data=data)

# ==========================================
# 7. FACTURACIÓN Y PAGOS (Con Fechas Corregidas)
# ==========================================

@app.route('/facturacion', methods=['GET', 'POST'])
def facturacion():
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    if session['usuario_actual'].get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard2'))

    pagos = cargar_datos('pagos.json')
    pacientes = cargar_datos('pacientes.json')
    mapa_pacientes = {p['id']: p['nombre'] for p in pacientes}
    
    if request.method == 'POST':
        nid = 1 if not pagos else pagos[-1]['id'] + 1
        
        # Conversión de fechas de entrada (YYYY-MM-DD)
        f_serv = datetime.strptime(request.form['fecha_servicio'], '%Y-%m-%d')
        f_pago = datetime.strptime(request.form['fecha_pago'], '%Y-%m-%d')
        
        pagos.append({
            "id": nid, "id_paciente": int(request.form['id_paciente']), "obra_social": request.form['obra_social'], "monto": int(request.form['monto']),
            # Guardamos como DD/MM/AAAA
            "fecha_servicio": f_serv.strftime("%d/%m/%Y"), 
            "fecha_pago": f_pago.strftime("%d/%m/%Y"),
            "dias_demora": (f_pago - f_serv).days
        })
        with open(os.path.join('datos', 'pagos.json'), 'w', encoding='utf-8') as f: json.dump(pagos, f, indent=4, ensure_ascii=False)
        return redirect(url_for('facturacion'))

    # Para ordenar usamos conversión inversa momentánea
    pagos.sort(key=lambda x: datetime.strptime(x['fecha_pago'], "%d/%m/%Y"), reverse=True)
    return render_template('facturacion.html', profesional=session['usuario_actual'], pagos=pagos, pacientes=pacientes, mapa_pacientes=mapa_pacientes)

# ==========================================
# 8. STAFF Y CONFIGURACIÓN
# ==========================================

@app.route('/profesionales', methods=['GET', 'POST'])
def profesionales():
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    profesional = session['usuario_actual']
    if profesional.get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard2'))

    lista = cargar_datos('profesionales.json')
    areas = {}
    titulares = [p for p in lista if p.get('jerarquia') == 'Titular']
    for p in lista: areas.setdefault(p['rol'], []).append(p)
    
    if request.method == 'POST':
        nid = 1 if not lista else lista[-1]['id'] + 1
        foto = None
        if 'foto_perfil' in request.files and request.files['foto_perfil'].filename != '':
            foto = secure_filename(f"profesional_{nid}.{request.files['foto_perfil'].filename.split('.')[-1]}")
            request.files['foto_perfil'].save(os.path.join(app.config['UPLOAD_FOLDER'], foto))
        
        lista.append({
            "id": nid, "nombre": request.form['nombre'], "usuario": request.form['usuario'], "contrasena": request.form['contrasena'], "rol": request.form['rol'],
            "iniciales": request.form['iniciales'].upper(), "foto": foto, "jerarquia": request.form.get('jerarquia', 'Titular'), "supervisor": request.form.get('supervisor'),
            "dni": request.form.get('dni', ''), "edad": request.form.get('edad', ''), "domicilio": request.form.get('domicilio', ''), "universidad": request.form.get('universidad', ''), "telefono": request.form.get('telefono', ''), "email": request.form.get('email', ''), "matricula": request.form.get('matricula', '')
        })
        with open(os.path.join('datos', 'profesionales.json'), 'w', encoding='utf-8') as f: json.dump(lista, f, indent=4, ensure_ascii=False)
        return redirect(url_for('profesionales'))
    return render_template('profesionales.html', profesional=profesional, lista_profesionales=lista, areas=areas, titulares=titulares)

@app.route('/profesional/editar/<int:id>', methods=['POST'])
def editar_profesional(id):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    lista = cargar_datos('profesionales.json')
    for p in lista:
        if p['id'] == id:
            p.update({k: request.form[k] for k in ['nombre', 'usuario', 'contrasena', 'rol']})
            p['iniciales'] = request.form['iniciales'].upper()
            p['jerarquia'] = request.form.get('jerarquia', 'Titular')
            p['supervisor'] = request.form.get('supervisor') if p['jerarquia'] == 'Auxiliar' else None
            p.update({k: request.form.get(k, '') for k in ['dni','edad','domicilio','universidad','telefono','email','matricula']})
            if 'foto_perfil' in request.files and request.files['foto_perfil'].filename != '':
                nom = secure_filename(f"profesional_{id}.{request.files['foto_perfil'].filename.split('.')[-1]}")
                request.files['foto_perfil'].save(os.path.join(app.config['UPLOAD_FOLDER'], nom))
                p['foto'] = nom
            break
    with open(os.path.join('datos', 'profesionales.json'), 'w', encoding='utf-8') as f: json.dump(lista, f, indent=4, ensure_ascii=False)
    return redirect(url_for('profesionales'))

@app.route('/profesional/<int:id>')
def perfil_profesional(id):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    profesionales = cargar_datos('profesionales.json')
    pacientes = cargar_datos('pacientes.json')
    prof_ver = next((p for p in profesionales if p['id'] == id), None)
    
    pacientes_cargo = [p for p in pacientes if 'profesionales' in p and prof_ver['nombre'] in p['profesionales']]
    pacientes_disponibles = [p for p in pacientes if 'profesionales' not in p or prof_ver['nombre'] not in p['profesionales']]
    auxiliares = [p for p in profesionales if p.get('supervisor') == prof_ver['nombre']] if prof_ver.get('jerarquia') == 'Titular' else []
    return render_template('ficha_profesional.html', profesional=session['usuario_actual'], prof_ver=prof_ver, pacientes=pacientes_cargo, pacientes_disponibles=pacientes_disponibles, equipo_supervisado=auxiliares)

@app.route('/profesional/asignar_paciente', methods=['POST'])
def asignar_paciente_a_profesional():
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    id_prof = int(request.form['id_profesional'])
    id_pac = int(request.form['id_paciente'])
    nombre_prof = request.form['nombre_profesional']
    pacientes = cargar_datos('pacientes.json')
    for p in pacientes:
        if p['id'] == id_pac:
            if nombre_prof not in p.get('profesionales', []): p.setdefault('profesionales', []).append(nombre_prof)
            break
    with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f: json.dump(pacientes, f, indent=4, ensure_ascii=False)
    return redirect(url_for('perfil_profesional', id=id_prof))

@app.route('/especialidad/<string:nombre_especialidad>')
def detalle_especialidad(nombre_especialidad):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    profesionales = cargar_datos('profesionales.json')
    pacientes = cargar_datos('pacientes.json')
    sesiones = cargar_datos('sesiones.json')
    
    equipo = [p for p in profesionales if p['rol'] == nombre_especialidad]
    nombres_equipo = [p['nombre'] for p in equipo]
    pacientes_area = [p for p in pacientes if 'profesionales' in p and any(pr in p['profesionales'] for pr in nombres_equipo)]
    turnos_area = [s for s in sesiones if s.get('profesional_especialidad') == nombre_especialidad]
    
    return render_template('detalle_especialidad.html', profesional=session['usuario_actual'], especialidad=nombre_especialidad, titulares=[p for p in equipo if p.get('jerarquia')=='Titular'], auxiliares=[p for p in equipo if p.get('jerarquia')!='Titular'], pacientes=pacientes_area, turnos=turnos_area)

@app.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    if 'usuario_actual' not in session: return redirect(url_for('login'))
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
                        request.files['foto_perfil'].save(os.path.join(app.config['UPLOAD_FOLDER'], nom))
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

@app.route('/configuracion/nuevo_profesional', methods=['POST'])
def nuevo_prof_desde_config():
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    lista = cargar_datos('profesionales.json')
    nid = 1 if not lista else lista[-1]['id'] + 1
    foto = None
    if 'foto_perfil' in request.files and request.files['foto_perfil'].filename != '':
        foto = secure_filename(f"profesional_{nid}.{request.files['foto_perfil'].filename.split('.')[-1]}")
        request.files['foto_perfil'].save(os.path.join(app.config['UPLOAD_FOLDER'], foto))
    
    lista.append({
        "id": nid, "nombre": request.form['nombre'], "usuario": request.form['usuario'], "contrasena": request.form['contrasena'], "rol": request.form['rol'],
        "iniciales": request.form['iniciales'].upper(), "foto": foto, "jerarquia": request.form.get('jerarquia', 'Titular'), "supervisor": request.form.get('supervisor'),
        "dni": request.form.get('dni',''), "edad": request.form.get('edad',''), "domicilio": request.form.get('domicilio',''), "universidad": request.form.get('universidad',''), "telefono": request.form.get('telefono',''), "email": request.form.get('email',''), "matricula": request.form.get('matricula','')
    })
    with open(os.path.join('datos', 'profesionales.json'), 'w', encoding='utf-8') as f: json.dump(lista, f, indent=4, ensure_ascii=False)
    return redirect(url_for('configuracion'))

@app.route('/configuracion/backup')
def descargar_backup():
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for folder in ['datos', 'static/uploads']:
            if os.path.exists(folder):
                for root, dirs, files in os.walk(folder):
                    for file in files: zip_file.write(os.path.join(root, file), os.path.join(folder, file))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Backup_Junami_{datetime.now().strftime('%d-%m-%Y')}.zip", mimetype='application/zip')

# ==========================================
# 9. RECORDATORIOS Y OTROS
# ==========================================

@app.route('/recordatorio/nuevo', methods=['POST'])
def nuevo_recordatorio():
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    lista = cargar_datos('recordatorios.json')
    nid = 1 if not lista else lista[-1]['id'] + 1
    # Guardamos ambas versiones
    fecha_guardar = procesar_fecha(request.form['fecha'])
    lista.append({
        "id": nid, "usuario": session['usuario_actual']['usuario'], "titulo": request.form['titulo'], "tipo": request.form['tipo'],
        "fecha": fecha_guardar, "fecha_iso": request.form['fecha'], "hora": request.form['hora'], "notas": request.form['notas']
    })
    with open(os.path.join('datos', 'recordatorios.json'), 'w', encoding='utf-8') as f: json.dump(lista, f, indent=4, ensure_ascii=False)
    return redirect(url_for('dashboard2'))

@app.route('/recordatorio/borrar/<int:id>')
def borrar_recordatorio(id):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    lista = [r for r in cargar_datos('recordatorios.json') if r['id'] != id]
    with open(os.path.join('datos', 'recordatorios.json'), 'w', encoding='utf-8') as f: json.dump(lista, f, indent=4, ensure_ascii=False)
    return redirect(url_for('dashboard2'))

# ==========================================
# 10. MÓDULO DE IMPRESIÓN
# ==========================================

@app.route('/paciente/imprimir/<int:id>/<string:seccion>')
def imprimir_seccion(id, seccion):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    p = next((x for x in cargar_datos('pacientes.json') if x['id'] == id), None)
    if not p: return "Error"
    
    data = p if seccion == 'datos' else {}
    if seccion == 'planificacion': data = {k: p.get(k,'') for k in ['plan_anual','objetivos_mensuales','sugerencias_hogar']}
    elif seccion == 'evoluciones': data = [h for h in cargar_datos('historias.json') if h['id_paciente']==id][::-1]
    
    return render_template('imprimir_seccion.html', paciente=p, seccion=seccion, titulo=seccion.capitalize(), datos=data, fecha_impresion=datetime.now().strftime("%d/%m/%Y"))

# --- RUTA FALTANTE PARA GESTIONAR EQUIPO ---
@app.route('/paciente/actualizar_equipo/<int:id>', methods=['POST'])
def actualizar_equipo(id):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    
    pacientes = cargar_datos('pacientes.json')
    paciente = next((p for p in pacientes if p['id'] == id), None)
    
    if paciente:
        # Obtenemos la lista de los checkboxes marcados
        # El nombre 'profesionales' debe coincidir con el name="profesionales" del input en el HTML
        seleccionados = request.form.getlist('profesionales')
        paciente['profesionales'] = seleccionados
        
        with open(os.path.join('datos', 'pacientes.json'), 'w', encoding='utf-8') as f:
            json.dump(pacientes, f, indent=4, ensure_ascii=False)
            
    return redirect(url_for('perfil_paciente', id=id))

@app.route('/paciente/asignar_horario/<int:id>', methods=['POST'])
def asignar_horario_fijo(id):
    if 'usuario_actual' not in session: return redirect(url_for('login'))
    
    sesiones = cargar_datos('sesiones.json')
    pacientes = cargar_datos('pacientes.json')
    profesionales = cargar_datos('profesionales.json') 
    
    paciente = next((p for p in pacientes if p['id'] == id), None)
    
    if paciente:
        nuevo_id_sesion = 1 if not sesiones else max(s['id'] for s in sesiones) + 1
        
        # Buscar datos del profesional
        nombre_prof = request.form.get('profesional')
        prof_obj = next((p for p in profesionales if p['nombre'] == nombre_prof), None)
        
        # BLINDAJE 1: Si no tiene especialidad, ponemos "T.O" por defecto para que no rompa
        especialidad = prof_obj.get('especialidad', 'T.O') if prof_obj else "T.O"

        # Guardamos la sesión con las CLAVES EXACTAS que pide agenda.html
        nueva_sesion = {
            "id": nuevo_id_sesion,
            "id_paciente": id,
            "nombre_paciente": paciente['nombre'], 
            "profesional_nombre": nombre_prof,      # <--- CORRECCIÓN CLAVE: Antes decía 'profesional'
            "profesional_especialidad": especialidad,
            "dias": request.form.getlist('dias'),
            "hora": request.form.get('hora'),
            "consultorio": request.form.get('consultorio'),
            "tipo": request.form.get('tipo')
        }
        
        sesiones.append(nueva_sesion)
        
        with open(os.path.join('datos', 'sesiones.json'), 'w', encoding='utf-8') as f:
            json.dump(sesiones, f, indent=4, ensure_ascii=False)
            
    return redirect(url_for('perfil_paciente', id=id))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
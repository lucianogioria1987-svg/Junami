from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime
from utils import cargar_datos, obtener_mapa_fotos_pacientes, obtener_mapa_fotos_profesionales

dashboard_loguin_bp = Blueprint('dashboard_loguin_bp', __name__)

@dashboard_loguin_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario_input = request.form['usuario']
        password_input = request.form['contrasena']
        profesionales = cargar_datos('profesionales.json')
        
        usuario_encontrado = next((p for p in profesionales if p['usuario'] == usuario_input and p['contrasena'] == password_input), None)
        
        if usuario_encontrado:
            session['usuario_actual'] = usuario_encontrado
            return redirect(url_for('dashboard_personal_bp.dashboard2')) 
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
    return render_template('login.html')

@dashboard_loguin_bp.route('/dashboard')
def dashboard():
    """ DASHBOARD GENERAL: Muestra estadísticas de TODA la clínica """
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    profesional = session['usuario_actual']
    
    # Si es Auxiliar, no debería ver el general, lo mandamos al personal
    if profesional.get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard_personal_bp.dashboard2'))
    
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

@dashboard_loguin_bp.route('/logout')
def logout():
    session.pop('usuario_actual', None)
    return redirect(url_for('dashboard_loguin_bp.login'))

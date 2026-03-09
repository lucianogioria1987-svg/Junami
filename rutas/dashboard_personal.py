from flask import Blueprint, render_template, request, redirect, url_for, session
import os
import json
from datetime import datetime
from utils import cargar_datos, obtener_mapa_fotos_pacientes, procesar_fecha

dashboard_personal_bp = Blueprint('dashboard_personal_bp', __name__)

@dashboard_personal_bp.route('/dashboard2')
def dashboard2():
    if 'usuario_actual' not in session:
        return redirect(url_for('dashboard_loguin_bp.login'))

    profesional = session['usuario_actual']
    
    # 1. Procesamiento de Turnos
    todas_sesiones = cargar_datos('sesiones.json')
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia_hoy_texto = dias_semana[datetime.now().weekday()]
    
    turnos_hoy = []
    for s in todas_sesiones:
        if dia_hoy_texto in s.get('dias', []) and s.get('profesional_nombre') == profesional['nombre']:
            turno_display = s.copy()
            turno_display.setdefault('estado_turno', 'Confirmado')
            turnos_hoy.append(turno_display)
            
    # Ordenar por hora
    turnos_hoy.sort(key=lambda x: x.get('hora', '00:00'))

    # 2. Procesamiento de Pacientes
    todos_pacientes = cargar_datos('pacientes.json')
    mis_pacientes = [p for p in todos_pacientes if profesional['nombre'] in p.get('profesionales', [])]
    
    # 3. Procesamiento de Equipo
    todos_profesionales = cargar_datos('profesionales.json')
    mi_equipo = []
    if profesional.get('jerarquia') == 'Titular':
        mi_equipo = [p for p in todos_profesionales if p.get('supervisor') == profesional['nombre']]
        
    # 4. Procesamiento de Recordatorios
    todos_recordatorios = cargar_datos('recordatorios.json')
    mis_recordatorios = [r for r in todos_recordatorios if r.get('usuario') == profesional['usuario']]
    mis_recordatorios.sort(key=lambda x: (x.get('fecha_iso', ''), x.get('hora', '')))

    mapa_fotos_pacientes = obtener_mapa_fotos_pacientes(todos_pacientes)
    
    # Añadir foto de paciente a los turnos
    for t in turnos_hoy:
        t['foto_paciente'] = mapa_fotos_pacientes.get(t['id_paciente'])

    stats = {
        "pacientes": len(mis_pacientes),
        "turnos_hoy": len(turnos_hoy),
        "equipo": len(mi_equipo) if mi_equipo else 0
    }

    return render_template('dashboard2.html', 
                           profesional=profesional, 
                           mis_pacientes=mis_pacientes, 
                           sesiones=turnos_hoy,
                           mi_equipo=mi_equipo,
                           recordatorios=mis_recordatorios,
                           mapa_fotos_pacientes=mapa_fotos_pacientes,
                           dia_hoy=dia_hoy_texto,
                           stats=stats)

@dashboard_personal_bp.route('/recordatorio/nuevo', methods=['POST'])
def nuevo_recordatorio():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    lista = cargar_datos('recordatorios.json')
    nid = 1 if not lista else lista[-1]['id'] + 1
    
    fecha_guardar = procesar_fecha(request.form['fecha'])
    lista.append({
        "id": nid, "usuario": session['usuario_actual']['usuario'], "titulo": request.form['titulo'], "tipo": request.form['tipo'],
        "fecha": fecha_guardar, "fecha_iso": request.form['fecha'], "hora": request.form['hora'], "notas": request.form['notas']
    })
    with open(os.path.join('datos', 'recordatorios.json'), 'w', encoding='utf-8') as f: json.dump(lista, f, indent=4, ensure_ascii=False)
    return redirect(url_for('dashboard_personal_bp.dashboard2'))

@dashboard_personal_bp.route('/recordatorio/borrar/<int:id>')
def borrar_recordatorio(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    lista = [r for r in cargar_datos('recordatorios.json') if r['id'] != id]
    with open(os.path.join('datos', 'recordatorios.json'), 'w', encoding='utf-8') as f: json.dump(lista, f, indent=4, ensure_ascii=False)
    return redirect(url_for('dashboard_personal_bp.dashboard2'))

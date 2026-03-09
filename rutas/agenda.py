from flask import Blueprint, render_template, request, redirect, url_for, session
import os
import json
from utils import cargar_datos, obtener_mapa_fotos_pacientes, obtener_mapa_fotos_profesionales

agenda_bp = Blueprint('agenda_bp', __name__)

@agenda_bp.route('/agenda', methods=['GET', 'POST'])
def agenda():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    profesional = session['usuario_actual']
    if profesional.get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard_personal_bp.dashboard2'))

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
            "id": nid, 
            "id_paciente": id_paciente, 
            "nombre_paciente": nombre_p,
            "dias": dias, 
            "hora": hora, 
            "tipo": request.form['tipo'],
            "consultorio": request.form['consultorio'],
            "profesional_nombre": profesional['nombre'], 
            "profesional_especialidad": profesional['rol'], 
            "estado_turno": "Confirmado"
        }
        sesiones.append(nueva)
        with open(os.path.join('datos', 'sesiones.json'), 'w', encoding='utf-8') as f:
            json.dump(sesiones, f, indent=4, ensure_ascii=False)
        return redirect(url_for('agenda_bp.agenda'))
                
    return render_template('agenda.html', profesional=profesional, turnos=sesiones, pacientes=pacientes)

@agenda_bp.route('/turno/cambiar_estado/<int:id>/<string:nuevo_estado>')
def cambiar_estado_turno(id, nuevo_estado):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    sesiones = cargar_datos('sesiones.json')
    for s in sesiones:
        if s['id'] == id: 
            s['estado_turno'] = nuevo_estado
            break
    with open(os.path.join('datos', 'sesiones.json'), 'w', encoding='utf-8') as f: 
        json.dump(sesiones, f, indent=4, ensure_ascii=False)
    # Según la especificación, debe redirigir a dashboard2
    return redirect(url_for('dashboard_personal_bp.dashboard2'))

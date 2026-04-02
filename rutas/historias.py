from flask import Blueprint, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime
from utils import cargar_datos, obtener_mapa_fotos_profesionales

historias_bp = Blueprint('historias_bp', __name__)

@historias_bp.route('/historias', methods=['GET', 'POST'])
def historias():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    profesional = session['usuario_actual']
    
    if profesional.get('jerarquia') == 'Auxiliar' and not request.args.get('id_paciente'):
         return redirect(url_for('dashboard_personal_bp.dashboard2'))

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

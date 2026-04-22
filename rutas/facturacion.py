from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import json
import os
from datetime import datetime
from utils import cargar_datos, cargar_configuracion

facturacion_bp = Blueprint('facturacion_bp', __name__)

@facturacion_bp.route('/facturacion', methods=['GET', 'POST'])
def facturacion():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    if session['usuario_actual'].get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard_personal_bp.dashboard2'))

    config = cargar_configuracion()
    if not config.get('licencia_activa', {}).get('facturacion', True):
        flash('Módulo de Facturación no contratado')
        return redirect(url_for('profesionales'))

    pagos = cargar_datos('pagos.json')
    pacientes = [p for p in cargar_datos('pacientes.json') if p.get('activo', True)]
    mapa_pacientes = {p['id']: p['nombre'] for p in pacientes}
    
    if request.method == 'POST':
        nid = 1 if not pagos else pagos[-1]['id'] + 1
        
        f_serv = datetime.strptime(request.form['fecha_servicio'], '%Y-%m-%d')
        f_pago = datetime.strptime(request.form['fecha_pago'], '%Y-%m-%d')
        
        pagos.append({
            "id": nid, 
            "id_paciente": int(request.form['id_paciente']), 
            "obra_social": request.form['obra_social'], 
            "monto": int(request.form['monto']),
            "fecha_servicio": f_serv.strftime("%d/%m/%Y"), 
            "fecha_pago": f_pago.strftime("%d/%m/%Y"),
            "dias_demora": (f_pago - f_serv).days,
            "usuario_registro": session['usuario_actual']['nombre'],
            "fecha_registro_sistema": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })
        with open(os.path.join('datos', 'pagos.json'), 'w', encoding='utf-8') as f: json.dump(pagos, f, indent=4, ensure_ascii=False)
        return redirect(url_for('facturacion'))

    pagos.sort(key=lambda x: datetime.strptime(x['fecha_pago'], "%d/%m/%Y"), reverse=True)
    return render_template('facturacion.html', profesional=session['usuario_actual'], pagos=pagos, pacientes=pacientes, mapa_pacientes=mapa_pacientes)

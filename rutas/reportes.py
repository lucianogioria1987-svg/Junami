from flask import Blueprint, render_template, request, redirect, url_for, session
from utils import cargar_datos

reportes_bp = Blueprint('reportes_bp', __name__)

@reportes_bp.route('/reportes', methods=['GET', 'POST'])
def reportes():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    if session['usuario_actual'].get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard_personal_bp.dashboard2'))

    pacientes = [p for p in cargar_datos('pacientes.json') if p.get('activo', True)]
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

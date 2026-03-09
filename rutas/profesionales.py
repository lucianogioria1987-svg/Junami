from flask import Blueprint, render_template, request, redirect, url_for, session
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from utils import cargar_datos

profesionales_bp = Blueprint('profesionales_bp', __name__)

@profesionales_bp.route('/profesionales', methods=['GET', 'POST'])
def profesionales():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    profesional = session['usuario_actual']
    if profesional.get('jerarquia') == 'Auxiliar': return redirect(url_for('dashboard_personal_bp.dashboard2'))

    lista = cargar_datos('profesionales.json')
    areas = {}
    titulares = [p for p in lista if p.get('jerarquia') == 'Titular']
    for p in lista: areas.setdefault(p['rol'], []).append(p)
    
    if request.method == 'POST':
        nid = 1 if not lista else lista[-1]['id'] + 1
        foto = None
        if 'foto_perfil' in request.files and request.files['foto_perfil'].filename != '':
            foto = secure_filename(f"profesional_{nid}.{request.files['foto_perfil'].filename.split('.')[-1]}")
            request.files['foto_perfil'].save(os.path.join(current_app.config['UPLOAD_FOLDER'], foto))
        
        lista.append({
            "id": nid, "nombre": request.form['nombre'], "usuario": request.form['usuario'], "contrasena": request.form['contrasena'], "rol": request.form['rol'],
            "iniciales": request.form['iniciales'].upper(), "foto": foto, "jerarquia": request.form.get('jerarquia', 'Titular'), "supervisor": request.form.get('supervisor'),
            "dni": request.form.get('dni', ''), "edad": request.form.get('edad', ''), "domicilio": request.form.get('domicilio', ''), "universidad": request.form.get('universidad', ''), "telefono": request.form.get('telefono', ''), "email": request.form.get('email', ''), "matricula": request.form.get('matricula', '')
        })
        with open(os.path.join('datos', 'profesionales.json'), 'w', encoding='utf-8') as f: json.dump(lista, f, indent=4, ensure_ascii=False)
        return redirect(url_for('profesionales'))
    return render_template('profesionales.html', profesional=profesional, lista_profesionales=lista, areas=areas, titulares=titulares)

@profesionales_bp.route('/profesional/editar/<int:id>', methods=['POST'])
def editar_profesional(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
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
                request.files['foto_perfil'].save(os.path.join(current_app.config['UPLOAD_FOLDER'], nom))
                p['foto'] = nom
            break
    with open(os.path.join('datos', 'profesionales.json'), 'w', encoding='utf-8') as f: json.dump(lista, f, indent=4, ensure_ascii=False)
    return redirect(url_for('profesionales'))

@profesionales_bp.route('/profesional/<int:id>')
def perfil_profesional(id):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    profesionales = cargar_datos('profesionales.json')
    pacientes = cargar_datos('pacientes.json')
    prof_ver = next((p for p in profesionales if p['id'] == id), None)
    
    pacientes_cargo = [p for p in pacientes if 'profesionales' in p and prof_ver['nombre'] in p['profesionales']]
    pacientes_disponibles = [p for p in pacientes if 'profesionales' not in p or prof_ver['nombre'] not in p['profesionales']]
    auxiliares = [p for p in profesionales if p.get('supervisor') == prof_ver['nombre']] if prof_ver.get('jerarquia') == 'Titular' else []
    return render_template('ficha_profesional.html', profesional=session['usuario_actual'], prof_ver=prof_ver, pacientes=pacientes_cargo, pacientes_disponibles=pacientes_disponibles, equipo_supervisado=auxiliares)

@profesionales_bp.route('/profesional/asignar_paciente', methods=['POST'])
def asignar_paciente_a_profesional():
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
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

@profesionales_bp.route('/especialidad/<string:nombre_especialidad>')
def detalle_especialidad(nombre_especialidad):
    if 'usuario_actual' not in session: return redirect(url_for('dashboard_loguin_bp.login'))
    profesionales = cargar_datos('profesionales.json')
    pacientes = cargar_datos('pacientes.json')
    sesiones = cargar_datos('sesiones.json')
    
    equipo = [p for p in profesionales if p['rol'] == nombre_especialidad]
    nombres_equipo = [p['nombre'] for p in equipo]
    pacientes_area = [p for p in pacientes if 'profesionales' in p and any(pr in p['profesionales'] for pr in nombres_equipo)]
    turnos_area = [s for s in sesiones if s.get('profesional_especialidad') == nombre_especialidad]
    
    return render_template('detalle_especialidad.html', profesional=session['usuario_actual'], especialidad=nombre_especialidad, titulares=[p for p in equipo if p.get('jerarquia')=='Titular'], auxiliares=[p for p in equipo if p.get('jerarquia')!='Titular'], pacientes=pacientes_area, turnos=turnos_area)

# Removed configuracion routes

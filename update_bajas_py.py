import json
import os

filepath = r"c:\Users\lucia\OneDrive\Escritorio\Junami 3.0\rutas\bajas.py"

new_content = """from flask import Blueprint, render_template, session, redirect, url_for, flash, request
import json
import os

bajas_bp = Blueprint('bajas', __name__)

@bajas_bp.route('/bajas')
def index():
    profesional = session.get('usuario_actual')
    print("DEBUG Bajas - Profesional en sesión:", profesional)
    
    if not profesional or profesional.get('jerarquia') != 'Titular':
        print("DEBUG Bajas - Acceso denegado. Razón: No hay profesional o no es Titular.")
        flash('Acceso denegado: Se requieren permisos de Titular para ingresar a Bajas.', 'error')
        return redirect(url_for('dashboard_loguin_bp.dashboard'))
        
    pacientes = []
    profesionales = []
    
    try:
        with open('datos/pacientes.json', 'r', encoding='utf-8') as f:
            pacientes = json.load(f)
            print("DEBUG Bajas - Pacientes cargados:", len(pacientes))
    except Exception as e:
        print("DEBUG Bajas - Error al cargar pacientes:", str(e))
        
    try:
        with open('datos/profesionales.json', 'r', encoding='utf-8') as f:
            profesionales = json.load(f)
            print("DEBUG Bajas - Profesionales cargados:", len(profesionales))
    except Exception as e:
        print("DEBUG Bajas - Error al cargar profesionales:", str(e))
        
    return render_template('bajas.html', pacientes=pacientes, profesionales=profesionales, profesional=profesional)

@bajas_bp.route('/bajas/eliminar', methods=['POST'])
def eliminar_entidad():
    profesional_actual = session.get('usuario_actual')
    if not profesional_actual or profesional_actual.get('jerarquia') != 'Titular':
        flash('Acceso denegado: Se requieren permisos de Titular.', 'error')
        return redirect(url_for('dashboard_loguin_bp.dashboard'))
        
    entidad_id = request.form.get('paciente_id') # Form name kept as paciente_id for generic ID mapping
    motivo = request.form.get('motivo')
    tipo = request.form.get('tipo', 'paciente') # 'paciente' or 'profesional'
    
    print(f"DEBUG Bajas - Intentando eliminar {tipo} ID: {entidad_id}")
    print(f"DEBUG Bajas - Motivo de la baja: {motivo}")
    
    if not entidad_id or not motivo:
        flash('Error: Faltan datos para procesar la baja.', 'error')
        return redirect(url_for('bajas.index'))
        
    try:
        if tipo == 'profesional':
            filepath_json = 'datos/profesionales.json'
            with open(filepath_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                
            entidad_a_eliminar = next((p for p in datos if str(p.get('id')) == str(entidad_id)), None)
            
            if entidad_a_eliminar:
                datos = [p for p in datos if str(p.get('id')) != str(entidad_id)]
                with open(filepath_json, 'w', encoding='utf-8') as f:
                    json.dump(datos, f, indent=4, ensure_ascii=False)
                flash(f'Profesional {entidad_a_eliminar["nombre"]} dado de baja exitosamente.', 'success')
                print(f"DEBUG Bajas - Profesional {entidad_a_eliminar['nombre']} eliminado exitosamente del JSON.")
            else:
                flash('Error: Profesional no encontrado.', 'error')
                
        else:
            filepath_json = 'datos/pacientes.json'
            with open(filepath_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                
            entidad_a_eliminar = next((p for p in datos if str(p.get('id')) == str(entidad_id)), None)
            
            if entidad_a_eliminar:
                datos = [p for p in datos if str(p.get('id')) != str(entidad_id)]
                with open(filepath_json, 'w', encoding='utf-8') as f:
                    json.dump(datos, f, indent=4, ensure_ascii=False)
                flash(f'Paciente {entidad_a_eliminar["nombre"]} dado de baja exitosamente.', 'success')
                print(f"DEBUG Bajas - Paciente {entidad_a_eliminar['nombre']} eliminado exitosamente del JSON.")
            else:
                flash('Error: Paciente no encontrado.', 'error')
                
    except Exception as e:
        print("DEBUG Bajas - Error al procesar baja:", str(e))
        flash(f'Hubo un error al procesar la baja del {tipo}.', 'error')
        
    return redirect(url_for('bajas.index'))
"""

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

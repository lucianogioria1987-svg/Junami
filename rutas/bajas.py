from flask import Blueprint, render_template, session, redirect, url_for, flash, request
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
        
    try:
        with open('datos/pacientes.json', 'r', encoding='utf-8') as f:
            pacientes_activos = json.load(f)
    except Exception as e:
        print("DEBUG Bajas - Error al cargar pacientes:", str(e))
        pacientes_activos = []
        
    try:
        with open('datos/profesionales.json', 'r', encoding='utf-8') as f:
            profesionales_activos = json.load(f)
    except Exception as e:
        print("DEBUG Bajas - Error al cargar profesionales:", str(e))
        profesionales_activos = []

    try:
        with open('datos/bajas_pacientes.json', 'r', encoding='utf-8') as f:
            pacientes_bajas = json.load(f)
    except Exception as e:
        print("DEBUG Bajas - Error al cargar bajas_pacientes.json:", str(e))
        pacientes_bajas = []
        
    try:
        with open('datos/bajas_profesionales.json', 'r', encoding='utf-8') as f:
            profesionales_bajas = json.load(f)
    except Exception as e:
        print("DEBUG Bajas - Error al cargar bajas_profesionales.json:", str(e))
        profesionales_bajas = []
        
    return render_template('bajas.html', pacientes_activos=pacientes_activos, pacientes_bajas=pacientes_bajas, profesionales_activos=profesionales_activos, profesionales_bajas=profesionales_bajas, profesional=profesional)

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
        filepath_json = 'datos/profesionales.json' if tipo == 'profesional' else 'datos/pacientes.json'
        with open(filepath_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            
        entidad_a_eliminar = next((p for p in datos if str(p.get('id')) == str(entidad_id)), None)
        
        if entidad_a_eliminar:
            # Eliminar del listado activo
            datos = [p for p in datos if str(p.get('id')) != str(entidad_id)]
            
            entidad_a_eliminar['activo'] = False
            entidad_a_eliminar['motivo_baja'] = motivo
            entidad_a_eliminar['tipo_entidad'] = tipo
            
            with open(filepath_json, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
                
            # Agregar al historico de bajas correspondiente
            filepath_bajas = 'datos/bajas_profesionales.json' if tipo == 'profesional' else 'datos/bajas_pacientes.json'
            bajas_data = []
            if os.path.exists(filepath_bajas):
                with open(filepath_bajas, 'r', encoding='utf-8') as f:
                    try:
                        bajas_data = json.load(f)
                    except json.JSONDecodeError:
                        bajas_data = []

            bajas_data.append(entidad_a_eliminar)
            with open(filepath_bajas, 'w', encoding='utf-8') as f:
                json.dump(bajas_data, f, indent=4, ensure_ascii=False)
                
            label = 'Profesional' if tipo == 'profesional' else 'Paciente'
            flash(f'{label} {entidad_a_eliminar["nombre"]} movido a bajas exitosamente.', 'success')
            print(f"DEBUG Bajas - {label} {entidad_a_eliminar['nombre']} movido a {filepath_bajas}.")
        else:
            flash(f'Error: {tipo.capitalize()} no encontrado.', 'error')
                
    except Exception as e:
        print("DEBUG Bajas - Error al procesar baja:", str(e))
        flash(f'Hubo un error al procesar la baja del {tipo}.', 'error')
        
    return redirect(url_for('bajas.index'))

@bajas_bp.route('/bajas/alta', methods=['POST'])
def restaurar_entidad():
    profesional_actual = session.get('usuario_actual')
    if not profesional_actual or profesional_actual.get('jerarquia') != 'Titular':
        flash('Acceso denegado: Se requieren permisos de Titular.', 'error')
        return redirect(url_for('dashboard_loguin_bp.dashboard'))
        
    entidad_id = request.form.get('paciente_id')
    tipo = request.form.get('tipo', 'paciente')
    
    if not entidad_id:
        flash('Error: Faltan datos para procesar el alta.', 'error')
        return redirect(url_for('bajas.index'))
        
    try:
        filepath_bajas = 'datos/bajas_profesionales.json' if tipo == 'profesional' else 'datos/bajas_pacientes.json'
        bajas_data = []
        if os.path.exists(filepath_bajas):
            with open(filepath_bajas, 'r', encoding='utf-8') as f:
                try: bajas_data = json.load(f)
                except: pass
                
        entidad_a_restaurar = next((p for p in bajas_data if str(p.get('id')) == str(entidad_id)), None)
        
        if entidad_a_restaurar:
            # Eliminar del archivo de bajas específico
            bajas_data = [p for p in bajas_data if str(p.get('id')) != str(entidad_id)]
            with open(filepath_bajas, 'w', encoding='utf-8') as f:
                json.dump(bajas_data, f, indent=4, ensure_ascii=False)
                
            # Limpiar metadato y activar
            entidad_a_restaurar['activo'] = True
            if 'tipo_entidad' in entidad_a_restaurar:
                del entidad_a_restaurar['tipo_entidad']
                
            # Agregar al json original
            filepath_json = 'datos/profesionales.json' if tipo == 'profesional' else 'datos/pacientes.json'
            original_data = []
            with open(filepath_json, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
            
            original_data.append(entidad_a_restaurar)
            with open(filepath_json, 'w', encoding='utf-8') as f:
                json.dump(original_data, f, indent=4, ensure_ascii=False)
                
            label = 'Profesional' if tipo == 'profesional' else 'Paciente'
            flash(f'{label} {entidad_a_restaurar["nombre"]} dado de alta exitosamente.', 'success')
        else:
            flash(f'Error: {tipo.capitalize()} inactivo no encontrado.', 'error')
                
    except Exception as e:
        print("DEBUG Bajas - Error al procesar alta:", str(e))
        flash(f'Hubo un error al procesar el alta del {tipo}.', 'error')
        
    return redirect(url_for('bajas.index'))

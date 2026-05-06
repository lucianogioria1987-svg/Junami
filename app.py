# 1. IMPORTACIONES PRINCIPALES DE FLASK Y PYTHON
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
from datetime import datetime

# 2. INICIALIZACIÓN DE LA APLICACIÓN
app = Flask(__name__, template_folder='plantillas')
app.secret_key = 'nidus_clave_secreta_segura'

# 3. CONFIGURACIÓN DE DIRECTORIOS
# Configuración de carpeta para subir archivos
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB limit para subir archivos


# 4. IMPORTACIÓN DE UTILIDADES LOCALES
from utils import cargar_datos, obtener_mapa_fotos_pacientes, obtener_mapa_fotos_profesionales, procesar_fecha, cargar_configuracion

# 5. FILTROS GLOBALES DE JINJA (FRONTEND)
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

from flask import flash

# --- CONTEXT PROCESSOR PARA CONFIGURACIÓN GLOBAL ---
@app.context_processor
def inyectar_configuracion():
    config = cargar_configuracion()
    
    # Mensajería global y lista de profesionales
    mensajes_sin_leer = 0
    lista_profesionales = []
    
    # Cargar pacientes globalmente de forma segura
    try:
        pacientes_data = cargar_datos('pacientes.json')
        lista_pacientes = [{"id": p["id"], "nombre": p["nombre"]} for p in pacientes_data if 'nombre' in p and 'id' in p]
    except Exception:
        lista_pacientes = []

    if 'usuario_actual' in session:
        mi_id = session['usuario_actual']['id']
        mensajes = cargar_datos('mensajeria.json')
        
        # Contar mensajes donde el último receptor es el usuario y está sin leer
        mensajes_sin_leer = sum(1 for m in mensajes if m.get('leido') == False and 
                    (m.get('respuestas')[-1]['emisor_id'] != mi_id if m.get('respuestas') else m.get('receptor_id') == mi_id))
        
        # Excluir al propio usuario de los posibles destinatarios
        lista_profesionales = [p for p in cargar_datos('profesionales.json') if p.get('activo', True) and p['id'] != mi_id]

    return dict(
        licencia_activa=config.get('licencia_activa', {}), 
        config_visual=config.get('config_visual', {}),
        mensajes_sin_leer=mensajes_sin_leer,
        lista_profesionales_global=lista_profesionales,
        lista_pacientes_global=lista_pacientes
    )

# ==========================================
# 1. LOGIN Y DASHBOARD (Extraído a Blueprint)
# ==========================================
from rutas.dashboard_y_loguin import dashboard_loguin_bp
from rutas.dashboard_personal import dashboard_personal_bp
app.register_blueprint(dashboard_loguin_bp)

# ==========================================
# 2. DASHBOARD PERSONAL (Extraído a Blueprint)
# ==========================================
app.register_blueprint(dashboard_personal_bp)
app.add_url_rule("/", endpoint="login", view_func=app.view_functions["dashboard_loguin_bp.login"])
app.add_url_rule("/dashboard", endpoint="dashboard", view_func=app.view_functions["dashboard_loguin_bp.dashboard"])
app.add_url_rule("/logout", endpoint="logout", view_func=app.view_functions["dashboard_loguin_bp.logout"])

# ==========================================
# 3. GESTIÓN DE PACIENTES (Extraído a Blueprint)
# ==========================================
from rutas.pacientes import pacientes_bp
app.register_blueprint(pacientes_bp)
app.add_url_rule("/pacientes", endpoint="pacientes", view_func=app.view_functions["pacientes_bp.pacientes"])
app.add_url_rule("/pacientes/nuevo", endpoint="crear_paciente", view_func=app.view_functions["pacientes_bp.crear_paciente"], methods=["GET", "POST"])
app.add_url_rule("/paciente/<int:id>", endpoint="perfil_paciente", view_func=app.view_functions["pacientes_bp.perfil_paciente"])
app.add_url_rule("/paciente/editar/<int:id>", endpoint="editar_paciente", view_func=app.view_functions["pacientes_bp.editar_paciente"], methods=["GET", "POST"])
app.add_url_rule("/paciente/subir_archivo", endpoint="subir_archivo_paciente", view_func=app.view_functions["pacientes_bp.subir_archivo_paciente"], methods=["POST"])
app.add_url_rule("/paciente/estado/<int:id>", endpoint="toggle_estado_paciente", view_func=app.view_functions["pacientes_bp.toggle_estado_paciente"])
app.add_url_rule("/paciente/asignar_turno/<int:id>", endpoint="asignar_turno", view_func=app.view_functions["pacientes_bp.asignar_turno"], methods=["POST"])
app.add_url_rule("/paciente/guardar_plan/<int:id>", endpoint="guardar_planificacion", view_func=app.view_functions["pacientes_bp.guardar_planificacion"], methods=["POST"])
app.add_url_rule("/paciente/actualizar_equipo/<int:id>", endpoint="actualizar_equipo", view_func=app.view_functions["pacientes_bp.actualizar_equipo"], methods=["POST"])
app.add_url_rule("/paciente/guardar_evolucion/<int:id>", endpoint="guardar_evolucion_paciente", view_func=app.view_functions["pacientes_bp.guardar_evolucion_paciente"], methods=["POST"])
app.add_url_rule("/paciente/imprimir/<int:id>/<string:seccion>", endpoint="imprimir_seccion", view_func=app.view_functions["pacientes_bp.imprimir_seccion"])
app.add_url_rule("/paciente/asignar_horario/<int:id>", endpoint="asignar_horario_fijo", view_func=app.view_functions["pacientes_bp.asignar_horario_fijo"], methods=["POST"])

# ==========================================
# 4. ADMISIONES (Extraído a Blueprint)
# ==========================================
from rutas.admisiones import admisiones_bp
app.register_blueprint(admisiones_bp)
app.add_url_rule("/admisiones", endpoint="admisiones", view_func=app.view_functions["admisiones_bp.admisiones"])
app.add_url_rule("/admision/<int:id>", endpoint="perfil_admision", view_func=app.view_functions["admisiones_bp.perfil_admision"])
app.add_url_rule("/admision/alta/<int:id>", endpoint="alta_admision", view_func=app.view_functions["admisiones_bp.alta_admision"])
app.add_url_rule("/admision/borrar/<int:id>", endpoint="borrar_admision", view_func=app.view_functions["admisiones_bp.borrar_admision"])
app.add_url_rule("/admision/imprimir/<int:id>", endpoint="imprimir_admision", view_func=app.view_functions["admisiones_bp.imprimir_admision"])

# ==========================================
# 5. AGENDA Y TURNOS (Extraído a Blueprint)
# ==========================================
from rutas.agenda import agenda_bp
app.register_blueprint(agenda_bp)
app.add_url_rule("/agenda", endpoint="agenda", view_func=app.view_functions["agenda_bp.agenda"])
app.add_url_rule("/turno/cambiar_estado/<int:id>/<string:nuevo_estado>", endpoint="cambiar_estado_turno", view_func=app.view_functions["agenda_bp.cambiar_estado_turno"])

# ==========================================
# 6. HISTORIAS CLINICAS (Extraído a Blueprint)
# ==========================================
from rutas.historias import historias_bp
app.register_blueprint(historias_bp)
app.add_url_rule("/historias", endpoint="historias", view_func=app.view_functions["historias_bp.historias"], methods=["GET", "POST"])

# ==========================================
# 7. REPORTES (Extraído a Blueprint)
# ==========================================
from rutas.reportes import reportes_bp
app.register_blueprint(reportes_bp)
app.add_url_rule("/reportes", endpoint="reportes", view_func=app.view_functions["reportes_bp.reportes"], methods=["GET", "POST"])

# ==========================================
# 8. MÓDULO DE PROFESIONALES
# ==========================================
from rutas.profesionales import profesionales_bp
app.register_blueprint(profesionales_bp)
app.add_url_rule("/profesionales", endpoint="profesionales", view_func=app.view_functions["profesionales_bp.profesionales"], methods=["GET", "POST"])
app.add_url_rule("/profesional/editar/<int:id>", endpoint="editar_profesional", view_func=app.view_functions["profesionales_bp.editar_profesional"], methods=["POST"])
app.add_url_rule("/profesional/<int:id>", endpoint="perfil_profesional", view_func=app.view_functions["profesionales_bp.perfil_profesional"])
app.add_url_rule("/profesional/asignar_paciente", endpoint="asignar_paciente_a_profesional", view_func=app.view_functions["profesionales_bp.asignar_paciente_a_profesional"], methods=["POST"])
app.add_url_rule("/especialidad/<string:nombre_especialidad>", endpoint="detalle_especialidad", view_func=app.view_functions["profesionales_bp.detalle_especialidad"])

# ==========================================
# 9. MÓDULO DE FACTURACIÓN Y PAGOS 
# ==========================================
from rutas.facturacion import facturacion_bp
app.register_blueprint(facturacion_bp)
app.add_url_rule("/facturacion", endpoint="facturacion", view_func=app.view_functions["facturacion_bp.facturacion"], methods=["GET", "POST"])

# ==========================================
# 10. MÓDULO DE CONFIGURACIÓN Y BACKUPS
# ==========================================
from rutas.configuracion import configuracion_bp
app.register_blueprint(configuracion_bp)
app.add_url_rule("/configuracion", endpoint="configuracion", view_func=app.view_functions["configuracion_bp.configuracion"], methods=["GET", "POST"])
app.add_url_rule("/configuracion/nuevo_profesional", endpoint="nuevo_prof_desde_config", view_func=app.view_functions["configuracion_bp.nuevo_prof_desde_config"], methods=["POST"])
app.add_url_rule("/configuracion/backup", endpoint="descargar_backup", view_func=app.view_functions["configuracion_bp.descargar_backup"])

# ==========================================
# 11. MÓDULOS DE ÁREAS ESPECIALIZADAS
# ==========================================
from modulos.teo import teo_bp
from modulos.fono import fono_bp
from modulos.psico import psico_bp
from modulos.psicoped import psicoped_bp

app.register_blueprint(teo_bp)
app.register_blueprint(fono_bp)
app.register_blueprint(psico_bp)
app.register_blueprint(psicoped_bp)

# ==========================================
# 12. MÓDULO DE BAJAS
# ==========================================
from rutas.bajas import bajas_bp
app.register_blueprint(bajas_bp)

# ==========================================
# 13. MÓDULO DE MENSAJERÍA
# ==========================================
from rutas.mensajeria import mensajeria_bp
app.register_blueprint(mensajeria_bp)



if __name__ == '__main__':
    app.run(debug=True, port=5000)
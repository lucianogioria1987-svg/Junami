import os
import json
from datetime import datetime

# --- HELPER: Cargar JSON ---
def cargar_datos(nombre_archivo):
    ruta = os.path.join('datos', nombre_archivo)
    try:
        with open(ruta, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []

# --- HELPER: Cargar Configuración ---
def cargar_configuracion():
    ruta = os.path.join('datos', 'config_clinica.json')
    try:
        with open(ruta, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return {}

# --- HELPER: Mapas de Fotos ---
def obtener_mapa_fotos_pacientes(pacientes):
    return {p['id']: p.get('foto') for p in pacientes}

def obtener_mapa_fotos_profesionales(profesionales):
    return {p['nombre']: p.get('foto') for p in profesionales}

# --- LÓGICA DE FECHAS (Backend) ---
def procesar_fecha(fecha_ymd):
    """
    Función Backend: Transforma '2025-12-31' (Input HTML) -> '31/12/2025' (JSON)
    """
    if not fecha_ymd: return ""
    try:
        return datetime.strptime(fecha_ymd, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        return fecha_ymd

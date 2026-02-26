import json
import os
import random
from datetime import datetime, timedelta

CARPETA = 'datos'
ARCHIVO_SALIDA = os.path.join(CARPETA, 'pacientes.json')
ARCHIVO_PROFS = os.path.join(CARPETA, 'profesionales.json')
CANTIDAD = 140

# --- DATOS BASE ---
nombres = ["Thiago", "Mateo", "Benjamín", "Felipe", "Bautista", "Juan", "Tomás", "Santiago", "Nicolás", "Lautaro", "Sofía", "María", "Lucía", "Catalina", "Agustina", "Valentina", "Martina", "Camila", "Julieta", "Renata", "Bruno", "Dante", "Gael", "Mía", "Emma"]
apellidos = ["García", "Rodríguez", "González", "Fernández", "López", "Martínez", "Pérez", "Gómez", "Sánchez", "Díaz", "Romero", "Sosa", "Torres", "Ruiz", "Flores", "Benítez", "Acosta", "Medina", "Herrera", "Suárez"]
calles = ["Av. San Martín", "Rivadavia", "Belgrano", "Mitre", "Sarmiento", "Moreno", "Alberdi", "Colon", "Las Heras", "Av. Perón"]

# --- DATOS CLÍNICOS ---
diagnosticos = ["TEA - Integración sensorial", "Retraso madurativo", "Dispraxia motora", "TDAH", "Parálisis Cerebral", "Síndrome de Down", "Dificultades AVD", "Trastorno proc. sensorial", "Rehabilitación mano", "Dif. aprendizaje", "Trastorno del Lenguaje"]
neurologos = ["Dr. Funes", "Dra. Kogan", "Dr. Anderson", "Dra. Blanco", "Hospital Gutiérrez", "Dr. Rossi"]
pediatras = ["Dra. Mónica Silva", "Dr. Jorge Pérez", "Dra. Ana Conti", "Clínica del Niño"]
obras_sociales = ["OSDE", "Prensa", "Colmed", "Subsidio", "Boreal", "Swiss Medical", "Particular"]

# --- DATOS ESCOLARES ---
escuelas = ["Escuela Normal", "Colegio San Patricio", "Instituto Belgrano", "Escuela Sarmiento", "Colegio del Huerto", "Jardín de Infantes N°4", "Escuela Técnica N°1", "Colegio Montessori"]
grados = ["Sala de 3", "Sala de 4", "Sala de 5", "1er Grado", "2do Grado", "3er Grado", "4to Grado", "5to Grado", "1er Año Secundaria"]
turnos = ["Mañana", "Tarde", "Jornada Completa"]

# --- PLANIFICACIÓN ---
planes_anuales = ["Lograr mayor autonomía en actividades de la vida diaria.", "Fomentar habilidades sociales y juego compartido.", "Desarrollar estrategias de afrontamiento ante la frustración."]
objetivos_mensuales = ["1. Mantener la atención por 15 minutos.\n2. Lograr atado de cordones.", "1. Reconocimiento de emociones básicas.\n2. Uso de tijeras."]
sugerencias_hogar = ["Realizar juegos de fuerza antes de dormir.", "Fomentar que se vista solo los fines de semana."]

def generar():
    if not os.path.exists(ARCHIVO_PROFS):
        print("❌ Error: Ejecuta primero el script de profesionales.")
        return

    with open(ARCHIVO_PROFS, 'r', encoding='utf-8') as f: profesionales = json.load(f)
    nombres_profs = [p['nombre'] for p in profesionales]
    
    pacientes = []
    hoy = datetime.now()

    for i in range(1, CANTIDAD + 1):
        nombre = f"{random.choice(nombres)} {random.choice(apellidos)}"
        equipo = random.sample(nombres_profs, k=random.randint(1, 2))
        
        # Edad y Fecha
        edad = random.randint(2, 16)
        fecha_nac = (hoy - timedelta(days=edad*365)).strftime("%d/%m/%Y")
        
        # Familia 2.0
        apellido_padre = nombre.split()[1]
        nombre_padre = f"{random.choice(nombres)} {apellido_padre}"
        nombre_madre = f"{random.choice(nombres)} {random.choice(apellidos)}"
        estado_padres = random.choice(["Conviven", "Separados", "Monoparental"])
        vive_con = "Ambos" if estado_padres == "Conviven" else random.choice(["Madre", "Padre"])

        pacientes.append({
            "id": i,
            "activo": True,
            "fecha_ingreso": (hoy - timedelta(days=random.randint(30, 365))).strftime("%d/%m/%Y"),
            
            # Datos Básicos
            "nombre": nombre,
            "dni": f"{random.randint(40, 59)}.{random.randint(100, 999)}.{random.randint(100, 999)}",
            "fecha_nacimiento": fecha_nac,
            "edad": edad,
            "domicilio": f"{random.choice(calles)} {random.randint(100, 9000)}",
            "obra_social": random.choice(obras_sociales) if random.random() < 0.6 else "Particular",
            
            # Familia Completa (NUEVOS CAMPOS)
            "nombre_padre": nombre_padre,
            "tel_padre": f"381-{random.randint(4000, 9999)}",
            "domicilio_padre": f"{random.choice(calles)} {random.randint(100, 900)}",
            "nombre_madre": nombre_madre,
            "tel_madre": f"381-{random.randint(4000, 9999)}",
            "domicilio_madre": f"{random.choice(calles)} {random.randint(100, 900)}",
            "estado_padres": estado_padres,
            "vive_con": vive_con,
            "hermanos": f"{random.choice(nombres)} ({random.randint(2,15)})" if random.random() > 0.4 else "",
            "email": f"contacto.{i}@gmail.com",
            
            # Escolaridad
            "escuela_nombre": random.choice(escuelas),
            "escuela_grado": random.choice(grados),
            "escuela_turno": random.choice(turnos),
            "escuela_apoyo_nombre": "Lic. Gómez (AT)" if random.random() > 0.8 else "",

            # Clínica
            "diagnostico": random.choice(diagnosticos),
            "medico_cabecera": random.choice(pediatras),
            "neurologo": random.choice(neurologos),
            "tiene_terapias_previas": "Si" if random.random() > 0.6 else "No",
            "terapias_previas_desc": "Estimulación temprana" if random.random() > 0.6 else "",
            "profesionales": equipo,
            
            # Planificación (Editables)
            "plan_anual": random.choice(planes_anuales),
            "objetivos_mensuales": random.choice(objetivos_mensuales),
            "sugerencias_hogar": random.choice(sugerencias_hogar),
            
            # Archivos (Estructura de Listas 2.0)
            "informe_derivacion": None,
            "informe_diagnostico": [],
            "archivo_informes_previos": [],
            "informe_escolar": [],
            "archivos_adjuntos": [], 
            "informe": None, # Legacy
            "foto": None,
            
            # Agenda / Turnos (NUEVO)
            "turnos_programados": []
        })

    with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
        json.dump(pacientes, f, indent=4, ensure_ascii=False)
    print(f"✅ {CANTIDAD} Pacientes generados con estructura COMPLETA 2.0 en '{ARCHIVO_SALIDA}'.")

if __name__ == "__main__":
    generar()
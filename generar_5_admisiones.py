import json
import os
import random
from datetime import datetime, timedelta

CARPETA = 'datos'
ARCHIVO_SALIDA = os.path.join(CARPETA, 'admisiones.json')
ARCHIVO_PROFS = os.path.join(CARPETA, 'profesionales.json')
CANTIDAD = 8

nombres = ["Lucas", "Ambar", "Ciro", "Mia", "Lorenzo", "Isabella", "Bastián", "Emma"]
apellidos = ["Peralta", "Nuñez", "Cordoba", "Moyano", "Ferreyra", "Villarroel", "Paz", "Mendez"]
motivos = ["Dificultades escritura", "Selectividad alimentaria", "Evaluación CUD", "Retraso lenguaje", "Conducta disruptiva"]
obras_sociales = ["OSDE", "Prensa", "Colmed", "Subsidio", "Boreal", "Swiss Medical", "Particular"]
calles = ["Av. Aconquija", "San Martín", "Laprida", "25 de Mayo", "Corrientes"]

def generar():
    if not os.path.exists(ARCHIVO_PROFS):
        print("❌ Error: Faltan profesionales.")
        return

    with open(ARCHIVO_PROFS, 'r', encoding='utf-8') as f: profs = json.load(f)
    nombres_titulares = [p['nombre'] for p in profs if p.get('jerarquia') == 'Titular']

    admisiones = []
    hoy = datetime.now()
    
    for i in range(1, CANTIDAD + 1):
        nombre = f"{random.choice(nombres)} {random.choice(apellidos)}"
        fecha_sol = hoy - timedelta(days=random.randint(1, 20))
        
        tiene_fecha = random.random() < 0.5
        fecha_ent = (hoy + timedelta(days=random.randint(1, 10))).strftime("%d/%m/%Y") if tiene_fecha else ""
        hora_ent = f"{random.randint(9,18)}:00" if tiene_fecha else ""
        
        # Lógica Familiar
        estado_padres = random.choice(["Conviven", "Separados", "Monoparental"])
        vive_con = "Ambos" if estado_padres == "Conviven" else random.choice(["Madre", "Padre"])
        apellido_padre = nombre.split()[1]

        admisiones.append({
            "id": i,
            "estado": "Recibidos", 
            "fecha_solicitud": fecha_sol.strftime("%d/%m/%Y"),
            "fecha_entrevista": fecha_ent,
            "hora_entrevista": hora_ent,
            "prioridad": random.choice(["Alta", "Media", "Baja"]),
            "disponibilidad_preferencia": random.choice(["Mañana", "Tarde"]),
            "profesional_admision": random.choice(nombres_titulares) if nombres_titulares else "Sin asignar",
            
            # Datos Personales
            "nombre": nombre,
            "dni": f"{random.randint(45, 60)}.{random.randint(100, 999)}.{random.randint(100, 999)}",
            "edad": random.randint(2, 12),
            "domicilio": f"{random.choice(calles)} {random.randint(100, 900)}",
            "obra_social": random.choice(obras_sociales),
            
            # Familia (Estructura Completa)
            "nombre_madre": f"Ana {random.choice(apellidos)}", 
            "tel_madre": f"381-{random.randint(4000, 9999)}",
            "domicilio_madre": f"{random.choice(calles)} {random.randint(100, 900)}",
            
            "nombre_padre": f"Juan {apellido_padre}", 
            "tel_padre": f"381-{random.randint(4000, 9999)}",
            "domicilio_padre": f"{random.choice(calles)} {random.randint(100, 900)}",
            
            "estado_padres": estado_padres,
            "vive_con": vive_con,
            "hermanos": f"Hno/a ({random.randint(3, 15)} años)" if random.random() > 0.5 else "",
            "email": f"padres.{i}@gmail.com",

            # Escolaridad
            "escuela_nombre": "Escuela Sarmiento", 
            "escuela_grado": "1er Grado", 
            "escuela_turno": "Mañana",
            "escuela_apoyo_nombre": "Lic. López (AT)" if random.random() > 0.8 else "",

            # Clínica
            "motivo_consulta": random.choice(motivos),
            "medico_cabecera": "Dr. Pérez (Pediatra)", 
            "neurologo": "Dra. Funes" if random.random() > 0.5 else "",
            "tiene_terapias_previas": "Si" if random.random() > 0.5 else "No",
            "terapias_previas_desc": "Fonoaudiología el año pasado" if random.random() > 0.5 else "",

            # Archivos (Listas vacías para el nuevo sistema)
            "informe_diagnostico": [],
            "archivo_informes_previos": [],
            "informe_escolar": [],
            "informe_derivacion": None, 
            "informe_entrevista": None,
            "equipo_sugerido": []
        })

    with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
        json.dump(admisiones, f, indent=4, ensure_ascii=False)
    print(f"✅ REINICIO TOTAL: {CANTIDAD} Admisiones generadas con estructura 2.0.")

if __name__ == "__main__":
    generar()
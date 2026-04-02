import json
import os
import random
from datetime import datetime, timedelta

CARPETA = 'datos'
ARCHIVO_SALIDA = os.path.join(CARPETA, 'admisiones.json')
ARCHIVO_PROFS = os.path.join(CARPETA, 'profesionales.json')
CANTIDAD = 8 

# Datos para la simulación
nombres = ["Lucas", "Ambar", "Ciro", "Mia", "Lorenzo", "Isabella", "Bastián", "Emma"]
apellidos = ["Peralta", "Nuñez", "Cordoba", "Moyano", "Ferreyra", "Villarroel", "Paz", "Mendez"]
motivos = ["Dificultades escritura", "Selectividad alimentaria", "Evaluación CUD", "Retraso lenguaje", "Conducta disruptiva"]

def generar():
    if not os.path.exists(ARCHIVO_PROFS):
        print("❌ Error: No se encuentra profesionales.json. Ejecutá el Paso 1 primero.")
        return

    # 1. CARGA Y FILTRADO CRÍTICO
    with open(ARCHIVO_PROFS, 'r', encoding='utf-8') as f:
        profs = json.load(f)
    
    # Solo tomamos a los que tienen jerarquía "Titular"
    titulares = [p['nombre'] for p in profs if p.get('jerarquia') == 'Titular']

    if not titulares:
        print("❌ Error: No se encontraron profesionales con jerarquía 'Titular'.")
        return

    admisiones = []
    hoy = datetime.now()
    
    for i in range(1, CANTIDAD + 1):
        nombre_pac = f"{random.choice(nombres)} {random.choice(apellidos)}"
        fecha_sol = hoy - timedelta(days=random.randint(1, 15))
        
        # Simulamos la entrevista
        tiene_fecha = random.random() < 0.7
        fecha_ent = (hoy + timedelta(days=random.randint(1, 10))).strftime("%d/%m/%Y") if tiene_fecha else ""
        
        admisiones.append({
            "id": i,
            "estado": "Recibidos", 
            "fecha_solicitud": fecha_sol.strftime("%d/%m/%Y"),
            "fecha_entrevista": fecha_ent,
            "hora_entrevista": f"{random.randint(9,12)}:00" if tiene_fecha else "", # Entrevistas suelen ser mañana
            
            # 2. ASIGNACIÓN RESTRINGIDA: Solo un nombre de la lista de titulares
            "profesional": random.choice(titulares),
            
            "nombre": nombre_pac,
            "dni": f"{random.randint(45, 60)}.{random.randint(100, 999)}.{random.randint(100, 999)}",
            "edad": random.randint(2, 10),
            "obra_social": random.choice(["OSDE", "Prensa", "Subsidio", "Particular"]),
            "motivo_consulta": random.choice(motivos),
            "tutor_nombre": f"{random.choice(nombres)} {random.choice(apellidos)}",
            "email": f"contacto.admision{i}@gmail.com",
            
            # Campos vacíos para que el sistema los complete luego
            "informe_entrevista": None,
            "equipo_sugerido": []
        })

    with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
        json.dump(admisiones, f, indent=4, ensure_ascii=False)
    
    print(f"✅ ¡Paso 5 completado! {CANTIDAD} admisiones asignadas exclusivamente a Titulares.")

if __name__ == "__main__":
    generar()
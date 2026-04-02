import json
import os
import random
from datetime import datetime, timedelta

CARPETA = 'datos'
ARCHIVO_SALIDA = os.path.join(CARPETA, 'historias.json')
ARCHIVO_PAC = os.path.join(CARPETA, 'pacientes.json')
ARCHIVO_PROF = os.path.join(CARPETA, 'profesionales.json')

def generar():
    if not os.path.exists(ARCHIVO_PAC) or not os.path.exists(ARCHIVO_PROF):
        return

    with open(ARCHIVO_PAC, 'r', encoding='utf-8') as f: patients = json.load(f)
    with open(ARCHIVO_PROF, 'r', encoding='utf-8') as f: profs = json.load(f)
    
    mapa_profs = {p['id']: p for p in profs}
    historias = []
    historia_id = 1
    
    for pac in patients:
        staff = pac['staff_fijo']
        for area, prof_id in staff.items():
            fecha = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%d/%m/%Y")
            
            historias.append({
                "id": historia_id,
                "id_paciente": pac['id'],
                "profesional": mapa_profs[prof_id]['nombre'],
                "profesional_nombre": mapa_profs[prof_id]['nombre'],
                "profesional_id": prof_id,
                "nota": f"Sesión de {area} realizada con éxito.",
                "fecha": fecha,
                "hora": f"{random.randint(9,18)}:00"
            })
            historia_id += 1

    with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
        json.dump(historias, f, indent=4, ensure_ascii=False)
    print("✅ Historias generadas con la clave 'profesional' corregida.")

if __name__ == "__main__":
    generar()
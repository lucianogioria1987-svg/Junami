import json
import os
import random
from datetime import datetime, timedelta

CARPETA = 'datos'
ARCHIVO_SALIDA = os.path.join(CARPETA, 'recordatorios.json')
ARCHIVO_PROFS = os.path.join(CARPETA, 'profesionales.json')

def generar():
    if not os.path.exists(ARCHIVO_PROFS):
        print("❌ Error: No se encuentra profesionales.json. Ejecutá el Paso 1.")
        return

    # 1. Cargamos los profesionales reales
    with open(ARCHIVO_PROFS, 'r', encoding='utf-8') as f:
        profs = json.load(f)

    recordatorios = []
    hoy = datetime.now()
    id_rec = 1

    # Tareas según jerarquía
    tareas_titular = ["Revisar informes de auxiliares", "Reunión de equipo interdisciplinario", "Llamar a obra social por presupuesto", "Supervisión de caso complejo"]
    tareas_auxiliar = ["Cargar evolución semanal", "Preparar materiales para sesión", "Subir informe escolar", "Actualizar disponibilidad"]

    for p in profs:
        # Generamos entre 2 y 4 recordatorios para cada uno de los 24 profesionales
        cantidad = random.randint(2, 4)
        
        for _ in range(cantidad):
            fecha = hoy + timedelta(days=random.randint(0, 5))
            
            # Elegimos la tarea según si es Titular o Auxiliar
            titulo = random.choice(tareas_titular) if p['jerarquia'] == 'Titular' else random.choice(tareas_auxiliar)
            
            recordatorios.append({
                "id": id_rec,
                "usuario": p['usuario'], # Vinculación por el nombre de usuario real
                "profesional": p['nombre'],
                "titulo": titulo,
                "fecha": fecha.strftime("%d/%m/%Y"),
                "hora": f"{random.randint(8, 18)}:00",
                "prioridad": random.choice(["Alta", "Media", "Baja"]),
                "completado": random.choice([True, False])
            })
            id_rec += 1

    with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
        json.dump(recordatorios, f, indent=4, ensure_ascii=False)
    
    print(f"✅ ¡Paso 6 completado! {len(recordatorios)} recordatorios generados para los 24 profesionales.")

if __name__ == "__main__":
    generar()
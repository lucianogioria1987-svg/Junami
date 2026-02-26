import json
import os
import random
from datetime import datetime, timedelta

CARPETA = 'datos'
ARCHIVO_SALIDA = os.path.join(CARPETA, 'recordatorios.json')

# Usuarios generados en generar_profesionalesTeo.py
usuarios_target = ["mariag", "sofiam", "javierr", "camilap", "luciad", "marcoss"]

tipos = ["Entrevista", "Reunión", "Escuela", "Personal", "Supervisión"]
titulos_titulares = [
    "Reunión con equipo directivo", "Supervisión de auxiliares", "Firma de informes mensuales", 
    "Llamado a Obra Social", "Entrevista de admisión nueva"
]
titulos_auxiliares = [
    "Entregar evolución diaria", "Preparar material sensorial", "Reunión de supervisión", 
    "Buscar historia clínica", "Actualizar datos de paciente"
]

def generar():
    recordatorios = []
    id_counter = 1
    hoy = datetime.now()

    for usuario in usuarios_target:
        cantidad = random.randint(3, 5)
        # Lógica simple para determinar rol
        es_titular = usuario in ["mariag", "sofiam", "javierr"]
        lista_titulos = titulos_titulares if es_titular else titulos_auxiliares

        for _ in range(cantidad):
            fecha_random = hoy + timedelta(days=random.randint(0, 7)) 
            
            rec = {
                "id": id_counter,
                "usuario": usuario,
                "titulo": random.choice(lista_titulos),
                "tipo": random.choice(tipos),
                "fecha": fecha_random.strftime("%d/%m/%Y"),
                "fecha_iso": fecha_random.strftime("%Y-%m-%d"),
                "hora": f"{random.randint(8, 19)}:00",
                "notas": "Recordar llevar la planilla correspondiente."
            }
            recordatorios.append(rec)
            id_counter += 1

    with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
        json.dump(recordatorios, f, indent=4, ensure_ascii=False)
    print(f"✅ Recordatorios generados en '{ARCHIVO_SALIDA}'.")

if __name__ == "__main__":
    generar()
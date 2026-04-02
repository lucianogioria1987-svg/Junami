import json
import os
import random
from datetime import datetime, timedelta

CARPETA = 'datos'
ARCHIVO_SALIDA = os.path.join(CARPETA, 'pagos.json')
ARCHIVO_PACIENTES = os.path.join(CARPETA, 'pacientes.json')

perfiles_os = {
    "OSDE": {"monto_base": 12000, "demora": 15},
    "Swiss Medical": {"monto_base": 11000, "demora": 20},
    "Prensa": {"monto_base": 7500, "demora": 45},
    "Colmed": {"monto_base": 8000, "demora": 30},
    "Boreal": {"monto_base": 6500, "demora": 60},
    "Subsidio": {"monto_base": 7000, "demora": 90},
    "Particular": {"monto_base": 10000, "demora": 0}
}

def generar():
    if not os.path.exists(ARCHIVO_PACIENTES): return

    with open(ARCHIVO_PACIENTES, 'r', encoding='utf-8') as f: pacientes = json.load(f)
    
    pagos = []
    id_pago = 1
    hoy = datetime.now()

    for pac in pacientes:
        os_pac = pac.get('obra_social', 'Particular')
        
        # Cálculo de fechas y demora
        fecha_servicio = datetime.now() - timedelta(days=random.randint(30, 90))
        dias_espera = random.randint(30, 60) # Lo que demora la obra social
        fecha_pago_obj = fecha_servicio + timedelta(days=dias_espera)

        pagos.append({
            "id": id_pago,
            "id_paciente": pac['id'],
            "obra_social": os_pac,
            "monto": random.choice([35000, 45000, 52000]),
            "fecha_servicio": fecha_servicio.strftime("%d/%m/%Y"),
            "fecha_pago": fecha_pago_obj.strftime("%d/%m/%Y"), # CLAVE CORRECTA
            "dias_demora": dias_espera,                       # CLAVE CORRECTA
            "estado": "Pagado"
        })
        id_pago += 1

    with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
        json.dump(pagos, f, indent=4, ensure_ascii=False)
    print(f"✅ Pagos generados para los 120 pacientes.")

if __name__ == "__main__":
    generar()
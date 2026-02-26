import json
import os
import random
from datetime import datetime, timedelta

CARPETA = 'datos'
ARCHIVO_SALIDA = os.path.join(CARPETA, 'pagos.json')
ARCHIVO_PACIENTES = os.path.join(CARPETA, 'pacientes.json')

# Configuración de "Personalidad" de cada Obra Social (Monto Promedio y Demora Promedio)
perfiles_os = {
    "OSDE":          {"monto_base": 8500, "demora_base": 15}, # Paga bien y rápido
    "Swiss Medical": {"monto_base": 8200, "demora_base": 20},
    "Prensa":        {"monto_base": 5500, "demora_base": 45}, # Paga menos y demora
    "Colmed":        {"monto_base": 6000, "demora_base": 30},
    "Boreal":        {"monto_base": 4800, "demora_base": 60}, # Demora mucho
    "Subsidio":      {"monto_base": 5200, "demora_base": 90}, # La más lenta
    "Particular":    {"monto_base": 7000, "demora_base": 0}   # Pago inmediato
}

def generar():
    if not os.path.exists(ARCHIVO_PACIENTES):
        print("❌ Error: Ejecuta primero generar_2_pacientes.py")
        return

    with open(ARCHIVO_PACIENTES, 'r', encoding='utf-8') as f:
        pacientes = json.load(f)

    pagos = []
    id_counter = 1
    hoy = datetime.now()

    # Generamos pagos para los últimos 6 meses
    for pac in pacientes:
        os_nombre = pac.get('obra_social', 'Particular')
        perfil = perfiles_os.get(os_nombre, {"monto_base": 5000, "demora_base": 30})
        
        # Simulamos 1 pago por mes durante 6 meses
        for mes_atras in range(6):
            fecha_servicio = hoy - timedelta(days=mes_atras*30)
            
            # Variación aleatoria para que no sea todo igual
            monto_real = perfil['monto_base'] + random.randint(-500, 500)
            dias_demora = max(0, perfil['demora_base'] + random.randint(-5, 15))
            
            fecha_pago = fecha_servicio + timedelta(days=dias_demora)
            
            if fecha_pago > hoy: continue # Si la fecha de pago es futura, aún no se cobró (no entra en estadística)

            pagos.append({
                "id": id_counter,
                "id_paciente": pac['id'],
                "obra_social": os_nombre,
                "monto": monto_real,
                "fecha_servicio": fecha_servicio.strftime("%d/%m/%Y"),
                "fecha_pago": fecha_pago.strftime("%d/%m/%Y"),
                "dias_demora": dias_demora
            })
            id_counter += 1

    with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
        json.dump(pagos, f, indent=4, ensure_ascii=False)
    print(f"✅ {len(pagos)} Pagos históricos generados en '{ARCHIVO_SALIDA}'.")

if __name__ == "__main__":
    generar()
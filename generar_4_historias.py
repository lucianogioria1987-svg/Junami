import json
import os
import random
from datetime import datetime, timedelta

CARPETA = 'datos'
ARCHIVO_SALIDA = os.path.join(CARPETA, 'historias.json')
ARCHIVO_PAC = os.path.join(CARPETA, 'pacientes.json')
ARCHIVO_PROF = os.path.join(CARPETA, 'profesionales.json')

frases_inicio = [
    "El paciente ingresa al consultorio con buen nivel de alerta.",
    "Se inicia la sesión trabajando sobre la regulación sensorial.",
    "Paciente asiste acompañado por su madre, ingresa tranquilo.",
    "Comenzamos trabajando en mesa con actividades de motricidad fina.",
    "Se realiza trabajo en el gimnasio sensorial enfocándonos en planificación motora."
]
frases_desarrollo = [
    "Se proponen actividades de enhebrado para fomentar la pinza trípode y la coordinación óculo-manual.",
    "Trabajamos con masa terapéutica buscando mayor fuerza en miembros superiores.",
    "Realizamos un circuito de obstáculos: trepar, saltar y rolar.",
    "Se trabaja en AVD (Actividades de la Vida Diaria), uso de cubiertos.",
    "Utilizamos texturas diversas para trabajar la defensa táctil.",
    "Se enfoca la sesión en la organización de la tarea escolar.",
    "Trabajamos control postural en pelota terapéutica."
]
frases_cierre = [
    "Finalizamos con vuelta a la calma y ejercicios de respiración.",
    "Se brinda devolución a los padres sobre estrategias para el hogar.",
    "El paciente se retira estable y regulado.",
    "Se sugiere continuar reforzando el vestido/desvestido en casa.",
    "Queda pendiente para la próxima sesión trabajar el atado de cordones."
]

def generar():
    if not os.path.exists(ARCHIVO_PAC):
        print("❌ Error: Faltan pacientes.")
        return

    with open(ARCHIVO_PAC, 'r', encoding='utf-8') as f: patients = json.load(f)
    
    # Cargamos profesionales si existen, sino usaremos genéricos
    profs = []
    if os.path.exists(ARCHIVO_PROF):
        with open(ARCHIVO_PROF, 'r', encoding='utf-8') as f: profs = json.load(f)
    
    historias = []
    historia_id = 1
    
    for pac in patients:
        # Elegir un profesional que lo atienda
        nombre_prof = "Lic. Genérico"
        if pac.get('profesionales'):
            nombre_prof = random.choice(pac['profesionales'])
        elif profs:
            nombre_prof = profs[0]['nombre']

        # Generar 3 historias para cada uno
        for _ in range(3):
            fecha = (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%d/%m/%Y")
            texto = f"{random.choice(frases_inicio)} {random.choice(frases_desarrollo)} {random.choice(frases_desarrollo)} {random.choice(frases_cierre)}"
            
            historias.append({
                "id": historia_id,
                "id_paciente": pac['id'],
                "profesional": nombre_prof,
                "nota": texto,
                "fecha": fecha,
                "hora": f"{random.randint(9,18)}:00"
            })
            historia_id += 1

    with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
        json.dump(historias, f, indent=4, ensure_ascii=False)
    print(f"✅ Historias generadas en '{ARCHIVO_SALIDA}'.")
    # NOTA: Se eliminó el borrado de admisiones que causaba pérdida de datos

if __name__ == "__main__":
    generar()
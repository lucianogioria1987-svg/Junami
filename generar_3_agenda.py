import json
import os
import random

CARPETA = 'datos'
ARCHIVO_SESIONES = os.path.join(CARPETA, 'sesiones.json')
ARCHIVO_PAC = os.path.join(CARPETA, 'pacientes.json')
ARCHIVO_PROF = os.path.join(CARPETA, 'profesionales.json')

HORARIOS_MANANA = ["08:00", "08:45", "09:30", "10:15", "11:00", "11:45", "12:15"]
HORARIOS_TARDE = ["16:00", "16:45", "17:30", "18:15", "19:00", "19:30"]
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

def generar():
    if not os.path.exists(ARCHIVO_PAC) or not os.path.exists(ARCHIVO_PROF):
        return

    with open(ARCHIVO_PAC, 'r', encoding='utf-8') as f: pacientes = json.load(f)
    with open(ARCHIVO_PROF, 'r', encoding='utf-8') as f: profesionales = json.load(f)
    
    mapa_profs = {p['id']: p for p in profesionales}
    ocupacion = set()
    sesiones = []
    id_sesion = 1

    for pac in pacientes:
        staff = pac['staff_fijo']
        combos_definidos = [
            [("Terapia Ocupacional", staff["Terapia Ocupacional"]), ("Psicología", staff["Psicología"])],
            [("Fonoaudiología", staff["Fonoaudiología"]), ("Psicopedagogía", staff["Psicopedagogía"])]
        ]
        dias_asignados = random.sample(DIAS, 2)

        for i, combo in enumerate(combos_definidos):
            dia = dias_asignados[i]
            todos_los_horarios = HORARIOS_MANANA + HORARIOS_TARDE
            random.shuffle(todos_los_horarios)

            for h_idx, hora_inicio in enumerate(todos_los_horarios):
                if h_idx + 1 >= len(todos_los_horarios): continue
                hora_siguiente = todos_los_horarios[h_idx + 1]
                
                if hora_inicio in HORARIOS_MANANA and hora_siguiente in HORARIOS_TARDE: continue

                prof1_id, prof2_id = combo[0][1], combo[1][1]

                if (prof1_id, dia, hora_inicio) not in ocupacion and \
                   (prof2_id, dia, hora_siguiente) not in ocupacion:
                    
                    for j, (area, p_id) in enumerate(combo):
                        h_actual = hora_inicio if j == 0 else hora_siguiente
                        
                        sesiones.append({
                            "id": id_sesion,
                            "id_paciente": pac['id'],
                            "nombre_paciente": pac['nombre'],
                            "dias": [dia],
                            "hora": h_actual,
                            "tipo": "Individual",
                            "consultorio": f"Consultorio {random.randint(1,8)}",
                            "profesional": mapa_profs[p_id]['nombre'],
                            "profesional_nombre": mapa_profs[p_id]['nombre'],
                            "profesional_especialidad": area,
                            "estado_turno": "Confirmado"
                        })
                        ocupacion.add((p_id, dia, h_actual))
                        id_sesion += 1
                    break

    with open(ARCHIVO_SESIONES, 'w', encoding='utf-8') as f:
        json.dump(sesiones, f, indent=4, ensure_ascii=False)
    print("✅ Agenda generada con la clave 'profesional' corregida.")

if __name__ == "__main__":
    generar()
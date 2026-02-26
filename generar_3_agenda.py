import json
import os
import random

CARPETA = 'datos'
ARCHIVO_SALIDA = os.path.join(CARPETA, 'sesiones.json')
ARCHIVO_PAC = os.path.join(CARPETA, 'pacientes.json')
ARCHIVO_PROF = os.path.join(CARPETA, 'profesionales.json')

# HORARIOS Y DÍAS
HORARIOS = ["09:00", "09:45", "10:30", "11:15", "12:00", "12:45", "13:30", 
            "16:00", "16:45", "17:30", "18:15", "19:00"]
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
MAPA_DIAS = {dia: i for i, dia in enumerate(DIAS)}

def generar():
    if not os.path.exists(ARCHIVO_PAC) or not os.path.exists(ARCHIVO_PROF):
        print("❌ Error: Faltan archivos previos (pacientes o profesionales).")
        return

    with open(ARCHIVO_PAC, 'r', encoding='utf-8') as f: patients = json.load(f)
    with open(ARCHIVO_PROF, 'r', encoding='utf-8') as f: profs = json.load(f)
    
    mapa_profs = {p['nombre']: p for p in profs}
    sesiones = []
    sesion_id = 1
    
    # Control de ocupación para no superponer turnos
    ocupados_medico = set() # (prof, dia, hora)
    historial_paciente = {p['id']: [] for p in patients} # [idx_dia, idx_dia]

    def asignar(pac):
        nonlocal sesion_id
        mis_profs = pac.get('profesionales', [])
        
        # Si el paciente no tiene profesionales asignados, asignamos uno al azar para la agenda
        if not mis_profs:
            mis_profs = [random.choice(profs)['nombre']]
            
        random.shuffle(mis_profs)
        
        # Intentar asignar turno
        for prof_nom in mis_profs:
            dias_rand = list(DIAS); random.shuffle(dias_rand)
            horas_rand = list(HORARIOS); random.shuffle(horas_rand)
            
            for d in dias_rand:
                idx_dia = MAPA_DIAS[d]
                mis_dias = historial_paciente[pac['id']]
                
                # Regla 1: Máximo 2 turnos por paciente
                if len(mis_dias) >= 2: return False
                
                # Regla 2: No días consecutivos (ej: Lunes y Martes no)
                conflicto = False
                for ocupado in mis_dias:
                    if idx_dia == ocupado or abs(idx_dia - ocupado) == 1: conflicto = True
                if conflicto: continue

                for h in horas_rand:
                    if (prof_nom, d, h) not in ocupados_medico:
                        # Obtenemos datos del profesional con seguridad
                        prof_data = mapa_profs.get(prof_nom)
                        if not prof_data: continue 
                        
                        especialidad = prof_data.get('especialidad', 'T.O') # Blindaje por si falta

                        sesiones.append({
                            "id": sesion_id,
                            "id_paciente": pac['id'],
                            "nombre_paciente": pac['nombre'], # CORREGIDO: Clave exacta para agenda.html
                            "dias": [d],
                            "hora": h,
                            "tipo": "Individual",
                            "consultorio": f"Consultorio {random.randint(1,4)}",
                            "profesional_nombre": prof_nom,
                            "profesional_especialidad": especialidad,
                            "estado_turno": "Confirmado"
                        })
                        
                        ocupados_medico.add((prof_nom, d, h))
                        historial_paciente[pac['id']].append(idx_dia)
                        sesion_id += 1
                        return True
        return False

    print("🔄 Generando Agenda 2.0...")
    
    # Ronda 1: Asegurar 1 turno a todos
    for p in patients: asignar(p)
    
    # Ronda 2: Dar segundo turno (al 85% de los pacientes)
    for p in patients: 
        if random.random() < 0.85: asignar(p)

    with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
        json.dump(sesiones, f, indent=4, ensure_ascii=False)
    print(f"✅ Agenda generada en '{ARCHIVO_SALIDA}' ({len(sesiones)} turnos).")

if __name__ == "__main__":
    generar()
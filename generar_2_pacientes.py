import json
import os
import random

# Configuración de rutas
CARPETA = 'datos'
ARCHIVO_SALIDA = os.path.join(CARPETA, 'pacientes.json')
ARCHIVO_PROFS = os.path.join(CARPETA, 'profesionales.json')
CANTIDAD_PACIENTES = 120

# Datos para la simulación
nombres = ["Benjamín", "Bautista", "Mateo", "Juan", "Felipe", "Emma", "Olivia", "Martina", "Isabella", "Catalina"]
apellidos = ["García", "Rodríguez", "González", "Fernández", "López", "Martínez", "Sánchez", "Pérez"]
obras_sociales = ["OSDE", "Prensa", "Colmed", "Subsidio", "Boreal", "Swiss Medical", "Particular"]
diagnosticos = ["TEA", "TDAH", "Retraso Madurativo", "Trastorno del Lenguaje", "Discapacidad Motriz"]

def generar():
    if not os.path.exists(ARCHIVO_PROFS):
        print("❌ Error: Ejecutá primero el Paso 1 (Profesionales).")
        return

    with open(ARCHIVO_PROFS, 'r', encoding='utf-8') as f:
        profs = json.load(f)

    # Organizamos profesionales por especialidad para el Staff Fijo
    especialidades = {
        "Terapia Ocupacional": [p['id'] for p in profs if p['especialidad'] == "Terapia Ocupacional"],
        "Fonoaudiología": [p['id'] for p in profs if p['especialidad'] == "Fonoaudiología"],
        "Psicología": [p['id'] for p in profs if p['especialidad'] == "Psicología"],
        "Psicopedagogía": [p['id'] for p in profs if p['especialidad'] == "Psicopedagogía"]
    }

    pacientes = []
    for i in range(1, CANTIDAD_PACIENTES + 1):
        nombre_completo = f"{random.choice(nombres)} {random.choice(apellidos)}"
        
        # STAFF FIJO: Asignamos un ID de cada especialidad
        staff_fijo = {esp: random.choice(ids) for esp, ids in especialidades.items()}

        paciente = {
            "id": i,
            "nombre": nombre_completo,
            "dni": f"{random.randint(45, 60)}.{random.randint(100, 999)}.{random.randint(100, 999)}",
            "edad": f"{random.randint(2, 12)} años",
            "nacimiento": f"{random.randint(1, 28)}/{random.randint(1, 12)}/{random.randint(2014, 2022)}",
            "obra_social": random.choice(obras_sociales),
            "numero_afiliado": f"{random.randint(1000000, 9999999)}",
            
            # --- CORRECCIÓN DE CAMPOS PARA LA TABLA (image_5ea665.png) ---
            "diagnostico": random.choice(diagnosticos),    # Antes era diagnostico_principal
            "contacto_tutor": f"381-{random.randint(400, 699)}-{random.randint(1000, 9999)}",
            
            # --- TRIPLE BLINDAJE DE ESTADO (Para que no salga 'Inactivo') ---
            "estado": "Activo",           # Versión A (Capitalized)
            "estado_paciente": "activo",  # Versión B (Lowercase)
            "activo": True,               # Versión C (Booleano)
            "estado_clinico": "Activo",   # Versión D (Alternativa)
            # -------------------------------------------------------------

            "staff_fijo": staff_fijo,
            "tutor_nombre": f"{random.choice(nombres)} {random.choice(apellidos)}",
            "domicilio": f"Calle {random.randint(100, 900)}",
            "email": f"paciente.{i}@gmail.com",
            "fecha_ingreso": "01/03/2026"
        }
        pacientes.append(paciente)

    # Guardado limpio
    if not os.path.exists(CARPETA): os.makedirs(CARPETA)
    with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
        json.dump(pacientes, f, indent=4, ensure_ascii=False)
    
    print(f"✅ ¡Paso 2 completado! 120 pacientes generados con 'Doble Diagnóstico' y 'Triple Blindaje de Estado'.")

if __name__ == "__main__":
    generar()
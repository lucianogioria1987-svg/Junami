import json
import os
import random

# Configuración
CARPETA = 'datos'
ARCHIVO = os.path.join(CARPETA, 'profesionales.json')
os.makedirs(CARPETA, exist_ok=True)

universidades = ["Universidad Nacional de Tucumán", "Universidad Favaloro", "UBA", "Universidad Siglo 21", "UNSTA"]
calles = ["Av. Aconquija", "24 de Septiembre", "Muñecas", "San Martín", "Laprida", "Av. Mate de Luna", "Corrientes"]

AREAS = {
    "Terapia Ocupacional": "Terapista Ocupacional",
    "Fonoaudiología": "Fonoaudiólogo/a",
    "Psicología": "Psicólogo/a",
    "Psicopedagogía": "Psicopedagogo/a"
}

# Pool de 24 nombres y 24 apellidos ÚNICOS para evitar repeticiones
NOMBRES_POOL = ["Maria", "Sofia", "Lucia", "Camila", "Elena", "Beatriz", "Juana", "Rosa", "Ana", "Carla", "Marta", "Julia", 
                "Javier", "Marcos", "Ricardo", "Pedro", "Pablo", "Luis", "Jorge", "Andres", "Federico", "Gonzalo", "Silvia", "Monica"]
APELLIDOS_POOL = ["Gonzalez", "Martinez", "Ruiz", "Perez", "Diaz", "Silva", "Paz", "Mendez", "Darin", "Pascal", "Sarlo", "Viale",
                  "Lopez", "Acosta", "Sosa", "Rodriguez", "Gomez", "Fernandez", "Torres", "Alvarez", "Benitez", "Quiroga", "Bravo", "Vera"]

def obtener_iniciales(nombre):
    partes = nombre.replace("Lic. ", "").replace("Aux. ", "").split()
    return "".join([p[0] for p in partes]).upper()

def generar():
    # Mezclamos los pools para que la asignación sea aleatoria pero sin repetir
    random.shuffle(NOMBRES_POOL)
    random.shuffle(APELLIDOS_POOL)
    
    profesionales = []
    id_counter = 1
    idx_pool = 0

    for area_nombre, rol_base in AREAS.items():
        titulares_nombres = []
        
        # --- 3 TITULARES ---
        for i in range(3):
            nom = f"Lic. {NOMBRES_POOL[idx_pool]} {APELLIDOS_POOL[idx_pool]}"
            user = f"{NOMBRES_POOL[idx_pool].lower()}{random.randint(10,99)}"
            
            prof = {
                "id": id_counter, "nombre": nom, "usuario": user, "contrasena": "1234",
                "rol": rol_base, "especialidad": area_nombre, "iniciales": obtener_iniciales(nom),
                "foto": None, "jerarquia": "Titular", "supervisor": None,
                "dni": f"{random.randint(20, 40)}.123.{random.randint(100, 999)}",
                "edad": random.randint(30, 55),
                "domicilio": f"{random.choice(calles)} {random.randint(100, 1500)}",
                "universidad": random.choice(universidades),
                "telefono": f"381-{random.randint(400, 699)}-{random.randint(1000, 9999)}",
                "email": f"{user}@nidus.com", "matricula": str(random.randint(1000, 9999))
            }
            profesionales.append(prof)
            titulares_nombres.append(nom)
            id_counter += 1
            idx_pool += 1

        # --- 3 AUXILIARES ---
        for i in range(3):
            nom_aux = f"Aux. {NOMBRES_POOL[idx_pool]} {APELLIDOS_POOL[idx_pool]}"
            user_aux = f"aux_{NOMBRES_POOL[idx_pool].lower()}{random.randint(10,99)}"
            
            prof_aux = {
                "id": id_counter, "nombre": nom_aux, "usuario": user_aux, "contrasena": "1234",
                "rol": f"Auxiliar {area_nombre[:4]}", "especialidad": area_nombre,
                "iniciales": obtener_iniciales(nom_aux), "foto": None, "jerarquia": "Auxiliar",
                "supervisor": titulares_nombres[i], # Vinculado a un titular del área
                "dni": f"{random.randint(40, 48)}.123.{random.randint(100, 999)}",
                "edad": random.randint(22, 28),
                "domicilio": f"{random.choice(calles)} {random.randint(100, 1500)}",
                "universidad": random.choice(universidades),
                "telefono": f"381-{random.randint(400, 699)}-{random.randint(1000, 9999)}",
                "email": f"{user_aux}@nidus.com", "matricula": ""
            }
            profesionales.append(prof_aux)
            id_counter += 1
            idx_pool += 1

    with open(ARCHIVO, 'w', encoding='utf-8') as f:
        json.dump(profesionales, f, indent=4, ensure_ascii=False)
    
    print(f"✅ ¡Paso 1 completado! 24 profesionales únicos generados en {ARCHIVO}")

if __name__ == "__main__":
    generar()
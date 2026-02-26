import json
import os
import random

# Configuración de ruta
CARPETA = 'datos'
ARCHIVO = os.path.join(CARPETA, 'profesionales.json')
os.makedirs(CARPETA, exist_ok=True)

universidades = ["Universidad Nacional de Tucumán", "Universidad Favaloro", "UBA", "Universidad Siglo 21", "Universidad del Norte Santo Tomás de Aquino"]
calles = ["Av. Aconquija", "24 de Septiembre", "Muñecas", "San Martín", "Laprida", "Av. Mate de Luna", "Corrientes"]

def generar_datos_extra():
    return {
        "dni": f"{random.randint(20, 42)}.{random.randint(100, 999)}.{random.randint(100, 999)}",
        "edad": random.randint(24, 55),
        "domicilio": f"{random.choice(calles)} {random.randint(100, 900)}",
        "universidad": random.choice(universidades),
        "telefono": f"381-{random.randint(400, 699)}-{random.randint(1000, 9999)}",
        "matricula": f"{random.randint(1000, 9999)}"
    }

def generar():
    profesionales = []
    id_counter = 1
    
    # --- TITULARES ---
    titulares_data = [
        {"nombre": "Lic. María González", "usuario": "mariag", "sexo": "F"},
        {"nombre": "Lic. Sofía Martinez", "usuario": "sofiam", "sexo": "F"},
        {"nombre": "Lic. Javier Ruiz",    "usuario": "javierr", "sexo": "M"}
    ]
    
    for t in titulares_data:
        extras = generar_datos_extra()
        profesionales.append({
            "id": id_counter,
            "nombre": t["nombre"],
            "usuario": t["usuario"],
            "contrasena": "1234",
            "rol": "Terapista Ocupacional",
            "iniciales": "".join([x[0] for x in t["nombre"].split() if len(x)>2]).upper(),
            "foto": None,
            "jerarquia": "Titular",
            "supervisor": None,
            "dni": extras["dni"],
            "edad": extras["edad"],
            "domicilio": extras["domicilio"],
            "universidad": extras["universidad"],
            "telefono": extras["telefono"],
            "email": f"{t['usuario']}@nidus.com",
            "matricula": extras["matricula"]
        })
        id_counter += 1

    # --- AUXILIARES ---
    auxiliares_data = [
        {"nombre": "Aux. Camila Perez", "usuario": "camilap", "supervisor": "Lic. María González"},
        {"nombre": "Aux. Lucía Diaz",   "usuario": "luciad",  "supervisor": "Lic. Sofía Martinez"},
        {"nombre": "Aux. Marcos Silva", "usuario": "marcoss", "supervisor": "Lic. Javier Ruiz"}
    ]

    for a in auxiliares_data:
        extras = generar_datos_extra()
        # Los auxiliares suelen ser más jóvenes y pueden no tener matrícula aún
        extras["edad"] = random.randint(22, 29)
        extras["matricula"] = "" 
        
        profesionales.append({
            "id": id_counter,
            "nombre": a["nombre"],
            "usuario": a["usuario"],
            "contrasena": "1234",
            "rol": "Terapista Ocupacional",
            "iniciales": "".join([x[0] for x in a["nombre"].split() if len(x)>2]).upper(),
            "foto": None,
            "jerarquia": "Auxiliar",
            "supervisor": a["supervisor"],
            "dni": extras["dni"],
            "edad": extras["edad"],
            "domicilio": extras["domicilio"],
            "universidad": extras["universidad"],
            "telefono": extras["telefono"],
            "email": f"{a['usuario']}@nidus.com",
            "matricula": extras["matricula"]
        })
        id_counter += 1

    with open(ARCHIVO, 'w', encoding='utf-8') as f:
        json.dump(profesionales, f, indent=4, ensure_ascii=False)
    print(f"✅ Profesionales generados en '{ARCHIVO}'.")

if __name__ == "__main__":
    generar()
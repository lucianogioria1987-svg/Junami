import json
import os
import glob

def reset_full_folder():
    # Buscamos todos los archivos .json dentro de la carpeta datos/
    ruta_datos = 'datos/*.json'
    archivos_encontrados = glob.glob(ruta_datos)
    
    print(f"\n--- 🛰️ Escaneando carpeta 'datos/' en la rama: actualizaciones2 ---")
    
    if not archivos_encontrados:
        print("⚠️ No se encontraron archivos JSON en la carpeta 'datos/'.")
        return

    for archivo in archivos_encontrados:
        nombre = os.path.basename(archivo)
        
        # --- NUEVA ORDEN: EXCLUIR CONFIGURACIÓN ---
        if nombre == 'config_clinica.json':
            print(f"⏭️  SALTADO: {nombre:<30} (Archivo protegido)")
            continue
        # ------------------------------------------

        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump([], f)
            
            print(f"✅ {nombre:<30} -> Contenido vaciado a []")
            
        except Exception as e:
            print(f"❌ Error al procesar {archivo}: {e}")

    print(f"\n--- ✨ Se resetearon los archivos de datos. Entorno 100% estéril. ---\n")

if __name__ == '__main__':
    reset_full_folder()
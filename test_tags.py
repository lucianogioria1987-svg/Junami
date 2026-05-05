import json
import re

with open('datos/pacientes.json', 'r', encoding='utf-8') as f:
    pacientes = json.load(f)

tag_a_paciente = {}
for p in pacientes:
    nombre = p['nombre']
    tag = "@" + "".join(nombre.split())
    tag_a_paciente[tag.lower()] = p

def procesar_menciones(texto, tag_a_paciente):
    menciones_encontradas = {}
    
    def reemplazar(match):
        tag = match.group(0)
        tag_lower = tag.lower()
        if tag_lower in tag_a_paciente:
            paciente = tag_a_paciente[tag_lower]
            menciones_encontradas[paciente['id']] = paciente['nombre']
            return f'<a href="/paciente/{paciente["id"]}" class="text-emerald-600 font-bold hover:underline">{tag}</a>'
        return tag

    if not texto: return texto, []
    
    texto_procesado = re.sub(r'@[A-Za-zÁÉÍÓÚáéíóúÑñ]+', reemplazar, str(texto))
    return texto_procesado, list(menciones_encontradas.values())

print(procesar_menciones("Hola @EmmaGarcía, revisá a @JuanMartínez y también a @nadie.", tag_a_paciente))

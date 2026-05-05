import re
from utils import cargar_datos

def update_mensajeria_py():
    with open('rutas/mensajeria.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Insert procesar_menciones function after allowed_file
    func_code = """
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
    
    import html
    texto_esc = html.escape(str(texto))
    # After escaping, we replace the tags back to links
    # But wait! If we escape, we need to apply regex on the escaped text.
    # We must match @Name which won't be escaped.
    texto_procesado = re.sub(r'@[A-Za-zÁÉÍÓÚáéíóúÑñ]+', reemplazar, texto_esc)
    return texto_procesado, list(menciones_encontradas.values())
"""
    content = content.replace("def allowed_file(filename):\n    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS\n", 
                              "def allowed_file(filename):\n    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS\n" + func_code)
    
    # 2. In inbox(), load pacientes and build tag_a_paciente
    inbox_setup = """
    mi_id = session['usuario_actual']['id']
    mensajes = cargar_datos('mensajeria.json')
    profesionales = cargar_datos('profesionales.json')
    
    pacientes = cargar_datos('pacientes.json')
    tag_a_paciente = {}
    for p in pacientes:
        nombre = p.get('nombre', '')
        if nombre:
            tag = "@" + "".join(nombre.split())
            tag_a_paciente[tag.lower()] = p
            
    mapa_profesionales = {p['id']: p for p in profesionales}
"""
    content = re.sub(r"mi_id = session\['usuario_actual'\]\['id'\]\s*mensajes = cargar_datos\('mensajeria\.json'\)\s*profesionales = cargar_datos\('profesionales\.json'\)\s*mapa_profesionales = \{p\['id'\]: p for p in profesionales\}", inbox_setup.strip(), content)

    # 3. Inside inbox loop, process mentions
    menciones_code = """
        archivado_por = m.get('archivado_por', [])
        es_archivado = mi_id in archivado_por
        m['tiene_adjunto'] = 'adjunto' in m or any('adjunto' in r for r in m.get('respuestas', []))
        
        todas_menciones = []
        _, m_menc = procesar_menciones(m['mensaje'], tag_a_paciente)
        todas_menciones.extend(m_menc)
        for r in m.get('respuestas', []):
            _, r_menc = procesar_menciones(r.get('texto', ''), tag_a_paciente)
            todas_menciones.extend(r_menc)
        m['menciones'] = list(set(todas_menciones))
"""
    content = re.sub(r"archivado_por = m\.get\('archivado_por', \[\]\)\s*es_archivado = mi_id in archivado_por\s*m\['tiene_adjunto'\] = 'adjunto' in m or any\('adjunto' in r for r in m\.get\('respuestas', \[\]\)\)", menciones_code.strip(), content)

    # 4. In hilo(), load tag_a_paciente and process text
    hilo_setup = """
    mensajes = cargar_datos('mensajeria.json')
    profesionales = cargar_datos('profesionales.json')
    mapa_profesionales = {p['id']: p for p in profesionales}
    
    pacientes = cargar_datos('pacientes.json')
    tag_a_paciente = {}
    for p in pacientes:
        nombre = p.get('nombre', '')
        if nombre:
            tag = "@" + "".join(nombre.split())
            tag_a_paciente[tag.lower()] = p
"""
    content = re.sub(r"mensajes = cargar_datos\('mensajeria\.json'\)\s*profesionales = cargar_datos\('profesionales\.json'\)\s*mapa_profesionales = \{p\['id'\]: p for p in profesionales\}", hilo_setup.strip(), content)

    # 5. Process in hilo
    content = content.replace('"texto": m[\'mensaje\'],', '"texto": procesar_menciones(m[\'mensaje\'], tag_a_paciente)[0],')
    content = content.replace('"texto": r[\'texto\'],', '"texto": procesar_menciones(r[\'texto\'], tag_a_paciente)[0],')

    with open('rutas/mensajeria.py', 'w', encoding='utf-8') as f:
        f.write(content)

update_mensajeria_py()
print("Backend updated.")

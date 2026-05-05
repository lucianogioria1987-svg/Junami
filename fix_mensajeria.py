import re

with open('c:/Users/lucia/OneDrive/Escritorio/Junami 3.0/plantillas/mensajeria.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add btn-ver and onclick
def repl_ver(m):
    cls = m.group(2)
    if 'class="' not in cls:
        cls = 'class="btn-ver"'
    elif 'btn-ver' not in cls:
        cls = cls.replace('class="', 'class="btn-ver ')
    
    end = m.group(3).replace('>', ' onclick="alert(\'Clic en Ver\')">', 1)
    return m.group(1) + cls + end

html = re.sub(r'(<button[^>]*?)((?:class=\"[^\"]*\")?)([^>]*?data-action=\"ver\"[^>]*?>)', repl_ver, html)

# 2. Add btn-archivar and onclick
def repl_archivar(m):
    cls = m.group(2)
    if 'class="' not in cls:
        cls = 'class="btn-archivar"'
    elif 'btn-archivar' not in cls:
        cls = cls.replace('class="', 'class="btn-archivar ')
    
    end = m.group(3).replace('>', ' onclick="alert(\'Clic en Archivar\')">', 1)
    return m.group(1) + cls + end

html = re.sub(r'(<button[^>]*?)((?:class=\"[^\"]*\")?)([^>]*?data-action=\"archivar\"[^>]*?>)', repl_archivar, html)

# 3. Add btn-borrar and onclick
def repl_borrar(m):
    cls = m.group(2)
    if 'class="' not in cls:
        cls = 'class="btn-borrar"'
    elif 'btn-borrar' not in cls:
        cls = cls.replace('class="', 'class="btn-borrar ')
    
    end = m.group(3).replace('>', ' onclick="alert(\'Clic en Borrar\')">', 1)
    return m.group(1) + cls + end

html = re.sub(r'(<button[^>]*?)((?:class=\"[^\"]*\")?)([^>]*?data-action=\"borrar\"[^>]*?>)', repl_borrar, html)

# 4. Extract all scripts and remove from html
scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
html = re.sub(r'<script>.*?</script>', '', html, flags=re.DOTALL)

# 5. Combine JS and wrap the delegation logic
js_content = '\n'.join(scripts)
delegation_pattern = r'// DELEGACION DE EVENTOS GLOBAL\s*document\.addEventListener\(\'click\', function\(e\) \{.*?\n        \}\);'

if '// DELEGACION DE EVENTOS GLOBAL' in js_content:
    delegation_block = re.search(delegation_pattern, js_content, re.DOTALL)
    if delegation_block:
        wrapped = f"""document.addEventListener('DOMContentLoaded', function() {{
    console.log("Botones encontrados: ", document.querySelectorAll('.btn-ver').length);
    {delegation_block.group(0)}
}});"""
        js_content = js_content.replace(delegation_block.group(0), wrapped)
else:
    print("Could not find DELEGACION DE EVENTOS GLOBAL block")

# 6. Insert scripts back at the bottom
final_script = f"\n<script>\n{js_content}\n</script>\n</body>"
html = html.replace('</body>', final_script)

with open('c:/Users/lucia/OneDrive/Escritorio/Junami 3.0/plantillas/mensajeria.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Success')

with open('c:/Users/lucia/OneDrive/Escritorio/Junami 3.0/plantillas/mensajeria.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('<buttonclass="btn-ver" class="', '<button class="btn-ver ')
html = html.replace('<buttonclass="btn-archivar" class="', '<button class="btn-archivar ')
html = html.replace('<buttonclass="btn-borrar" class="', '<button class="btn-borrar ')

with open('c:/Users/lucia/OneDrive/Escritorio/Junami 3.0/plantillas/mensajeria.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Fixed HTML syntax')

import re
with open('plantillas/mensajeria.html', 'r', encoding='utf-8') as f:
    html = f.read()

scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
with open('test_js.js', 'w', encoding='utf-8') as f:
    f.write('\n'.join(scripts))

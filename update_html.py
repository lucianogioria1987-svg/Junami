with open('c:/Users/lucia/OneDrive/Escritorio/Junami 3.0/plantillas/mensajeria.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove onclick alerts
html = html.replace(' onclick="alert(\'Clic en Ver\')"', '')
html = html.replace(' onclick="alert(\'Clic en Archivar\')"', '')
html = html.replace(' onclick="alert(\'Clic en Borrar\')"', '')

# 2. Add mentions badge
# Find all occurrences of:
# {{ msg.asunto }} {% if msg.tiene_adjunto %} <i class="fas fa-paperclip text-emerald-500 ml-2" title="Contiene archivo adjunto"></i>{% endif %}</td>
badge_html = """{{ msg.asunto }} {% if msg.tiene_adjunto %} <i class="fas fa-paperclip text-emerald-500 ml-2" title="Contiene archivo adjunto"></i>{% endif %}
                                        {% if msg.menciones %}
                                        <div class="mt-1.5 flex flex-wrap gap-1">
                                            {% for m in msg.menciones %}
                                            <span class="inline-flex items-center px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-600 text-[10px] font-bold border border-emerald-100"><i class="fas fa-user text-[9px] mr-1"></i> {{ m }}</span>
                                            {% endfor %}
                                        </div>
                                        {% endif %}
                                    </td>"""

html = html.replace(
    '{{ msg.asunto }} {% if msg.tiene_adjunto %} <i class="fas fa-paperclip text-emerald-500 ml-2" title="Contiene archivo adjunto"></i>{% endif %}</td>',
    badge_html
)

with open('c:/Users/lucia/OneDrive/Escritorio/Junami 3.0/plantillas/mensajeria.html', 'w', encoding='utf-8') as f:
    f.write(html)

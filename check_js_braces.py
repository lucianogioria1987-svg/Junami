import re

with open('plantillas/mensajeria.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract script content
script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if script_match:
    js_code = script_match.group(1)
    
    # Very simple brace counting
    brace_count = 0
    in_string = False
    string_char = ''
    in_template_literal = False
    
    for i, char in enumerate(js_code):
        if in_template_literal:
            if char == '`' and js_code[i-1] != '\\':
                in_template_literal = False
            continue
            
        if in_string:
            if char == string_char and js_code[i-1] != '\\':
                in_string = False
            continue
            
        if char == '`':
            in_template_literal = True
            continue
        elif char in ["'", '"']:
            in_string = True
            string_char = char
            continue
            
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count < 0:
                print(f"Error: Unmatched closing brace at offset {i}")
                break

    print(f"Final brace count (0 is good): {brace_count}")
else:
    print("No script found")

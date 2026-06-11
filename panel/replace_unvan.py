import os
import re

search_dir = 'c:/Users/asus/Desktop/VollProjeler/MYKEEPfurkansonhal/panel'
replacements = [
    (r'>Unvan<', r'>Muhatap<'),
    (r'>UNVAN<', r'>MUHATAP<'),
    (r'\(Unvan\)', r'(Muhatap)'),
    (r'\(UNVAN\)', r'(MUHATAP)'),
    (r'"Unvan"', r'"Muhatap"'),
    (r"\'Unvan\'", r"'Muhatap'"),
]

for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith('.html') or file.endswith('forms.py') or file.endswith('views.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            for old, new in replacements:
                content = re.sub(old, new, content)
                
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'Updated {filepath}')

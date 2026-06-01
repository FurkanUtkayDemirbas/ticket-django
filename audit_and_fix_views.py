import os
import re

def add_decorator_if_missing(filepath, decorator, view_names=None):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ensure import exists
    if decorator == '@admin_required':
        if 'admin_required' not in content:
            content = "from uyelik.decorators import admin_required\n" + content
    elif decorator == '@firma_required':
        pass # Add if needed
    elif decorator == '@login_required':
        if 'login_required' not in content:
            content = "from django.contrib.auth.decorators import login_required\n" + content
            
    # Find all defs
    defs = re.findall(r'^def (\w+)\(request', content, re.MULTILINE)
    
    modified = False
    for d in defs:
        if view_names and d not in view_names:
            continue
            
        # Check if it has the decorator
        # Find the def line
        def_pattern = re.compile(r'^(.*?)(@\w+\s+)*def ' + d + r'\(', re.MULTILINE)
        match = def_pattern.search(content)
        if match:
            pre_text = match.group(0)
            if decorator not in pre_text:
                # Add decorator right above def
                content = content.replace(f'def {d}(', f'{decorator}\ndef {d}(')
                modified = True
                
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

# Admin only views
admin_only_apps = ['departman', 'destekturu', 'modul']
for app in admin_only_apps:
    add_decorator_if_missing(f'panel/{app}/views.py', '@admin_required')

# Muhatap views - Admin only for everything except maybe some list? Let's make it admin only
add_decorator_if_missing(f'panel/muhatap/views.py', '@admin_required')

print("Audit and fix completed.")

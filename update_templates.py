import os
import re

template_dir = 'panel/templates'
for filename in os.listdir(template_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(template_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Replace occurrences of a.ticketno.pk -> a.ticketno.hash_id
        content = re.sub(r"\{% url 'ticket_duzenle' (\w+)\.ticketno\.pk %\}", r"{% url 'ticket_duzenle' \1.ticketno.hash_id %}", content)
        content = re.sub(r"\{% url 'ticket_duzenle' row\.ticket_no %\}", r"{% url 'ticket_duzenle' row.ticket.hash_id %}", content) # Assumes we can pass hash_id or we need to fix it manually if row doesn't have ticket
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Updated {filename}')

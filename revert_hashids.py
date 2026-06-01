import os
import re

# 1. Update URLs
urls_path = 'panel/panel/urls.py'
with open(urls_path, 'r', encoding='utf-8') as f:
    urls_content = f.read()

urls_content = urls_content.replace('<str:hash_pk>', '<int:pk>')
urls_content = urls_content.replace('<str:hash_ticket_pk>', '<int:ticket_pk>')

with open(urls_path, 'w', encoding='utf-8') as f:
    f.write(urls_content)

# 2. Update Views
views_path = 'panel/ticket/views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    views_content = f.read()

# Regex to remove hash_pk logic
# E.g.:
# def ticket_duzenle(request, hash_pk=None, pk=None):
#     if hash_pk:
#         from .utils import decode_ticket_id
#         pk = decode_ticket_id(hash_pk)
#         if not pk:
#             from django.http import Http404
#             raise Http404("Ticket bulunamadı")
pattern_duzenle = re.compile(r'def ticket_duzenle\(request,\s*hash_pk=None,\s*pk=None\):\s*if hash_pk:.*?raise Http404\("Ticket bulunamadı"\)', re.DOTALL)
views_content = pattern_duzenle.sub('def ticket_duzenle(request, pk):', views_content)

pattern_sil = re.compile(r'def ticket_sil\(request,\s*hash_pk=None,\s*pk=None\):\s*if hash_pk:.*?raise Http404\("Ticket bulunamadı"\)', re.DOTALL)
views_content = pattern_sil.sub('def ticket_sil(request, pk):', views_content)

pattern_tamamla = re.compile(r'def ticket_tamamla\(request,\s*hash_pk=None,\s*pk=None\):\s*if hash_pk:.*?raise Http404\("Ticket bulunamadı"\)', re.DOTALL)
views_content = pattern_tamamla.sub('def ticket_tamamla(request, pk):', views_content)

pattern_fatura = re.compile(r'def ticket_faturalama_tamamla\(request,\s*hash_pk=None,\s*pk=None\):\s*if hash_pk:.*?raise Http404\("Ticket bulunamadı"\)', re.DOTALL)
views_content = pattern_fatura.sub('def ticket_faturalama_tamamla(request, pk):', views_content)

pattern_akt_sil = re.compile(r'def ticket_aktivite_sil\(request,\s*ticket_pk=None,\s*aktivite_pk=None,\s*hash_ticket_pk=None\):\s*if hash_ticket_pk:.*?raise Http404\("Ticket bulunamadı"\)', re.DOTALL)
views_content = pattern_akt_sil.sub('def ticket_aktivite_sil(request, ticket_pk, aktivite_pk):', views_content)

pattern_efor_sil = re.compile(r'def ticket_efor_sil\(request,\s*ticket_pk=None,\s*efor_pk=None,\s*hash_ticket_pk=None\):\s*if hash_ticket_pk:.*?raise Http404\("Ticket bulunamadı"\)', re.DOTALL)
views_content = pattern_efor_sil.sub('def ticket_efor_sil(request, ticket_pk, efor_pk):', views_content)

with open(views_path, 'w', encoding='utf-8') as f:
    f.write(views_content)


# 3. Update Templates
template_dir = 'panel/templates'
for filename in os.listdir(template_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(template_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Replace .hash_id with .pk
        # Watch out for row.ticket.hash_id -> row.ticket_no or row.ticket.pk
        # Depending on what we replaced earlier
        content = content.replace('.hash_id %}', '.pk %}')
        content = content.replace('row.ticket.pk %}', 'row.ticket_no %}') # Ticket_ozet_raporu uses row.ticket_no
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

# 4. Remove hash_id from models
models_path = 'panel/ticket/models.py'
with open(models_path, 'r', encoding='utf-8') as f:
    models_content = f.read()

pattern_hashid = re.compile(r'\s*@property\s*def hash_id\(self\):.*?return encode_ticket_id\(self\.ticketno\)', re.DOTALL)
models_content = pattern_hashid.sub('', models_content)

with open(models_path, 'w', encoding='utf-8') as f:
    f.write(models_content)

print('Revert completed successfully.')

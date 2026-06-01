import os

file_path = 'panel/ticket/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Make the changes
content = content.replace('def ticket_duzenle(request, pk):', 'def ticket_duzenle(request, hash_pk=None, pk=None):\n    if hash_pk:\n        from .utils import decode_ticket_id\n        pk = decode_ticket_id(hash_pk)\n        if not pk:\n            from django.http import Http404\n            raise Http404("Ticket bulunamadı")')

content = content.replace('def ticket_sil(request, pk):', 'def ticket_sil(request, hash_pk=None, pk=None):\n    if hash_pk:\n        from .utils import decode_ticket_id\n        pk = decode_ticket_id(hash_pk)\n        if not pk:\n            from django.http import Http404\n            raise Http404("Ticket bulunamadı")')

content = content.replace('def ticket_tamamla(request, pk):', 'def ticket_tamamla(request, hash_pk=None, pk=None):\n    if hash_pk:\n        from .utils import decode_ticket_id\n        pk = decode_ticket_id(hash_pk)\n        if not pk:\n            from django.http import Http404\n            raise Http404("Ticket bulunamadı")')

content = content.replace('def ticket_faturalama_tamamla(request, pk):', 'def ticket_faturalama_tamamla(request, hash_pk=None, pk=None):\n    if hash_pk:\n        from .utils import decode_ticket_id\n        pk = decode_ticket_id(hash_pk)\n        if not pk:\n            from django.http import Http404\n            raise Http404("Ticket bulunamadı")')

content = content.replace('def ticket_aktivite_sil(request, ticket_pk, aktivite_pk):', 'def ticket_aktivite_sil(request, ticket_pk=None, aktivite_pk=None, hash_ticket_pk=None):\n    if hash_ticket_pk:\n        from .utils import decode_ticket_id\n        ticket_pk = decode_ticket_id(hash_ticket_pk)\n        if not ticket_pk:\n            from django.http import Http404\n            raise Http404("Ticket bulunamadı")')

content = content.replace('def ticket_efor_sil(request, ticket_pk, efor_pk):', 'def ticket_efor_sil(request, ticket_pk=None, efor_pk=None, hash_ticket_pk=None):\n    if hash_ticket_pk:\n        from .utils import decode_ticket_id\n        ticket_pk = decode_ticket_id(hash_ticket_pk)\n        if not ticket_pk:\n            from django.http import Http404\n            raise Http404("Ticket bulunamadı")')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated views.py')

import django, os, tempfile
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
django.setup()
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from raporlar.views import _ticket_headers, _ticket_rows, link_callback
from ticket.models import ticket

ticketlar = ticket.objects.order_by('-ticketno')[:1]
rows = _ticket_rows(ticketlar)
headers = _ticket_headers()
widths = ['8%','15%','15%','10%','20%','12%','10%','10%']
context = {
    'rapor_baslik': 'TICKET RAPORU',
    'headers': headers,
    'pdf_widths': ', '.join(widths),
    'rows': rows
}
html = render_to_string('pdf_rapor_sablonu.html', context)
orig = tempfile.NamedTemporaryFile
tempfile.NamedTemporaryFile = lambda *a, **k: orig(*a, **{**k, 'delete': False})
with open('test_output.pdf', 'wb') as f:
    pisa.CreatePDF(html, dest=f, link_callback=link_callback)

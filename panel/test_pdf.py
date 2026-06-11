import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "panel.settings")
django.setup()

from django.test import RequestFactory
from masraf.views import masraf_rapor_pdf
from ticket.models import User

# Superuser olustur veya al
user = User.objects.filter(is_superuser=True).first()

factory = RequestFactory()
request = factory.get('/masraf/rapor/pdf/')
request.user = user

response = masraf_rapor_pdf(request)

if response.status_code == 200:
    with open("test_masraf.pdf", "wb") as f:
        f.write(response.content)
    print("PDF basariyla uretildi: test_masraf.pdf")
else:
    print(f"Hata: {response.status_code}")

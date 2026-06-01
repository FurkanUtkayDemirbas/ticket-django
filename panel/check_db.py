import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
django.setup()

from muhatap.models import muhatap
from uyelik.models import UserProfile
from ticket.models import ticket
from django.contrib.auth.models import User

print("--- FİRMALAR ---")
for m in muhatap.objects.all():
    print(f"ID: {m.id}, Unvan: {m.unvan}")

print("\n--- KULLANICILAR VE PROFİLLERİ ---")
for p in UserProfile.objects.all():
    print(f"User: {p.user.username}, Role: {p.role}, Firma: {p.muhatap_firma_id if p.muhatap_firma else 'Yok'}")

print("\n--- TICKETLAR ---")
for t in ticket.objects.all():
    print(f"Ticket No: {t.ticketno}, Konu: {t.konu}, Firma: {t.unvan_id if t.unvan else 'Yok'}")

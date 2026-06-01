import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
django.setup()

from muhatap.models import muhatap
from uyelik.models import UserProfile
from ticket.models import ticket, aktivite, atama
from sozlesme.models import sozlesmeler
from proje.models import projeler
from django.contrib.auth.models import User

try:
    gercek_voll = muhatap.objects.get(unvan="VOLL YAZILIM")
    sahte_voll = muhatap.objects.get(unvan="VOLL")
    
    # Bütün Ticket'ları gerçek Voll'e taşı
    ticket.objects.filter(unvan=sahte_voll).update(unvan=gercek_voll)
    print("Ticketlar VOLL YAZILIM firmasına taşındı.")

    # Sözleşmeleri gerçek Voll'e taşı
    sozlesmeler.objects.filter(muhatap=sahte_voll).update(muhatap=gercek_voll)
    print("Sözleşmeler VOLL YAZILIM firmasına taşındı.")

    # User_test kullanıcısını sil
    User.objects.filter(username="voll_test").delete()
    print("voll_test kullanıcısı silindi.")

    # Sahte VOLL firmasını sil
    sahte_voll.delete()
    print("Sahte 'VOLL' firması silindi.")
    
except Exception as e:
    print(f"Hata: {e}")

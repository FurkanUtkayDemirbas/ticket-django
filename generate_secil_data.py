import os
import django
from django.utils import timezone
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
django.setup()

from django.contrib.auth.models import User
from uyelik.models import UserProfile
from muhatap.models import muhatap
from sozlesme.models import sozlesmeler
from proje.models import projeler
from ticket.models import ticket, atama, aktivite
from destekturu.models import destektur
from modul.models import bolum

# 1. Get Secil User and Firm
secil_user = User.objects.filter(username='Secil').first()
if not secil_user:
    print("Secil user not found")
    exit()

secil_profile = getattr(secil_user, 'userprofile', None)
secil_firma = secil_profile.muhatap_firma if secil_profile else None

if not secil_firma:
    print("Secil firma not found")
    exit()

# Ensure we have some base definitions
modul_obj = bolum.objects.first() or bolum.objects.create(kod='ERP')
destek_obj = destektur.objects.first() or destektur.objects.create(ad='Yazılım Desteği')

# Get a danisman
danisman_profile = UserProfile.objects.filter(role='Danisman').first()
danisman_user = danisman_profile.user if danisman_profile else User.objects.first()



# 4. Create Tickets
tickets_data = [
    {'konu': 'ERP Modülünde Hata Alınıyor', 'durum': 'Yeni', 'onaydurum': False},
    {'konu': 'Fatura Raporu Eksik Çıkıyor', 'durum': 'Birim Testi', 'onaydurum': False},
    {'konu': 'Kullanıcı Yetkilendirme Sorunu', 'durum': 'Tamamlandı', 'onaydurum': True},
    {'konu': 'Maliyet Hesaplaması Hatalı', 'durum': 'Efor Onayında', 'onaydurum': False},
]

created_tickets = []
for idx, tdata in enumerate(tickets_data):
    t, created = ticket.objects.get_or_create(
        konu=tdata['konu'],
        unvan=secil_firma,
        defaults={
            'musteri_ticket_no': f'SC-{idx+100}',
            'olusturan': secil_user,
            'guncelleyen': secil_user,
            'modul': modul_obj,
            'destekturu': destek_obj,
            'aciliyet': 'Normal',
            'onaydurum': tdata['onaydurum'],
            'durum': tdata['durum'],
            'aktif': True
        }
    )
    if created:
        created_tickets.append(t)

print(f"Created {len(created_tickets)} tickets for Secil.")

# 5. Create Efor and Aktiviteler
for t in created_tickets:
    # Efor (atama)
    e, created = atama.objects.get_or_create(
        ticketno=t,
        danisman=danisman_user,
        defaults={
            'aciklama': f'{t.konu} için atama yapıldı.',
            'efor': 2.5,
            'onay': False
        }
    )
    
    # Aktivite
    aktivite.objects.get_or_create(
        ticketno=t,
        modul=None,
        defaults={
            'aciklama': f'{t.konu} üzerinde çalışmalara başlandı.',
            'date': timezone.now(),
            'time': 60,
            'danisman': None
        }
    )

print("Mock data generation completed successfully!")

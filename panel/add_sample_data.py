import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
django.setup()

from muhatap.models import muhatap
from sozlesme.models import sozlesmeler
from proje.models import projeler
from ticket.models import ticket, aktivite, atama
from departman.models import departman
from destekturu.models import destektur
from modul.models import bolum, danisman
from django.contrib.auth.models import User

# 1. Firmayı (Muhatap) Bul veya Oluştur
voll_firma, created = muhatap.objects.get_or_create(
    unvan="VOLL",
    defaults={
        "vkn": "1234567890",
        "telefon": "0212 555 44 33",
        "adres": "Levent, İstanbul",
        "aktif": True
    }
)
print(f"Firma: {voll_firma.unvan} (Oluşturuldu: {created})")

# Departman, Destek Turu, Bolum, Danisman lazim mi?
dpt, _ = departman.objects.get_or_create(kod="IT", defaults={"tanim": "Bilgi İşlem"})
dt, _ = destektur.objects.get_or_create(kod="YAZ", defaults={"definition": "Yazılım Desteği"})
mod, _ = bolum.objects.get_or_create(kod="ERP", defaults={"program": "SAP", "isim": "ERP Yönetimi"})

user, _ = User.objects.get_or_create(username="danisman_ali", defaults={"email": "ali@voll.com"})
dan, _ = danisman.objects.get_or_create(
    username="danisman_ali",
    defaults={
        "isim": "Ali Veli",
        "email": "ali@voll.com",
        "telefon": "5551112233",
        "tur": "Kıdemli"
    }
)
dan.yetkinlik.add(mod)

# 2. Sözleşme Oluştur
sozlesme, _ = sozlesmeler.objects.get_or_create(
    sozlesmeno="VOLL-2026-001",
    defaults={
        "muhatap": voll_firma,
        "tanim": "VOLL Bakım Anlaşması",
        "baslangic_tarihi": timezone.now().date(),
        "bitis_tarihi": (timezone.now() + timedelta(days=365)).date(),
        "aciklama": "VOLL Yıllık Bakım Anlaşması"
    }
)

prj, _ = projeler.objects.get_or_create(
    tanim="ERP Entegrasyon Projesi",
    defaults={
        "sozlesme_baglantisi": sozlesme,
        "aciklama": "VOLL firması için muhasebe ERP entegrasyonu."
    }
)

# 4. Ticketlar Oluştur
if not ticket.objects.filter(konu="Fatura modülünde hata alınıyor").exists():
    t1 = ticket.objects.create(
        unvan=voll_firma,
        konu="Fatura modülünde hata alınıyor",
        aciklama="Fatura keserken sistemsel bir hata mesajı çıkıyor. Acil incelenmeli.",
        bolumkod=mod,
        destekturu=dt,
        taleptarih=timezone.now(),
        musteri_ticket_no="MST-111"
    )
    t1.danisman.add(dan)

    # 5. Aktiviteler ve Eforlar Oluştur
    aktivite.objects.create(
        ticketno=t1,
        date=timezone.now(),
        time=2.5,
        aciklama="Hata logları incelendi, veritabanındaki kısıtlamadan kaynaklandığı tespit edildi.",
        danisman=dan,
        modul=mod
    )

    atama.objects.create(
        ticketno=t1,
        danisman=dan,
        efor=2.5,
        onay=False,
        modul=mod
    )

if not ticket.objects.filter(konu="Yeni raporlama ekranı talebi").exists():
    t2 = ticket.objects.create(
        unvan=voll_firma,
        konu="Yeni raporlama ekranı talebi",
        aciklama="Yönetim için aylık bazda özet satış raporu ekranı geliştirilmesi talep edilmektedir.",
        bolumkod=mod,
        destekturu=dt,
        taleptarih=timezone.now() - timedelta(days=2),
        musteri_ticket_no="MST-112"
    )

print("VOLL firması için örnek veriler (Sözleşme, Proje, Ticket, Aktivite, Efor) başarıyla oluşturuldu!")

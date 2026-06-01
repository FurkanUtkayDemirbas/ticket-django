import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
django.setup()

from modul.models import danisman
from django.contrib.auth.models import User
from uyelik.models import UserProfile

try:
    # İsmi Hüseyin Ağaç (veya benzeri) olan danışmanı bulmaya çalışalım
    huseyin = danisman.objects.filter(isim__icontains="h").filter(isim__icontains="ağaç").first()
    
    if not huseyin:
        # Belki 'huseyin' olarak yazılmıştır, tüm danışmanları yazdıralım
        print("Hüseyin Ağaç adında danışman bulunamadı. Mevcut danışmanlar:")
        for d in danisman.objects.all():
            print(f"- {d.username} : {d.isim}")
            
        # O zaman biz oluşturalım
        huseyin, created = danisman.objects.get_or_create(
            username="huseyin",
            defaults={
                "isim": "Hüseyin Ağaç",
                "email": "huseyin@voll.com.tr",
                "telefon": "5550001122",
                "tur": "İç Kaynak"
            }
        )
        print("Hüseyin Ağaç adında yeni bir danışman kaydı oluşturuldu.")

    # User hesabını bul veya oluştur
    usr, u_created = User.objects.get_or_create(username=huseyin.username)
    usr.set_password("agac1234")
    usr.save()

    # UserProfile oluştur veya güncelle
    prof, p_created = UserProfile.objects.get_or_create(user=usr)
    prof.role = "Danisman"
    prof.danisman_profil = huseyin
    prof.is_approved = True
    prof.save()

    print(f"Kullanıcı başarıyla bağlandı/oluşturuldu!")
    print(f"Giriş Kullanıcı Adı: {usr.username}")
    print(f"Giriş Şifresi: agac1234")
    
except Exception as e:
    print(f"Hata: {e}")

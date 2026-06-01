import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
django.setup()

from modul.models import danisman
from django.contrib.auth.models import User
from uyelik.models import UserProfile

try:
    # İsmi furkan olan danışmanı bul
    furkan = danisman.objects.filter(isim__icontains="furkan").first()
    
    if not furkan:
        print("Furkan adında danışman bulunamadı, oluşturuluyor...")
        furkan, created = danisman.objects.get_or_create(
            username="furkan",
            defaults={
                "isim": "Furkan Danışman",
                "email": "furkan@voll.com.tr",
                "telefon": "5551112233",
                "tur": "İç Kaynak"
            }
        )
    else:
        print(f"Mevcut Furkan bulundu: {furkan.username}")

    # User hesabını bul veya oluştur
    usr, u_created = User.objects.get_or_create(username=furkan.username)
    usr.set_password("furkan1234")
    usr.save()

    # UserProfile oluştur veya güncelle
    prof, p_created = UserProfile.objects.get_or_create(user=usr)
    prof.role = "Danisman"
    prof.danisman_profil = furkan
    prof.is_approved = True
    prof.save()

    print(f"Kullanıcı başarıyla bağlandı/oluşturuldu!")
    print(f"Giriş Kullanıcı Adı: {usr.username}")
    print(f"Giriş Şifresi: furkan1234")
    
except Exception as e:
    print(f"Hata: {e}")

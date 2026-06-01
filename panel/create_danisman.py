import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
django.setup()

from modul.models import danisman, bolum
from django.contrib.auth.models import User
from uyelik.models import UserProfile

# 1. Danışman nesnesini oluştur
dan, created = danisman.objects.get_or_create(
    username="mehmet",
    defaults={
        "isim": "Mehmet Danışman",
        "email": "mehmet@voll.com.tr",
        "telefon": "5551234567",
        "tur": "İç Kaynak"
    }
)

# 2. Yetkinlik (Bölüm) ekle
# Varsa bir bölüm bul, yoksa oluşturup ekle
mod, mod_created = bolum.objects.get_or_create(
    kod="TEST",
    defaults={
        "program": "TEST-PROG",
        "isim": "Test Modülü"
    }
)
dan.yetkinlik.add(mod)

# 3. Giriş yapabilmesi için User nesnesi oluştur
usr, u_created = User.objects.get_or_create(username="mehmet")
usr.set_password("danisman123")
usr.save()

# 4. UserProfile oluştur ve rolünü "Danisman" yap
prof, p_created = UserProfile.objects.get_or_create(user=usr)
prof.role = "Danisman"
prof.danisman_profil = dan
prof.is_approved = True
prof.save()

print("Danışman kullanıcısı başarıyla oluşturuldu!")
print("Kullanıcı Adı: mehmet")
print("Şifre: danisman123")

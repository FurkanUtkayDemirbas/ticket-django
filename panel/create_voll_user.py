import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
django.setup()

from django.contrib.auth.models import User
from uyelik.models import UserProfile
from muhatap.models import muhatap

voll_firma = muhatap.objects.get(unvan="VOLL")

# Kullanıcıyı oluştur veya al
user, created = User.objects.get_or_create(username="voll_test")
user.set_password("voll1234")
user.save()

# Profili oluştur veya güncelle
profile, p_created = UserProfile.objects.get_or_create(user=user)
profile.role = "Firma"
profile.muhatap_firma = voll_firma
profile.is_approved = True
profile.save()

print(f"Kullanıcı adı: voll_test")
print(f"Şifre: voll1234")

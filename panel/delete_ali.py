import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
django.setup()

from modul.models import danisman
from django.contrib.auth.models import User

# Danışman Ali'yi sil
try:
    dan = danisman.objects.get(username="danisman_ali")
    dan.delete()
    print("Danışman 'Ali' başarıyla silindi.")
except danisman.DoesNotExist:
    print("Danışman 'Ali' bulunamadı.")

# User'ı sil
try:
    usr = User.objects.get(username="danisman_ali")
    usr.delete()
    print("Kullanıcı 'danisman_ali' başarıyla silindi.")
except User.DoesNotExist:
    print("Kullanıcı 'danisman_ali' bulunamadı.")

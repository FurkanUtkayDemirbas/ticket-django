from django.urls import path
from . import views

app_name = 'uyelik'

urlpatterns = [
    path('giris/', views.giris_view, name='giris'),
    path('kayit/', views.kayit_view, name='kayit'),
    path('cikis/', views.cikis_view, name='cikis'),

    # Kullanıcı Yönetimi (Admin Only)
    path('kullanicilar/', views.kullanici_listesi, name='kullanici_listesi'),
    path('kullanicilar/ekle/', views.kullanici_ekle, name='kullanici_ekle'),
    path('kullanicilar/<int:user_id>/sil/', views.kullanici_sil, name='kullanici_sil'),
    path('kullanicilar/<int:user_id>/onay/', views.kullanici_onay, name='kullanici_onay'),
    path('kullanicilar/<int:user_id>/sifre/', views.kullanici_sifre_sifirla, name='kullanici_sifre'),
]
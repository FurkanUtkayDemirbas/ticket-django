from django.urls import path
from . import views

urlpatterns = [
    path('', views.masraf_listesi, name='masraf_listesi'),
    path('ekle/', views.masraf_ekle, name='masraf_ekle'),
    path('<int:pk>/duzenle/', views.masraf_duzenle, name='masraf_duzenle'),
    path('<int:pk>/sil/', views.masraf_sil, name='masraf_sil'),
    
    path('turler/', views.masraf_turu_listesi, name='masraf_turu_listesi'),
    path('turler/ekle/', views.masraf_turu_ekle, name='masraf_turu_ekle'),
    path('turler/<int:pk>/duzenle/', views.masraf_turu_duzenle, name='masraf_turu_duzenle'),
    path('turler/<int:pk>/sil/', views.masraf_turu_sil, name='masraf_turu_sil'),
    
    path('api/get-sozlesme-muhatap/', views.get_sozlesme_muhatap, name='get_sozlesme_muhatap'),
]

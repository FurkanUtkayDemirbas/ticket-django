from django.urls import path
from . import views

urlpatterns = [
    path('', views.masraf_listesi, name='masraf_listesi'),
    path('excel/', views.masraf_excel, name='masraf_excel'),
    path('pdf/', views.masraf_pdf, name='masraf_pdf'),
    path('ekle/', views.masraf_ekle, name='masraf_ekle'),
    path('<int:pk>/duzenle/', views.masraf_duzenle, name='masraf_duzenle'),
    path('<int:pk>/sil/', views.masraf_sil, name='masraf_sil'),
    
    path('turler/', views.masraf_turu_listesi, name='masraf_turu_listesi'),
    path('turler/ekle/', views.masraf_turu_ekle, name='masraf_turu_ekle'),
    path('turler/<int:pk>/duzenle/', views.masraf_turu_duzenle, name='masraf_turu_duzenle'),
    path('turler/<int:pk>/sil/', views.masraf_turu_sil, name='masraf_turu_sil'),
    
    path('api/get-proje-muhatap/', views.get_proje_muhatap, name='get_proje_muhatap'),
    path('<int:pk>/odeme-durumu/', views.masraf_odeme_durumu_degistir, name='masraf_odeme_durumu_degistir'),
]

from django.urls import path
from . import views



app_name = 'uyelik'
urlpatterns = [
    path('giris/', views.giris_view, name='giris'),
    path('kayit/', views.kayit_view, name='kayit'),
    path('cikis/', views.cikis_view, name='cikis'),
]
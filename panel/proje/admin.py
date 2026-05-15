from django.contrib import admin
from .models import projeler

class projelerAdmin(admin.ModelAdmin):
    # Modelinde hangi alanlar varsa sadece onları yazabilirsin
    # 'sozlesmeno' ve 'tip' alanları senin modellerinde yok, o yüzden hata veriyordu.
    list_display = ('projeno', 'sozlesme_baglantisi')
    list_filter = ('sozlesme_baglantisi',)
    search_fields = ('projeno', 'sozlesme_baglantisi__sozlesmeno') # Çift alt tire ile sözleşme no içinde arama yapar

admin.site.register(projeler, projelerAdmin)
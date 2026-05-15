from django.contrib import admin

from .models import bolum, danisman

class bolumAdmin(admin.ModelAdmin):
    list_display = ('kod','isim', 'programresim')
admin.site.register(bolum,bolumAdmin)
class danismanAdmin(admin.ModelAdmin):
    list_display = ('username','isim','telefon')
admin.site.register(danisman,danismanAdmin)
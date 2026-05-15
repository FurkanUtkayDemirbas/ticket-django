from django.contrib import admin
from.models import hesapgrubu
from.models import muhatap

class hesapgrubuAdmin(admin.ModelAdmin):
    list_display = ('grupkod','name')
    search_fields = ('grupkod','name')

admin.site.register(hesapgrubu,hesapgrubuAdmin)



class muhatapAdmin(admin.ModelAdmin):
    list_display = ['unvan', 'vkn', 'adres', 'telefon','grupkod','slug','aktif']
    list_filter =  ['unvan','aktif']
    search_fields = ['unvan','aktif']

admin.site.register(muhatap,muhatapAdmin)
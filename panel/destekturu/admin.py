from django.contrib import admin

from .models import destektur
from .models import oncelik

class destekturAdmin(admin.ModelAdmin):
    list_display = ('kod','definition')
admin.site.register(destektur,destekturAdmin)
class oncelikAdmin(admin.ModelAdmin):
    list_display = ('kod','tanim')
admin.site.register(oncelik,oncelikAdmin)

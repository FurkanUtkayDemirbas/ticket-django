from django.contrib import admin
from .models import sozlesmeler,sozlesmetip,projelist


admin.site.register(sozlesmetip)


class sozlesmelerAdmin(admin.ModelAdmin):
    list_display = ('sozlesmeno','tanim','muhatap','tanim','baslangic_tarihi','bitis_tarihi','aciklama')
    list_filter = ('sozlesmeno','tanim','muhatap')
    list_search_fields = ('sozlesmeno','tanim','muhatap')
    search_fields = ('sozlesmeno','tanim','muhatap')


admin.site.register(sozlesmeler,sozlesmelerAdmin)


class projelistAdmin( admin.ModelAdmin):
    list_display = ('projeno','projetanim')
    list_filter = ('projeno','projetanim')
    search_fields = ('projeno','projetanim')


admin.site.register(projelist,projelistAdmin)
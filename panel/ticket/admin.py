from doctest import set_unittest_reportflags

from django.contrib import admin
from .models import ticket, statu, atama, aktivite

admin.site.register(statu)


class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticketno', 'konu', 'unvan', 'destekturu', 'bolumkod', 'taleptarih', 'termintarih', 'oncelikkod',
                    'aciklama', 'durumtanim', 'faturadurum']
    list_filter = ['ticketno', 'konu', 'unvan', 'destekturu', 'bolumkod', 'taleptarih', 'termintarih']
    search_fields = ['konu', 'unvan', 'destekturu', 'bolumkod', 'taleptarih', 'termintarih']


admin.site.register(ticket, TicketAdmin)


class AtamaAdmin(admin.ModelAdmin):
    list_display = ['danisman', 'ticketno', 'efor']
    list_filter = ['danisman', 'ticketno', 'efor']
    search_fields = ['danisman', 'ticketno', 'efor']


admin.site.register(atama, AtamaAdmin)


class AktiviteAdmin(admin.ModelAdmin):
    list_display = [ 'ticketno', 'date', 'time', 'danisman', 'modul']
    list_filter = ['number', 'ticketno', 'date', 'time', 'danisman', 'modul']
    search_fields = ['number', 'ticketno', 'date', 'time', 'danisman', 'modul']


admin.site.register(aktivite, AktiviteAdmin)

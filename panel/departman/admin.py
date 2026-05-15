from django.contrib import admin

# Register your models here.
from .models import departman
from.models import departman


class departmanAdmin ( admin.ModelAdmin ):
    list_display = ('kod','tanim' )
admin.site.register(departman)

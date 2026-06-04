from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Kullanıcı Profili ve Yetkilendirme'

# Orijinal User modelini admin panelinden çıkarıyoruz
admin.site.unregister(User)

# Yeni UserAdmin oluşturuyoruz ve UserProfile'ı içine ekliyoruz
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'get_muhatap_firmalar', 'get_danisman_profiller', 'is_approved')
    list_filter = ('role', 'is_approved')
    search_fields = ('user__username',)

    def get_muhatap_firmalar(self, obj):
        return ", ".join([f.unvan for f in obj.muhatap_firmalar.all()])
    get_muhatap_firmalar.short_description = 'Firmalar'

    def get_danisman_profiller(self, obj):
        return ", ".join([d.username for d in obj.danisman_profiller.all()])
    get_danisman_profiller.short_description = 'Danışman Profilleri'

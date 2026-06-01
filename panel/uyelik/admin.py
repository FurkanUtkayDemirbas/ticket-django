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
    list_display = ('user', 'role', 'muhatap_firma', 'danisman_profil', 'is_approved')
    list_filter = ('role', 'is_approved')
    search_fields = ('user__username', 'muhatap_firma__unvan')

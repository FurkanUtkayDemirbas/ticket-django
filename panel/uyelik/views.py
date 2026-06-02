from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import KayitForm, AdminKullaniciForm, AdminSifreSifirlaForm
from .models import UserProfile
from .decorators import admin_only


def kayit_view(request):
    # Kayıt olma sayfası dışarıya kapatıldı. Ziyaretçiyi uyarıp giriş sayfasına yönlendir.
    messages.warning(request, "Yeni kayıt işlemleri sadece sistem yöneticisi tarafından yapılmaktadır.")
    return redirect('uyelik:giris')


def giris_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Profil onayı kontrolü
            if hasattr(user, 'userprofile'):
                if not user.userprofile.is_approved:
                    messages.warning(request, "Hesabınız henüz onaylanmamış. Lütfen yönetici onayını bekleyin.")
                    return redirect('uyelik:giris')

            login(request, user)
            messages.success(request, "Giriş başarılı.")
            return redirect('index')
        else:
            messages.error(request, "Kullanıcı adı veya şifre hatalı.")

    return render(request, 'uyelik/giris.html')


def cikis_view(request):
    logout(request)
    messages.info(request, "Çıkış yapıldı.")
    return redirect('uyelik:giris')


# ─────────────────────────────────────────────────────────
#   KULLANICI YÖNETİMİ (Sadece Admin)
# ─────────────────────────────────────────────────────────

@admin_only
def kullanici_listesi(request):
    """Tüm kullanıcıları listeler."""
    kullanicilar = User.objects.select_related('userprofile').all().order_by('username')

    toplam = kullanicilar.count()
    admin_sayisi = sum(1 for u in kullanicilar if u.is_superuser or (hasattr(u, 'userprofile') and u.userprofile.role == 'Admin'))
    danisman_sayisi = sum(1 for u in kullanicilar if not u.is_superuser and hasattr(u, 'userprofile') and u.userprofile.role == 'Danisman')
    firma_sayisi = sum(1 for u in kullanicilar if not u.is_superuser and hasattr(u, 'userprofile') and u.userprofile.role == 'Firma')
    onay_bekleyen = sum(1 for u in kullanicilar if hasattr(u, 'userprofile') and not u.userprofile.is_approved)

    stat_cards = [
        ('Toplam Kullanıcı', toplam, 'fa-solid fa-users', 'bg-blue-500'),
        ('Admin', admin_sayisi, 'fa-solid fa-shield-halved', 'bg-purple-500'),
        ('Danışman', danisman_sayisi, 'fa-solid fa-user-tie', 'bg-cyan-500'),
        ('Firma', firma_sayisi, 'fa-solid fa-building', 'bg-emerald-500'),
    ]

    return render(request, 'uyelik/kullanici_listesi.html', {
        'kullanicilar': kullanicilar,
        'stat_cards': stat_cards,
        'onay_bekleyen': onay_bekleyen,
    })


@admin_only
def kullanici_ekle(request):
    """Yeni kullanıcı (Firma / Danışman / Admin) ekler."""
    if request.method == 'POST':
        form = AdminKullaniciForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.create_user(
                username=cd['username'],
                password=cd['password1'],
                first_name=cd.get('first_name', ''),
                last_name=cd.get('last_name', ''),
                email=cd.get('email', ''),
            )
            role = cd['role']
            UserProfile.objects.create(
                user=user,
                role=role,
                muhatap_firma=cd.get('muhatap_firma') if role == 'Firma' else None,
                danisman_profil=cd.get('danisman_profil') if role == 'Danisman' else None,
                is_approved=True,
            )
            messages.success(request, f'"{user.username}" kullanıcısı başarıyla oluşturuldu.')
            return redirect('uyelik:kullanici_listesi')
    else:
        form = AdminKullaniciForm()

    return render(request, 'uyelik/kullanici_ekle.html', {'form': form})


@admin_only
def kullanici_sil(request, user_id):
    """Kullanıcıyı siler (kendi hesabını silemez)."""
    kullanici = get_object_or_404(User, pk=user_id)
    if kullanici == request.user:
        messages.error(request, 'Kendi hesabınızı silemezsiniz.')
        return redirect('uyelik:kullanici_listesi')
    if request.method == 'POST':
        isim = kullanici.username
        kullanici.delete()
        messages.success(request, f'"{isim}" kullanıcısı silindi.')
        return redirect('uyelik:kullanici_listesi')
    return render(request, 'uyelik/kullanici_sil.html', {'kullanici': kullanici})


@admin_only
def kullanici_onay(request, user_id):
    """Kullanıcı hesabını onaylar veya onayı kaldırır."""
    kullanici = get_object_or_404(User, pk=user_id)
    if hasattr(kullanici, 'userprofile'):
        profil = kullanici.userprofile
        profil.is_approved = not profil.is_approved
        profil.save()
        durum = 'onaylandı' if profil.is_approved else 'onayı kaldırıldı'
        messages.success(request, f'"{kullanici.username}" {durum}.')
    return redirect('uyelik:kullanici_listesi')


@admin_only
def kullanici_sifre_sifirla(request, user_id):
    """Admin başka bir kullanıcının şifresini sıfırlar."""
    kullanici = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = AdminSifreSifirlaForm(request.POST)
        if form.is_valid():
            kullanici.set_password(form.cleaned_data['new_password1'])
            kullanici.save()
            messages.success(request, f'"{kullanici.username}" şifresi güncellendi.')
            return redirect('uyelik:kullanici_listesi')
    else:
        form = AdminSifreSifirlaForm()
    return render(request, 'uyelik/kullanici_sifre.html', {'form': form, 'kullanici': kullanici})

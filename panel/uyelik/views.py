from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import KayitForm, AdminKullaniciForm, AdminKullaniciDuzenleForm, AdminSifreSifirlaForm
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
            profile = UserProfile.objects.create(
                user=user,
                role=role,
                is_approved=True,
            )
            if role == 'Firma' and cd.get('muhatap_firmalar'):
                profile.muhatap_firmalar.set(cd.get('muhatap_firmalar'))
            if role == 'Danisman' and cd.get('danisman_profiller'):
                profile.danisman_profiller.set(cd.get('danisman_profiller'))
            messages.success(request, f'"{user.username}" kullanıcısı başarıyla oluşturuldu.')
            return redirect('uyelik:kullanici_listesi')
    else:
        form = AdminKullaniciForm()

    return render(request, 'uyelik/kullanici_ekle.html', {'form': form})


@admin_only
def kullanici_duzenle(request, user_id):
    """Mevcut kullanıcıyı düzenler (ad, soyad, e-posta, rol, bağlı firma/danışman)."""
    kullanici = get_object_or_404(User, pk=user_id)

    # Kendi superuser hesabını düzenlemeye çalışanı engelle (isteğe bağlı koruma)
    if kullanici.is_superuser and not request.user.is_superuser:
        return render(request, '403.html', status=403)

    # Mevcut değerler
    profile = getattr(kullanici, 'userprofile', None)
    mevcut_firmalar = list(profile.muhatap_firmalar.all()) if profile else []
    mevcut_danismanlar = list(profile.danisman_profiller.all()) if profile else []

    if request.method == 'POST':
        form = AdminKullaniciDuzenleForm(request.POST, kullanici=kullanici)
        if form.is_valid():
            cd = form.cleaned_data
            kullanici.username = cd['username']
            kullanici.first_name = cd.get('first_name', '')
            kullanici.last_name = cd.get('last_name', '')
            kullanici.email = cd.get('email', '')
            kullanici.save()

            role = cd['role']
            if profile is None:
                profile = UserProfile.objects.create(user=kullanici, role=role, is_approved=True)
            else:
                profile.role = role
                profile.save()

            # M2M güncelle
            profile.muhatap_firmalar.set(cd.get('muhatap_firmalar') or [])
            profile.danisman_profiller.set(cd.get('danisman_profiller') or [])

            messages.success(request, f'"{kullanici.username}" kullanıcısı başarıyla güncellendi.')
            return redirect('uyelik:kullanici_listesi')
    else:
        # Formu mevcut değerlerle doldur
        initial = {
            'username': kullanici.username,
            'first_name': kullanici.first_name,
            'last_name': kullanici.last_name,
            'email': kullanici.email,
            'role': profile.role if profile else 'Admin',
            'muhatap_firmalar': mevcut_firmalar,
            'danisman_profiller': mevcut_danismanlar,
        }
        form = AdminKullaniciDuzenleForm(initial=initial, kullanici=kullanici)

    return render(request, 'uyelik/kullanici_duzenle.html', {
        'form': form,
        'kullanici': kullanici,
        'mevcut_firmalar': mevcut_firmalar,
        'mevcut_danismanlar': mevcut_danismanlar,
    })


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

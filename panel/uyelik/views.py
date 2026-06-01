from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import KayitForm
from .models import UserProfile

def kayit_view(request):
    # Kayıt olma sayfası dışarıya kapatıldı. Ziyaretçiyi uyarıp giriş sayfasına yönlendir.
    messages.warning(request, "Yeni kayıt işlemleri sadece sistem yöneticisi tarafından yapılmaktadır.")
    return redirect('uyelik:giris')

    if request.method == "POST":
        form = KayitForm(request.POST)

        if form.is_valid():
            user = form.save()
            # Profil oluştur ve firmayı ata
            muhatap_firma = form.cleaned_data.get('muhatap_firma')
            UserProfile.objects.create(
                user=user,
                role='Firma',
                muhatap_firma=muhatap_firma,
                is_approved=False
            )
            messages.success(request, "Kayıt başarılı. Yöneticiler hesabınızı onayladıktan sonra işlem yapabilirsiniz.")
            return redirect('uyelik:giris')
        else:
            print(form.errors)
            messages.error(request, "Kayıt başarısız. Lütfen bilgileri kontrol edin.")
    else:
        form = KayitForm()

    return render(request, 'uyelik/kayit.html', {'form': form})

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

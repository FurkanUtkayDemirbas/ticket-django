from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .forms import KayitForm


def kayit_view(request):
    if request.method == "POST":
        form = KayitForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Kayıt başarılı. Hoş geldiniz!")
            return redirect('index')
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

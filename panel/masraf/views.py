from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Masraf, MasrafTuru
from .forms import MasrafForm, MasrafTuruForm
from sozlesme.models import sozlesmeler
from proje.models import projeler
from uyelik.decorators import admin_veya_danisman_only, admin_only

@admin_veya_danisman_only
def masraf_listesi(request):
    masraflar = Masraf.objects.all().order_by('-tarih', '-id')
    return render(request, 'masraf/masraf_listesi.html', {'masraflar': masraflar})

@admin_veya_danisman_only
def masraf_ekle(request):
    if request.method == 'POST':
        form = MasrafForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Masraf başarıyla eklendi.')
            return redirect('masraf_listesi')
    else:
        form = MasrafForm()
    return render(request, 'masraf/masraf_form.html', {'form': form, 'title': 'Masraf Ekle'})

@admin_veya_danisman_only
def masraf_duzenle(request, pk):
    masraf = get_object_or_404(Masraf, pk=pk)
    if request.method == 'POST':
        form = MasrafForm(request.POST, instance=masraf)
        if form.is_valid():
            form.save()
            messages.success(request, 'Masraf başarıyla güncellendi.')
            return redirect('masraf_listesi')
    else:
        form = MasrafForm(instance=masraf)
    return render(request, 'masraf/masraf_form.html', {'form': form, 'title': 'Masraf Düzenle'})

@admin_veya_danisman_only
def masraf_sil(request, pk):
    masraf = get_object_or_404(Masraf, pk=pk)
    if request.method == 'POST':
        masraf.delete()
        messages.success(request, 'Masraf başarıyla silindi.')
        return redirect('masraf_listesi')
    return render(request, 'masraf/masraf_sil.html', {'masraf': masraf})

@admin_only
def masraf_turu_listesi(request):
    turler = MasrafTuru.objects.all().select_related('muhatap').order_by('muhatap__unvan', 'tanim')
    return render(request, 'masraf/masraf_turu_listesi.html', {'turler': turler})

@admin_only
def masraf_turu_ekle(request):
    if request.method == 'POST':
        form = MasrafTuruForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Masraf Türü başarıyla eklendi.')
            return redirect('masraf_turu_listesi')
    else:
        form = MasrafTuruForm()
    return render(request, 'masraf/masraf_turu_form.html', {'form': form, 'title': 'Masraf Türü Ekle'})

@admin_only
def masraf_turu_duzenle(request, pk):
    tur = get_object_or_404(MasrafTuru, pk=pk)
    if request.method == 'POST':
        form = MasrafTuruForm(request.POST, instance=tur)
        if form.is_valid():
            form.save()
            messages.success(request, 'Masraf Türü başarıyla güncellendi.')
            return redirect('masraf_turu_listesi')
    else:
        form = MasrafTuruForm(instance=tur)
    return render(request, 'masraf/masraf_turu_form.html', {'form': form, 'title': 'Masraf Türü Düzenle'})

@admin_only
def masraf_turu_sil(request, pk):
    tur = get_object_or_404(MasrafTuru, pk=pk)
    if request.method == 'POST':
        try:
            tur.delete()
            messages.success(request, 'Masraf Türü başarıyla silindi.')
        except Exception as e:
            messages.error(request, 'Bu Masraf Türü kullanımda olduğu için silinemez.')
        return redirect('masraf_turu_listesi')
    return render(request, 'masraf/masraf_turu_sil.html', {'tur': tur})

@login_required
def get_proje_muhatap(request):
    proje_id = request.GET.get('proje_id')
    if proje_id:
        try:
            proje = projeler.objects.get(pk=proje_id)
            sozlesme = proje.sozlesme_baglantisi
            muhatap_adi = ''
            masraf_turleri = []

            if sozlesme and sozlesme.muhatap:
                muhatap_adi = str(sozlesme.muhatap).strip()
                muhatap_obj = sozlesme.muhatap
                # Genel türler (muhatap=NULL) + firmaya özel türler
                turler = MasrafTuru.objects.filter(
                    muhatap__isnull=True
                ) | MasrafTuru.objects.filter(muhatap=muhatap_obj)
                turler = turler.order_by('tanim')
                masraf_turleri = [{'id': t.pk, 'tanim': t.tanim} for t in turler]
            else:
                # muhatap yoksa sadece genel türler
                turler = MasrafTuru.objects.filter(muhatap__isnull=True).order_by('tanim')
                masraf_turleri = [{'id': t.pk, 'tanim': t.tanim} for t in turler]

            return JsonResponse({'muhatap_adi': muhatap_adi, 'masraf_turleri': masraf_turleri})
        except (projeler.DoesNotExist, ValueError):
            pass
    return JsonResponse({'muhatap_adi': '', 'masraf_turleri': []})

@admin_veya_danisman_only
def masraf_odeme_durumu_degistir(request, pk):
    masraf = get_object_or_404(Masraf, pk=pk)
    if request.method == 'POST':
        masraf.odendi_mi = not masraf.odendi_mi
        masraf.save()
        messages.success(request, f'Masraf ödeme durumu "{"Ödendi" if masraf.odendi_mi else "Ödenmedi"}" olarak güncellendi.')
    return redirect('masraf_listesi')


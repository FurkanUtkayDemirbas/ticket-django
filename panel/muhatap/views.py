from django.shortcuts import render, get_object_or_404, redirect
from .models import muhatap
from .forms import MuhatapForm
from uyelik.decorators import admin_only

# MUHATAP LİSTESİ
@admin_only
def muhatap_listesi(request):
    muhataplar = muhatap.objects.all().order_by('id')
    secili_unvan = request.GET.get("unvan", "").strip()
    secili_vkn = request.GET.get("vkn", "").strip()
    secili_hesap_grubu = request.GET.get("hesap_grubu", "").strip()
    durum = request.GET.get("durum", "").strip()

    if secili_unvan:
        muhataplar = muhataplar.filter(unvan=secili_unvan)
    if secili_vkn:
        muhataplar = muhataplar.filter(vkn=secili_vkn)
    if secili_hesap_grubu:
        muhataplar = muhataplar.filter(grupkod_id=secili_hesap_grubu)
    if durum in {"aktif", "pasif"}:
        muhataplar = muhataplar.filter(aktif=(durum == "aktif"))

    tum_muhataplar = muhatap.objects.select_related("grupkod").all().order_by("id")

    return render(request, 'muhatap_listesi.html', {
        'muhataplar': muhataplar,
        'unvanlar': tum_muhataplar.values_list("unvan", flat=True).distinct().order_by("unvan"),
        'vknler': tum_muhataplar.exclude(vkn="").values_list("vkn", flat=True).distinct().order_by("vkn"),
        'hesap_gruplari': tum_muhataplar.exclude(grupkod__isnull=True).values("grupkod_id", "grupkod__name").distinct().order_by("grupkod__name"),
        'secili_unvan': secili_unvan,
        'secili_vkn': secili_vkn,
        'secili_hesap_grubu': secili_hesap_grubu,
        'secili_durum': durum,
    })

# YENİ MUHATAP EKLEME
@admin_only
def muhatap_ekle(request):
    if request.method == "POST":
        form = MuhatapForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('muhatap_listesi')
    else:
        form = MuhatapForm()
    return render(request, 'muhatap_ekle.html', {'form': form})

# MEVCUT MUHATABI DÜZENLEME
@admin_only
def muhatap_duzenle(request, pk):
    kayit = get_object_or_404(muhatap, pk=pk)
    if request.method == "POST":
        form = MuhatapForm(request.POST, instance=kayit)
        if form.is_valid():
            form.save()
            return redirect('muhatap_listesi')
    else:
        form = MuhatapForm(instance=kayit)
    return render(request, 'muhatap_duzenle.html', {'form': form, 'kayit': kayit})

# MUHATAP SİLME
@admin_only
def muhatap_sil(request, pk):
    kayit = get_object_or_404(muhatap, pk=pk)
    kayit.delete()
    return redirect('muhatap_listesi')

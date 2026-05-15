from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import muhatap
from .forms import MuhatapForm

# MUHATAP LİSTESİ
def muhatap_listesi(request):
    muhataplar = muhatap.objects.all().order_by('unvan')
    arama = request.GET.get("arama", "").strip()
    durum = request.GET.get("durum", "").strip()

    if arama:
        muhataplar = muhataplar.filter(
            Q(unvan__icontains=arama)
            | Q(vkn__icontains=arama)
            | Q(telefon__icontains=arama)
            | Q(adres__icontains=arama)
            | Q(grupkod__name__icontains=arama)
        )
    if durum in {"aktif", "pasif"}:
        muhataplar = muhataplar.filter(aktif=(durum == "aktif"))

    return render(request, 'muhatap_listesi.html', {
        'muhataplar': muhataplar,
        'arama': arama,
        'secili_durum': durum,
    })

# YENİ MUHATAP EKLEME
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
def muhatap_sil(request, pk):
    kayit = get_object_or_404(muhatap, pk=pk)
    kayit.delete()
    return redirect('muhatap_listesi')

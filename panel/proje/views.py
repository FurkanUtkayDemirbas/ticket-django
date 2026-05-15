from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import projeler
from .forms import ProjeForm

def proje_listesi(request):
    veriler = projeler.objects.select_related("sozlesme_baglantisi", "sozlesme_baglantisi__muhatap").all()
    arama = request.GET.get("arama", "").strip()

    if arama:
        veriler = veriler.filter(
            Q(projeno__icontains=arama)
            | Q(sozlesme_baglantisi__sozlesmeno__icontains=arama)
            | Q(sozlesme_baglantisi__muhatap__unvan__icontains=arama)
        )

    return render(request, 'proje_listesi.html', {'projeler': veriler, 'arama': arama})

def proje_ekle(request):
    if request.method == "POST":
        form = ProjeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('proje_listesi')
    else:
        form = ProjeForm()
    return render(request, 'proje_ekle.html', {'form': form})

def proje_duzenle(request, pk):
    kayit = get_object_or_404(projeler, pk=pk)
    if request.method == "POST":
        form = ProjeForm(request.POST, instance=kayit)
        if form.is_valid():
            form.save()
            return redirect('proje_listesi')
    else:
        form = ProjeForm(instance=kayit)
    return render(request, 'proje_duzenle.html', {'form': form, 'kayit': kayit})

def proje_sil(request, pk):
    kayit = get_object_or_404(projeler, pk=pk)
    kayit.delete()
    return redirect('proje_listesi')

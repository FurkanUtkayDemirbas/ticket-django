from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import departman
from .forms import DepartmanForm
from uyelik.decorators import admin_only

@admin_only
def departman_listesi(request):
    veriler = departman.objects.all().order_by('kod')
    arama = request.GET.get("arama", "").strip()
    kod = request.GET.get("kod", "").strip()
    tanim = request.GET.get("tanim", "").strip()

    if arama:
        veriler = veriler.filter(Q(kod__icontains=arama) | Q(tanim__icontains=arama))
    if kod:
        veriler = veriler.filter(kod__icontains=kod)
    if tanim:
        veriler = veriler.filter(tanim__icontains=tanim)

    return render(request, 'departman_listesi.html', {
        'departmanlar': veriler,
        'arama': arama,
        'kod': kod,
        'tanim': tanim,
    })

@admin_only
def departman_duzenle(request, pk):
    """Mevcut bir departman kaydını günceller."""
    kayit = get_object_or_404(departman, pk=pk)
    if request.method == "POST":
        form = DepartmanForm(request.POST, instance=kayit)
        if form.is_valid():
            form.save()
            return redirect('departman_listesi')
    else:
        form = DepartmanForm(instance=kayit)
    return render(request, 'departman_duzenle.html', {'form': form, 'kayit': kayit})

@admin_only
def departman_ekle(request):
    if request.method == "POST":
        form = DepartmanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('departman_listesi')
    else:
        form = DepartmanForm()
    return render(request, 'departman_ekle.html', {'form': form})

@admin_only
def departman_sil(request, pk):
    kayit = get_object_or_404(departman, pk=pk)
    kayit.delete()
    return redirect('departman_listesi')

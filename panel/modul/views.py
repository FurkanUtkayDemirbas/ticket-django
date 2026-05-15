from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q

from .models import bolum, danisman
from .forms import BolumForm, DanismanForm


def bolum_listesi(request):
    veriler = bolum.objects.all().order_by("kod")
    arama = request.GET.get("arama", "").strip()
    kod = request.GET.get("kod", "").strip()
    program = request.GET.get("program", "").strip()
    isim = request.GET.get("isim", "").strip()

    if arama:
        veriler = veriler.filter(
            Q(kod__icontains=arama) | Q(program__icontains=arama) | Q(isim__icontains=arama)
        )
    if kod:
        veriler = veriler.filter(kod__icontains=kod)
    if program:
        veriler = veriler.filter(program__icontains=program)
    if isim:
        veriler = veriler.filter(isim__icontains=isim)

    return render(request, "modul_listesi.html", {
        "moduller": veriler,
        "arama": arama,
        "kod": kod,
        "program": program,
        "isim": isim,
    })


def bolum_ekle(request):
    if request.method == "POST":
        form = BolumForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("modul_listesi")
    else:
        form = BolumForm()

    return render(request, "modul_ekle.html", {"form": form})


def bolum_duzenle(request, pk):
    kayit = get_object_or_404(bolum, pk=pk)
    if request.method == "POST":
        form = BolumForm(request.POST, request.FILES, instance=kayit)
        if form.is_valid():
            form.save()
            return redirect("modul_listesi")
    else:
        form = BolumForm(instance=kayit)

    return render(request, "modul_duzenle.html", {"form": form, "kayit": kayit})


def bolum_sil(request, pk):
    kayit = get_object_or_404(bolum, pk=pk)
    kayit.delete()
    return redirect("modul_listesi")


def danisman_listesi(request):
    veriler = danisman.objects.prefetch_related("yetkinlik").all().order_by("username")
    arama = request.GET.get("arama", "").strip()
    tur = request.GET.get("tur", "").strip()

    if arama:
        veriler = veriler.filter(
            Q(username__icontains=arama)
            | Q(isim__icontains=arama)
            | Q(email__icontains=arama)
            | Q(telefon__icontains=arama)
            | Q(yetkinlik__isim__icontains=arama)
            | Q(yetkinlik__program__icontains=arama)
        ).distinct()
    if tur:
        veriler = veriler.filter(tur=tur)

    return render(request, "danisman_listesi.html", {
        "danismanlar": veriler,
        "arama": arama,
        "secili_tur": tur,
        "turler": danisman._meta.get_field("tur").choices,
    })


def danisman_ekle(request):
    if request.method == "POST":
        form = DanismanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("danisman_listesi")
    else:
        form = DanismanForm()

    return render(request, "danisman_ekle.html", {"form": form})


def danisman_duzenle(request, pk):
    kayit = get_object_or_404(danisman, pk=pk)
    if request.method == "POST":
        form = DanismanForm(request.POST, instance=kayit)
        if form.is_valid():
            form.save()
            return redirect("danisman_listesi")
    else:
        form = DanismanForm(instance=kayit)

    return render(request, "danisman_duzenle.html", {"form": form, "kayit": kayit})


def danisman_sil(request, pk):
    kayit = get_object_or_404(danisman, pk=pk)
    kayit.delete()
    return redirect("danisman_listesi")

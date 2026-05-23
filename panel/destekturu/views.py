from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q

from .forms import DestekTurForm
from .models import destektur


def destekturu_listesi(request):
    destek_turleri = destektur.objects.all().order_by("kod")
    arama = request.GET.get("arama", "").strip()

    if arama:
        destek_turleri = destek_turleri.filter(
            Q(kod__icontains=arama) | Q(definition__icontains=arama)
        )

    return render(request, "destekturu_listesi.html", {"destek_turleri": destek_turleri, "arama": arama})


def destekturu_ekle(request):
    if request.method == "POST":
        form = DestekTurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("destekturu_listesi")
    else:
        form = DestekTurForm()

    return render(request, "destekturu_ekle.html", {"form": form})


def destekturu_duzenle(request, pk):
    kayit = get_object_or_404(destektur, pk=pk)
    if request.method == "POST":
        form = DestekTurForm(request.POST, instance=kayit)
        if form.is_valid():
            form.save()
            return redirect("destekturu_listesi")
    else:
        form = DestekTurForm(instance=kayit)

    return render(request, "destekturu_duzenle.html", {"form": form, "kayit": kayit})


def destekturu_sil(request, pk):
    from django.db.models import ProtectedError
    kayit = get_object_or_404(destektur, pk=pk)
    try:
        kayit.delete()
        return redirect("destekturu_listesi")
    except ProtectedError:
        destek_turleri = destektur.objects.all().order_by("kod")
        arama = request.GET.get("arama", "").strip()
        error_msg = "Bu destek türü bir veya daha fazla ticket'a atanmış olduğu için silinemez."
        return render(request, "destekturu_listesi.html", {"destek_turleri": destek_turleri, "arama": arama, "error": error_msg})

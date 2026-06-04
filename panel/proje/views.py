from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import projeler
from .forms import ProjeForm

def proje_listesi(request):
    veriler = projeler.objects.select_related("sozlesme_baglantisi", "sozlesme_baglantisi__muhatap").all()
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            veriler = veriler.filter(sozlesme_baglantisi__muhatap__in=profile.muhatap_firmalar.all())
        # Danışmanlar tüm projeleri (salt-okunur) görebilir, o yüzden ekstra filtre yok.

    arama = request.GET.get("arama", "").strip()

    if arama:
        veriler = veriler.filter(
            Q(projeno__icontains=arama)
            | Q(sozlesme_baglantisi__sozlesmeno__icontains=arama)
            | Q(sozlesme_baglantisi__muhatap__unvan__icontains=arama)
        )

    return render(request, 'proje_listesi.html', {'projeler': veriler, 'arama': arama})

def proje_ekle(request):
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'Danisman':
        return render(request, '403.html', status=403)
        
    if request.method == "POST":
        form = ProjeForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('proje_listesi')
    else:
        form = ProjeForm(user=request.user)
    return render(request, 'proje_ekle.html', {'form': form})

def proje_duzenle(request, pk):
    kayit = get_object_or_404(projeler, pk=pk)
    
    # YETKİ KONTROLÜ
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            if kayit.sozlesme_baglantisi.muhatap not in profile.muhatap_firmalar.all():
                return render(request, '403.html', status=403)
        elif profile.role == 'Danisman':
            return render(request, '403.html', status=403)

    if request.method == "POST":
        form = ProjeForm(request.POST, instance=kayit, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('proje_listesi')
    else:
        form = ProjeForm(instance=kayit, user=request.user)
    return render(request, 'proje_duzenle.html', {'form': form, 'kayit': kayit})

def proje_sil(request, pk):
    kayit = get_object_or_404(projeler, pk=pk)
    
    # YETKİ KONTROLÜ
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            if kayit.sozlesme_baglantisi.muhatap not in profile.muhatap_firmalar.all():
                return render(request, '403.html', status=403)
        elif profile.role == 'Danisman':
            return render(request, '403.html', status=403)
                
    kayit.delete()
    return redirect('proje_listesi')

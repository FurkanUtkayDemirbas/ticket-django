from django.shortcuts import render, redirect, get_object_or_404
from .models import projeler
from .forms import ProjeForm

def _gorunur_projeler(request):
    veriler = projeler.objects.select_related("sozlesme_baglantisi", "sozlesme_baglantisi__muhatap").all()
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            veriler = veriler.filter(sozlesme_baglantisi__muhatap__in=profile.muhatap_firmalar.all())
        # Danışmanlar tüm projeleri (salt-okunur) görebilir, o yüzden ekstra filtre yok.

    return veriler.order_by("projeno")


def proje_listesi(request):
    secili_proje_no = request.GET.get("proje_no", "").strip()
    secili_sozlesme_no = request.GET.get("sozlesme_no", "").strip()
    secili_muhatap = request.GET.get("muhatap", "").strip()

    tum_projeler = _gorunur_projeler(request)
    veriler = tum_projeler

    if secili_proje_no:
        veriler = veriler.filter(projeno=secili_proje_no)
    if secili_sozlesme_no:
        veriler = veriler.filter(sozlesme_baglantisi__sozlesmeno=secili_sozlesme_no)
    if secili_muhatap:
        veriler = veriler.filter(sozlesme_baglantisi__muhatap__unvan=secili_muhatap)

    context = {
        'projeler': veriler,
        'proje_nolari': tum_projeler.values_list("projeno", flat=True).distinct(),
        'sozlesme_nolari': tum_projeler.values_list("sozlesme_baglantisi__sozlesmeno", flat=True).distinct().order_by("sozlesme_baglantisi__sozlesmeno"),
        'muhataplar': tum_projeler.values_list("sozlesme_baglantisi__muhatap__unvan", flat=True).distinct().order_by("sozlesme_baglantisi__muhatap__unvan"),
        'secili_proje_no': secili_proje_no,
        'secili_sozlesme_no': secili_sozlesme_no,
        'secili_muhatap': secili_muhatap,
    }

    return render(request, 'proje_listesi.html', context)

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

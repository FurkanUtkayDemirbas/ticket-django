from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import sozlesmeler
from .forms import SozlesmeForm

def sozlesme_listesi(request):
    veriler = sozlesmeler.objects.select_related("tip", "muhatap").all().order_by('-baslangic_tarihi')
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            veriler = veriler.filter(muhatap__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman':
            veriler = veriler.none() # Danışmanlar sözleşmeleri göremez

    arama = request.GET.get("arama", "").strip()
    sozlesme_no = request.GET.get("sozlesme_no", "").strip()
    tip = request.GET.get("tip", "").strip()
    muhatap = request.GET.get("muhatap", "").strip()
    baslangic = request.GET.get("baslangic", "").strip()
    bitis = request.GET.get("bitis", "").strip()

    if arama:
        veriler = veriler.filter(
            Q(sozlesmeno__icontains=arama)
            | Q(tanim__icontains=arama)
            | Q(tip__tanim__icontains=arama)
            | Q(muhatap__unvan__icontains=arama)
        )
    if sozlesme_no:
        veriler = veriler.filter(sozlesmeno__icontains=sozlesme_no)
    if tip:
        veriler = veriler.filter(tip_id=tip)
    if muhatap:
        veriler = veriler.filter(muhatap_id=muhatap)
    if baslangic:
        veriler = veriler.filter(baslangic_tarihi__date__gte=baslangic)
    if bitis:
        veriler = veriler.filter(bitis_tarihi__date__lte=bitis)

    return render(request, 'sozlesme_listesi.html', {
        'sozlesmeler': veriler,
        'arama': arama,
        'sozlesme_no': sozlesme_no,
        'secili_tip': tip,
        'secili_muhatap': muhatap,
        'baslangic': baslangic,
        'bitis': bitis,
        'sozlesme_tipleri': sozlesmeler._meta.get_field("tip").remote_field.model.objects.order_by("tanim"),
        'muhataplar': sozlesmeler._meta.get_field("muhatap").remote_field.model.objects.filter(pk__in=request.user.userprofile.muhatap_firmalar.all()) if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'Firma' else sozlesmeler._meta.get_field('muhatap').remote_field.model.objects.order_by('unvan'),
    })

def sozlesme_ekle(request):
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'Danisman':
        return render(request, '403.html', status=403)
        
    if request.method == "POST":
        form = SozlesmeForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('sozlesme_listesi')
    else:
        form = SozlesmeForm(user=request.user)
    return render(request, 'sozlesme_ekle.html', {'form': form})

def sozlesme_duzenle(request, pk):
    kayit = get_object_or_404(sozlesmeler, pk=pk)
    
    # YETKİ KONTROLÜ
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            if kayit.muhatap not in profile.muhatap_firmalar.all():
                return render(request, '403.html', status=403)
        elif profile.role == 'Danisman':
            return render(request, '403.html', status=403)

    if request.method == "POST":
        form = SozlesmeForm(request.POST, instance=kayit, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('sozlesme_listesi')
    else:
        form = SozlesmeForm(instance=kayit, user=request.user)
    return render(request, 'sozlesme_duzenle.html', {'form': form, 'kayit': kayit})

def sozlesme_sil(request, pk):
    kayit = get_object_or_404(sozlesmeler, pk=pk)
    
    # YETKİ KONTROLÜ
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            if kayit.muhatap not in profile.muhatap_firmalar.all():
                return render(request, '403.html', status=403)
        elif profile.role == 'Danisman':
            return render(request, '403.html', status=403)
                
    kayit.delete()
    return redirect('sozlesme_listesi')

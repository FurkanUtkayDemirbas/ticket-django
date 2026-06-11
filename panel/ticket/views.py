from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.urls import reverse
from django.http import JsonResponse
from muhatap.models import muhatap
from sozlesme.models import sozlesmeler
from .models import TicketYazisma, aktivite, ticket, atama
from .forms import AktiviteForm, TicketForm, TicketIciAktiviteForm, AtamaForm, TicketIciEforForm, TicketYazismaForm


def _ticket_listesi_redirect(request):
    query_string = request.GET.urlencode()
    if query_string:
        return redirect(f"{reverse('ticket_listesi')}?{query_string}")
    return redirect(reverse('ticket_listesi'))

# 1. DASHBOARD (ANA SAYFA)
def ana_sayfa(request):
    """Sistem özetini ve istatistikleri gösteren ana ekran."""
    ticket_qs = ticket.objects.all()
    muhatap_qs = muhatap.objects.all()
    sozlesme_qs = sozlesmeler.objects.all()

    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            ticket_qs = ticket_qs.filter(unvan__in=profile.muhatap_firmalar.all())
            muhatap_qs = muhatap_qs.filter(pk__in=profile.muhatap_firmalar.all())
            sozlesme_qs = sozlesme_qs.filter(muhatap__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            ticket_qs = ticket_qs.filter(danisman__in=profile.danisman_profiller.all())

    toplam = ticket_qs.count()
    toplam_muhatap = muhatap_qs.count()
    toplam_sozlesme = sozlesme_qs.count()
    acik = ticket_qs.exclude(durumtanim__durumtanim="Tamamlandı").count()
    tamamlanan = ticket_qs.filter(durumtanim__durumtanim="Tamamlandı").count()
    son_eklenenler = ticket_qs.order_by('-taleptarih')[:5]

    context = {
        'toplam_kayit': toplam,
        'toplam_muhatap': toplam_muhatap,
        'toplam_sozlesme': toplam_sozlesme,
        'acik_ticketlar': acik,
        'tamamlanan_count': tamamlanan,
        'son_ticketlar': son_eklenenler,
    }
    return render(request, 'index.html', context)

# 2. LİSTELEME
def ticket_listesi(request):
    """Tüm ticket kayıtlarını tablo halinde listeler."""
    tum_ticketlar = ticket.objects.select_related(
        "unvan", "durumtanim", "faturadurum", "bolumkod", "oncelikkod"
    ).prefetch_related("danisman").all().order_by('-ticketno')
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            tum_ticketlar = tum_ticketlar.filter(unvan__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            tum_ticketlar = tum_ticketlar.filter(danisman__in=profile.danisman_profiller.all()).distinct()

    arama = request.GET.get("arama", "").strip()
    muhatap_secimi = request.GET.get("muhatap", "").strip() or request.GET.get("unvan", "").strip()
    durum = request.GET.get("durum", "").strip()
    durum_grubu = request.GET.get("durum_grubu", "").strip()
    danisman = request.GET.get("danisman", "").strip()
    baslangic_tarihi = request.GET.get("baslangic_tarihi", "").strip()
    bitis_tarihi = request.GET.get("bitis_tarihi", "").strip()
    bolum = request.GET.get("bolum", "").strip()
    faturalama = request.GET.get("faturalama", "").strip()
    oncelik = request.GET.get("oncelik", "").strip()

    if arama:
        tum_ticketlar = tum_ticketlar.filter(
            Q(ticketno__icontains=arama)
            | Q(konu__icontains=arama)
            | Q(musteri_ticket_no__icontains=arama)
        )
    if muhatap_secimi:
        tum_ticketlar = tum_ticketlar.filter(unvan_id=muhatap_secimi)
    if durum:
        tum_ticketlar = tum_ticketlar.filter(durumtanim_id=durum)
    elif durum_grubu == "bekleyen":
        tum_ticketlar = tum_ticketlar.exclude(durumtanim__durumtanim="Tamamlandı")
    elif durum_grubu == "cozulen":
        tum_ticketlar = tum_ticketlar.filter(durumtanim__durumtanim="Tamamlandı")
    if danisman:
        tum_ticketlar = tum_ticketlar.filter(danisman__username=danisman)
    if baslangic_tarihi:
        tum_ticketlar = tum_ticketlar.filter(taleptarih__date__gte=baslangic_tarihi)
    if bitis_tarihi:
        tum_ticketlar = tum_ticketlar.filter(taleptarih__date__lte=bitis_tarihi)
    if bolum:
        tum_ticketlar = tum_ticketlar.filter(bolumkod_id=bolum)
    if faturalama:
        tum_ticketlar = tum_ticketlar.filter(faturadurum_id=faturalama)
    if oncelik:
        tum_ticketlar = tum_ticketlar.filter(oncelikkod_id=oncelik)

    # Her ticket için danışman eforlarını hesapla
    tum_ticketlar_list = list(tum_ticketlar)
    for t in tum_ticketlar_list:
        danisman_eforlari = {}
        for a in t.atama_set.all():
            if a.danisman:
                isim = a.danisman.isim or a.danisman.username
                danisman_eforlari[isim] = danisman_eforlari.get(isim, 0) + (a.efor or 0)
        t.danisman_efor_list = [f"{isim} — {efor} Saat" for isim, efor in danisman_eforlari.items()]

    filtre_ticketlar = ticket.objects.select_related("unvan").all()
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            filtre_ticketlar = filtre_ticketlar.filter(unvan__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            filtre_ticketlar = filtre_ticketlar.filter(danisman__in=profile.danisman_profiller.all()).distinct()

    context = {
        'ticketlar': tum_ticketlar_list,
        'arama': arama,
        'secili_muhatap': muhatap_secimi,
        'secili_durum': durum,
        'secili_durum_grubu': durum_grubu,
        'secili_danisman': danisman,
        'secili_baslangic_tarihi': baslangic_tarihi,
        'secili_bitis_tarihi': bitis_tarihi,
        'secili_bolum': bolum,
        'secili_faturalama': faturalama,
        'secili_oncelik': oncelik,
        'durumlar': ticket._meta.get_field("durumtanim").remote_field.model.objects.order_by("durumtanim"),
        'faturalamalar': ticket._meta.get_field("faturadurum").remote_field.model.objects.order_by("faturadurum"),
        'bolumler': ticket._meta.get_field("bolumkod").remote_field.model.objects.order_by("kod"),
        'oncelikler': ticket._meta.get_field("oncelikkod").remote_field.model.objects.order_by("kod"),
        'danismanlar': ticket._meta.get_field("danisman").related_model.objects.order_by("isim"),
        'muhataplar': ticket._meta.get_field("unvan").remote_field.model.objects.filter(ticket__in=filtre_ticketlar).distinct().order_by("unvan"),
    }
    return render(request, 'ticket_listesi.html', context)

# 3. YENİ EKLEME
def ticket_ekle(request):
    """Sıfırdan yeni bir ticket oluşturur. Aynı ekranda aktivite ve atama da eklenebilir."""
    if request.method == "POST":
        form = TicketForm(request.POST, user=request.user, is_creation=True)
        aktivite_form = TicketIciAktiviteForm(request.POST)
        efor_form = TicketIciEforForm(request.POST)

        if form.is_valid():
            yeni_ticket = form.save(commit=False)
            # Durum seçilmemişse "Yeni Talep" olarak ata (fallback)
            if not yeni_ticket.durumtanim:
                from .models import statu
                statu_obj = statu.objects.filter(durumtanim="Yeni Talep").first()
                if statu_obj:
                    yeni_ticket.durumtanim = statu_obj
            yeni_ticket.save()
            form.save_m2m()
            
            # Eğer aktivite formu doldurulmuşsa (örn: açıklama veya süre varsa) kaydet
            if aktivite_form.is_valid() and (aktivite_form.cleaned_data.get('aciklama') or aktivite_form.cleaned_data.get('time')):
                yeni_aktivite = aktivite_form.save(commit=False)
                yeni_aktivite.ticketno = yeni_ticket
                yeni_aktivite.save()
                if yeni_aktivite.danisman:
                    yeni_ticket.danisman.add(yeni_aktivite.danisman)
            
            # Eğer efor formu doldurulmuşsa (örn: efor saati veya danışman varsa) kaydet
            if efor_form.is_valid() and (efor_form.cleaned_data.get('efor') or efor_form.cleaned_data.get('danisman')):
                yeni_efor = efor_form.save(commit=False)
                yeni_efor.ticketno = yeni_ticket
                yeni_efor.save()
                if yeni_efor.danisman:
                    yeni_ticket.danisman.add(yeni_efor.danisman)

            return redirect('ticket_listesi')
    else:
        form = TicketForm(initial={'faturadurum': 'Bekliyor'}, user=request.user, is_creation=True)
        aktivite_form = TicketIciAktiviteForm()
        efor_form = TicketIciEforForm()
    
    return render(request, 'ticket_ekle.html', {
        'form': form,
        'aktivite_form': aktivite_form,
        'efor_form': efor_form
    })

# 4. DÜZENLEME (Aktivite + Efor sekmeli destek ile)
def ticket_duzenle(request, pk):
    """Mevcut bir ticket kaydını günceller. Aktivite ve Efor ekleme/listeleme desteği içerir."""
    kayit = get_object_or_404(ticket, pk=pk)

    # YETKİ KONTROLÜ: Firma başka firmanın ticket'ına URL'den erişmeye çalışıyorsa engelle
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            if kayit.unvan not in profile.muhatap_firmalar.all():
                return render(request, '403.html', status=403)
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            if not profile.danisman_profiller.filter(pk__in=kayit.danisman.all()).exists():
                return render(request, '403.html', status=403)
    aktiviteler = aktivite.objects.filter(ticketno=kayit).select_related("danisman", "modul").order_by('-date')
    toplam_efor = sum(a.time or 0 for a in aktiviteler)

    # Ticket'a ait eforlar (atamalar)
    eforlar = atama.objects.filter(ticketno=kayit).select_related("danisman", "modul").order_by('-pk')
    toplam_atama_efor = sum(e.efor or 0 for e in eforlar)
    yazismalar = TicketYazisma.objects.filter(ticketno=kayit).select_related("kullanici")

    if request.method == "POST":
        if 'aktivite_ekle' in request.POST:
            # Aktivite ekleme işlemi
            aktivite_form = TicketIciAktiviteForm(request.POST)
            if aktivite_form.is_valid():
                yeni = aktivite_form.save(commit=False)
                yeni.ticketno = kayit
                yeni.save()
                if yeni.danisman:
                    kayit.danisman.add(yeni.danisman)
                return redirect('ticket_duzenle', pk=pk)
            # Aktivite form hatalıysa ticket formunu boş oluştur
            form = TicketForm(instance=kayit, user=request.user)
            efor_form = TicketIciEforForm()
            yazisma_form = TicketYazismaForm()
        elif 'efor_ekle' in request.POST:
            # Efor ekleme işlemi
            efor_form = TicketIciEforForm(request.POST)
            if efor_form.is_valid():
                yeni_efor = efor_form.save(commit=False)
                yeni_efor.ticketno = kayit
                yeni_efor.save()
                if yeni_efor.danisman:
                    kayit.danisman.add(yeni_efor.danisman)
                return redirect('ticket_duzenle', pk=pk)
            form = TicketForm(instance=kayit, user=request.user)
            aktivite_form = TicketIciAktiviteForm()
            yazisma_form = TicketYazismaForm()
        elif 'yazisma_ekle' in request.POST:
            yazisma_form = TicketYazismaForm(request.POST, request.FILES)
            if yazisma_form.is_valid():
                yeni_yazisma = yazisma_form.save(commit=False)
                yeni_yazisma.ticketno = kayit
                if request.user.is_authenticated:
                    yeni_yazisma.kullanici = request.user
                yeni_yazisma.save()
                return redirect('ticket_duzenle', pk=pk)
            form = TicketForm(instance=kayit, user=request.user)
            aktivite_form = TicketIciAktiviteForm()
            efor_form = TicketIciEforForm()
        else:
            # Ticket güncelleme işlemi
            form = TicketForm(request.POST, instance=kayit, user=request.user)
            if form.is_valid():
                form.save()
                return redirect('ticket_listesi')
            aktivite_form = TicketIciAktiviteForm()
            efor_form = TicketIciEforForm()
            yazisma_form = TicketYazismaForm()
    else:
        form = TicketForm(instance=kayit, user=request.user)
        aktivite_form = TicketIciAktiviteForm()
        efor_form = TicketIciEforForm()
        yazisma_form = TicketYazismaForm()

    return render(request, 'ticket_duzenle.html', {
        'form': form,
        'kayit': kayit,
        'aktiviteler': aktiviteler,
        'aktivite_form': aktivite_form,
        'toplam_efor': toplam_efor,
        'eforlar': eforlar,
        'efor_form': efor_form,
        'toplam_atama_efor': toplam_atama_efor,
        'yazismalar': yazismalar,
        'yazisma_form': yazisma_form,
    })

# 5. SİLME
def ticket_sil(request, pk):
    """Bir ticket kaydını kalıcı olarak siler."""
    kayit = get_object_or_404(ticket, pk=pk)
    
    # YETKİ KONTROLÜ: Firma başka firmanın ticket'ını URL'den silmeye çalışıyorsa engelle
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            if kayit.unvan not in profile.muhatap_firmalar.all():
                return render(request, '403.html', status=403)
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            if not profile.danisman_profiller.filter(pk__in=kayit.danisman.all()).exists():
                return render(request, '403.html', status=403)
    kayit.delete()
    return _ticket_listesi_redirect(request)

# 5.5 TICKET TAMAMLA
def ticket_tamamla(request, pk):
    """Bir ticket kaydının durumunu Tamamlandı olarak günceller."""
    if request.method == "POST":
        kayit = get_object_or_404(ticket, pk=pk)
        
        # YETKİ KONTROLÜ
        if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
            profile = request.user.userprofile
            if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
                if kayit.unvan not in profile.muhatap_firmalar.all():
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': 'Yetkisiz erişim'}, status=403)
                    return render(request, '403.html', status=403)
            elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
                if not profile.danisman_profiller.filter(pk__in=kayit.danisman.all()).exists():
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': 'Yetkisiz erişim'}, status=403)
                    return render(request, '403.html', status=403)
                    
        from .models import statu
        tamamlandi_statu = statu.objects.filter(durumtanim="Tamamlandı").first()
        if tamamlandi_statu:
            kayit.durumtanim = tamamlandi_statu
            kayit.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': '"Tamamlandı" durumu sistemde tanımlı değil'}, status=400)
    return _ticket_listesi_redirect(request)


def ticket_faturalama_tamamla(request, pk):
    """Bir ticket kaydının faturalama durumunu 'Faturalandı' olarak günceller."""
    if request.method == "POST":
        kayit = get_object_or_404(ticket, pk=pk)
        
        # YETKİ KONTROLÜ
        if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
            profile = request.user.userprofile
            if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
                if kayit.unvan not in profile.muhatap_firmalar.all():
                    return render(request, '403.html', status=403)
            elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
                if not profile.danisman_profiller.filter(pk__in=kayit.danisman.all()).exists():
                    return render(request, '403.html', status=403)
                    
        from .models import faturalama
        fatura_statu = faturalama.objects.filter(faturadurum="Faturalandı").first()
        if fatura_statu:
            kayit.faturadurum = fatura_statu
            kayit.save()
    return _ticket_listesi_redirect(request)


# 6. TICKET İÇİNDEN AKTİVİTE SİLME
def ticket_aktivite_sil(request, ticket_pk, aktivite_pk):
    """Ticket düzenleme sayfasından bir aktiviteyi siler."""
    kayit = get_object_or_404(aktivite, pk=aktivite_pk, ticketno_id=ticket_pk)
    
    # YETKİ KONTROLÜ
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            if kayit.ticketno and kayit.ticketno.unvan not in profile.muhatap_firmalar.all():
                return render(request, '403.html', status=403)
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            if kayit.danisman not in profile.danisman_profiller.all():
                return render(request, '403.html', status=403)
                
    kayit.delete()
    return redirect('ticket_duzenle', pk=ticket_pk)


# 7. TICKET İÇİNDEN EFOR SİLME
def ticket_efor_sil(request, ticket_pk, efor_pk):
    """Ticket düzenleme sayfasından bir efor kaydını siler."""
    kayit = get_object_or_404(atama, pk=efor_pk, ticketno_id=ticket_pk)
    
    # YETKİ KONTROLÜ
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            if kayit.ticketno and kayit.ticketno.unvan not in profile.muhatap_firmalar.all():
                return render(request, '403.html', status=403)
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            if kayit.danisman not in profile.danisman_profiller.all():
                return render(request, '403.html', status=403)
                
    kayit.delete()
    return redirect('ticket_duzenle', pk=ticket_pk)


def yazisma_sil(request, yazisma_pk):
    from .models import TicketYazisma
    yazisma = get_object_or_404(TicketYazisma, pk=yazisma_pk)
    ticket_id = yazisma.ticketno.pk
    
    # Sadece kendi yazdığı mesajı veya superuser silebilir
    if request.user.is_superuser or yazisma.kullanici == request.user:
        yazisma.delete()
    else:
        return render(request, '403.html', status=403)
        
    return redirect('ticket_duzenle', pk=ticket_id)



# ═══════════════════════════════════════════════════════
#               AKTİVİTE MODÜLÜ (Bağımsız Sayfalar)
# ═══════════════════════════════════════════════════════

def aktivite_listesi(request):
    aktiviteler = aktivite.objects.select_related("ticketno", "ticketno__unvan", "danisman", "modul").all().order_by("-number")
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            aktiviteler = aktiviteler.filter(ticketno__unvan__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            aktiviteler = aktiviteler.filter(danisman__in=profile.danisman_profiller.all())

    aktivite_no = request.GET.get("aktivite_no", "").strip()
    muhatap = request.GET.get("muhatap", "").strip()
    ticket_secimi = request.GET.get("ticket", "").strip()
    danisman = request.GET.get("danisman", "").strip()
    modul = request.GET.get("modul", "").strip()
    baslangic_tarihi = request.GET.get("baslangic_tarihi", "").strip()
    bitis_tarihi = request.GET.get("bitis_tarihi", "").strip()

    if aktivite_no:
        aktiviteler = aktiviteler.filter(number=aktivite_no)
    if muhatap:
        aktiviteler = aktiviteler.filter(ticketno__unvan__pk=muhatap)
    if ticket_secimi:
        aktiviteler = aktiviteler.filter(ticketno_id=ticket_secimi)
    if danisman:
        aktiviteler = aktiviteler.filter(danisman__username=danisman)
    if modul:
        aktiviteler = aktiviteler.filter(modul_id=modul)
    if baslangic_tarihi:
        aktiviteler = aktiviteler.filter(date__date__gte=baslangic_tarihi)
    if bitis_tarihi:
        aktiviteler = aktiviteler.filter(date__date__lte=bitis_tarihi)

    a_qs = aktivite.objects.select_related("ticketno", "ticketno__unvan").order_by("number")
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            a_qs = a_qs.filter(ticketno__unvan__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            a_qs = a_qs.filter(danisman__in=profile.danisman_profiller.all())
            
    context = {
        "aktiviteler": aktiviteler,
        "aktivite_nolari": a_qs.values_list("number", flat=True),
        "filtre_ticketlari": ticket.objects.filter(aktivite__in=a_qs).distinct().order_by("-ticketno"),
        "filtre_muhataplari": ticket._meta.get_field("unvan").remote_field.model.objects.filter(ticket__aktivite__in=a_qs).distinct().order_by("unvan"),
        "secili_aktivite_no": aktivite_no,
        "secili_muhatap": muhatap,
        "secili_ticket": ticket_secimi,
        "secili_danisman": danisman,
        "secili_modul": modul,
        "secili_baslangic_tarihi": baslangic_tarihi,
        "secili_bitis_tarihi": bitis_tarihi,
        "form": AktiviteForm(user=request.user),
    }
    return render(request, "aktivite_listesi.html", context)


def aktivite_ekle(request):
    if request.method == "POST":
        form = AktiviteForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("aktivite_listesi")
    else:
        form = AktiviteForm(user=request.user)

    return render(request, "aktivite_ekle.html", {"form": form})


def aktivite_duzenle(request, pk):
    kayit = get_object_or_404(aktivite, pk=pk)
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            if kayit.ticketno and kayit.ticketno.unvan not in profile.muhatap_firmalar.all():
                return render(request, '403.html', status=403)
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            if kayit.danisman not in profile.danisman_profiller.all():
                return render(request, '403.html', status=403)

    if request.method == "POST":
        form = AktiviteForm(request.POST, instance=kayit, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("aktivite_listesi")
    else:
        form = AktiviteForm(instance=kayit, user=request.user)

    return render(request, "aktivite_duzenle.html", {"form": form, "kayit": kayit})


def aktivite_sil(request, pk):
    kayit = get_object_or_404(aktivite, pk=pk)
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            if kayit.ticketno and kayit.ticketno.unvan not in profile.muhatap_firmalar.all():
                return render(request, '403.html', status=403)
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            if kayit.danisman not in profile.danisman_profiller.all():
                return render(request, '403.html', status=403)
                
    kayit.delete()
    return redirect("aktivite_listesi")


# ═══════════════════════════════════════════════════════
#               EFOR (ATAMA) MODÜLÜ (Bağımsız Sayfalar)
# ═══════════════════════════════════════════════════════

def efor_listesi(request):
    """Tüm efor/atama kayıtlarını listeler."""
    atamalar = atama.objects.select_related(
        "danisman", "ticketno", "ticketno__unvan", "ticketno__durumtanim", "modul"
    ).all().order_by("-pk")

    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            atamalar = atamalar.filter(ticketno__unvan__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            atamalar = atamalar.filter(danisman__in=profile.danisman_profiller.all())

    arama = request.GET.get("arama", "").strip()
    danisman_filtre = request.GET.get("danisman", "").strip()
    ticket_secimi = request.GET.get("ticket", "").strip()
    modul = request.GET.get("modul", "").strip()
    onay = request.GET.get("onay", "").strip()
    secili_unvan = request.GET.get("unvan", "").strip()
    secili_durum = request.GET.get("durum", "").strip()
    secili_fatura_durumu = request.GET.get("fatura_durumu", "").strip()

    if arama:
        atamalar = atamalar.filter(
            Q(danisman__isim__icontains=arama)
            | Q(danisman__username__icontains=arama)
            | Q(ticketno__ticketno__icontains=arama)
            | Q(ticketno__konu__icontains=arama)
        )
    if danisman_filtre:
        atamalar = atamalar.filter(danisman__username=danisman_filtre)
    if ticket_secimi:
        atamalar = atamalar.filter(ticketno_id=ticket_secimi)
    if modul:
        atamalar = atamalar.filter(modul_id=modul)
    if onay == "1":
        atamalar = atamalar.filter(onay=True)
    elif onay == "0":
        atamalar = atamalar.filter(onay=False)
    if secili_unvan:
        atamalar = atamalar.filter(ticketno__unvan__pk=secili_unvan)
    if secili_durum:
        atamalar = atamalar.filter(ticketno__durumtanim__pk=secili_durum)
    if secili_fatura_durumu:
        atamalar = atamalar.filter(ticketno__faturadurum__pk=secili_fatura_durumu)

    a_qs = atama.objects.all()
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            a_qs = a_qs.filter(ticketno__unvan__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            a_qs = a_qs.filter(danisman__in=profile.danisman_profiller.all())

    # Filtrelerde gösterilecek listeler
    from muhatap.models import muhatap as Muhatap
    from ticket.models import statu, faturalama
    filtre_unvanlar = Muhatap.objects.filter(
        ticket__atama__isnull=False
    ).distinct().order_by("unvan")
    durumlar = statu.objects.order_by("durumtanim")
    fatura_durumlari = faturalama.objects.order_by("faturadurum")

    context = {
        "atamalar": atamalar,
        "filtre_ticketlari": ticket.objects.filter(atama__in=a_qs).distinct().order_by("-ticketno"),
        "filtre_unvanlar": filtre_unvanlar,
        "durumlar": durumlar,
        "fatura_durumlari": fatura_durumlari,
        "arama": arama,
        "secili_danisman": danisman_filtre,
        "secili_ticket": ticket_secimi,
        "secili_modul": modul,
        "secili_onay": onay,
        "secili_unvan": secili_unvan,
        "secili_durum": secili_durum,
        "secili_fatura_durumu": secili_fatura_durumu,
        "form": AtamaForm(user=request.user),
    }
    return render(request, "atama_listesi.html", context)


def efor_ekle(request):
    """Yeni efor/atama kaydı oluşturur."""
    if request.method == "POST":
        form = AtamaForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("efor_listesi")
    else:
        form = AtamaForm(user=request.user)
    return render(request, "atama_ekle.html", {"form": form})


def efor_duzenle(request, pk):
    """Mevcut bir efor/atama kaydını günceller."""
    kayit = get_object_or_404(atama, pk=pk)
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            if kayit.ticketno and kayit.ticketno.unvan not in profile.muhatap_firmalar.all():
                return render(request, '403.html', status=403)
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            if kayit.danisman not in profile.danisman_profiller.all():
                return render(request, '403.html', status=403)

    if request.method == "POST":
        form = AtamaForm(request.POST, instance=kayit, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("efor_listesi")
    else:
        form = AtamaForm(instance=kayit, user=request.user)
    return render(request, "atama_duzenle.html", {"form": form, "kayit": kayit})


def efor_sil(request, pk):
    """Bir efor/atama kaydını siler."""
    kayit = get_object_or_404(atama, pk=pk)
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            if kayit.ticketno and kayit.ticketno.unvan not in profile.muhatap_firmalar.all():
                return render(request, '403.html', status=403)
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            if kayit.danisman not in profile.danisman_profiller.all():
                return render(request, '403.html', status=403)
                
    kayit.delete()
    return redirect("efor_listesi")

def efor_onayla(request, pk):
    """Bir efor/atama kaydını onaylar."""
    kayit = get_object_or_404(atama, pk=pk)
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            if kayit.ticketno and kayit.ticketno.unvan not in profile.muhatap_firmalar.all():
                return render(request, '403.html', status=403)
        elif profile.role == 'Danisman':
            return render(request, '403.html', status=403)
                
    kayit.onay = True
    kayit.save()
    return redirect("efor_listesi")

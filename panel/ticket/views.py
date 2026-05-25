from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import aktivite, ticket, atama
from .forms import AktiviteForm, TicketForm, TicketIciAktiviteForm, AtamaForm, TicketIciEforForm

# 1. DASHBOARD (ANA SAYFA)
def ana_sayfa(request):
    """Sistem özetini ve istatistikleri gösteren ana ekran."""
    toplam = ticket.objects.count()
    acik = ticket.objects.exclude(durumtanim__durumtanim="Tamamlandı").count()
    tamamlanan = ticket.objects.filter(durumtanim__durumtanim="Tamamlandı").count()
    son_eklenenler = ticket.objects.all().order_by('-taleptarih')[:5]

    context = {
        'toplam_kayit': toplam,
        'acik_ticketlar': acik,
        'tamamlanan_count': tamamlanan,
        'son_ticketlar': son_eklenenler,
    }
    return render(request, 'index.html', context)

# 2. LİSTELEME
def ticket_listesi(request):
    """Tüm ticket kayıtlarını tablo halinde listeler."""
    tum_ticketlar = ticket.objects.select_related("unvan", "durumtanim").prefetch_related("danisman").all().order_by('-ticketno')
    arama = request.GET.get("arama", "").strip()
    durum = request.GET.get("durum", "").strip()
    danisman = request.GET.get("danisman", "").strip()
    tarih = request.GET.get("tarih", "").strip()

    if arama:
        tum_ticketlar = tum_ticketlar.filter(
            Q(ticketno__icontains=arama)
            | Q(konu__icontains=arama)
            | Q(musteri_ticket_no__icontains=arama)
            | Q(unvan__unvan__icontains=arama)
        )
    if durum:
        tum_ticketlar = tum_ticketlar.filter(durumtanim_id=durum)
    if danisman:
        tum_ticketlar = tum_ticketlar.filter(danisman__username=danisman)
    if tarih:
        tum_ticketlar = tum_ticketlar.filter(taleptarih__date=tarih)

    # Her ticket için danışman eforlarını hesapla
    tum_ticketlar_list = list(tum_ticketlar)
    for t in tum_ticketlar_list:
        danisman_eforlari = {}
        for a in t.atama_set.all():
            if a.danisman:
                isim = a.danisman.isim or a.danisman.username
                danisman_eforlari[isim] = danisman_eforlari.get(isim, 0) + (a.efor or 0)
        t.danisman_efor_list = [f"{isim} — {efor} Saat" for isim, efor in danisman_eforlari.items()]

    context = {
        'ticketlar': tum_ticketlar_list,
        'arama': arama,
        'secili_durum': durum,
        'secili_danisman': danisman,
        'tarih': tarih,
        'durumlar': ticket._meta.get_field("durumtanim").remote_field.model.objects.order_by("durumtanim"),
        'danismanlar': ticket._meta.get_field("danisman").related_model.objects.order_by("isim"),
    }
    return render(request, 'ticket_listesi.html', context)

# 3. YENİ EKLEME
def ticket_ekle(request):
    """Sıfırdan yeni bir ticket oluşturur. Aynı ekranda aktivite ve atama da eklenebilir."""
    if request.method == "POST":
        form = TicketForm(request.POST)
        aktivite_form = TicketIciAktiviteForm(request.POST)
        efor_form = TicketIciEforForm(request.POST)

        if form.is_valid():
            yeni_ticket = form.save()
            
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
        form = TicketForm(initial={'durumtanim': 'Efor Onayında', 'faturadurum': 'Bekliyor'})
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

    # Ticket'a ait aktiviteler
    aktiviteler = aktivite.objects.filter(ticketno=kayit).select_related("danisman", "modul").order_by('-date')
    toplam_efor = sum(a.time or 0 for a in aktiviteler)

    # Ticket'a ait eforlar (atamalar)
    eforlar = atama.objects.filter(ticketno=kayit).select_related("danisman", "modul").order_by('-pk')
    toplam_atama_efor = sum(e.efor or 0 for e in eforlar)

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
            form = TicketForm(instance=kayit)
            efor_form = TicketIciEforForm()
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
            form = TicketForm(instance=kayit)
            aktivite_form = TicketIciAktiviteForm()
        else:
            # Ticket güncelleme işlemi
            form = TicketForm(request.POST, instance=kayit)
            if form.is_valid():
                form.save()
                return redirect('ticket_listesi')
            aktivite_form = TicketIciAktiviteForm()
            efor_form = TicketIciEforForm()
    else:
        form = TicketForm(instance=kayit)
        aktivite_form = TicketIciAktiviteForm()
        efor_form = TicketIciEforForm()

    return render(request, 'ticket_duzenle.html', {
        'form': form,
        'kayit': kayit,
        'aktiviteler': aktiviteler,
        'aktivite_form': aktivite_form,
        'toplam_efor': toplam_efor,
        'eforlar': eforlar,
        'efor_form': efor_form,
        'toplam_atama_efor': toplam_atama_efor,
    })

# 5. SİLME
def ticket_sil(request, pk):
    """Bir ticket kaydını kalıcı olarak siler."""
    kayit = get_object_or_404(ticket, pk=pk)
    kayit.delete()
    return redirect('ticket_listesi')

# 5.5 TICKET TAMAMLA
def ticket_tamamla(request, pk):
    """Bir ticket kaydının durumunu Tamamlandı olarak günceller."""
    if request.method == "POST":
        kayit = get_object_or_404(ticket, pk=pk)
        from .models import statu
        tamamlandi_statu = statu.objects.filter(durumtanim="Tamamlandı").first()
        if tamamlandi_statu:
            kayit.durumtanim = tamamlandi_statu
            kayit.save()
    return redirect('ticket_listesi')


def ticket_faturalama_tamamla(request, pk):
    """Bir ticket kaydının faturalama durumunu 'Faturalandı' olarak günceller."""
    if request.method == "POST":
        kayit = get_object_or_404(ticket, pk=pk)
        from .models import faturalama
        fatura_statu = faturalama.objects.filter(faturadurum="Faturalandı").first()
        if fatura_statu:
            kayit.faturadurum = fatura_statu
            kayit.save()
    return redirect('ticket_listesi')


# 6. TICKET İÇİNDEN AKTİVİTE SİLME
def ticket_aktivite_sil(request, ticket_pk, aktivite_pk):
    """Ticket düzenleme sayfasından bir aktiviteyi siler."""
    kayit = get_object_or_404(aktivite, pk=aktivite_pk, ticketno_id=ticket_pk)
    kayit.delete()
    return redirect('ticket_duzenle', pk=ticket_pk)


# 7. TICKET İÇİNDEN EFOR SİLME
def ticket_efor_sil(request, ticket_pk, efor_pk):
    """Ticket düzenleme sayfasından bir efor kaydını siler."""
    kayit = get_object_or_404(atama, pk=efor_pk, ticketno_id=ticket_pk)
    kayit.delete()
    return redirect('ticket_duzenle', pk=ticket_pk)


# ═══════════════════════════════════════════════════════
#               AKTİVİTE MODÜLÜ (Bağımsız Sayfalar)
# ═══════════════════════════════════════════════════════

def aktivite_listesi(request):
    aktiviteler = aktivite.objects.select_related("ticketno", "danisman", "modul").all().order_by("-date")
    aktivite_no = request.GET.get("aktivite_no", "").strip()
    ticket_secimi = request.GET.get("ticket", "").strip()
    danisman = request.GET.get("danisman", "").strip()
    modul = request.GET.get("modul", "").strip()
    tarih = request.GET.get("tarih", "").strip()

    if aktivite_no:
        aktiviteler = aktiviteler.filter(number=aktivite_no)
    if ticket_secimi:
        aktiviteler = aktiviteler.filter(ticketno_id=ticket_secimi)
    if danisman:
        aktiviteler = aktiviteler.filter(danisman__username=danisman)
    if modul:
        aktiviteler = aktiviteler.filter(modul_id=modul)
    if tarih:
        aktiviteler = aktiviteler.filter(date__date=tarih)

    context = {
        "aktiviteler": aktiviteler,
        "aktivite_nolari": aktivite.objects.order_by("number").values_list("number", flat=True),
        "secili_aktivite_no": aktivite_no,
        "secili_ticket": ticket_secimi,
        "secili_danisman": danisman,
        "secili_modul": modul,
        "tarih": tarih,
        "form": AktiviteForm(),
    }
    return render(request, "aktivite_listesi.html", context)


def aktivite_ekle(request):
    if request.method == "POST":
        form = AktiviteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("aktivite_listesi")
    else:
        form = AktiviteForm()

    return render(request, "aktivite_ekle.html", {"form": form})


def aktivite_duzenle(request, pk):
    kayit = get_object_or_404(aktivite, pk=pk)
    if request.method == "POST":
        form = AktiviteForm(request.POST, instance=kayit)
        if form.is_valid():
            form.save()
            return redirect("aktivite_listesi")
    else:
        form = AktiviteForm(instance=kayit)

    return render(request, "aktivite_duzenle.html", {"form": form, "kayit": kayit})


def aktivite_sil(request, pk):
    kayit = get_object_or_404(aktivite, pk=pk)
    kayit.delete()
    return redirect("aktivite_listesi")


# ═══════════════════════════════════════════════════════
#               EFOR (ATAMA) MODÜLÜ (Bağımsız Sayfalar)
# ═══════════════════════════════════════════════════════

def efor_listesi(request):
    """Tüm efor/atama kayıtlarını listeler."""
    atamalar = atama.objects.select_related("danisman", "ticketno", "modul").all().order_by("-pk")
    arama = request.GET.get("arama", "").strip()
    danisman = request.GET.get("danisman", "").strip()
    ticket_secimi = request.GET.get("ticket", "").strip()
    modul = request.GET.get("modul", "").strip()
    onay = request.GET.get("onay", "").strip()

    if arama:
        atamalar = atamalar.filter(
            Q(danisman__isim__icontains=arama)
            | Q(danisman__username__icontains=arama)
            | Q(ticketno__ticketno__icontains=arama)
            | Q(ticketno__konu__icontains=arama)
        )
    if danisman:
        atamalar = atamalar.filter(danisman__username=danisman)
    if ticket_secimi:
        atamalar = atamalar.filter(ticketno_id=ticket_secimi)
    if modul:
        atamalar = atamalar.filter(modul_id=modul)
    if onay == "1":
        atamalar = atamalar.filter(onay=True)
    elif onay == "0":
        atamalar = atamalar.filter(onay=False)

    context = {
        "atamalar": atamalar,
        "arama": arama,
        "secili_danisman": danisman,
        "secili_ticket": ticket_secimi,
        "secili_modul": modul,
        "secili_onay": onay,
        "form": AtamaForm(),
    }
    return render(request, "atama_listesi.html", context)


def efor_ekle(request):
    """Yeni efor/atama kaydı oluşturur."""
    if request.method == "POST":
        form = AtamaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("efor_listesi")
    else:
        form = AtamaForm()
    return render(request, "atama_ekle.html", {"form": form})


def efor_duzenle(request, pk):
    """Mevcut bir efor/atama kaydını günceller."""
    kayit = get_object_or_404(atama, pk=pk)
    if request.method == "POST":
        form = AtamaForm(request.POST, instance=kayit)
        if form.is_valid():
            form.save()
            return redirect("efor_listesi")
    else:
        form = AtamaForm(instance=kayit)
    return render(request, "atama_duzenle.html", {"form": form, "kayit": kayit})


def efor_sil(request, pk):
    """Bir efor/atama kaydını siler."""
    kayit = get_object_or_404(atama, pk=pk)
    kayit.delete()
    return redirect("efor_listesi")

def efor_onayla(request, pk):
    """Bir efor/atama kaydını onaylar."""
    kayit = get_object_or_404(atama, pk=pk)
    kayit.onay = True
    kayit.save()
    return redirect("efor_listesi")

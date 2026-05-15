from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import aktivite, ticket
from .forms import AktiviteForm, TicketForm

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
    tum_ticketlar = ticket.objects.select_related("unvan", "danisman", "durumtanim").all().order_by('-ticketno')
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
        tum_ticketlar = tum_ticketlar.filter(danisman_id=danisman)
    if tarih:
        tum_ticketlar = tum_ticketlar.filter(taleptarih__date=tarih)

    context = {
        'ticketlar': tum_ticketlar,
        'arama': arama,
        'secili_durum': durum,
        'secili_danisman': danisman,
        'tarih': tarih,
        'durumlar': ticket._meta.get_field("durumtanim").remote_field.model.objects.order_by("durumtanim"),
        'danismanlar': ticket._meta.get_field("danisman").remote_field.model.objects.order_by("isim"),
    }
    return render(request, 'ticket_listesi.html', context)

# 3. YENİ EKLEME
def ticket_ekle(request):
    """Sıfırdan yeni bir ticket oluşturur."""
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ticket_listesi')
    else:
        form = TicketForm()
    return render(request, 'ticket_ekle.html', {'form': form})

# 4. DÜZENLEME
def ticket_duzenle(request, pk):
    """Mevcut bir ticket kaydını günceller."""
    kayit = get_object_or_404(ticket, pk=pk)
    if request.method == "POST":
        form = TicketForm(request.POST, instance=kayit)
        if form.is_valid():
            form.save()
            return redirect('ticket_listesi')
    else:
        form = TicketForm(instance=kayit)
    return render(request, 'ticket_duzenle.html', {'form': form, 'kayit': kayit})

# 5. SİLME
def ticket_sil(request, pk):
    """Bir ticket kaydını kalıcı olarak siler."""
    kayit = get_object_or_404(ticket, pk=pk)
    kayit.delete()
    return redirect('ticket_listesi')


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
        aktiviteler = aktiviteler.filter(danisman_id=danisman)
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

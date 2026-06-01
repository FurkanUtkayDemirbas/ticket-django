import openpyxl
import textwrap
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from xhtml2pdf import pisa
from django.template.loader import render_to_string

from ticket.models import aktivite, atama, ticket
from proje.models import projeler


def raporlar_merkezi(request):
    t_qs = ticket.objects.all()
    a_qs = aktivite.objects.all()
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firma:
            t_qs = t_qs.filter(unvan=profile.muhatap_firma)
            a_qs = a_qs.filter(ticketno__unvan=profile.muhatap_firma)
        elif profile.role == 'Danisman' and profile.danisman_profil:
            t_qs = t_qs.filter(danisman=profile.danisman_profil)
            a_qs = a_qs.filter(danisman=profile.danisman_profil)

    context = {
        "toplam_ticket": t_qs.count(),
        "atanmamis_ticket": t_qs.filter(danisman=None).count(),
        "onay_bekleyen": t_qs.filter(onay=False).count(),
        "toplam_aktivite_sure": a_qs.aggregate(toplam=Sum("time"))["toplam"] or 0,
    }
    return render(request, "raporlar_merkezi.html", context)


def _filter_context(request):
    t_qs = ticket.objects.order_by("-ticketno")
    m_qs = ticket._meta.get_field("unvan").remote_field.model.objects.order_by("unvan")
    p_qs = projeler.objects.order_by("projeno")
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firma:
            t_qs = t_qs.filter(unvan=profile.muhatap_firma)
            m_qs = m_qs.filter(unvan=profile.muhatap_firma.unvan)
            p_qs = p_qs.filter(sozlesme_baglantisi__muhatap=profile.muhatap_firma)
        elif profile.role == 'Danisman' and profile.danisman_profil:
            t_qs = t_qs.filter(danisman=profile.danisman_profil)
            m_qs = m_qs.filter(ticket__danisman=profile.danisman_profil).distinct()
            p_qs = p_qs.filter(sozlesme_baglantisi__ticket__danisman=profile.danisman_profil).distinct()

    return {
        "arama": request.GET.get("arama", "").strip(),
        "ticket_secimi": request.GET.get("ticket", "").strip(),
        "secili_durum": request.GET.get("durum", "").strip(),
        "secili_danisman": request.GET.get("danisman", "").strip(),
        "secili_modul": request.GET.get("modul", "").strip(),
        "secili_muhatap": request.GET.get("muhatap", "").strip(),
        "secili_proje": request.GET.get("proje", "").strip(),
        "baslangic": request.GET.get("baslangic", "").strip(),
        "bitis": request.GET.get("bitis", "").strip(),
        "durumlar": ticket._meta.get_field("durumtanim").remote_field.model.objects.order_by("durumtanim"),
        "danismanlar": ticket._meta.get_field("danisman").related_model.objects.order_by("isim"),
        "moduller": aktivite._meta.get_field("modul").remote_field.model.objects.order_by("program", "isim"),
        "ticketlar": t_qs,
        "muhataplar": m_qs,
        "projeler": p_qs,
    }


def _ticket_queryset(request, base_queryset=None):
    queryset = base_queryset if base_queryset is not None else ticket.objects.all()
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firma:
            queryset = queryset.filter(unvan=profile.muhatap_firma)
        elif profile.role == 'Danisman' and profile.danisman_profil:
            queryset = queryset.filter(danisman=profile.danisman_profil)

    queryset = queryset.select_related(
        "unvan", "sozlesmeno", "bolumkod", "destekturu", "oncelikkod",
        "durumtanim", "faturadurum",
    ).prefetch_related("danisman").order_by("-ticketno")

    arama = request.GET.get("arama", "").strip()
    durum = request.GET.get("durum", "").strip()
    danisman = request.GET.get("danisman", "").strip()
    baslangic = request.GET.get("baslangic", "").strip()
    bitis = request.GET.get("bitis", "").strip()

    if arama:
        queryset = queryset.filter(
            Q(ticketno__icontains=arama)
            | Q(konu__icontains=arama)
            | Q(musteri_ticket_no__icontains=arama)
            | Q(unvan__unvan__icontains=arama)
        )
    if durum:
        queryset = queryset.filter(durumtanim_id=durum)
    if danisman:
        queryset = queryset.filter(danisman__username=danisman)
    if baslangic:
        queryset = queryset.filter(taleptarih__date__gte=baslangic)
    if bitis:
        queryset = queryset.filter(taleptarih__date__lte=bitis)

    ticketlar = list(queryset)
    for t in ticketlar:
        danisman_eforlari = {}
        for a in t.atama_set.all():
            if a.danisman:
                danisman_eforlari[a.danisman] = danisman_eforlari.get(a.danisman, 0) + (a.efor or 0)
        
        t.danisman_efor_detay = []
        for d, efor in danisman_eforlari.items():
            t.danisman_efor_detay.append({"danisman": d, "efor": efor})

    return ticketlar


def _ticket_detay_base_queryset(request):
    queryset = ticket.objects.select_related(
        "unvan", "durumtanim", "faturadurum"
    ).order_by("-ticketno")

    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firma:
            queryset = queryset.filter(unvan=profile.muhatap_firma)
        elif profile.role == 'Danisman' and profile.danisman_profil:
            queryset = queryset.filter(danisman=profile.danisman_profil)

    return queryset


def _ticket_detay_rows(request):
    ticket_no = request.GET.get("ticket", "").strip()
    if not ticket_no:
        return []

    ticketlar = _ticket_detay_base_queryset(request).filter(ticketno=ticket_no)
    rows = []
    for t in ticketlar:
        eforlar = atama.objects.filter(ticketno=t).select_related("modul")
        aktiviteler = aktivite.objects.filter(ticketno=t).select_related("modul")

        yazilim_eforu = sum((e.efor or 0) for e in eforlar if e.modul and e.modul.yazilim_eforuna_dahil)
        modul_eforu = sum((e.efor or 0) for e in eforlar if not (e.modul and e.modul.yazilim_eforuna_dahil))
        yazilim_aktivite = sum((a.time or 0) for a in aktiviteler if a.modul and a.modul.yazilim_eforuna_dahil)
        modul_aktivite = sum((a.time or 0) for a in aktiviteler if not (a.modul and a.modul.yazilim_eforuna_dahil))

        rows.append({
            "ticket_no": t.ticketno,
            "ticket_tanimi": t.konu,
            "musteri_adi": t.unvan.unvan if t.unvan else "-",
            "termin_tarihi": t.termintarih,
            "ticket_durumu": t.durumtanim.durumtanim if t.durumtanim else "-",
            "faturalama_durumu": t.faturadurum.faturadurum if t.faturadurum else "-",
            "yazilim_eforu": yazilim_eforu,
            "modul_eforu": modul_eforu,
            "yazilim_aktivite_toplami": yazilim_aktivite,
            "modul_aktivite_toplami": modul_aktivite,
        })
    return rows


def _aktivite_queryset(request):
    queryset = aktivite.objects.all()
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firma:
            queryset = queryset.filter(ticketno__unvan=profile.muhatap_firma)
        elif profile.role == 'Danisman' and profile.danisman_profil:
            queryset = queryset.filter(danisman=profile.danisman_profil)

    queryset = queryset.select_related("ticketno", "danisman", "modul").order_by("-date")

    ticket_no = request.GET.get("ticket", "").strip()
    danisman = request.GET.get("danisman", "").strip()
    modul = request.GET.get("modul", "").strip()
    muhatap = request.GET.get("muhatap", "").strip()
    proje = request.GET.get("proje", "").strip()
    baslangic = request.GET.get("baslangic", "").strip()
    bitis = request.GET.get("bitis", "").strip()

    if ticket_no:
        queryset = queryset.filter(ticketno_id=ticket_no)
    if danisman:
        queryset = queryset.filter(danisman_id=danisman)
    if modul:
        queryset = queryset.filter(modul_id=modul)
    if muhatap:
        queryset = queryset.filter(ticketno__unvan__unvan=muhatap)
    if proje:
        queryset = queryset.filter(ticketno__sozlesmeno__projeler__projeno=proje)
    if baslangic:
        queryset = queryset.filter(date__date__gte=baslangic)
    if bitis:
        queryset = queryset.filter(date__date__lte=bitis)

    return queryset


def ticket_rapor_detay(request):
    ticketlar = _ticket_queryset(request)
    context = _filter_context(request)
    context.update({
        "ticketlar": ticketlar,
        "rapor_baslik": "Genel Ticket Raporu",
        "rapor_aciklama": "Destek talepleri için durum, müşteri, danışman ve tarih bazlı rapor.",
        "show_excel": True,
        "export_excel_url": reverse("rapor_indir_excel"),
        "export_pdf_url": reverse("ticket_rapor_pdf"),
    })
    return render(request, "ticket_rapor_detay.html", context)


def rapor_indir_excel(request):
    ticketlar = _ticket_queryset(request)
    rows = _ticket_rows(ticketlar)
    return _excel_response("Ticket Raporu", _ticket_headers(), rows, "ticket_raporu.xlsx")


def ticket_rapor_pdf(request):
    ticketlar = _ticket_queryset(request)
    return _pdf_response(request, "TICKET RAPORU", _ticket_headers(), _ticket_rows(ticketlar), "ticket_raporu.pdf", "Destek talepleri icin genel kayit listesi.")


def ticket_detay_raporu(request):
    context = {
        "ticketlar": _ticket_detay_base_queryset(request),
        "ticket_secimi": request.GET.get("ticket", "").strip(),
        "rows": _ticket_detay_rows(request),
        "rapor_baslik": "Ticket Özet Raporu",
        "rapor_aciklama": "Seçilen ticket için durum, fatura, yazılım ve modül efor özetleri.",
        "export_excel_url": reverse("ticket_ozet_raporu_excel"),
        "export_pdf_url": reverse("ticket_ozet_raporu_pdf"),
    }
    return render(request, "ticket_detay_raporu.html", context)


def ticket_detay_raporu_excel(request):
    rows = _ticket_detay_export_rows(_ticket_detay_rows(request))
    return _excel_response("Ticket Özet Raporu", _ticket_detay_headers(), rows, "ticket_ozet_raporu.xlsx")


def ticket_detay_raporu_pdf(request):
    rows = _ticket_detay_export_rows(_ticket_detay_rows(request))
    return _pdf_response(request, "TICKET OZET RAPORU", _ticket_detay_headers(), rows, "ticket_ozet_raporu.pdf", "Secilen ticket icin efor ve aktivite ozetleri.")


def aktivite_rapor_detay(request):
    aktiviteler = _aktivite_queryset(request)
    context = _filter_context(request)
    
    a_qs = aktivite.objects.all()
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firma:
            a_qs = a_qs.filter(ticketno__unvan=profile.muhatap_firma)
        elif profile.role == 'Danisman' and profile.danisman_profil:
            a_qs = a_qs.filter(danisman=profile.danisman_profil)
            
    context.update({
        "aktiviteler": aktiviteler,
        "ticketlar": ticket.objects.filter(aktivite__in=a_qs).distinct().order_by("-ticketno"),
        "toplam_sure": aktiviteler.aggregate(toplam=Sum("time"))["toplam"] or 0,
        "rapor_baslik": "Genel Aktivite Raporu",
        "rapor_aciklama": "Danışman, modül, ticket ve tarih aralığına göre aktivite ve efor raporu.",
        "export_excel_url": reverse("aktivite_rapor_indir_excel"),
        "export_pdf_url": reverse("aktivite_rapor_pdf"),
    })
    return render(request, "aktivite_rapor_detay.html", context)


def aktivite_rapor_indir_excel(request):
    aktiviteler = _aktivite_queryset(request)
    rows = _aktivite_rows(aktiviteler)
    rows.append(["", "", "", "", "Toplam Süre", aktiviteler.aggregate(toplam=Sum("time"))["toplam"] or 0, "", ""])
    return _excel_response("Aktivite Raporu", _aktivite_headers(), rows, "aktivite_raporu.xlsx")


def aktivite_rapor_pdf(request):
    aktiviteler = _aktivite_queryset(request)
    rows = _aktivite_rows(aktiviteler)
    toplam_sure = aktiviteler.aggregate(toplam=Sum("time"))["toplam"] or 0
    return _pdf_response(request, "AKTIVITE RAPORU", _aktivite_headers(), rows, "aktivite_raporu.pdf", "Tum danisman ve efor sureleri", "Toplam Kayitli Sure", f"{toplam_sure} Saat")


def atanmamis_ticket_raporu(request):
    ticketlar = _ticket_queryset(request, ticket.objects.filter(atama__isnull=True))
    context = _filter_context(request)
    context.update({
        "ticketlar": ticketlar,
        "rapor_baslik": "Atanmamış Ticketlar",
        "rapor_aciklama": "Henüz danışman ataması yapılmamış destek talepleri.",
        "show_excel": False,
        "export_excel_url": reverse("atanmamis_ticket_excel"),
        "export_pdf_url": reverse("atanmamis_ticket_pdf"),
    })
    return render(request, "ticket_rapor_detay.html", context)


def atanmamis_ticket_excel(request):
    ticketlar = _ticket_queryset(request, ticket.objects.filter(atama__isnull=True))
    return _excel_response("Atanmamış Ticketlar", _ticket_headers(), _ticket_rows(ticketlar), "atanmamis_ticketlar.xlsx")


def atanmamis_ticket_pdf(request):
    ticketlar = _ticket_queryset(request, ticket.objects.filter(atama__isnull=True))
    return _pdf_response(request, "ATANMAMIS TICKETLAR RAPORU", _ticket_headers(), _ticket_rows(ticketlar), "atanmamis_ticketlar.pdf", "Henuz danisman atamasi yapilmamis talepler.")


def efor_onayi_bekleyen_raporu(request):
    ticketlar = _ticket_queryset(request, ticket.objects.filter(onay=False))
    context = _filter_context(request)
    context.update({
        "ticketlar": ticketlar,
        "rapor_baslik": "Efor Onayı Bekleyenler",
        "rapor_aciklama": "Onay bekleyen ticket ve efor kayıtları.",
        "show_excel": False,
        "export_excel_url": reverse("efor_onayi_bekleyen_excel"),
        "export_pdf_url": reverse("efor_onayi_bekleyen_pdf"),
    })
    return render(request, "ticket_rapor_detay.html", context)


def efor_onayi_bekleyen_excel(request):
    ticketlar = _ticket_queryset(request, ticket.objects.filter(onay=False))
    return _excel_response("Efor Onayı Bekleyenler", _ticket_headers(), _ticket_rows(ticketlar), "efor_onayi_bekleyenler.xlsx")


def efor_onayi_bekleyen_pdf(request):
    ticketlar = _ticket_queryset(request, ticket.objects.filter(onay=False))
    return _pdf_response(request, "EFOR ONAYI BEKLEYENLER", _ticket_headers(), _ticket_rows(ticketlar), "efor_onayi_bekleyenler.pdf", "Onay bekleyen ticket ve efor kayitlari.")


def danisman_efor_ozeti(request):
    aktiviteler = _aktivite_queryset(request)
    ozetler = aktiviteler.values(
        "danisman__pk", "danisman__isim"
    ).annotate(
        toplam_sure=Sum("time"),
        aktivite_sayisi=Count("number"),
        ticket_sayisi=Count("ticketno", distinct=True),
    ).order_by("danisman__isim")

    context = _filter_context(request)
    context.update({
        "ozetler": ozetler,
        "rapor_baslik": "Danışman Efor Özeti",
        "rapor_aciklama": "Danışman bazında toplam süre, aktivite ve ticket sayısı.",
        "grup_tipi": "danisman",
        "export_excel_url": reverse("danisman_efor_excel"),
        "export_pdf_url": reverse("danisman_efor_pdf"),
    })
    return render(request, "efor_ozet_raporu.html", context)


def danisman_efor_excel(request):
    ozetler = _danisman_ozet_rows(request)
    return _excel_response("Danışman Efor Özeti", _ozet_headers(), ozetler, "danisman_efor_ozeti.xlsx")


def danisman_efor_pdf(request):
    ozetler = _danisman_ozet_rows(request)
    return _pdf_response(request, "DANISMAN EFOR OZETI", _ozet_headers(), ozetler, "danisman_efor_ozeti.pdf", "Danisman bazinda toplam sure ve aktivite sayilari.")


def modul_efor_ozeti(request):
    aktiviteler = _aktivite_queryset(request)
    ozetler = aktiviteler.values(
        "modul__pk", "modul__program", "modul__isim"
    ).annotate(
        toplam_sure=Sum("time"),
        aktivite_sayisi=Count("number"),
        ticket_sayisi=Count("ticketno", distinct=True),
    ).order_by("modul__program", "modul__isim")

    context = _filter_context(request)
    context.update({
        "ozetler": ozetler,
        "rapor_baslik": "Modül Efor Özeti",
        "rapor_aciklama": "Modül bazında toplam süre, aktivite ve ticket sayısı.",
        "grup_tipi": "modul",
        "export_excel_url": reverse("modul_efor_excel"),
        "export_pdf_url": reverse("modul_efor_pdf"),
    })
    return render(request, "efor_ozet_raporu.html", context)


def modul_efor_excel(request):
    ozetler = _modul_ozet_rows(request)
    return _excel_response("Modül Efor Özeti", _ozet_headers(), ozetler, "modul_efor_ozeti.xlsx")


def modul_efor_pdf(request):
    ozetler = _modul_ozet_rows(request)
    return _pdf_response(request, "MODUL EFOR OZETI", _ozet_headers(), ozetler, "modul_efor_ozeti.pdf", "Modul bazinda toplam sure ve ticket sayilari.")


def _ticket_headers():
    return ["Ticket No", "Konu", "Müşteri", "Danışman", "Modül", "Tarih", "Efor", "Onay"]


def _ticket_detay_headers():
    return [
        "Ticket No",
        "Ticket Tanımı",
        "Müşteri Adı",
        "Termin Tarihi",
        "Ticket Durumu",
        "Faturalama Durumu",
        "Yazılım Eforu",
        "Modül Eforu",
        "Yazılım Aktivite Toplamı",
        "Modül Aktivite Toplamı",
    ]


def _ticket_detay_export_rows(rows):
    return [[
        row["ticket_no"],
        row["ticket_tanimi"],
        row["musteri_adi"],
        row["termin_tarihi"].strftime("%Y-%m-%d %H:%M") if row["termin_tarihi"] else "-",
        row["ticket_durumu"],
        row["faturalama_durumu"],
        row["yazilim_eforu"],
        row["modul_eforu"],
        row["yazilim_aktivite_toplami"],
        row["modul_aktivite_toplami"],
    ] for row in rows]


def _ticket_rows(ticketlar):
    return [[
        t.ticketno,
        t.konu,
        str(t.unvan) if t.unvan else "-",
        "\n".join([f"{d['danisman'].isim} ({d['efor']} sa)" for d in getattr(t, 'danisman_efor_detay', [])]) or "-",
        str(t.bolumkod) if t.bolumkod else "-",
        t.taleptarih.strftime("%Y-%m-%d") if t.taleptarih else "-",
        t.efor or 0,
        "Onaylı" if t.onay else "Bekliyor",
    ] for t in ticketlar]


def _aktivite_headers():
    return ["Muhatap Kodu", "Muhatap Adı", "Ticket No", "Ticket Adı", "Tarih", "Süre", "Danışman", "Modül"]


def _aktivite_rows(aktiviteler):
    return [[
        a.ticketno.unvan.vkn if a.ticketno and a.ticketno.unvan else "",
        a.ticketno.unvan.unvan if a.ticketno and a.ticketno.unvan else "",
        a.ticketno.ticketno if a.ticketno else "",
        a.ticketno.konu if a.ticketno else "",
        a.date.strftime("%Y-%m-%d %H:%M") if a.date else "",
        a.time or 0,
        str(a.danisman) if a.danisman else "",
        str(a.modul) if a.modul else "",
    ] for a in aktiviteler]


def _ozet_headers():
    return ["Grup", "Toplam Süre", "Aktivite Sayısı", "Ticket Sayısı"]


def _danisman_ozet_rows(request):
    return [[
        row["danisman__isim"] or "Atanmamış",
        row["toplam_sure"] or 0,
        row["aktivite_sayisi"],
        row["ticket_sayisi"],
    ] for row in _aktivite_queryset(request).values(
        "danisman_id", "danisman__isim"
    ).annotate(
        toplam_sure=Sum("time"),
        aktivite_sayisi=Count("number"),
        ticket_sayisi=Count("ticketno", distinct=True),
    ).order_by("danisman__isim")]


def _modul_ozet_rows(request):
    rows = _aktivite_queryset(request).values(
        "modul_id", "modul__program", "modul__isim"
    ).annotate(
        toplam_sure=Sum("time"),
        aktivite_sayisi=Count("number"),
        ticket_sayisi=Count("ticketno", distinct=True),
    ).order_by("modul__program", "modul__isim")
    return [[
        f"{row['modul__program'] or '-'} - {row['modul__isim'] or '-'}" if row["modul_id"] else "Atanmamış",
        row["toplam_sure"] or 0,
        row["aktivite_sayisi"],
        row["ticket_sayisi"],
    ] for row in rows]


def _excel_response(title, headers, rows, filename):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = title[:31]
    sheet.append(headers)

    for cell in sheet[1]:
        cell.font = openpyxl.styles.Font(bold=True)

    for row in rows:
        sheet.append(row)

    _fit_sheet_columns(sheet)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    workbook.save(response)
    return response



import os
from django.conf import settings

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources. Handles Windows path joining properly.
    """
    sUrl = settings.STATIC_URL
    sRoot = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else os.path.join(settings.BASE_DIR, 'static')
    mUrl = settings.MEDIA_URL
    mRoot = settings.MEDIA_ROOT

    # Normalize URLs to match uri formatting
    if not sUrl.startswith('/') and uri.startswith('/'):
        sUrl = '/' + sUrl
    if not mUrl.startswith('/') and uri.startswith('/'):
        mUrl = '/' + mUrl

    if uri.startswith(mUrl):
        relative_path = uri.replace(mUrl, "", 1).lstrip('/\\')
        path = os.path.join(mRoot, relative_path)
    elif uri.startswith(sUrl):
        relative_path = uri.replace(sUrl, "", 1).lstrip('/\\')
        path = os.path.join(sRoot, relative_path)
    else:
        raise Exception(f'URI DID NOT MATCH: uri="{uri}", sUrl="{sUrl}", mUrl="{mUrl}"')

    if not os.path.isfile(path):
        raise Exception('media URI must start with %s or %s (Path resolved to: %s)' % (sUrl, mUrl, path))
    
    return path

import tempfile

def _pdf_response(request, title, headers, rows, filename, description="", summary_title=None, summary_value=None):
    # Enforce strict column widths using xhtml2pdf native pdf:widths property
    if len(headers) == 8 and headers[0] == "Ticket No":
        widths = ["8%", "22%", "15%", "20%", "10%", "10%", "5%", "10%"]
    elif len(headers) == 10 and headers[0] == "Ticket No":
        widths = ["7%", "13%", "11%", "11%", "10%", "11%", "9%", "9%", "10%", "9%"]
    elif len(headers) == 7 and headers[0] == "Ticket No":
        widths = ["10%", "25%", "20%", "15%", "15%", "5%", "10%"]
    elif len(headers) == 7 and headers[0] == "Aktivite No":
        widths = ["10%", "12%", "20%", "15%", "8%", "20%", "15%"]
    elif len(headers) == 4 and headers[0] == "Grup":
        widths = ["40%", "20%", "20%", "20%"]
    else:
        widths = [f"{100.0/len(headers)}%"] * len(headers)
        
    pdf_widths_str = ", ".join(widths)

    context = {
        "rapor_baslik": title,
        "rapor_aciklama": description,
        "headers": zip(headers, widths),
        "pdf_widths": pdf_widths_str,
        "rows": rows,
        "summary_title": summary_title,
        "summary_value": summary_value,
        "request": request,
    }
    html = render_to_string("pdf_rapor_sablonu.html", context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    
    # Monkeypatch NamedTemporaryFile for Windows to prevent TTFError (file lock)
    _orig_NamedTemporaryFile = tempfile.NamedTemporaryFile
    def _patched_NamedTemporaryFile(*args, **kwargs):
        kwargs['delete'] = False
        return _orig_NamedTemporaryFile(*args, **kwargs)
    
    import hashlib
    _orig_md5 = hashlib.md5
    def _patched_md5(*args, **kwargs):
        kwargs.pop('usedforsecurity', None)
        return _orig_md5(*args, **kwargs)
    
    import reportlab.pdfbase.pdfdoc
    _orig_rl_md5 = getattr(reportlab.pdfbase.pdfdoc, 'md5', None)
    
    tempfile.NamedTemporaryFile = _patched_NamedTemporaryFile
    hashlib.md5 = _patched_md5
    if _orig_rl_md5:
        reportlab.pdfbase.pdfdoc.md5 = _patched_md5
        
    try:
        pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    finally:
        tempfile.NamedTemporaryFile = _orig_NamedTemporaryFile
        hashlib.md5 = _orig_md5
        if _orig_rl_md5:
            reportlab.pdfbase.pdfdoc.md5 = _orig_rl_md5

    if pisa_status.err:
        return HttpResponse("PDF oluşturulurken hata oluştu", status=500)
    return response


def _fit_sheet_columns(sheet):
    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if cell.value and len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except Exception:
                pass
        sheet.column_dimensions[column].width = min(max_length + 2, 50)

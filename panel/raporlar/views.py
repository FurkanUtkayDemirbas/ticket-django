import openpyxl
import textwrap
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ticket.models import aktivite, atama, ticket
from proje.models import projeler


def raporlar_merkezi(request):
    t_qs = ticket.objects.all()
    a_qs = aktivite.objects.all()
    
    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            t_qs = t_qs.filter(unvan__in=profile.muhatap_firmalar.all())
            a_qs = a_qs.filter(ticketno__unvan__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            t_qs = t_qs.filter(danisman__in=profile.danisman_profiller.all())
            a_qs = a_qs.filter(danisman__in=profile.danisman_profiller.all())

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
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            t_qs = t_qs.filter(unvan__in=profile.muhatap_firmalar.all())
            m_qs = m_qs.filter(unvan__in=profile.muhatap_firmalar.all())
            p_qs = p_qs.filter(sozlesme_baglantisi__muhatap__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            t_qs = t_qs.filter(danisman__in=profile.danisman_profiller.all())
            m_qs = m_qs.filter(ticket__danisman__in=profile.danisman_profiller.all()).distinct()
            p_qs = p_qs.filter(sozlesme_baglantisi__ticket__danisman__in=profile.danisman_profiller.all()).distinct()

    return {
        "arama": request.GET.get("arama", "").strip(),
        "ticket_secimi": request.GET.get("ticket", "").strip(),
        "secili_durum": request.GET.get("durum", "").strip(),
        "secili_faturalama": request.GET.get("faturalama", "").strip(),
        "secili_oncelik": request.GET.get("oncelik", "").strip(),
        "secili_danisman": request.GET.get("danisman", "").strip(),
        "secili_modul": request.GET.get("modul", "").strip(),
        "secili_muhatap": request.GET.get("muhatap", "").strip(),
        "secili_proje": request.GET.get("proje", "").strip(),
        "secili_aktivite": request.GET.get("aktivite", "").strip(),
        "ticket_no": request.GET.get("ticket_no", "").strip(),
        "baslangic": request.GET.get("baslangic", "").strip(),
        "bitis": request.GET.get("bitis", "").strip(),
        "durumlar": ticket._meta.get_field("durumtanim").remote_field.model.objects.order_by("durumtanim"),
        "faturalamalar": ticket._meta.get_field("faturadurum").remote_field.model.objects.order_by("faturadurum"),
        "oncelikler": ticket._meta.get_field("oncelikkod").remote_field.model.objects.order_by("kod"),
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
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            queryset = queryset.filter(unvan__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            queryset = queryset.filter(danisman__in=profile.danisman_profiller.all())

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
        "unvan", "durumtanim", "faturadurum", "oncelikkod"
    ).prefetch_related("danisman").order_by("-ticketno")

    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            queryset = queryset.filter(unvan__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            queryset = queryset.filter(danisman__in=profile.danisman_profiller.all())

    return queryset


def _ticket_detay_rows(request):
    ticket_no = request.GET.get("ticket_no", "").strip() or request.GET.get("ticket", "").strip()
    muhatap = request.GET.get("muhatap", "").strip()
    danisman = request.GET.get("danisman", "").strip()
    oncelik = request.GET.get("oncelik", "").strip()
    durum = request.GET.get("durum", "").strip()
    faturalama_durum = request.GET.get("faturalama", "").strip()
    baslangic = request.GET.get("baslangic", "").strip()
    bitis = request.GET.get("bitis", "").strip()

    ticketlar = _ticket_detay_base_queryset(request)
    if ticket_no:
        ticketlar = ticketlar.filter(ticketno__icontains=ticket_no)
    if muhatap:
        ticketlar = ticketlar.filter(unvan_id=muhatap)
    if danisman:
        ticketlar = ticketlar.filter(danisman__username=danisman)
    if oncelik:
        ticketlar = ticketlar.filter(oncelikkod_id=oncelik)
    if durum:
        ticketlar = ticketlar.filter(durumtanim_id=durum)
    if faturalama_durum:
        ticketlar = ticketlar.filter(faturadurum_id=faturalama_durum)
    if baslangic:
        ticketlar = ticketlar.filter(termintarih__date__gte=baslangic)
    if bitis:
        ticketlar = ticketlar.filter(termintarih__date__lte=bitis)

    ticketlar = ticketlar.distinct()
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
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            queryset = queryset.filter(ticketno__unvan__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            queryset = queryset.filter(danisman__in=profile.danisman_profiller.all())

    queryset = queryset.select_related("ticketno", "danisman", "modul").order_by("-date")

    ticket_no = request.GET.get("ticket", "").strip()
    danisman = request.GET.get("danisman", "").strip()
    modul = request.GET.get("modul", "").strip()
    muhatap = request.GET.get("muhatap", "").strip()
    proje = request.GET.get("proje", "").strip()
    aktivite_no = request.GET.get("aktivite", "").strip()
    baslangic = request.GET.get("baslangic", "").strip()
    bitis = request.GET.get("bitis", "").strip()

    if aktivite_no:
        queryset = queryset.filter(number=aktivite_no)
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


def _aktivite_secim_queryset(request):
    queryset = aktivite.objects.select_related("ticketno", "ticketno__unvan").order_by("-date")

    if hasattr(request.user, 'userprofile') and not request.user.is_superuser:
        profile = request.user.userprofile
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            queryset = queryset.filter(ticketno__unvan__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            queryset = queryset.filter(danisman__in=profile.danisman_profiller.all())

    muhatap = request.GET.get("muhatap", "").strip()
    proje = request.GET.get("proje", "").strip()

    if muhatap:
        queryset = queryset.filter(ticketno__unvan__unvan=muhatap)
    if proje:
        queryset = queryset.filter(ticketno__sozlesmeno__projeler__projeno=proje)

    return queryset.distinct()


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
    context = _filter_context(request)
    context.update({
        "rows": _ticket_detay_rows(request),
        "rapor_baslik": "Ticket Özet Raporu",
        "rapor_aciklama": "Seçilen ticket için durum, fatura, yazılım ve modül efor özetleri.",
        "rapor_aciklama": "Filtrelere g\u00f6re ticket durum, fatura, yaz\u0131l\u0131m ve mod\u00fcl efor \u00f6zetleri.",
        "export_excel_url": reverse("ticket_ozet_raporu_excel"),
        "export_pdf_url": reverse("ticket_ozet_raporu_pdf"),
    })
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
        if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
            a_qs = a_qs.filter(ticketno__unvan__in=profile.muhatap_firmalar.all())
        elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
            a_qs = a_qs.filter(danisman__in=profile.danisman_profiller.all())
            
    context.update({
        "aktiviteler": aktiviteler,
        "aktivite_secimleri": _aktivite_secim_queryset(request),
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
    rows.append(["", "", "", "", "Toplam Süre", aktiviteler.aggregate(toplam=Sum("time"))["toplam"] or 0, "", "", ""])
    return _excel_response("Aktivite Raporu", _aktivite_headers(), rows, "aktivite_raporu.xlsx")


def aktivite_rapor_pdf(request):
    aktiviteler = _aktivite_queryset(request)
    rows = _aktivite_pdf_table_rows(aktiviteler)
    toplam_sure = aktiviteler.aggregate(toplam=Sum("time"))["toplam"] or 0
    return _aktivite_reportlab_pdf_response(request, _aktivite_headers(), rows, toplam_sure)


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
        _format_number(row["yazilim_eforu"]),
        _format_number(row["modul_eforu"]),
        _format_number(row["yazilim_aktivite_toplami"]),
        _format_number(row["modul_aktivite_toplami"]),
    ] for row in rows]


def _format_number(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


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


def _aktivite_headers(include_aciklama=True):
    headers = ["Muhatap Kodu", "Muhatap Adı", "Ticket No", "Ticket Adı", "Tarih", "Süre", "Danışman", "Modül"]
    if include_aciklama:
        headers.append("Açıklama")
    return headers


def _aktivite_rows(aktiviteler, include_aciklama=True, aciklama_in_ticket=False):
    rows = []
    for a in aktiviteler:
        ticket_adi = a.ticketno.konu if a.ticketno else ""
        if aciklama_in_ticket and a.aciklama:
            ticket_adi = f"{ticket_adi}\nAçıklama: {a.aciklama}" if ticket_adi else f"Açıklama: {a.aciklama}"

        row = [
            a.ticketno.unvan.vkn if a.ticketno and a.ticketno.unvan else "",
            a.ticketno.unvan.unvan if a.ticketno and a.ticketno.unvan else "",
            a.ticketno.ticketno if a.ticketno else "",
            ticket_adi,
            a.date.strftime("%Y-%m-%d %H:%M") if a.date else "",
            a.time or 0,
            str(a.danisman) if a.danisman else "",
            str(a.modul) if a.modul else "",
        ]
        if include_aciklama:
            row.append(a.aciklama or "")
        rows.append(row)
    return rows


def _pdf_wrap_text(value, width=18):
    text = str(value or "").strip()
    if not text:
        return ""
    wrapped_lines = []
    for line in text.replace("-", "- ").splitlines():
        wrapped_lines.extend(textwrap.wrap(line, width=width, break_long_words=True, break_on_hyphens=True) or [""])
    return "\n".join(wrapped_lines)


def _aktivite_pdf_table_rows(aktiviteler):
    rows = []
    for a in aktiviteler:
        rows.append([
            a.ticketno.unvan.vkn if a.ticketno and a.ticketno.unvan else "",
            _pdf_wrap_text(a.ticketno.unvan.unvan if a.ticketno and a.ticketno.unvan else "", width=16),
            a.ticketno.ticketno if a.ticketno else "",
            _pdf_wrap_text(a.ticketno.konu if a.ticketno else "", width=24),
            a.date.strftime("%d.%m.%Y\n%H:%M") if a.date else "",
            a.time or 0,
            _pdf_wrap_text(str(a.danisman) if a.danisman else "", width=16),
            _pdf_wrap_text(str(a.modul) if a.modul else "", width=14),
            _pdf_wrap_text(a.aciklama or "", width=28),
        ])
    return rows


def _register_pdf_fonts():
    regular_path = os.path.join(settings.BASE_DIR, "static", "fonts", "Roboto-Regular.ttf")
    bold_path = os.path.join(settings.BASE_DIR, "static", "fonts", "Roboto-Bold.ttf")
    if "Roboto" not in pdfmetrics.getRegisteredFontNames() and os.path.exists(regular_path):
        pdfmetrics.registerFont(TTFont("Roboto", regular_path))
    if "Roboto-Bold" not in pdfmetrics.getRegisteredFontNames() and os.path.exists(bold_path):
        pdfmetrics.registerFont(TTFont("Roboto-Bold", bold_path))
    return (
        "Roboto" if "Roboto" in pdfmetrics.getRegisteredFontNames() else "Helvetica",
        "Roboto-Bold" if "Roboto-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold",
    )


def _rl_text(value, style):
    text = str(value or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(text.replace("\n", "<br/>"), style)


def _aktivite_reportlab_pdf_response(request, headers, rows, toplam_sure):
    font_name, bold_font_name = _register_pdf_fonts()
    now = timezone.localtime()
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="aktivite_raporu.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        leftMargin=0.65 * cm,
        rightMargin=0.65 * cm,
        topMargin=0.7 * cm,
        bottomMargin=0.7 * cm,
    )

    title_style = ParagraphStyle(
        "ReportTitle",
        fontName=bold_font_name,
        fontSize=17,
        leading=20,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=3,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        fontName=font_name,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569"),
    )
    meta_style = ParagraphStyle(
        "ReportMeta",
        fontName=font_name,
        fontSize=7,
        leading=10,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#475569"),
    )
    summary_label_style = ParagraphStyle(
        "SummaryLabel",
        fontName=bold_font_name,
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1d4ed8"),
    )
    summary_value_style = ParagraphStyle(
        "SummaryValue",
        fontName=bold_font_name,
        fontSize=13,
        leading=15,
        textColor=colors.HexColor("#1e40af"),
        alignment=TA_RIGHT,
    )
    header_style = ParagraphStyle(
        "TableHeader",
        fontName=bold_font_name,
        fontSize=6.4,
        leading=7.4,
        textColor=colors.white,
        alignment=TA_LEFT,
    )
    cell_style = ParagraphStyle(
        "TableCell",
        fontName=font_name,
        fontSize=6.2,
        leading=7.4,
        textColor=colors.HexColor("#334155"),
        wordWrap="CJK",
    )
    center_cell_style = ParagraphStyle(
        "TableCellCenter",
        parent=cell_style,
        alignment=TA_CENTER,
    )

    story = [
        Table(
            [[
                Paragraph("AKTIVITE RAPORU", title_style),
                Paragraph(f"<b>Tarih:</b> {now:%d.%m.%Y %H:%M}<br/><b>Belge No:</b> RPR-{now:%Y%m%d%H%M}", meta_style),
            ]],
            colWidths=[doc.width * 0.68, doc.width * 0.32],
            style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("LINEBELOW", (0, 0), (-1, -1), 1.5, colors.HexColor("#2F5BEA")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]),
        ),
        Paragraph("Tum danisman ve efor sureleri", subtitle_style),
        Spacer(1, 8),
        Table(
            [[Paragraph("Toplam Kayitli Sure", summary_label_style), Paragraph(f"{toplam_sure} Saat", summary_value_style)]],
            colWidths=[doc.width * 0.5, doc.width * 0.5],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
                ("LINEBEFORE", (0, 0), (0, 0), 3, colors.HexColor("#3b82f6")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dbeafe")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]),
        ),
        Spacer(1, 10),
    ]

    table_data = [[_rl_text(header, header_style) for header in headers]]
    center_columns = {2, 4, 5}
    for row in rows:
        table_data.append([
            _rl_text(cell, center_cell_style if index in center_columns else cell_style)
            for index, cell in enumerate(row)
        ])

    col_widths = [1.9 * cm, 3.2 * cm, 1.7 * cm, 5.0 * cm, 2.2 * cm, 1.1 * cm, 2.6 * cm, 2.7 * cm, 6.9 * cm]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(table)

    def draw_footer(canvas, document):
        canvas.saveState()
        canvas.setFont(font_name, 7)
        canvas.setFillColor(colors.HexColor("#94a3b8"))
        canvas.drawCentredString(
            landscape(A4)[0] / 2,
            0.35 * cm,
            f"Bu belge MYKEEP Sistemleri tarafindan otomatik olarak olusturulmustur. | Sayfa {document.page}",
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    return response


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
    elif len(headers) == 8 and headers[0] == "Muhatap Kodu":
        widths = ["9%", "13%", "8%", "28%", "11%", "6%", "12%", "13%"]
    elif len(headers) == 9 and headers[0] == "Muhatap Kodu":
        widths = ["7%", "10%", "7%", "17%", "9%", "5%", "10%", "10%", "25%"]
    elif len(headers) == 4 and headers[0] == "Grup":
        widths = ["40%", "20%", "20%", "20%"]
    else:
        widths = [f"{100.0/len(headers)}%"] * len(headers)
        
    context = {
        "rapor_baslik": title,
        "rapor_aciklama": description,
        "headers": list(zip(headers, widths)),
        "col_count": len(headers),
        "widths": widths,
        "pdf_widths": " ".join(width.rstrip("%") for width in widths),
        "rows": rows,
        "compact_table": headers and headers[0] == "Muhatap Kodu",
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

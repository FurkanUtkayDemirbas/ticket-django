import openpyxl
import textwrap
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from ticket.models import aktivite, ticket


def raporlar_merkezi(request):
    context = {
        "toplam_ticket": ticket.objects.count(),
        "atanmamis_ticket": ticket.objects.filter(danisman__isnull=True).count(),
        "onay_bekleyen": ticket.objects.filter(onay=False).count(),
        "toplam_aktivite_sure": aktivite.objects.aggregate(toplam=Sum("time"))["toplam"] or 0,
    }
    return render(request, "raporlar_merkezi.html", context)


def _filter_context(request):
    return {
        "arama": request.GET.get("arama", "").strip(),
        "ticket_secimi": request.GET.get("ticket", "").strip(),
        "secili_durum": request.GET.get("durum", "").strip(),
        "secili_danisman": request.GET.get("danisman", "").strip(),
        "secili_modul": request.GET.get("modul", "").strip(),
        "baslangic": request.GET.get("baslangic", "").strip(),
        "bitis": request.GET.get("bitis", "").strip(),
        "durumlar": ticket._meta.get_field("durumtanim").remote_field.model.objects.order_by("durumtanim"),
        "danismanlar": ticket._meta.get_field("danisman").remote_field.model.objects.order_by("isim"),
        "moduller": aktivite._meta.get_field("modul").remote_field.model.objects.order_by("program", "isim"),
        "ticketlar": ticket.objects.order_by("-ticketno"),
    }


def _ticket_queryset(request, base_queryset=None):
    queryset = base_queryset if base_queryset is not None else ticket.objects.all()
    queryset = queryset.select_related(
        "unvan", "sozlesmeno", "bolumkod", "destekturu", "oncelikkod",
        "durumtanim", "faturadurum", "danisman",
    ).order_by("-ticketno")

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
        queryset = queryset.filter(danisman_id=danisman)
    if baslangic:
        queryset = queryset.filter(taleptarih__date__gte=baslangic)
    if bitis:
        queryset = queryset.filter(taleptarih__date__lte=bitis)

    return queryset


def _aktivite_queryset(request):
    queryset = aktivite.objects.select_related("ticketno", "danisman", "modul").order_by("-date")

    ticket_no = request.GET.get("ticket", "").strip()
    danisman = request.GET.get("danisman", "").strip()
    modul = request.GET.get("modul", "").strip()
    baslangic = request.GET.get("baslangic", "").strip()
    bitis = request.GET.get("bitis", "").strip()

    if ticket_no:
        queryset = queryset.filter(ticketno_id=ticket_no)
    if danisman:
        queryset = queryset.filter(danisman_id=danisman)
    if modul:
        queryset = queryset.filter(modul_id=modul)
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
    return _pdf_response(
        "Ticket Raporu",
        _ticket_headers(),
        _ticket_rows(ticketlar),
        "ticket_raporu.pdf",
        [8, 22, 18, 16, 14, 12, 12, 10],
    )


def aktivite_rapor_detay(request):
    aktiviteler = _aktivite_queryset(request)
    context = _filter_context(request)
    context.update({
        "aktiviteler": aktiviteler,
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
    rows.append(["", "", "", "Toplam Süre", aktiviteler.aggregate(toplam=Sum("time"))["toplam"] or 0, "", ""])
    return _excel_response("Aktivite Raporu", _aktivite_headers(), rows, "aktivite_raporu.xlsx")


def aktivite_rapor_pdf(request):
    aktiviteler = _aktivite_queryset(request)
    rows = _aktivite_rows(aktiviteler)
    rows.append(["", "", "", "Toplam Sure", aktiviteler.aggregate(toplam=Sum("time"))["toplam"] or 0, "", ""])
    return _pdf_response(
        "Aktivite Raporu",
        _aktivite_headers(),
        rows,
        "aktivite_raporu.pdf",
        [10, 12, 26, 16, 10, 18, 24],
    )


def atanmamis_ticket_raporu(request):
    ticketlar = _ticket_queryset(request, ticket.objects.filter(danisman__isnull=True))
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
    ticketlar = _ticket_queryset(request, ticket.objects.filter(danisman__isnull=True))
    return _excel_response("Atanmamış Ticketlar", _ticket_headers(), _ticket_rows(ticketlar), "atanmamis_ticketlar.xlsx")


def atanmamis_ticket_pdf(request):
    ticketlar = _ticket_queryset(request, ticket.objects.filter(danisman__isnull=True))
    return _pdf_response(
        "Atanmamis Ticketlar",
        _ticket_headers(),
        _ticket_rows(ticketlar),
        "atanmamis_ticketlar.pdf",
        [8, 22, 18, 16, 14, 12, 12, 10],
    )


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
    return _pdf_response(
        "Efor Onayi Bekleyenler",
        _ticket_headers(),
        _ticket_rows(ticketlar),
        "efor_onayi_bekleyenler.pdf",
        [8, 22, 18, 16, 14, 12, 12, 10],
    )


def danisman_efor_ozeti(request):
    aktiviteler = _aktivite_queryset(request)
    ozetler = aktiviteler.values(
        "danisman_id", "danisman__isim"
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
    return _pdf_response("Danisman Efor Ozeti", _ozet_headers(), ozetler, "danisman_efor_ozeti.pdf", [34, 16, 16, 16])


def modul_efor_ozeti(request):
    aktiviteler = _aktivite_queryset(request)
    ozetler = aktiviteler.values(
        "modul_id", "modul__program", "modul__isim"
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
    return _pdf_response("Modul Efor Ozeti", _ozet_headers(), ozetler, "modul_efor_ozeti.pdf", [34, 16, 16, 16])


def _ticket_headers():
    return ["Ticket No", "Konu", "Müşteri", "Modül", "Danışman", "Tarih", "Efor", "Onay"]


def _ticket_rows(ticketlar):
    return [[
        t.ticketno,
        t.konu,
        str(t.unvan) if t.unvan else "",
        str(t.bolumkod) if t.bolumkod else "",
        str(t.danisman) if t.danisman else "",
        t.taleptarih.strftime("%Y-%m-%d") if t.taleptarih else "",
        t.efor or 0,
        "Onaylı" if t.onay else "Bekliyor",
    ] for t in ticketlar]


def _aktivite_headers():
    return ["Aktivite No", "Ticket", "Ticket Konusu", "Tarih", "Süre", "Danışman", "Modül"]


def _aktivite_rows(aktiviteler):
    return [[
        a.number,
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


def _pdf_response(title, headers, rows, filename, widths):
    lines = [_format_pdf_row(headers, widths), "-" * min(sum(widths) + (3 * (len(widths) - 1)), 165)]
    lines.extend(_format_pdf_row(row, widths) for row in rows)
    pdf = _make_simple_pdf(title, lines)
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _format_pdf_row(row, widths):
    parts = []
    for value, width in zip(row, widths):
        text = _pdf_text(value)
        parts.append(textwrap.shorten(text, width=width, placeholder="..").ljust(width))
    return " | ".join(parts)


def _pdf_text(value):
    text = "" if value is None else str(value)
    translation = str.maketrans({
        "ç": "c", "Ç": "C", "ğ": "g", "Ğ": "G", "ı": "i", "İ": "I",
        "ö": "o", "Ö": "O", "ş": "s", "Ş": "S", "ü": "u", "Ü": "U",
    })
    return text.translate(translation).encode("latin-1", "ignore").decode("latin-1")


def _escape_pdf_text(text):
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _make_simple_pdf(title, lines):
    page_width = 842
    page_height = 595
    margin_x = 32
    start_y = 555
    line_height = 11
    lines_per_page = 45
    chunks = [lines[i:i + lines_per_page] for i in range(0, len(lines), lines_per_page)] or [[]]

    objects = ["<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>"]
    page_ids = []
    content_ids = []

    for chunk in chunks:
        content_lines = [
            "BT",
            "/F1 12 Tf",
            f"{margin_x} {start_y} Td",
            f"({_escape_pdf_text(_pdf_text(title))}) Tj",
            "0 -20 Td",
            "/F1 7 Tf",
        ]
        for line in chunk:
            content_lines.append(f"({_escape_pdf_text(line)}) Tj")
            content_lines.append(f"0 -{line_height} Td")
        content_lines.append("ET")
        content = "\n".join(content_lines)
        content_ids.append(len(objects) + 1)
        page_ids.append(len(objects) + 2)
        objects.append(f"<< /Length {len(content.encode('latin-1'))} >>\nstream\n{content}\nendstream")
        objects.append("")

    pages_id = len(objects) + 1
    for index, page_id in enumerate(page_ids):
        content_id = content_ids[index]
        objects[page_id - 1] = (
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 1 0 R >> >> /Contents {content_id} 0 R >>"
        )

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>")
    catalog_id = len(objects) + 1
    objects.append(f"<< /Type /Catalog /Pages {pages_id} 0 R >>")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_id, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_id} 0 obj\n{body}\nendobj\n".encode("latin-1"))
    xref_pos = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("latin-1"))
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_pos}\n%%EOF".encode("latin-1")
    )
    return bytes(pdf)


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

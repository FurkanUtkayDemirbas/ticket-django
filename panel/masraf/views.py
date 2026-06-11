from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os
import tempfile
import hashlib
import openpyxl
import reportlab.pdfbase.pdfdoc
from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa
from .models import Masraf, MasrafTuru
from .forms import MasrafForm, MasrafTuruForm
from sozlesme.models import sozlesmeler
from proje.models import projeler
from modul.models import danisman
from uyelik.decorators import admin_veya_danisman_only, admin_only


def _masraf_queryset(request):
    queryset = Masraf.objects.select_related("proje", "danisman", "masraf_turu").order_by("-tarih", "-id")

    fis_no = request.GET.get("fis_no", "").strip()
    proje_no = request.GET.get("proje_no", "").strip()
    proje_adi = request.GET.get("proje_adi", "").strip()
    danisman_secimi = request.GET.get("danisman", "").strip()
    masraf_turu = request.GET.get("masraf_turu", "").strip()
    baslangic_tarihi = request.GET.get("baslangic_tarihi", "").strip()
    bitis_tarihi = request.GET.get("bitis_tarihi", "").strip()
    odeme_durumu = request.GET.get("odeme_durumu", "").strip()

    if fis_no:
        queryset = queryset.filter(fis_no=fis_no)
    if proje_no:
        queryset = queryset.filter(proje__projeno=proje_no)
    if proje_adi:
        # tanim ile eşleştir; eğer sayısal değer geldiyse projeno ile dene
        if proje_adi.isdigit():
            queryset = queryset.filter(proje__projeno=proje_adi)
        else:
            queryset = queryset.filter(proje__tanim=proje_adi)
    if danisman_secimi:
        queryset = queryset.filter(danisman_id=danisman_secimi)
    if masraf_turu:
        queryset = queryset.filter(masraf_turu_id=masraf_turu)
    if baslangic_tarihi:
        queryset = queryset.filter(tarih__gte=baslangic_tarihi)
    if bitis_tarihi:
        queryset = queryset.filter(tarih__lte=bitis_tarihi)
    if odeme_durumu == "odendi":
        queryset = queryset.filter(odendi_mi=True)
    elif odeme_durumu == "odenmedi":
        queryset = queryset.filter(odendi_mi=False)

    return queryset


def _masraf_filter_context(request):
    return {
        "secili_fis_no": request.GET.get("fis_no", "").strip(),
        "secili_proje_no": request.GET.get("proje_no", "").strip(),
        "secili_proje_adi": request.GET.get("proje_adi", "").strip(),
        "secili_danisman": request.GET.get("danisman", "").strip(),
        "secili_masraf_turu": request.GET.get("masraf_turu", "").strip(),
        "secili_baslangic_tarihi": request.GET.get("baslangic_tarihi", "").strip(),
        "secili_bitis_tarihi": request.GET.get("bitis_tarihi", "").strip(),
        "secili_odeme_durumu": request.GET.get("odeme_durumu", "").strip(),
        "fis_nolari": Masraf.objects.exclude(fis_no="").values_list("fis_no", flat=True).distinct().order_by("fis_no"),
        "projeler": projeler.objects.order_by("projeno"),
        "danismanlar": danisman.objects.order_by("isim"),
        "masraf_turleri": MasrafTuru.objects.order_by("tanim"),
    }


def _masraf_headers():
    return ["Tarih", "Fis No", "Proje", "Danisman", "Masraf Turu", "Aciklama", "Tutar", "Durum"]


def _masraf_rows(masraflar):
    rows = []
    for masraf in masraflar:
        proje_text = "-"
        if masraf.proje:
            proje_text = str(masraf.proje.projeno)
            if masraf.muhatap_adi:
                proje_text = f"{proje_text} - {masraf.muhatap_adi}"

        rows.append([
            masraf.tarih.strftime("%d.%m.%Y") if masraf.tarih else "",
            masraf.fis_no,
            proje_text,
            str(masraf.danisman) if masraf.danisman else "-",
            masraf.masraf_turu.tanim if masraf.masraf_turu else "-",
            masraf.aciklama,
            f"{masraf.tutar} {masraf.para_birimi}",
            "Odendi" if masraf.odendi_mi else "Odenmedi",
        ])
    return rows


def _masraf_totals(masraflar):
    return list(
        masraflar.values("para_birimi")
        .annotate(toplam=Sum("tutar"))
        .order_by("para_birimi")
    )


def _format_masraf_total(total):
    return f"{total['toplam'] or 0:.2f} {total['para_birimi']}"


def _masraf_total_rows(totals):
    return [
        ["", "", "", "", "", "Toplam Tutar", _format_masraf_total(total), ""]
        for total in totals
    ]


def _fit_sheet_columns(sheet):
    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            if cell.value and len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        sheet.column_dimensions[column].width = min(max_length + 2, 50)


def _excel_response(title, headers, rows, filename, total_rows=None):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = title[:31]
    sheet.append(headers)

    for cell in sheet[1]:
        cell.font = openpyxl.styles.Font(bold=True)

    for row in rows:
        sheet.append(row)

    if total_rows:
        for row in total_rows:
            sheet.append(row)
            for cell in sheet[sheet.max_row]:
                cell.font = openpyxl.styles.Font(bold=True)

    _fit_sheet_columns(sheet)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    workbook.save(response)
    return response


def link_callback(uri, rel):
    s_url = settings.STATIC_URL
    s_root = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else os.path.join(settings.BASE_DIR, "static")
    m_url = settings.MEDIA_URL
    m_root = settings.MEDIA_ROOT

    if not s_url.startswith("/") and uri.startswith("/"):
        s_url = "/" + s_url
    if not m_url.startswith("/") and uri.startswith("/"):
        m_url = "/" + m_url

    if uri.startswith(m_url):
        path = os.path.join(m_root, uri.replace(m_url, "", 1).lstrip("/\\"))
    elif uri.startswith(s_url):
        path = os.path.join(s_root, uri.replace(s_url, "", 1).lstrip("/\\"))
    else:
        raise Exception(f'URI DID NOT MATCH: uri="{uri}", sUrl="{s_url}", mUrl="{m_url}"')

    if not os.path.isfile(path):
        raise Exception(f"media URI path not found: {path}")
    return path


def _pdf_response(request, title, headers, rows, filename, description=""):
    widths = ["10%", "10%", "16%", "14%", "13%", "20%", "10%", "7%"]
    context = {
        "rapor_baslik": title,
        "rapor_aciklama": description,
        "headers": list(zip(headers, widths)),
        "col_count": len(headers),
        "widths": widths,
        "pdf_widths": " ".join(width.rstrip("%") for width in widths),
        "rows": rows,
        "request": request,
    }
    html = render_to_string("pdf_rapor_sablonu.html", context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    orig_named_temporary_file = tempfile.NamedTemporaryFile
    orig_md5 = hashlib.md5
    orig_rl_md5 = getattr(reportlab.pdfbase.pdfdoc, "md5", None)

    def patched_named_temporary_file(*args, **kwargs):
        kwargs["delete"] = False
        return orig_named_temporary_file(*args, **kwargs)

    def patched_md5(*args, **kwargs):
        kwargs.pop("usedforsecurity", None)
        return orig_md5(*args, **kwargs)

    tempfile.NamedTemporaryFile = patched_named_temporary_file
    hashlib.md5 = patched_md5
    if orig_rl_md5:
        reportlab.pdfbase.pdfdoc.md5 = patched_md5

    try:
        pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    finally:
        tempfile.NamedTemporaryFile = orig_named_temporary_file
        hashlib.md5 = orig_md5
        if orig_rl_md5:
            reportlab.pdfbase.pdfdoc.md5 = orig_rl_md5

    if pisa_status.err:
        return HttpResponse("PDF olusturulurken hata olustu", status=500)
    return response


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


def _pdf_paragraph(value, style):
    text = str(value or "")
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(text.replace("\n", "<br/>"), style)


def _masraf_reportlab_pdf_response(headers, rows):
    font_name, bold_font_name = _register_pdf_fonts()
    now = timezone.localtime()
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="masraf_listesi.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        leftMargin=0.4 * cm,
        rightMargin=0.4 * cm,
        topMargin=0.55 * cm,
        bottomMargin=0.7 * cm,
    )
    title_style = ParagraphStyle(
        "MasrafReportTitle",
        fontName=bold_font_name,
        fontSize=17,
        leading=20,
        textColor=colors.HexColor("#1e3a8a"),
    )
    subtitle_style = ParagraphStyle(
        "MasrafReportSubtitle",
        fontName=font_name,
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#475569"),
    )
    meta_style = ParagraphStyle(
        "MasrafReportMeta",
        fontName=font_name,
        fontSize=7,
        leading=10,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#475569"),
    )
    header_style = ParagraphStyle(
        "MasrafTableHeader",
        fontName=bold_font_name,
        fontSize=8.2,
        leading=10,
        textColor=colors.white,
        alignment=TA_LEFT,
        wordWrap="CJK",
    )
    cell_style = ParagraphStyle(
        "MasrafTableCell",
        fontName=font_name,
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#334155"),
        wordWrap="CJK",
        splitLongWords=True,
    )
    center_style = ParagraphStyle("MasrafTableCellCenter", parent=cell_style, alignment=TA_CENTER)
    right_style = ParagraphStyle("MasrafTableCellRight", parent=cell_style, alignment=TA_RIGHT)

    story = [
        Table(
            [[
                Paragraph("MASRAF LISTESI", title_style),
                Paragraph(
                    f"<b>Tarih:</b> {now:%d.%m.%Y %H:%M}<br/><b>Belge No:</b> RPR-{now:%Y%m%d%H%M}",
                    meta_style,
                ),
            ]],
            colWidths=[doc.width * 0.68, doc.width * 0.32],
            style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("LINEBELOW", (0, 0), (-1, -1), 1.5, colors.HexColor("#2563eb")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]),
        ),
        Paragraph("Masraf kayitlari listesi.", subtitle_style),
        Spacer(1, 10),
    ]

    table_data = [[_pdf_paragraph(header, header_style) for header in headers]]
    for row in rows:
        table_data.append([
            _pdf_paragraph(
                cell,
                right_style if index == 6 else center_style if index in {0, 1, 7} else cell_style,
            )
            for index, cell in enumerate(row)
        ])

    col_widths = [2.2 * cm, 2.1 * cm, 4.4 * cm, 3.7 * cm, 3.4 * cm, 7.4 * cm, 3.0 * cm, 2.5 * cm]
    table = Table(table_data, colWidths=col_widths, repeatRows=1, splitByRow=1)
    table_styles = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]
    if rows and len(rows[-1]) > 5 and rows[-1][5] == "Toplam Tutar":
        table_styles.extend([
            ("FONTNAME", (0, -1), (-1, -1), bold_font_name),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eff6ff")),
        ])
    table.setStyle(TableStyle(table_styles))
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


@admin_veya_danisman_only
def masraf_listesi(request):
    masraflar = _masraf_queryset(request)
    context = {"masraflar": masraflar, "masraf_toplamlari": _masraf_totals(masraflar)}
    context.update(_masraf_filter_context(request))
    return render(request, 'masraf/masraf_listesi.html', context)


@admin_veya_danisman_only
def masraf_excel(request):
    masraflar = _masraf_queryset(request)
    rows = _masraf_rows(masraflar)
    total_rows = _masraf_total_rows(_masraf_totals(masraflar))
    return _excel_response("Masraf Listesi", _masraf_headers(), rows, "masraf_listesi.xlsx", total_rows)


@admin_veya_danisman_only
def masraf_pdf(request):
    masraflar = _masraf_queryset(request)
    rows = _masraf_rows(masraflar)
    rows.extend(_masraf_total_rows(_masraf_totals(masraflar)))
    return _pdf_response(request, "MASRAF LİSTESİ", _masraf_headers(), rows, "masraf_listesi.pdf", description="Masraf kayıtları listesi.")

@admin_veya_danisman_only
def masraf_ekle(request):
    if request.method == 'POST':
        form = MasrafForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Masraf başarıyla eklendi.')
            return redirect('masraf_listesi')
    else:
        form = MasrafForm()
    return render(request, 'masraf/masraf_form.html', {'form': form, 'title': 'Masraf Ekle'})

@admin_veya_danisman_only
def masraf_duzenle(request, pk):
    masraf = get_object_or_404(Masraf, pk=pk)
    if request.method == 'POST':
        form = MasrafForm(request.POST, request.FILES, instance=masraf)
        if form.is_valid():
            form.save()
            messages.success(request, 'Masraf başarıyla güncellendi.')
            return redirect('masraf_listesi')
    else:
        form = MasrafForm(instance=masraf)
    return render(request, 'masraf/masraf_form.html', {'form': form, 'title': 'Masraf Düzenle', 'masraf': masraf})

@admin_veya_danisman_only
def masraf_sil(request, pk):
    masraf = get_object_or_404(Masraf, pk=pk)
    if request.method == 'POST':
        masraf.delete()
        messages.success(request, 'Masraf başarıyla silindi.')
        return redirect('masraf_listesi')
    return render(request, 'masraf/masraf_sil.html', {'masraf': masraf})

@admin_only
def masraf_turu_listesi(request):
    turler = MasrafTuru.objects.all().select_related('muhatap').order_by('muhatap__unvan', 'tanim')
    return render(request, 'masraf/masraf_turu_listesi.html', {'turler': turler})

@admin_only
def masraf_turu_ekle(request):
    if request.method == 'POST':
        form = MasrafTuruForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Masraf Türü başarıyla eklendi.')
            return redirect('masraf_turu_listesi')
    else:
        form = MasrafTuruForm()
    return render(request, 'masraf/masraf_turu_form.html', {'form': form, 'title': 'Masraf Türü Ekle'})

@admin_only
def masraf_turu_duzenle(request, pk):
    tur = get_object_or_404(MasrafTuru, pk=pk)
    if request.method == 'POST':
        form = MasrafTuruForm(request.POST, instance=tur)
        if form.is_valid():
            form.save()
            messages.success(request, 'Masraf Türü başarıyla güncellendi.')
            return redirect('masraf_turu_listesi')
    else:
        form = MasrafTuruForm(instance=tur)
    return render(request, 'masraf/masraf_turu_form.html', {'form': form, 'title': 'Masraf Türü Düzenle'})

@admin_only
def masraf_turu_sil(request, pk):
    tur = get_object_or_404(MasrafTuru, pk=pk)
    if request.method == 'POST':
        try:
            tur.delete()
            messages.success(request, 'Masraf Türü başarıyla silindi.')
        except Exception as e:
            messages.error(request, 'Bu Masraf Türü kullanımda olduğu için silinemez.')
        return redirect('masraf_turu_listesi')
    return render(request, 'masraf/masraf_turu_sil.html', {'tur': tur})

@login_required
def get_proje_muhatap(request):
    proje_id = request.GET.get('proje_id')
    if proje_id:
        try:
            proje = projeler.objects.get(pk=proje_id)
            sozlesme = proje.sozlesme_baglantisi
            muhatap_adi = ''

            if sozlesme and sozlesme.muhatap:
                muhatap_adi = str(sozlesme.muhatap).strip()

            # Tüm masraf türlerini döndür (genel + firmaya özel hepsi)
            turler = MasrafTuru.objects.order_by('tanim')
            masraf_turleri = [{'id': t.pk, 'tanim': str(t)} for t in turler]

            return JsonResponse({'muhatap_adi': muhatap_adi, 'masraf_turleri': masraf_turleri})
        except (projeler.DoesNotExist, ValueError):
            pass
    return JsonResponse({'muhatap_adi': '', 'masraf_turleri': []})

@admin_veya_danisman_only
def masraf_odeme_durumu_degistir(request, pk):
    masraf = get_object_or_404(Masraf, pk=pk)
    if request.method == 'POST':
        masraf.odendi_mi = not masraf.odendi_mi
        masraf.save()
        messages.success(request, f'Masraf ödeme durumu "{"Ödendi" if masraf.odendi_mi else "Ödenmedi"}" olarak güncellendi.')
    return redirect('masraf_listesi')

from django.contrib import admin
from django.urls import path
from ticket import views as ticket_views
from muhatap import views as muhatap_views
from sozlesme import views as sozlesme_views # Bu importun olduğundan emin ol
from proje import views as proje_views
from departman import views as departman_views
from modul import views as modul_views
from destekturu import views as destekturu_views
from raporlar import views as raporlar_views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('uyelik/', include('uyelik.urls')),
    
    # Ticket Modülü
    path('', ticket_views.ana_sayfa, name='index'),
    path('ticketlar/', ticket_views.ticket_listesi, name='ticket_listesi'),
    path('ticketlar/ekle/', ticket_views.ticket_ekle, name='ticket_ekle'),
    path('ticketlar/duzenle/<int:pk>/', ticket_views.ticket_duzenle, name='ticket_duzenle'),
    path('ticketlar/sil/<int:pk>/', ticket_views.ticket_sil, name='ticket_sil'),
    path('ticketlar/tamamla/<int:pk>/', ticket_views.ticket_tamamla, name='ticket_tamamla'),
    path('ticketlar/fatura-tamamla/<int:pk>/', ticket_views.ticket_faturalama_tamamla, name='ticket_faturalama_tamamla'),
    path('ticketlar/yazisma-sil/<int:yazisma_pk>/', ticket_views.yazisma_sil, name='yazisma_sil'),
    path('ticketlar/duzenle/<int:ticket_pk>/aktivite-sil/<int:aktivite_pk>/', ticket_views.ticket_aktivite_sil, name='ticket_aktivite_sil'),
    path('ticketlar/duzenle/<int:ticket_pk>/efor-sil/<int:efor_pk>/', ticket_views.ticket_efor_sil, name='ticket_efor_sil'),
    path('aktiviteler/', ticket_views.aktivite_listesi, name='aktivite_listesi'),
    path('aktiviteler/ekle/', ticket_views.aktivite_ekle, name='aktivite_ekle'),
    path('aktiviteler/duzenle/<int:pk>/', ticket_views.aktivite_duzenle, name='aktivite_duzenle'),
    path('aktiviteler/sil/<int:pk>/', ticket_views.aktivite_sil, name='aktivite_sil'),

    # Efor (Atama) Modülü
    path('eforlar/', ticket_views.efor_listesi, name='efor_listesi'),
    path('eforlar/ekle/', ticket_views.efor_ekle, name='efor_ekle'),
    path('eforlar/duzenle/<int:pk>/', ticket_views.efor_duzenle, name='efor_duzenle'),
    path('eforlar/sil/<int:pk>/', ticket_views.efor_sil, name='efor_sil'),
    path('eforlar/onayla/<int:pk>/', ticket_views.efor_onayla, name='efor_onayla'),


    # Muhatap Modülü
    path('muhataplar/', muhatap_views.muhatap_listesi, name='muhatap_listesi'),
    path('muhataplar/ekle/', muhatap_views.muhatap_ekle, name='muhatap_ekle'),
    path('muhataplar/duzenle/<int:pk>/', muhatap_views.muhatap_duzenle, name='muhatap_duzenle'),
    path('muhataplar/sil/<int:pk>/', muhatap_views.muhatap_sil, name='muhatap_sil'),

    # Sözleşme Modülü
    path('sozlesmeler/', sozlesme_views.sozlesme_listesi, name='sozlesme_listesi'),
    path('sozlesmeler/ekle/', sozlesme_views.sozlesme_ekle, name='sozlesme_ekle'),
    path('sozlesmeler/duzenle/<int:pk>/', sozlesme_views.sozlesme_duzenle, name='sozlesme_duzenle'),
    path('sozlesmeler/sil/<int:pk>/', sozlesme_views.sozlesme_sil, name='sozlesme_sil'),

    # Proje Modülü
    path('projeler/', proje_views.proje_listesi, name='proje_listesi'),
    path('projeler/ekle/', proje_views.proje_ekle, name='proje_ekle'),
    path('projeler/duzenle/<int:pk>/', proje_views.proje_duzenle, name='proje_duzenle'),
    path('projeler/sil/<int:pk>/', proje_views.proje_sil, name='proje_sil'),

    # Departman Modülü
    path('departmanlar/', departman_views.departman_listesi, name='departman_listesi'),
    path('departmanlar/ekle/', departman_views.departman_ekle, name='departman_ekle'),
    path('departmanlar/duzenle/<int:pk>/', departman_views.departman_duzenle, name='departman_duzenle'),
    path('departmanlar/sil/<int:pk>/', departman_views.departman_sil, name='departman_sil'),

    # Modül Modülü
    path('moduller/', modul_views.bolum_listesi, name='modul_listesi'),
    path('moduller/ekle/', modul_views.bolum_ekle, name='modul_ekle'),
    path('moduller/duzenle/<int:pk>/', modul_views.bolum_duzenle, name='modul_duzenle'),
    path('moduller/sil/<int:pk>/', modul_views.bolum_sil, name='modul_sil'),

    # Danışman Modülü
    path('danismanlar/', modul_views.danisman_listesi, name='danisman_listesi'),
    path('danismanlar/ekle/', modul_views.danisman_ekle, name='danisman_ekle'),
    path('danismanlar/duzenle/<int:pk>/', modul_views.danisman_duzenle, name='danisman_duzenle'),
    path('danismanlar/sil/<int:pk>/', modul_views.danisman_sil, name='danisman_sil'),

    # Destek Türü Modülü
    path('destekturleri/', destekturu_views.destekturu_listesi, name='destekturu_listesi'),
    path('destekturleri/ekle/', destekturu_views.destekturu_ekle, name='destekturu_ekle'),
    path('destekturleri/duzenle/<int:pk>/', destekturu_views.destekturu_duzenle, name='destekturu_duzenle'),
    path('destekturleri/sil/<int:pk>/', destekturu_views.destekturu_sil, name='destekturu_sil'),

    # Raporlar Modülü
    path('raporlar/', raporlar_views.raporlar_merkezi, name='raporlar_sayfasi'),
    path('raporlar/ticket/', raporlar_views.ticket_rapor_detay, name='ticket_rapor_detay'),
    path('raporlar/ticket/indir/', raporlar_views.rapor_indir_excel, name='rapor_indir_excel'),
    path('raporlar/ticket/pdf/', raporlar_views.ticket_rapor_pdf, name='ticket_rapor_pdf'),
    path('raporlar/ticket-ozet/', raporlar_views.ticket_detay_raporu, name='ticket_ozet_raporu'),
    path('raporlar/ticket-ozet/indir/', raporlar_views.ticket_detay_raporu_excel, name='ticket_ozet_raporu_excel'),
    path('raporlar/ticket-ozet/pdf/', raporlar_views.ticket_detay_raporu_pdf, name='ticket_ozet_raporu_pdf'),
    path('raporlar/ticket-detay/', raporlar_views.ticket_detay_raporu, name='ticket_detay_raporu'),
    path('raporlar/ticket-detay/indir/', raporlar_views.ticket_detay_raporu_excel, name='ticket_detay_raporu_excel'),
    path('raporlar/ticket-detay/pdf/', raporlar_views.ticket_detay_raporu_pdf, name='ticket_detay_raporu_pdf'),
    path('raporlar/aktivite/', raporlar_views.aktivite_rapor_detay, name='aktivite_rapor_detay'),
    path('raporlar/aktivite/indir/', raporlar_views.aktivite_rapor_indir_excel, name='aktivite_rapor_indir_excel'),
    path('raporlar/aktivite/pdf/', raporlar_views.aktivite_rapor_pdf, name='aktivite_rapor_pdf'),
    path('raporlar/atanmamis-ticketlar/', raporlar_views.atanmamis_ticket_raporu, name='atanmamis_ticket_raporu'),
    path('raporlar/atanmamis-ticketlar/indir/', raporlar_views.atanmamis_ticket_excel, name='atanmamis_ticket_excel'),
    path('raporlar/atanmamis-ticketlar/pdf/', raporlar_views.atanmamis_ticket_pdf, name='atanmamis_ticket_pdf'),
    path('raporlar/efor-onayi-bekleyenler/', raporlar_views.efor_onayi_bekleyen_raporu, name='efor_onayi_bekleyen_raporu'),
    path('raporlar/efor-onayi-bekleyenler/indir/', raporlar_views.efor_onayi_bekleyen_excel, name='efor_onayi_bekleyen_excel'),
    path('raporlar/efor-onayi-bekleyenler/pdf/', raporlar_views.efor_onayi_bekleyen_pdf, name='efor_onayi_bekleyen_pdf'),
    path('raporlar/danisman-efor-ozeti/', raporlar_views.danisman_efor_ozeti, name='danisman_efor_ozeti'),
    path('raporlar/danisman-efor-ozeti/indir/', raporlar_views.danisman_efor_excel, name='danisman_efor_excel'),
    path('raporlar/danisman-efor-ozeti/pdf/', raporlar_views.danisman_efor_pdf, name='danisman_efor_pdf'),
    path('raporlar/modul-efor-ozeti/', raporlar_views.modul_efor_ozeti, name='modul_efor_ozeti'),
    path('raporlar/modul-efor-ozeti/indir/', raporlar_views.modul_efor_excel, name='modul_efor_excel'),
    path('raporlar/modul-efor-ozeti/pdf/', raporlar_views.modul_efor_pdf, name='modul_efor_pdf'),


# ... Üstteki mevcut raporlar modülü yolları aynen kalacak ...
    path('raporlar/modul-efor-ozeti/pdf/', raporlar_views.modul_efor_pdf, name='modul_efor_pdf'),

    # ====== BURAYI EKLEYİN ======
    # Masraf Modülü
    path('masraflar/', include('masraf.urls')),
]
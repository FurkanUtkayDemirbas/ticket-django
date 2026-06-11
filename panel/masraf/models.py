from django.db import models
from sozlesme.models import sozlesmeler
from muhatap.models import muhatap

class MasrafTuru(models.Model):
    tanim = models.CharField(max_length=100, verbose_name="Masraf Türü")
    muhatap = models.ForeignKey(
        "muhatap.muhatap",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Firmaya Özel (Boş = Genel)",
        related_name="masraf_turleri"
    )

    def __str__(self):
        if self.muhatap:
            return f"{self.tanim} ({self.muhatap.unvan})"
        return self.tanim

    class Meta:
        verbose_name = "Masraf Türü"
        verbose_name_plural = "Masraf Türleri"
        unique_together = [('tanim', 'muhatap')]

class Masraf(models.Model):
    PARA_BIRIMI_CHOICES = [
        ('TRY', 'TRY'),
        ('EUR', 'EUR'),
        ('USD', 'USD'),
    ]

    proje = models.ForeignKey('proje.projeler', on_delete=models.CASCADE, verbose_name="Proje", null=True)
    danisman = models.ForeignKey('modul.danisman', on_delete=models.SET_NULL, verbose_name="Danışman", null=True, blank=True)
    muhatap_adi = models.CharField(max_length=200, verbose_name="Muhatap Adı", blank=True, null=True)
    tarih = models.DateField(verbose_name="Tarih")
    masraf_turu = models.ForeignKey(MasrafTuru, on_delete=models.PROTECT, verbose_name="Masraf Türü")
    fis_no = models.CharField(max_length=50, verbose_name="Fiş No")
    aciklama = models.CharField(max_length=60, verbose_name="Açıklama")
    tutar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tutar")
    para_birimi = models.CharField(max_length=3, choices=PARA_BIRIMI_CHOICES, default='TRY', verbose_name="Para Birimi")
    odendi_mi = models.BooleanField(default=False, verbose_name="Ödendi mi?")
    dosya = models.FileField(upload_to='masraf_dosyalari/', null=True, blank=True, verbose_name="Dosya (PDF/Resim)")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fis_no} - {self.tutar} {self.para_birimi}"

    class Meta:
        verbose_name = "Masraf"
        verbose_name_plural = "Masraflar"

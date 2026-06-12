from django.db import models

class projeler(models.Model):
    projeno = models.IntegerField(primary_key=True, blank=False)
    # sozlesmeler uygulamasındaki sozlesmeler modeline bağlanıyoruz
    sozlesme_baglantisi = models.ForeignKey(
        'sozlesme.sozlesmeler', 
        to_field='sozlesmeno', 
        on_delete=models.CASCADE,
        verbose_name="İlgili Sözleşme"
    )
    tanim = models.CharField(max_length=255, null=True, blank=True, verbose_name="Proje Tanımı")
    aciklama = models.TextField(null=True, blank=True, verbose_name="Proje Açıklaması")

    def __str__(self):
        if self.tanim:
            return f"{self.projeno} - {self.tanim}"
        return f"{self.projeno}"
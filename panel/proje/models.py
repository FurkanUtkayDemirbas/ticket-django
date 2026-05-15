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
    # Tip bilgisini sözleşmeden otomatik çekebiliriz, modelde tekrar tutmana gerek yok
    # Ama illa tutmak istersen CharField yapabilirsin.

    def __str__(self):
        return f"{self.projeno} - {self.sozlesme_baglantisi}"
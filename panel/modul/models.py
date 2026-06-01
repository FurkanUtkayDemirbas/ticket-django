from django.db import models


class bolum(models.Model):
    kod = models.CharField(max_length=10, unique=True)
    program = models.CharField(max_length=40, null=True)
    isim = models.CharField(max_length=20)
    programresim = models.ImageField(upload_to='resimler', null=True, blank=True)
    yazilim_eforuna_dahil = models.BooleanField(default=False)

    list_display = ('kod', 'program', 'isim', 'programresim', 'yazilim_eforuna_dahil')

    @property
    def efor_tipi(self):
        return "YAZILIM" if self.yazilim_eforuna_dahil else "MODUL"

    def __str__(self):
        return f"{self.program}-{self.isim}"


class danisman(models.Model):
    username = models.CharField(max_length=10, unique=True)
    isim = models.CharField(max_length=40)
    email = models.EmailField(max_length=100, null=True, blank=True)
    telefon = models.CharField(max_length=10)
    tur = models.CharField(
        max_length=20, 
        choices=[('İç Kaynak', 'İç Kaynak'), ('Dış Kaynak', 'Dış Kaynak')], 
        default='İç Kaynak',
        verbose_name="Danışman Türü"
    )
    yetkinlik = models.ManyToManyField(bolum, related_name="yetkinlikler")

    def __str__(self):
        return f"{self.isim}"

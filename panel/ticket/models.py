from typing import Any

from django.db import models
from django.db.models import CharField

class statu(models.Model):
    durumtanim = models.CharField(max_length=70, null=True, unique=True)
    def __str__(self):
        return f"{self.durumtanim}"



class faturalama(models.Model):
    faturadurum = models.CharField(max_length=70, null=True, unique=True)
    def __str__(self):
        return f"{self.faturadurum}"




class ticket(models.Model):
    ticketno = models.IntegerField(primary_key=True, unique=True, blank=True)
    konu: models.CharField= models.CharField(max_length=100)
    unvan = models.ForeignKey("muhatap.muhatap", to_field="unvan", on_delete=models.CASCADE, null=True)
    sozlesmeno = models.ForeignKey("sozlesme.sozlesmeler", to_field="sozlesmeno", on_delete=models.CASCADE, null=True)
    bolumkod = models.ForeignKey("modul.bolum", to_field="kod", on_delete=models.CASCADE, null=True)
    destekturu = models.ForeignKey("destekturu.destektur", to_field="definition", on_delete=models.CASCADE, null=True)
    taleptarih = models.DateTimeField(auto_now_add=True)
    termintarih = models.DateTimeField(null=True, blank=True)
    oncelikkod = models.ForeignKey("destekturu.oncelik", to_field="kod", on_delete=models.CASCADE, null=True)
    aciklama = models.TextField(null=True, blank=True)
    durumtanim = models.ForeignKey("statu", to_field="durumtanim", on_delete=models.CASCADE, null=True)
    faturadurum = models.ForeignKey("faturalama", to_field="faturadurum", on_delete=models.CASCADE, null=True)
    danisman = models.ForeignKey("modul.danisman", to_field="username", on_delete=models.CASCADE, null=True, blank=True)
    efor = models.FloatField(null=True, blank=True)
    onay = models.BooleanField(default=False)
    musteri_ticket_no = models.CharField(max_length=50, null=True, blank=True, verbose_name="Müşteri Ticket No")


    def save(self, *args, **kwargs):
        if not self.ticketno:
            # Mevcut en yüksek ticketno'yu bul
            last_ticket = ticket.objects.all().order_by('ticketno').last()
            if last_ticket:
                self.ticketno = last_ticket.ticketno + 1
            else:
                self.ticketno = 1000  # Başlangıç değeri belirleyebilirsiniz
        super(ticket, self).save(*args, **kwargs)




    def __str__(self):
        return f" {self.ticketno}-{self.konu} {self.unvan}"


class atama (models.Model):
    danisman = models.ForeignKey("modul.danisman", to_field="username", on_delete=models.CASCADE, null=True)
    modul = models.ForeignKey("modul.bolum", to_field="kod", on_delete=models.CASCADE, null=True)
    ticketno = models.ForeignKey("ticket", to_field="ticketno" , on_delete=models.CASCADE, null=True)
    efor = models.FloatField(null=True, blank=True)
    onay = models.BooleanField(default=False)



class aktivite ( models.Model):
    number = models.IntegerField(auto_created= True,primary_key=True,unique=True, blank=True)
    ticketno = models.ForeignKey("ticket",to_field="ticketno", on_delete=models.CASCADE ,null=True)
    date = models.DateTimeField(blank = False, auto_now_add=False, null=False)
    time = models.IntegerField(null=False, blank=True)
    danisman = models.ForeignKey("modul.danisman", to_field="username", on_delete=models.CASCADE, null=True)
    modul = models.ForeignKey("modul.bolum", to_field="kod", on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        if not self.number:
            last_aktivite = aktivite.objects.all().order_by("number").last()
            self.number = last_aktivite.number + 1 if last_aktivite else 1
        super(aktivite, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.number} - {self.ticketno}"

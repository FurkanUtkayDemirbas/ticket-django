from typing import Any

from django.db import models
from django.db.models import CharField
from django.utils import timezone

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
    destekturu = models.ForeignKey("destekturu.destektur", to_field="definition", on_delete=models.PROTECT, null=True)
    taleptarih = models.DateTimeField(default=timezone.now)
    termintarih = models.DateTimeField(null=True, blank=True)
    oncelikkod = models.ForeignKey("destekturu.oncelik", to_field="kod", on_delete=models.CASCADE, null=True)
    aciklama = models.TextField(null=True, blank=True)
    durumtanim = models.ForeignKey("statu", to_field="durumtanim", on_delete=models.CASCADE, null=True)
    faturadurum = models.ForeignKey("faturalama", to_field="faturadurum", on_delete=models.CASCADE, null=True)
    danisman = models.ManyToManyField("modul.danisman", blank=True, related_name="ticket_danismanlar")
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
    aciklama = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.number:
            last_aktivite = aktivite.objects.all().order_by("number").last()
            self.number = last_aktivite.number + 1 if last_aktivite else 100
        super(aktivite, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.number} - {self.ticketno}"


from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum

@receiver([post_save, post_delete], sender=atama)
def update_ticket_efor_onay(sender, instance, **kwargs):
    if instance.ticketno:
        ticket_obj = instance.ticketno
        # Calculate sum of atama efor
        toplam = atama.objects.filter(ticketno=ticket_obj).aggregate(Sum('efor'))['efor__sum']
        ticket_obj.efor = toplam or 0
        
        # Determine ticket approval status based on atama approvals
        onayli_var_mi = atama.objects.filter(ticketno=ticket_obj, onay=True).exists()
        ticket_obj.onay = onayli_var_mi
        
        ticket_obj.save()
        
        # Danışmanı ticket'a otomatik ekle
        if instance.danisman and hasattr(ticket_obj, 'danisman'):
            ticket_obj.danisman.add(instance.danisman)

@receiver([post_save, post_delete], sender=aktivite)
def update_ticket_aktivite_danisman(sender, instance, **kwargs):
    if instance.ticketno and instance.danisman:
        ticket_obj = instance.ticketno
        if hasattr(ticket_obj, 'danisman'):
            ticket_obj.danisman.add(instance.danisman)

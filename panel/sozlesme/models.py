from tkinter.constants import CASCADE
from typing import Any

from django.db import models
from django.db.models import CharField


class sozlesmetip(models.Model):
    tanim = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.tanim


# Create your models here.
class sozlesmeler(models.Model):
    sozlesmeno = models.CharField(unique=True, null=False, blank=False, default="2026-")
    tip = models.ForeignKey("sozlesmetip", to_field="tanim", on_delete=models.CASCADE,null=True)
    tanim = models.CharField(null=False, blank=False)
    muhatap = models.ForeignKey("muhatap.muhatap", to_field="unvan", on_delete=models.CASCADE)
    baslangic_tarihi = models.DateTimeField(blank=True, null=True)
    bitis_tarihi = models.DateTimeField(blank=True, null=True)
    aciklama = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.sozlesmeno} {self.tip}  {self.tanim} {str(self.muhatap)}"
class projelist(models.Model):
    projeno = models.IntegerField(unique=True,auto_created=True,primary_key=True, null=False )
    projetanim = models.CharField(null = False ,blank = False , max_length=100)
    sozlesmeno = models.ForeignKey("sozlesmeler", to_field="sozlesmeno", on_delete=models.CASCADE,null=True)

    def __str__(self):
        return  f" {self.projeno} {self.sozlesmeno}  {self.projetanim} {str(self.sozlesmeno)}"
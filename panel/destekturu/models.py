from django.db import models


# Create your models here.

class destektur(models.Model):
    kod = models.CharField(max_length=10)
    definition = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.kod} {self.definition}"


class oncelik(models.Model):
    kod = models.CharField(max_length=3, unique=True)
    tanim = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.kod} {self.tanim}"

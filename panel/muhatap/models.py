from django.db import models




# Create your models here.
""""
class bolum(models.Model):
    kod = models.CharField(max_length=10,unique=True)
    isim = models.CharField(max_length=10)
    def __str__(self):
        return ( self.isim )


class danisman (models.Model):
    username = models.CharField(max_length=10)
    isim = models.CharField(max_length=40)
    telefon = models.CharField(max_length=10)
    bolumkod = models.ForeignKey("bolum",to_field="kod",on_delete=models.CASCADE)

    def __str__(self):
        return ( self.isim )
        
        
"""

class hesapgrubu(models.Model):
    grupkod = models.CharField(max_length=10,unique=True)
    name = models.CharField(max_length=50)
    def __str__(self):
        return ( self.name )


class muhatap(models.Model):
    unvan = models.CharField(max_length=100,unique=True)
    vkn = models.CharField(max_length=11)
    adres = models.TextField()
    telefon =models.CharField(max_length=10, null=True)
    grupkod = models.ForeignKey("hesapgrubu", to_field="grupkod", on_delete=models.CASCADE ,null=True)
    slug = models.SlugField(max_length=100,unique=True,null=True)
    aktif = models.BooleanField(default=False,null=True)

    def __str__(self):
        return f"{self.unvan}   "

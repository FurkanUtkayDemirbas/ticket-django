from django.db import models

# Create your models here.
class departman (models.Model):
    kod = models.CharField(max_length=10 , unique=True)
    tanim = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.kod} - {self.tanim}"


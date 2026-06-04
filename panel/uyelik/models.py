from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Firma', 'Firma (Müşteri)'),
        ('Danisman', 'Danışman'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Admin')
    
    # Yeni çoklu seçim alanları
    muhatap_firmalar = models.ManyToManyField("muhatap.muhatap", blank=True, related_name="kullanici_profilleri_coklu")
    danisman_profiller = models.ManyToManyField("modul.danisman", blank=True, related_name="kullanici_profilleri_coklu")
    
    is_approved = models.BooleanField(default=True) # Varsayılan Adminler için True, Firma kaydında False yapacağız

    def __str__(self):
        return f"{self.user.username} - {self.role}"

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
    muhatap_firma = models.ForeignKey("muhatap.muhatap", to_field="unvan", on_delete=models.SET_NULL, null=True, blank=True)
    danisman_profil = models.ForeignKey("modul.danisman", to_field="username", on_delete=models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=True) # Varsayılan Adminler için True, Firma kaydında False yapacağız

    def __str__(self):
        return f"{self.user.username} - {self.role}"

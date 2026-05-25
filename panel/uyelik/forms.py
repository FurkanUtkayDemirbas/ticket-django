from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from muhatap.models import muhatap

class KayitForm(UserCreationForm):
    muhatap_firma = forms.ModelChoiceField(
        queryset=muhatap.objects.all(),
        required=True,
        label="Firmanız",
        empty_label="Firma Seçiniz..."
    )

    class Meta:
        model = User
        fields = ['username', 'muhatap_firma']
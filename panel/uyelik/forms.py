from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from muhatap.models import muhatap
from modul.models import danisman


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


WIDGET_CLASS = (
    'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm '
    'focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 '
    'outline-none transition-all'
)


class AdminKullaniciForm(forms.Form):
    """Admin tarafından kullanıcı eklemek için form."""
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Danisman', 'Danışman'),
        ('Firma', 'Firma (Müşteri)'),
    ]

    username = forms.CharField(
        label='Kullanıcı Adı',
        max_length=150,
        widget=forms.TextInput(attrs={'class': WIDGET_CLASS, 'placeholder': 'örn: furkan.demirbas'})
    )
    first_name = forms.CharField(
        label='Ad',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': WIDGET_CLASS, 'placeholder': 'Ad'})
    )
    last_name = forms.CharField(
        label='Soyad',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': WIDGET_CLASS, 'placeholder': 'Soyad'})
    )
    email = forms.EmailField(
        label='E-posta',
        required=False,
        widget=forms.EmailInput(attrs={'class': WIDGET_CLASS, 'placeholder': 'ornek@firma.com'})
    )
    password1 = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={'class': WIDGET_CLASS, 'placeholder': '••••••••'})
    )
    password2 = forms.CharField(
        label='Şifre (Tekrar)',
        widget=forms.PasswordInput(attrs={'class': WIDGET_CLASS, 'placeholder': '••••••••'})
    )
    role = forms.ChoiceField(
        label='Rol',
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={'class': WIDGET_CLASS, 'id': 'id_role', 'data-no-ts': 'true'})
    )
    muhatap_firma = forms.ModelChoiceField(
        queryset=muhatap.objects.all(),
        required=False,
        label='Firma',
        empty_label='--- Firma Seçiniz ---',
        widget=forms.Select(attrs={'class': WIDGET_CLASS, 'id': 'id_muhatap_firma', 'data-no-ts': 'true'})
    )
    danisman_profil = forms.ModelChoiceField(
        queryset=danisman.objects.all(),
        required=False,
        label='Danışman Profili',
        empty_label='--- Danışman Seçiniz ---',
        widget=forms.Select(attrs={'class': WIDGET_CLASS, 'id': 'id_danisman_profil', 'data-no-ts': 'true'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Bu kullanıcı adı zaten alınmış.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        role = cleaned_data.get('role')

        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Şifreler eşleşmiyor.')

        if role == 'Firma' and not cleaned_data.get('muhatap_firma'):
            self.add_error('muhatap_firma', 'Firma rolü için bir firma seçmelisiniz.')

        if role == 'Danisman' and not cleaned_data.get('danisman_profil'):
            self.add_error('danisman_profil', 'Danışman rolü için bir danışman profili seçmelisiniz.')

        return cleaned_data


class AdminSifreSifirlaForm(forms.Form):
    """Admin'in başka bir kullanıcının şifresini sıfırlaması için."""
    new_password1 = forms.CharField(
        label='Yeni Şifre',
        widget=forms.PasswordInput(attrs={'class': WIDGET_CLASS, 'placeholder': '••••••••'})
    )
    new_password2 = forms.CharField(
        label='Yeni Şifre (Tekrar)',
        widget=forms.PasswordInput(attrs={'class': WIDGET_CLASS, 'placeholder': '••••••••'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')
        if p1 and p2 and p1 != p2:
            self.add_error('new_password2', 'Şifreler eşleşmiyor.')
        return cleaned_data
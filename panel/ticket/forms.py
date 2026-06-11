from django import forms
from .models import TicketYazisma, aktivite, ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = ticket
        fields = ['konu', 'unvan', 'sozlesmeno', 'departmankod', 'bolumkod', 'destekturu', 'taleptarih', 'termintarih', 'oncelikkod', 'musteri_ticket_no', 'aciklama', 'durumtanim', 'faturadurum']
        labels = {
            'departmankod': 'Departman Kodu',
            'bolumkod': 'Bölüm Kodu',
            'unvan': 'Muhatap',
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.is_creation = kwargs.pop('is_creation', False)
        super().__init__(*args, **kwargs)
        
        # Yeni ticket acilisinda mevcut is akisi durumunu varsayilan sec.
        if self.is_creation and not self.instance.pk:
            from .models import statu
            yeni_talep = statu.objects.filter(durumtanim="Yeni Talep").first()
            if yeni_talep:
                self.fields['durumtanim'].initial = yeni_talep
            
        for field_name, field in self.fields.items():
            # Modern ve sade sınıflar
            field.widget.attrs['class'] = (
                'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm '
                'focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 '
                'outline-none transition-all cursor-pointer select-none'
            )
            # Açıklama (textarea) yüksekliğini sabitle
            if field_name == 'aciklama':
                field.widget.attrs['rows'] = '4'
            
            # Tarihler için HTML5 datetime-local tipi ekle (Flatpickr takvimi için)
            if field_name in ['taleptarih', 'termintarih']:
                field.widget.input_type = 'datetime-local'
        
        # Firmalar sadece kendi firmaları için ticket oluşturabilir ve sadece kendi sözleşmelerini seçebilir
        if self.user and hasattr(self.user, 'userprofile') and not self.user.is_superuser:
            profile = self.user.userprofile
            if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
                self.fields['unvan'].queryset = self.fields['unvan'].queryset.filter(unvan__in=profile.muhatap_firmalar.all())
                self.fields['unvan'].initial = profile.muhatap_firmalar.first() if profile.muhatap_firmalar.exists() else None
                self.fields['sozlesmeno'].queryset = self.fields['sozlesmeno'].queryset.filter(muhatap__in=profile.muhatap_firmalar.all())

from .models import atama

class AtamaForm(forms.ModelForm):
    class Meta:
        model = atama
        fields = ['ticketno', 'danisman', 'modul', 'efor', 'onay']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user and hasattr(self.user, 'userprofile') and not self.user.is_superuser:
            profile = self.user.userprofile
            if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
                self.fields['ticketno'].queryset = self.fields['ticketno'].queryset.filter(unvan__in=profile.muhatap_firmalar.all())
            elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
                self.fields['ticketno'].queryset = self.fields['ticketno'].queryset.filter(danisman__in=profile.danisman_profiller.all())
                
        for field_name, field in self.fields.items():
            if field_name != 'onay':
                field.widget.attrs['class'] = (
                    'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm '
                    'focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 '
                    'outline-none transition-all cursor-pointer select-none'
                )


class AktiviteForm(forms.ModelForm):
    date = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"],
        label="Aktivite Tarihi",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
    )

    class Meta:
        model = aktivite
        fields = ["ticketno", "date", "time", "danisman", "modul", "aciklama"]
        labels = {
            "ticketno": "Ticket",
            "time": "Süre (Saat)",
            "danisman": "Danışman",
            "modul": "Modül",
            "aciklama": "Açıklama",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user and hasattr(self.user, 'userprofile') and not self.user.is_superuser:
            profile = self.user.userprofile
            if profile.role == 'Firma' and profile.muhatap_firmalar.exists():
                self.fields['ticketno'].queryset = self.fields['ticketno'].queryset.filter(unvan__in=profile.muhatap_firmalar.all())
            elif profile.role == 'Danisman' and profile.danisman_profiller.exists():
                self.fields['ticketno'].queryset = self.fields['ticketno'].queryset.filter(danisman__in=profile.danisman_profiller.all())
                
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                "w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm "
                "focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 "
                "outline-none transition-all cursor-pointer select-none"
            )
        self.fields["aciklama"].widget = forms.Textarea(attrs={
            "class": (
                "w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm "
                "focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 "
                "outline-none transition-all"
            ),
            "rows": 4,
        })


class TicketIciAktiviteForm(forms.ModelForm):
    """Ticket düzenleme sayfasında kullanılan aktivite formu (ticketno hariç)."""
    date = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"],
        label="Aktivite Tarihi",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
    )

    class Meta:
        model = aktivite
        fields = ["date", "time", "danisman", "modul", "aciklama"]
        labels = {
            "time": "Süre (Saat)",
            "danisman": "Danışman",
            "modul": "Modül",
            "aciklama": "Açıklama",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
            field.widget.attrs["class"] = (
                "w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm "
                "focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 "
                "outline-none transition-all cursor-pointer select-none"
            )
        self.fields["aciklama"].widget = forms.Textarea(attrs={
            "class": (
                "w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm "
                "focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 "
                "outline-none transition-all"
            ),
            "rows": 3,
        })


class TicketIciEforForm(forms.ModelForm):
    """Ticket düzenleme sayfasında kullanılan efor/atama formu (ticketno hariç)."""

    class Meta:
        model = atama
        fields = ["danisman", "modul", "efor", "onay"]
        labels = {
            "danisman": "Danışman",
            "modul": "Modül",
            "efor": "Efor (Saat)",
            "onay": "Onay",
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = False
            if field_name != 'onay':
                field.widget.attrs["class"] = (
                    "w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm "
                    "focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 "
                    "outline-none transition-all cursor-pointer select-none"
                )

class TicketYazismaForm(forms.ModelForm):
    class Meta:
        model = TicketYazisma
        fields = ["mesaj", "dosya"]
        labels = {
            "mesaj": "Yazışma",
            "dosya": "Dosya Eki",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["mesaj"].widget = forms.Textarea(attrs={
            "class": (
                "w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm "
                "focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 "
                "outline-none transition-all"
            ),
            "rows": 4,
            "placeholder": "Ticket ile ilgili yazışma veya açıklama ekleyin...",
        })
        
        self.fields["dosya"].widget = forms.ClearableFileInput(attrs={
            "class": "block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        })

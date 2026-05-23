from django import forms
from .models import aktivite, ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = ticket
        fields = ['konu', 'unvan', 'sozlesmeno', 'bolumkod', 'destekturu', 'termintarih', 'oncelikkod', 'musteri_ticket_no', 'aciklama', 'durumtanim', 'faturadurum', 'danisman']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
            
            # Termin tarihi için HTML5 datetime-local tipi ekle (Flatpickr takvimi için)
            if field_name == 'termintarih':
                field.widget.input_type = 'datetime-local'

from .models import atama

class AtamaForm(forms.ModelForm):
    class Meta:
        model = atama
        fields = ['ticketno', 'danisman', 'modul', 'efor', 'onay']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        fields = ["ticketno", "date", "time", "danisman", "modul"]
        labels = {
            "ticketno": "Ticket",
            "time": "Süre (Saat)",
            "danisman": "Danışman",
            "modul": "Modül",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                "w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm "
                "focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 "
                "outline-none transition-all cursor-pointer select-none"
            )


class TicketIciAktiviteForm(forms.ModelForm):
    """Ticket düzenleme sayfasında kullanılan aktivite formu (ticketno hariç)."""
    date = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"],
        label="Aktivite Tarihi",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
    )

    class Meta:
        model = aktivite
        fields = ["date", "time", "danisman", "modul"]
        labels = {
            "time": "Süre (Saat)",
            "danisman": "Danışman",
            "modul": "Modül",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                "w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm "
                "focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 "
                "outline-none transition-all cursor-pointer select-none"
            )


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
            if field_name != 'onay':
                field.widget.attrs["class"] = (
                    "w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm "
                    "focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 "
                    "outline-none transition-all cursor-pointer select-none"
                )

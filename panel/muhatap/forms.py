from django import forms
from .models import muhatap

class MuhatapForm(forms.ModelForm):
    class Meta:
        model = muhatap
        # Modellerindeki alan isimleri: unvan, vkn, adres, telefon, grupkod, aktif
        fields = ['unvan', 'vkn', 'adres', 'telefon', 'grupkod', 'aktif']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['aktif'].initial = True
        for field_name, field in self.fields.items():
            if field_name != 'aktif':
                field.widget.attrs['class'] = (
                    'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 text-sm '
                    'focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 '
                    'outline-none transition-all duration-200 text-slate-700'
                )
            if field_name == 'adres':
                field.widget.attrs['rows'] = '4'
            if field_name == 'aktif':
                field.widget.attrs['class'] = (
                    'h-5 w-5 rounded border-slate-300 text-blue-600 '
                    'focus:ring-blue-500'
                )

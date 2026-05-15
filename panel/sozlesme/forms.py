from django import forms
from .models import sozlesmeler

class SozlesmeForm(forms.ModelForm):
    class Meta:
        model = sozlesmeler
        fields = ['sozlesmeno', 'tip', 'tanim', 'muhatap', 'baslangic_tarihi', 'bitis_tarihi', 'aciklama']
        labels = {
            'sozlesmeno': 'Sözleşme Numarası',
            'tip': 'Sözleşme Tipi',
            'tanim': 'Sözleşme Tanımı',
            'muhatap': 'İlgili Muhatap',
            'baslangic_tarihi': 'Başlangıç Tarihi',
            'bitis_tarihi': 'Bitiş Tarihi',
            'aciklama': 'Sözleşme Detayları'
        }
        widgets = {
            'baslangic_tarihi': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'bitis_tarihi': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = (
                'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm '
                'focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 '
                'outline-none transition-all duration-200 text-slate-700'
            )
            if field_name == 'aciklama':
                field.widget.attrs['rows'] = '4'
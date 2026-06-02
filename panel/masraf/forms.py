from django import forms
from .models import Masraf, MasrafTuru

class MasrafTuruForm(forms.ModelForm):
    class Meta:
        model = MasrafTuru
        fields = ['tanim', 'muhatap']
        widgets = {
            'tanim': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
            'muhatap': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['muhatap'].required = False
        self.fields['muhatap'].empty_label = '--- Genel (Tüm Firmalara Açık) ---'

class MasrafForm(forms.ModelForm):
    class Meta:
        model = Masraf
        fields = ['sozlesme', 'muhatap_adi', 'tarih', 'masraf_turu', 'fis_no', 'aciklama', 'tutar', 'para_birimi', 'odendi_mi']
        widgets = {
            'sozlesme': forms.Select(attrs={'class': 'w-full', 'id': 'id_sozlesme'}),
            'muhatap_adi': forms.TextInput(attrs={'class': 'w-full px-5 py-3.5 bg-slate-50 border border-slate-100 rounded-2xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-sm font-semibold text-slate-700', 'readonly': 'readonly', 'id': 'id_muhatap_adi'}),
            'tarih': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-5 py-3.5 bg-slate-50 border border-slate-100 rounded-2xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-sm font-semibold text-slate-700'}),
            'masraf_turu': forms.Select(attrs={'class': 'w-full'}),
            'fis_no': forms.TextInput(attrs={'class': 'w-full px-5 py-3.5 bg-slate-50 border border-slate-100 rounded-2xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-sm font-semibold text-slate-700'}),
            'aciklama': forms.TextInput(attrs={'class': 'w-full px-5 py-3.5 bg-slate-50 border border-slate-100 rounded-2xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-sm font-semibold text-slate-700', 'maxlength': '60'}),
            'tutar': forms.NumberInput(attrs={'class': 'w-full px-5 py-3.5 bg-slate-50 border border-slate-100 rounded-2xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-sm font-semibold text-slate-700', 'step': '0.01'}),
            'para_birimi': forms.Select(attrs={'class': 'w-full'}),
            'odendi_mi': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-blue-600 bg-slate-50 border-slate-200 rounded focus:ring-blue-500'}),
        }

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
        fields = ['proje', 'muhatap_adi', 'danisman', 'tarih', 'masraf_turu', 'fis_no', 'aciklama', 'tutar', 'para_birimi', 'dosya']
        widgets = {
            'proje': forms.Select(attrs={'class': 'w-full', 'id': 'id_proje'}),
            'muhatap_adi': forms.TextInput(attrs={'class': 'w-full px-5 py-3.5 bg-slate-50 border border-slate-100 rounded-2xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-sm font-semibold text-slate-700', 'readonly': 'readonly', 'id': 'id_muhatap_adi'}),
            'danisman': forms.Select(attrs={'class': 'w-full', 'id': 'id_danisman'}),
            'tarih': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-5 py-3.5 bg-slate-50 border border-slate-100 rounded-2xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-sm font-semibold text-slate-700'}),
            'masraf_turu': forms.Select(attrs={'class': 'w-full', 'id': 'id_masraf_turu'}),
            'fis_no': forms.TextInput(attrs={'class': 'w-full px-5 py-3.5 bg-slate-50 border border-slate-100 rounded-2xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-sm font-semibold text-slate-700'}),
            'aciklama': forms.TextInput(attrs={'class': 'w-full px-5 py-3.5 bg-slate-50 border border-slate-100 rounded-2xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-sm font-semibold text-slate-700', 'maxlength': '60'}),
            'tutar': forms.NumberInput(attrs={'class': 'w-full px-5 py-3.5 bg-slate-50 border border-slate-100 rounded-2xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-sm font-semibold text-slate-700', 'step': '0.01'}),
            'para_birimi': forms.Select(attrs={'class': 'w-full'}),
            'dosya': forms.ClearableFileInput(attrs={
                'class': 'hidden',
                'id': 'id_dosya',
                'accept': 'image/*,application/pdf',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proje'].empty_label = 'Proje seçiniz...'
        self.fields['dosya'].required = False

    def clean(self):
        cleaned_data = super().clean()
        proje = cleaned_data.get('proje')
        if proje and proje.sozlesme_baglantisi_id:
            muhatap = proje.sozlesme_baglantisi.muhatap
            cleaned_data['muhatap_adi'] = muhatap.unvan if muhatap else ''
        else:
            cleaned_data['muhatap_adi'] = ''
        return cleaned_data

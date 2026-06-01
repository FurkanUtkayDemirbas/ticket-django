from django import forms
from .models import projeler

class ProjeForm(forms.ModelForm):
    class Meta:
        model = projeler
        fields = ['projeno', 'sozlesme_baglantisi', 'tanim', 'aciklama']
        labels = {
            'projeno': 'Proje Numarası',
            'sozlesme_baglantisi': 'Sözleşme Seçin',
            'tanim': 'Proje Tanımı',
            'aciklama': 'Proje Açıklaması',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Firmalar sadece kendi firmalarına ait sözleşmeleri seçebilir
        if self.user and hasattr(self.user, 'userprofile') and not self.user.is_superuser:
            profile = self.user.userprofile
            if profile.role == 'Firma' and profile.muhatap_firma:
                self.fields['sozlesme_baglantisi'].queryset = self.fields['sozlesme_baglantisi'].queryset.filter(muhatap=profile.muhatap_firma)
                
        for field_name, field in self.fields.items():
            if field_name == 'aciklama':
                field.widget = forms.Textarea(attrs={
                    'class': (
                        'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm '
                        'focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 '
                        'outline-none transition-all resize-none'
                    ),
                    'rows': '4',
                    'placeholder': 'Proje hakkında detaylı açıklama yazın...',
                })
            else:
                field.widget.attrs['class'] = (
                    'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm '
                    'focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none transition-all'
                )
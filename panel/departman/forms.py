from django import forms
from .models import departman

class DepartmanForm(forms.ModelForm):
    class Meta:
        model = departman
        fields = ['kod', 'tanim']
        labels = {
            'kod': 'Departman Kodu',
            'tanim': 'Departman Tanımı (Adı)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                'w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm '
                'focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 '
                'outline-none transition-all duration-200'
            )
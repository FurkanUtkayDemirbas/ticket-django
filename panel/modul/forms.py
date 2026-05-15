from django import forms

from .models import bolum, danisman


BASE_INPUT_CLASS = (
    "w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm "
    "focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 "
    "outline-none transition-all duration-200"
)


class BolumForm(forms.ModelForm):
    class Meta:
        model = bolum
        fields = ["kod", "program", "isim", "programresim"]
        labels = {
            "kod": "Modül Kodu",
            "program": "Program",
            "isim": "Modül Adı",
            "programresim": "Program Görseli",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = BASE_INPUT_CLASS


class DanismanForm(forms.ModelForm):
    class Meta:
        model = danisman
        fields = ["username", "isim", "email", "telefon", "tur", "yetkinlik"]
        labels = {
            "username": "Danışman Kodu",
            "isim": "Danışman Adı",
            "email": "E-Posta",
            "telefon": "Telefon",
            "tur": "Danışman Türü",
            "yetkinlik": "Yetkin Olduğu Modüller",
        }
        widgets = {
            "yetkinlik": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == "yetkinlik":
                continue
            field.widget.attrs["class"] = BASE_INPUT_CLASS

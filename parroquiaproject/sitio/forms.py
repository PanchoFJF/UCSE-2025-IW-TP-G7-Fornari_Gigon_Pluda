from django import forms
from .models import Iglesia
from .models import Noticia

class IglesiaForm(forms.ModelForm):
    class Meta:
        model = Iglesia
        fields = ['nombre', 'direccion', 'contacto_secretaria', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_secretaria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+54...'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ["titulo", "descripcion", "imagen"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Título de la publicación"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Escribí tu noticia o anuncio..."}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

from django import forms
from .models import Iglesia

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

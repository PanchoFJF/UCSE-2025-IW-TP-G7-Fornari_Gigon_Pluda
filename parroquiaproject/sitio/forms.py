from django import forms
from .models import Iglesia, UsuarioIglesias
from .models import Noticia
from .models import Actividades, Iglesia
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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


class AutorizacionForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "ejemplo@correo.com"})
    )
    iglesia_id = forms.ModelChoiceField(
        label="Iglesia",
        queryset=Iglesia.objects.none(),  # se setea en __init__
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label="Seleccionar iglesia"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # recibimos opcionalmente el user
        super().__init__(*args, **kwargs)
        if user:
            try:
                usuario_iglesias = UsuarioIglesias.objects.get(usuario=user)
                self.fields['iglesia_id'].queryset = usuario_iglesias.iglesias_admin.all()
            except UsuarioIglesias.DoesNotExist:
                self.fields['iglesia_id'].queryset = Iglesia.objects.none()


class EmailChangeForm(forms.Form):
    email = forms.EmailField(
        label="Nuevo correo electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        # Recibimos el usuario actual para validaciones
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        nuevo_email = self.cleaned_data.get('email').lower()

        if not self.user:
            raise ValidationError("No se pudo determinar el usuario actual.")

        # Validación 1: distinto del correo actual
        if nuevo_email == self.user.email.lower():
            raise ValidationError("El nuevo correo no puede ser igual al actual.")

        # Validación 2: único en la base de datos
        if User.objects.filter(email__iexact=nuevo_email).exclude(pk=self.user.pk).exists():
            raise ValidationError("Este correo ya está en uso por otro usuario.")

        return nuevo_email
    
class AutorizacionForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "ejemplo@correo.com"})
    )
    iglesia_id = forms.ModelChoiceField(
        label="Iglesia",
        queryset=Iglesia.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label="Seleccionar iglesia"
    )

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner', None) or kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if owner:
            self.fields['iglesia_id'].queryset = Iglesia.objects.filter(administrador=owner)
        else:
            self.fields['iglesia_id'].queryset = Iglesia.objects.none()



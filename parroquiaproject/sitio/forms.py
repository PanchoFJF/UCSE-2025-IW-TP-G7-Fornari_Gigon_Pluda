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
        help_texts = {
            "contacto_secretaria": "(opcional)",
            "imagen": "(opcional)",
        }  

class NoticiaForm(forms.ModelForm):
    iglesiaAsociada = forms.ModelChoiceField(
        queryset=Iglesia.objects.all(),
        required=True,
        label="Iglesia asociada",
        empty_label="-- Seleccionar Iglesia --",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    class Meta:
        model = Noticia
        fields = ["titulo", "descripcion", "imagen", "iglesiaAsociada"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Título de la publicación"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Escribí tu noticia o anuncio..."}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "iglesiaAsociada": forms.Select(attrs={"class": "form-control"}),
        }
        help_texts = {
            "imagen": "(opcional)",
        }  

class NoticiaEditForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ["titulo", "descripcion", "imagen"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
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
                self.fields["iglesia_id"].queryset = Iglesia.objects.filter(administrador=user)


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
    
class ActividadesForm(forms.ModelForm):
    tipo = forms.ChoiceField(
        choices=[("permanente", "Permanente"), ("especial", "Especial")],
        required=True,
        label="Tipo de actividad"
    )

    categoria = forms.ChoiceField(choices=[
        ("Misa", "Misa"),
        ("Adoración", "Adoración"),
        ("Bingo", "Bingo"),
        ("Retiro", "Retiro"),
        ("Grupo Juvenil", "Grupo Juvenil"),
        ("Otro", "Otro"),
    ], required=True, label="Categoría")

    dia = forms.ChoiceField(choices=[
        ("Lunes", "Lunes"),
        ("Martes", "Martes"),
        ("Miércoles", "Miércoles"),
        ("Jueves", "Jueves"),
        ("Viernes", "Viernes"),
        ("Sábado", "Sábado"),
        ("Domingo", "Domingo"),
    ], required=False, label="Día")

    hora = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}),
        input_formats=['%H:%M'],
        required=False,
        label="Hora"
    )

    fecha_inicio = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        required=False,
        label="Fecha y hora de inicio"
    )

    fechaVencimiento = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        required=False,
        label="Fecha de finalización"
    )

    class Meta:
        model = Actividades
        fields = ["tipo", "categoria", "iglesia", "titulo", "texto", "dia", "hora", "fecha_inicio", "fechaVencimiento"]
        labels = {
            "texto": "Descripción",
            "fechaVencimiento": "Fecha de finalización",
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")

        if tipo == "permanente":
            if not cleaned_data.get("dia") or not cleaned_data.get("hora"):
                raise forms.ValidationError("Debe completar Día y Hora para una actividad permanente.")
            cleaned_data["fecha_inicio"] = None
            cleaned_data["fechaVencimiento"] = None

        elif tipo == "especial":
            fecha_inicio = cleaned_data.get("fecha_inicio")
            if not fecha_inicio:
                raise forms.ValidationError("Debe ingresar la fecha de inicio para una actividad especial.")

            # Día en español automáticamente
            dias_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            dia_nombre = dias_es[fecha_inicio.weekday()]
            cleaned_data["dia"] = dia_nombre
            cleaned_data["hora"] = fecha_inicio.time()
            

        return cleaned_data



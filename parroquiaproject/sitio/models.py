from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Iglesia(models.Model):
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    #horarioMisa = models.ForeignKey('HorarioMisa', blank=True, null=True, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='iglesias/', blank=True, null=True)
    contacto_secretaria = models.CharField(max_length=20, blank=True, null=True)
    def __str__(self):
        return self.nombre

class HorarioMisa(models.Model):
    dia = models.CharField(max_length=20, null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)
    iglesia = models.ForeignKey(Iglesia, blank=True, null=True, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.dia} a las {self.hora}"

class Actividades(models.Model):
    categoria = models.CharField(max_length=50, blank=True, null=True)
    dia = models.CharField(max_length=20, null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)
    iglesia = models.ForeignKey(Iglesia, blank=True, null=True, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=50)
    texto = models.CharField(max_length=200)
    fechaVencimiento = models.DateTimeField()
    def __str__(self):
        return self.titulo

class UsuarioIglesias(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil_iglesias")

    iglesias_suscripto = models.ManyToManyField(Iglesia, blank=True, related_name="suscriptores")
    iglesias_admin = models.ManyToManyField(Iglesia, blank=True, related_name="administradores")

    def __str__(self):
        return self.usuario.username
    

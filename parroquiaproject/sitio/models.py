from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils.timezone import now

# Create your models here.
def fecha_vencimiento(dias):
    return now() + timedelta(days=dias) 

class Iglesia(models.Model):
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='iglesias/', blank=True, null=True)
    contacto_secretaria = models.CharField(max_length=20, blank=True, null=True)
    administrador = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="iglesias_admin")
    def __str__(self):
        return self.nombre
    
class Noticia(models.Model):
    titulo = models.CharField(max_length=40)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to="inicio/", blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    iglesiaAsociada = models.ForeignKey(Iglesia, blank=True, null=True, on_delete=models.CASCADE)
    creador = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.BooleanField(null=True, default=None)  # True = visible, False = archivada | estado=True/False/None
    fechaVencimiento = models.DateTimeField(null=True, default=fecha_vencimiento(30))
    fechaAceptacion = models.DateTimeField(null=True, default=fecha_vencimiento(7))
    def __str__(self):
        return self.titulo
 
class Actividades(models.Model):
    categoria = models.CharField(max_length=50, blank=True, null=True)
    dia = models.CharField(max_length=20, null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)
    iglesia = models.ForeignKey(Iglesia, blank=True, null=True, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=50)
    texto = models.CharField(max_length=200)
    fechaVencimiento = models.DateTimeField(null=True)
    def __str__(self):
        return self.titulo

class UsuarioIglesias(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil_iglesias")
    iglesias_suscripto = models.ManyToManyField(Iglesia, blank=True, related_name="suscriptores")
    iglesias_admin = models.ManyToManyField(Iglesia, blank=True, related_name="administradores")

    def __str__(self):  
        return self.usuario.username
    



    

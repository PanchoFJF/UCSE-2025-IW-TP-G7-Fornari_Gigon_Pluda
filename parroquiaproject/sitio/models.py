from django.db import models

# Create your models here.
class Categoria(models.Model):
    nombre = models.CharField(max_length=50)

class Iglesia(models.Model):
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    horarioMisa = models.ForeignKey('HorarioMisa', blank=True, null=True, on_delete=models.CASCADE)
    listaActividades = models.ManyToManyField('Actividades', blank=True)
    imagen_url = models.URLField(blank=True, null=True)

class HorarioMisa(models.Model):
    texto = models.CharField(max_length=1000)

class Actividades(models.Model):
    titulo = models.CharField(max_length=50)
    texto = models.CharField(max_length=200)
    fechaVencimiento = models.DateTimeField()

class Noticia(models.Model):
    titulo = models.CharField(max_length=50)
    texto = models.CharField(max_length=200)
    fecha = models.DateTimeField()
    archivada = models.BooleanField(default=False)
    categoria = models.ForeignKey(Categoria, blank=True, null=True, on_delete=models.CASCADE)

def __str__(self):
    return self.nombre
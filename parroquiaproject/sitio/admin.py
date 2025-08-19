from django.contrib import admin

# Register your models here.
from sitio.models import Iglesia, HorarioMisa, Actividades

@admin.register(Iglesia)
class AdminNoticia(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'direccion', 'horarioMisa')
    #list_filter = ('archivada', 'fecha', 'categoria')
    #search_fields = ('texto', )
    #date_hierarchy = 'fecha'

@admin.register(HorarioMisa)
class AdminCategoria(admin.ModelAdmin):
    list_display = ('id', 'texto')

@admin.register(Actividades)
class AdminActividades(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'texto', 'fechaVencimiento')
    #list_filter = ('archivada', 'fecha', 'categoria')
    #search_fields = ('texto', )
    #date_hierarchy = 'fecha'
from django.contrib import admin

# Register your models here.
from sitio.models import Iglesia, HorarioMisa

@admin.register(Iglesia)
class AdminNoticia(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'direccion', 'horarioMisa')
    #list_filter = ('archivada', 'fecha', 'categoria')
    #search_fields = ('texto', )
    #date_hierarchy = 'fecha'

@admin.register(HorarioMisa)
class AdminCategoria(admin.ModelAdmin):
    list_display = ('id', 'texto')
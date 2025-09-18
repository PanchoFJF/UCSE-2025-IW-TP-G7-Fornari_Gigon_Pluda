from django.contrib import admin

# Register your models here.
from sitio.models import Iglesia, Actividades, Noticia, UsuarioIglesias

@admin.register(Iglesia)
class AdminNoticia(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'direccion', 'administrador')
    #list_filter = ('archivada', 'fecha', 'categoria')
    #search_fields = ('texto', )
    #date_hierarchy = 'fecha'

@admin.register(Actividades)
class AdminActividades(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'texto', 'fechaVencimiento')
    #list_filter = ('archivada', 'fecha', 'categoria')
    #search_fields = ('texto', )
    #date_hierarchy = 'fecha'


@admin.register(UsuarioIglesias)
class UsuariosIglesiasAdmin(admin.ModelAdmin):
    list_display = ("usuario",)
    filter_horizontal = ("iglesias_suscripto", "iglesias_admin")

@admin.register(Noticia)
class AdminActividades(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'descripcion')
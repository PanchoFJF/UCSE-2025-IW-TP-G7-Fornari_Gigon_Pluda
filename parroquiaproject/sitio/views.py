from collections import defaultdict
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sitio.models import Actividades, HorarioMisa, Iglesia
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


#h = HorarioMisa(texto="Domingos a las 10:00 AM")
#h.save()


#i = Iglesia(nombre="Iglesia San Juan", direccion="Calle Falsa 123", horarioMisa=h)
#i.save()


# Create your views here.
ORDEN_DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']

def inicio(request):
    actividades = Actividades.objects.select_related('iglesia').all()

    # Crear un diccionario para agrupar por día
    actividades_por_dia = {dia: [] for dia in ORDEN_DIAS}
    for act in actividades:
        dia_lower = act.dia.lower()
        if dia_lower in actividades_por_dia:
            actividades_por_dia[dia_lower].append(act)

    # Ordenar cada lista por hora
    for dia in actividades_por_dia:
        actividades_por_dia[dia].sort(key=lambda x: x.hora)

    return render(request, 'inicio.html', {
        'actividades_por_dia': actividades_por_dia
    })
@login_required
@never_cache
def dashboard(request):
    return render(request, "dashboard.html")
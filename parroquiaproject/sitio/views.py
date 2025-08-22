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
ORDEN_DIAS = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']

"""def inicio(request):
    actividades = Actividades.objects.select_related('iglesia').all()

    # Crear un diccionario para agrupar por día
    actividades_por_dia = {dia: [] for dia in ORDEN_DIAS}
    for act in actividades:
        if act.dia in actividades_por_dia:
            actividades_por_dia[act.dia].append(act)

    # Ordenar cada lista por hora
    for dia in actividades_por_dia:
        actividades_por_dia[dia].sort(key=lambda x: x.hora)

    return render(request, 'inicio.html', {
        'actividades_por_dia': actividades_por_dia
    }) """

def iglesias(request):
    # Traemos todas las iglesias
    iglesias = Iglesia.objects.all()

    return render(request, "iglesias.html", {
        "iglesias": iglesias
    })

from collections import defaultdict
from django.shortcuts import render
from django.template.defaultfilters import capfirst
from .models import Actividades

def inicio(request):
    # Obtener parámetros de la URL
    dia = request.GET.get("dia")                # ejemplo: ?dia=Lunes
    categoria = request.GET.get("categoria")    # ejemplo: ?categoria=Catequesis
    parroquia_nombre = request.GET.get("parroquia")  # ejemplo: ?parroquia=San Juan

    # Obtener todas las actividades con JOIN a iglesia
    actividades = Actividades.objects.select_related("iglesia").all()

    # Aplicar filtros si vienen
    if dia:
        actividades = actividades.filter(dia__iexact=dia)
    if categoria:
        actividades = actividades.filter(categoria__iexact=categoria)
    if parroquia_nombre:
        actividades = actividades.filter(iglesia__nombre__iexact=parroquia_nombre)

    # Ordenar por hora
    actividades = actividades.order_by("hora")

    # Agrupar por día (primera letra mayúscula)
    actividades_por_dia = defaultdict(list)
    for act in actividades:
        dia_normalizado = capfirst(act.dia.strip().lower())
        actividades_por_dia[dia_normalizado].append(act)

    # Ordenar días
    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    actividades_por_dia_ordenadas = {
        dia: actividades_por_dia[dia] 
        for dia in orden_dias if dia in actividades_por_dia
    }

    return render(request, "inicio.html", {
        "actividades_por_dia": actividades_por_dia_ordenadas,
        "filtros": {"dia": dia, "categoria": categoria, "parroquia": parroquia_nombre},
    })


@login_required
@never_cache
def dashboard(request):
    return render(request, "dashboard.html")
    
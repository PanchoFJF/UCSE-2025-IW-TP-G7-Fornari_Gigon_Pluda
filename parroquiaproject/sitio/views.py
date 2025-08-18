from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sitio.models import HorarioMisa, Iglesia
from datetime import datetime
from django.contrib.auth.decorators import login_required


#h = HorarioMisa(texto="Domingos a las 10:00 AM")
#h.save()


#i = Iglesia(nombre="Iglesia San Juan", direccion="Calle Falsa 123", horarioMisa=h)
#i.save()

"""
# Create your views here.
def inicio(request):
    iglesias = Iglesia.objects.all()
    return render(request, 'inicio.html', {'lista_iglesias': iglesias})

@login_required
def privado(request):
    return render(request, 'publicacion.html')


@login_required
def dashboard(request):
    return render(request, "dashboard.html")
"""

def inicio(request):
    return render(request, "sitio/inicio.html")

@login_required
def dashboard(request):
    return render(request, "sitio/dashboard.html")
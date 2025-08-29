"""
URL configuration for parroquiaproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from sitio import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('accounts/', include('accounts.urls')),     # Rutas personalizadas de tu app accounts (ej. registro)
    path('iglesias/', views.iglesias, name='iglesias'),
    path('calendario/', views.calendario, name='calendario'),
    path('horarios/', views.horarios, name='horarios'),
    path('actividades/', views.actividades, name='actividades'),
    path("autorizacion/", views.autorizacion_view, name="autorizacion"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
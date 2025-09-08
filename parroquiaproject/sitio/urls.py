from django.urls import path
from . import views

app_name = 'sitio'  # namespace para usar en reverse()

urlpatterns = [
    # Página de inicio y dashboard
    path('', views.inicio, name='inicio'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Iglesias y calendario, etc
    path('iglesias/', views.iglesias, name='iglesias'),
    path('calendario/', views.calendario, name='calendario'),
    path('horarios/', views.horarios, name='horarios'),
    path('actividades/', views.actividades, name='actividades'),

    # URLs de configuración de usuario
    path('configuracion/', views.configuracion_view, name="configuracion"),
    path('configuracion/enviar/', views.configuracion_enviar_email, name='configuracion_reset_email'),
    path('configuracion/nuevo/<uidb64>/<token>/', views.configuracion_reset_email, name='config_reset_confirm'),
    path('configuracion/activar/<uidb64>/<token>/', views.configuracion_new_email, name='config_activate'),
]

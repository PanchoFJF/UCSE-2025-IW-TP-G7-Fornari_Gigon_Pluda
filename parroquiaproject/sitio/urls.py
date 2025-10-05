from django.urls import path
from . import views
#from accounts.views import delete_users_view

app_name = 'sitio'  # namespace para usar en reverse()

urlpatterns = [
    # Página de inicio y dashboard
    path('', views.inicio, name='inicio'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("autorizacion/", views.autorizacion_view, name="autorizacion"),
    path("suscribirse/<int:iglesia_id>/", views.suscribirse_iglesia, name="suscribirse_iglesia"),
    path('iglesia/<int:iglesia_id>/desuscribirse/', views.desuscribirse_iglesia, name='desuscribirse_iglesia'),

    # Iglesias y calendario, etc
    path('iglesias/', views.iglesias, name='iglesias'),
    path('calendario/', views.calendario, name='calendario'),
    path('actividades/', views.actividades, name='actividades'),

    # URLs de configuración de usuario
    path('configuracion/', views.configuracion_view, name="configuracion"),
    path('configuracion/enviar/', views.configuracion_enviar_email, name='configuracion_reset_email'),
    #path('configuracion/nuevo/<uidb64>/<token>/', views.configuracion_reset_email, name='config_reset_confirm'),
    #path('configuracion/activar/<uidb64>/<token>/', views.configuracion_new_email, name='config_activate'),
    path("configuracion/delete/send/", views.config_delete_send, name="config_delete_send"),
    #path("configuracion/delete/confirm/<uidb64>/<token>/", views.config_delete_confirm, name="config_delete_confirm"),
    path("configuracion/delete/final/", views.config_delete_final, name="config_delete_final"),

    # Elimnar usuarios no verificados
    #path("delete_users/", delete_users_view, name="delete_users"),

    # Revisión de Post
    path('check_post/', views.check_post_view, name="check_post"),

    path('rebuild_index/', views.rebuild_index),
    path('actividad/ajax/<int:pk>/', views.actividad_detalle_ajax, name='actividad_ajax'),
]

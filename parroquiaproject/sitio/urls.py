from django.urls import path
from parroquiaproject.sitio import admin
from sitio import views

"""
urlpatterns = [
    path('admin/', admin.site.urls),  # 👉 URL del panel de administración
    path('inicio/', views.inicio),    # Tu vista personalizada
]
"""

urlpatterns = [
    path("", views.inicio, name="inicio"),  # público
    path("dashboard/", views.dashboard, name="dashboard"),  # privado
]
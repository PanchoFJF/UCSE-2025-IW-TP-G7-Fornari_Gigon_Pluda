from django.urls import path
from parroquiaproject.sitio import admin
from sitio import views

urlpatterns = [
    path('admin/', admin.site.urls),  # 👉 URL del panel de administración
    path("", views.inicio, name="inicio"),    # Tu vista personalizada
    path("dashboard/", views.dashboard, name="dashboard"),  # privado
]
from django.urls import path
from parroquiaproject.sitio import admin
from sitio import views


urlpatterns = [
    path('admin/', admin.site.urls),  # 👉 URL del panel de administración
    path('inicio/', views.inicio),    # Tu vista personalizada
]
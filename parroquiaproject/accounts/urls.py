from django.urls import path
from sitio import views as sitio_views  # vistas de sitio
from .views import CustomLoginView, CustomLogoutView, SignUpView, activate  # vistas de accounts

urlpatterns = [
    # Página de inicio (del sitio)
    path("", sitio_views.inicio, name="inicio"),

    # Registro
    path("signup/", SignUpView.as_view(), name="signup"),
    path("activate/<uidb64>/<token>/", activate, name="activate"),

    # Autenticación
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(next_page="inicio"), name="logout"),
]
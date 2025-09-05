from django.urls import path
from django.contrib.auth import views as auth_views
from sitio import views as sitio_views  # vistas de sitio
from .views import CustomLoginView, CustomLogoutView, SignUpView, activate, password_reset_custom, password_reset_confirm_custom  # vistas de accounts
from .forms import CustomPasswordResetForm

urlpatterns = [
    # Página de inicio (del sitio)
    path("", sitio_views.inicio, name="inicio"),

    # Registro
    path("signup/", SignUpView.as_view(), name="signup"),
    path("activate/<uidb64>/<token>/", activate, name="activate"),

    # Autenticación
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(next_page="inicio"), name="logout"),

    # Recuperar contraseña
    path("password_reset_custom/", password_reset_custom, name="password_reset_custom"),
    path("reset/<uidb64>/<token>/", password_reset_confirm_custom, name="password_reset_confirm_custom"),
]
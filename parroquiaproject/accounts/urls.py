from django.urls import path
from django.contrib.auth import views as auth_views
from sitio import views
from .views import CustomLoginView, CustomLogoutView, SignUpView

urlpatterns = [
    path("", views.inicio, name="inicio"),

    # Registro
    path("signup/", SignUpView.as_view(), name="signup"),

    # Autenticación
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(next_page="inicio"), name="logout"),
]
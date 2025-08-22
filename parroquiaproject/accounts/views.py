from django.shortcuts import render

# Create your views here.
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

# from django.core.mail import send_mail


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")  # después de registrarse va al login
    template_name = "registration/signup.html"

    def form_valid(self, form):
        messages.success(self.request, "¡Tu cuenta fue creada con éxito!")
        return super().form_valid(form)
    
class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def get_success_url(self):
        username = self.request.user.username  # <- acá obtenemos el username
        messages.success(self.request, f"¡Bienvenido de nuevo {username}!")
        return super().get_success_url()
    
class CustomLogoutView(LogoutView):
    next_page = "inicio"

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Sesión cerrada correctamente.")
        return super().dispatch(request, *args, **kwargs)
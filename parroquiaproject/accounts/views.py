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
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings

from .forms import SignUpForm

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
    
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # 👈 queda inactivo hasta confirmar
            user.save()

            # datos para el mail
            current_site = get_current_site(request)
            subject = "Activa tu cuenta"
            message = render_to_string("registration/activation_email.html", {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            return render(request, "registration/activation_sent.html")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})

# views.py
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, "registration/activation_success.html")
    else:
        return render(request, "registration/activation_invalid.html")
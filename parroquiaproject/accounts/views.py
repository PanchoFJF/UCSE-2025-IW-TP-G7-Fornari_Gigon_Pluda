# accounts/views.py
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from .forms import SignUpForm

User = get_user_model()

# --- Registro con confirmación por email ---
class SignUpView(generic.CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")  # Vista que muestra mensaje "revisa tu correo"

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # usuario inactivo hasta confirmar
        user.save()

        # enviar email de activación
        current_site = get_current_site(self.request)
        mail_subject = "Activa tu cuenta"
        message = render_to_string("registration/activation_email.html", {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        })

        email = EmailMessage(mail_subject, message, to=[user.email])
        email.content_subtype = "html"
        email.send()

        messages.success(self.request, "¡Cuenta creada! Revisa tu correo para activarla.")
        return super().form_valid(form)

# --- Vista de mensaje "email enviado" ---
class EmailVerificationSentView(generic.TemplateView):
    template_name = "registration/email_verification_sent.html"

# --- Login y Logout personalizados ---
class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def get_success_url(self):
        username = self.request.user.username
        messages.success(self.request, f"¡Bienvenido de nuevo {username}!")
        return super().get_success_url()

class CustomLogoutView(LogoutView):
    next_page = "inicio"

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Sesión cerrada correctamente.")
        return super().dispatch(request, *args, **kwargs)

# --- Activación de usuario ---
def activate(request, uidb64, token):
    try:
        uid = int(force_str(urlsafe_base64_decode(uidb64)))  # ⚡ corregido: convertir a entero
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Tu cuenta fue activada correctamente. Ya podés iniciar sesión.")
        return redirect("login")
    else:
        messages.error(request, "El enlace de activación no es válido o expiró.")
        return redirect("signup")
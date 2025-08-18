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
# from django.core.mail import send_mail

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")  # después de registrarse va al login
    template_name = "registration/signup.html"

"""
    def form_valid(self, form):
        user = form.save(commit=False)
        # Usuario inactivo hasta que confirme el email
        user.is_active = False
        user.save()

        # Generar token y link de activación
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activate_url = self.request.build_absolute_uri(
            reverse("accounts:activate", args=[uidb64, token])
        )

        # Enviar email
        send_mail(
            subject="Activá tu cuenta",
            message=f"Hola {user.username}, activá tu cuenta con este enlace:\n{activate_url}",
            from_email=None,  # usa DEFAULT_FROM_EMAIL
            recipient_list=[user.email],
        )

        return render(self.request, "registration/activation_sent.html", {"email": user.email})

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        # Opcional: loguearlo automáticamente
        # auth_login(request, user)
        return render(request, "registration/activation_complete.html", {"user": user})
    else:
        return render(request, "registration/activation_invalid.html", status=400)
"""
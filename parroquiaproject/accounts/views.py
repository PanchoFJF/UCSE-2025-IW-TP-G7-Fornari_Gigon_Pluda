from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from .forms import SignUpForm, CustomPasswordResetForm
from django.contrib.auth.password_validation import validate_password
from django.utils.timezone import now
from django.contrib.auth.decorators import user_passes_test
from accounts.management.commands.delete_invalid_users import delete_invalid_users_and_rejected_posts
import smtplib
from django.conf import settings
from socket import timeout
User = get_user_model()

# --- Eliminar usuarios inválidos ---
@user_passes_test(lambda u: u.is_superuser)  # solo superusuarios
def delete_users_view(request):
    user_count, post_count = delete_invalid_users_and_rejected_posts()
    messages.success(request, f"Se eliminaron {user_count} usuarios no verificados y {post_count} publicaciones rechazadas.")
    return redirect("sitio:dashboard")

# --- Registro con confirmación por email ---
class SignUpView(generic.CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")

        # Chequear si ya existe otro usuario (activo o inactivo) con ese correo
        if User.objects.filter(email=email).exists():
            form.add_error("email", "Ya existe un usuario registrado con ese correo.")
            return self.form_invalid(form)  # <-- importante, no redirect

        # Crear usuario inactivo
        user = form.save(commit=False)
        user.is_active = True
        user.save()

        # Generar uid y token
        #uid = urlsafe_base64_encode(force_bytes(user.pk))
        #token = default_token_generator.make_token(user)

        # Construir link de activación
       #path = reverse("activate", kwargs={"uidb64": uid, "token": token})
       # activation_link = self.request.build_absolute_uri(path)

        # Enviar email
        #mail_subject = "Activa tu cuenta"
        #message = render_to_string(
        #    "registration/activation_email.html",
        #    {"user": user, "activation_link": activation_link},
        #)
        #email_message = EmailMessage(mail_subject, message, to=[user.email])
        #email_message.content_subtype = "html"

        # --- CÓDIGO DE PRUEBA TEMPORAL ---
        #try:
        #    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10) as server:
        #        server.starttls()
        #        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        #    print("¡La conexión al servidor SMTP se ha establecido correctamente!")
        #except timeout:
        #    print("¡Error! La conexión ha fallado por tiempo de espera. La red está bloqueada.")
        #except Exception as e:
        #    print(f"¡Error! No se pudo conectar al servidor SMTP. Error: {e}")
        # --- FIN DEL CÓDIGO DE PRUEBA ---
        #email_message.send()

        messages.success(self.request, "¡Cuenta creada! ")
        return redirect(self.success_url)

# --- Activación de usuario ---
def activate(request, uidb64, token):
    # 1. Intento de decodificar y cargar usuario
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None
        uid = None

    # 2. Compruebo el token y almaceno resultado
    valid = False
    if user is not None:
        valid = default_token_generator.check_token(user, token)
        elapsed_seconds = (now() - user.date_joined).total_seconds()
        if elapsed_seconds > 15 * 60 and not user.is_active:
            user.delete()
            messages.error(request, "El enlace de activación expiró. Registrate de nuevo.")
            return redirect("signup")

    # 3. Depuración antes del if
    print(
        "DEBUG activate:",
        "uidb64=", uidb64,
        "-> uid=", uid,
        "user_exists=", bool(user),
        "token_recibido=", token,
        "token_válido?=", valid,
    )

    # 4. Lógica de activación
    if user is not None and valid:
        user.is_active = True
        user.save()
        messages.success(request, "Tu cuenta fue activada correctamente. Ya podés iniciar sesión.")
        return redirect("login")
    else:
        messages.error(request, "El enlace de activación no es válido o expiró.")
        return redirect("signup")

# --- Olvidé mi contraseña (pide correo) ---
def password_reset_custom(request):
    if request.method == "POST":
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "El correo no está asociado a ninguna cuenta.")
                return redirect("password_reset_custom")

            # Generar uid y token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Guardar timestamp en la sesión
            request.session[f"password_reset_{user.pk}_sent_at"] = now().timestamp()

            # Construir link absoluto
            reset_link = request.build_absolute_uri(
                reverse("password_reset_confirm_custom", kwargs={"uidb64": uid, "token": token})
            )

            # Enviar email
            message = render_to_string("registration/password_reset_email_custom.html", {
                "user": user,
                "reset_link": reset_link,
            })
            email_message = EmailMessage(
                subject="Restablecer tu contraseña",
                body=message,
                to=[user.email],
            )
            email_message.content_subtype = "html"
            email_message.send()

            messages.success(request, "Te enviamos un correo con el enlace para restablecer tu contraseña.")
            return redirect("password_reset_custom")
    else:
        form = CustomPasswordResetForm()

    return render(request, "registration/password_reset_custom.html", {"form": form})


# --- Confirmar nueva contraseña ---
def password_reset_confirm_custom(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "El enlace no es válido o expiró.")
        return redirect("password_reset_custom")

    # --- Validación de timeout: 60 segundos ---
    sent_at_timestamp = request.session.get(f"password_reset_{user.pk}_sent_at")
    if not sent_at_timestamp:
        messages.error(request, "No se puede validar el enlace.")
        return redirect("password_reset_custom")

    elapsed_seconds = now().timestamp() - sent_at_timestamp
    if elapsed_seconds > 60:
        messages.error(request, "El enlace expiró después de 60 segundos.")
        return redirect("password_reset_custom")
    # -----------------------------------------

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not password1 or not password2:
            messages.error(request, "Por favor completa ambos campos de contraseña.")
        elif password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
        else:
            # Validaciones de seguridad como en el registro
            try:
                validate_password(password1, user=user)
            except ValidationError:
                messages.error(request, "La contraseña no cumple con los requisitos de seguridad.")
                return render(request, "registration/password_reset_confirm_custom.html", {"user": user})

            # Guardar nueva contraseña y limpiar timestamp
            user.set_password(password1)
            user.save()
            update_session_auth_hash(request, user)
            request.session.pop(f"password_reset_{user.pk}_sent_at", None)
            messages.success(request, "Contraseña cambiada correctamente.")
            return redirect("login")

    return render(request, "registration/password_reset_confirm_custom.html", {"user": user})

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

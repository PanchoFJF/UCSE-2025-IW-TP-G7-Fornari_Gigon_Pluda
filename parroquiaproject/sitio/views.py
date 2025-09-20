from collections import defaultdict
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from sitio.models import Actividades, Iglesia
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404
from .models import Iglesia
from .forms import AutorizacionForm, IglesiaForm, EmailChangeForm
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.db.models import Q
from django.contrib.auth import logout

# Create your views here.
ORDEN_DIAS = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']

from django.contrib.auth.tokens import default_token_generator
from collections import defaultdict
from django.shortcuts import render
from django.template.defaultfilters import capfirst
from .models import Actividades, UsuarioIglesias
from .models import Noticia
from django.core.mail import EmailMessage, EmailMultiAlternatives
from .forms import NoticiaForm, NoticiaEditForm
from django.http import JsonResponse
from django.conf import settings

def inicio(request):    
    noticias = Noticia.objects.filter(estado="aprobada").order_by("-fecha")  # timeline descendente
    form = NoticiaForm()
     
    if request.user.is_authenticated:
        perfil = getattr(request.user, "perfil_iglesias", None)

        for noticia in noticias:
            noticia.puede_editar = False

            # creador
            if noticia.creador == request.user:
                noticia.puede_editar = True
            # admin principal de la iglesia
            elif noticia.iglesiaAsociada and noticia.iglesiaAsociada.administrador == request.user:
                noticia.puede_editar = True
            # admin delegado desde UsuarioIglesias
            elif perfil and noticia.iglesiaAsociada:
                if perfil.iglesias_admin.filter(pk=noticia.iglesiaAsociada.pk).exists():
                    noticia.puede_editar = True

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "crear":
            form = NoticiaForm(request.POST, request.FILES)
            if form.is_valid():
                noticia = form.save(commit=False)
                noticia.creador = request.user
                noticia.save()   

                # Notificar por correo a los suscriptores
                nueva_publicacion_email(noticia, request)

                messages.info(request, "Tu publicación ha sido enviada a revisión.")
                return redirect("inicio")

        elif action == "editar":
            noticia = get_object_or_404(Noticia, pk=request.POST.get("noticia_id"))
            form = NoticiaEditForm(request.POST, request.FILES, instance=noticia)
            if form.is_valid():
                form.save()
                return redirect("inicio")

        elif action == "eliminar":
            noticia = get_object_or_404(Noticia, pk=request.POST.get("noticia_id"))
            noticia.delete()
            return redirect("inicio")

    return render(request, "inicio.html", {"noticias": noticias, "form": form})

def iglesias(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # Crear nueva iglesia
        if action == "crear":
            form = IglesiaForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect("sitio:iglesias")

        # Editar iglesia
        elif action == "editar":
            iglesia_id = request.POST.get("iglesia_id")
            iglesia = get_object_or_404(Iglesia, id=iglesia_id)
            iglesia.nombre = request.POST.get("nombre")
            iglesia.direccion = request.POST.get("direccion")
            iglesia.contacto_secretaria = request.POST.get("contacto_secretaria")
            if request.FILES.get("imagen"):
                iglesia.imagen = request.FILES["imagen"]
            iglesia.save()
            return redirect("sitio:iglesias")

        # Eliminar iglesia
        elif action == "eliminar":
            iglesia_id = request.POST.get("iglesia_id")
            iglesia = get_object_or_404(Iglesia, id=iglesia_id)
            iglesia.delete()
            return redirect("sitio:iglesias")

    else:
        form = IglesiaForm()

    iglesias = Iglesia.objects.all()
    return render(request, "iglesias.html", {
        "iglesias": iglesias,
        "form": form
    })

def calendario(request):
    return render(request, "calendario.html", {
    })

def horarios(request):
    dia = request.GET.get("dia")
    categoria = request.GET.get("categoria")
    parroquia_nombre = request.GET.get("parroquia")

    actividades = Actividades.objects.select_related("iglesia").all()

    if dia:
        actividades = actividades.filter(dia__iexact=dia)
    if categoria:
        actividades = actividades.filter(categoria__iexact=categoria)
    if parroquia_nombre:
        actividades = actividades.filter(iglesia__nombre__iexact=parroquia_nombre)

    actividades = actividades.order_by("hora")

    actividades_por_dia = defaultdict(list)
    for act in actividades:
        dia_normalizado = capfirst(act.dia.strip().lower())
        actividades_por_dia[dia_normalizado].append(act)

    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    actividades_por_dia_ordenadas = {dia: actividades_por_dia[dia] for dia in orden_dias if dia in actividades_por_dia}

    # Obtener todas las categorías y parroquias para llenar los selects
    categorias = Actividades.objects.values_list("categoria", flat=True).distinct()
    parroquias = Iglesia.objects.all()

    return render(request, "horarios.html", {
        "actividades_por_dia": actividades_por_dia_ordenadas,
        "filtros": {"dia": dia, "categoria": categoria, "parroquia": parroquia_nombre},
        "categorias": categorias,
        "parroquias": parroquias,
    })

def actividades(request):
    actividades = Actividades.objects.all()

    # Filtros dinámicos
    categorias = Actividades.objects.values_list("categoria", flat=True).distinct()
    parroquias = Iglesia.objects.all()

    return render(request, "actividades.html", {
        "actividades": actividades,
        "categorias": categorias,
        "parroquias": parroquias,
    })

@login_required
@never_cache
def dashboard(request):
    try:
        usuario_iglesias = UsuarioIglesias.objects.get(usuario=request.user)
        iglesias = usuario_iglesias.iglesias_suscripto.all()
        permisos_iglesias = usuario_iglesias.iglesias_admin.all()
        actividades = Actividades.objects.filter(iglesia__in=iglesias)
    except UsuarioIglesias.DoesNotExist:
        iglesias = []
        permisos_iglesias = []
        actividades = []

    # Iglesias donde el usuario es administrador principal (FK en Iglesia)
    admin_iglesias = Iglesia.objects.filter(administrador=request.user)

    # Solo se puede autorizar si es admin principal de al menos una iglesia
    can_authorize = admin_iglesias.exists()

    context = {
        "iglesias": iglesias,
        "permisos_iglesias": permisos_iglesias,
        "admin_iglesias": admin_iglesias,
        "actividades": actividades,
        "can_authorize": can_authorize,
    }
    return render(request, "dashboard.html", context)

@login_required
def configuracion_view(request):
    if request.method == "POST" and "cambiar_username" in request.POST:
        nuevo_username = request.POST.get("username").strip()

        # Validar que no exista otro usuario con ese username
        if User.objects.filter(Q(username=nuevo_username) & ~Q(pk=request.user.pk)).exists():
            messages.error(request, "Ese nombre de usuario ya está en uso.")
        elif not nuevo_username:
            messages.error(request, "El nombre de usuario no puede estar vacío.")
        else:
            request.user.username = nuevo_username
            request.user.save()
            messages.success(request, "Tu nombre de usuario se actualizó correctamente.")
            return redirect("sitio:configuracion")

    return render(request, "configuracion.html")

# CAMBIAR CORREO
# --- Enviar enlace al correo actual ---
@login_required
def configuracion_reset(request):
    user = request.user

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    reset_link = request.build_absolute_uri(
        reverse("sitio:config_reset_confirm", kwargs={"uidb64": uid, "token": token})
    )

    message = render_to_string("configuracion_reset_email.html", {
        "user": user,
        "reset_link": reset_link,
    })

    email_message = EmailMessage(
        subject="Cambio de correo en CatholicRafaela",
        body=message,
        to=[user.email],
    )
    email_message.content_subtype = "html"
    email_message.send()

    messages.success(request, "Te enviamos un enlace a tu correo actual para continuar con el cambio.")
    return redirect("sitio:configuracion")


# --- Enviar enlace de confirmación al nuevo correo ---
@login_required
def configuracion_enviar_email(request):
    user = request.user
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # Aquí usamos el name correcto: config_reset_confirm
    reset_link = request.build_absolute_uri(
        reverse("sitio:config_reset_confirm", kwargs={"uidb64": uid, "token": token})
    )

    message = render_to_string("configuracion_reset_email.html", {
        "user": user,
        "reset_link": reset_link,
    })

    email_message = EmailMessage(
        subject="Cambio de correo",
        body=message,
        to=[user.email],
    )
    email_message.content_subtype = "html"
    email_message.send()

    # Guardar timestamp de envío en sesión
    request.session[f"email_reset_{user.pk}_sent_at"] = now().timestamp()

    messages.success(request, "Te enviamos un enlace a tu correo actual para continuar con el cambio.")
    return redirect("sitio:configuracion")


# --- Página donde se ingresa el nuevo correo ---
@login_required
def configuracion_reset_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "El enlace no es válido o expiró.")
        return redirect("sitio:configuracion")

    # Validación de timeout
    sent_at_timestamp = request.session.get(f"email_reset_{user.pk}_sent_at")
    if not sent_at_timestamp or (now().timestamp() - sent_at_timestamp > 300):
        messages.error(request, "El enlace expiró después de 5 minutos.")
        return redirect("sitio:configuracion")

    if request.method == "POST":
        form = EmailChangeForm(request.POST, user=request.user)
        if form.is_valid():
            nuevo_email = form.cleaned_data["email"]

            request.session["nuevo_email"] = nuevo_email
            request.session["uidb64"] = uidb64
            request.session["token"] = token

            # Enviar email de confirmación al nuevo correo
            activation_link = request.build_absolute_uri(
                reverse("sitio:config_activate", kwargs={"uidb64": uidb64, "token": token})
            )

            email_message = EmailMessage(
                subject="Confirma tu nuevo correo en CatholicRafaela",
                body=render_to_string("configuracion_new_email.html", {
                    "user": user,
                    "activation_link": activation_link,
                }),
                to=[nuevo_email],
            )
            email_message.content_subtype = "html"
            email_message.send()

            request.session[f"email_new_reset_{user.pk}_sent_at"] = now().timestamp()
            messages.success(request, "Te enviamos un enlace al nuevo correo para validarlo.")
            return redirect("sitio:configuracion")
    else:
        form = EmailChangeForm()

    return render(request, "configuracion_reset.html", {"form": form})


# --- Confirmar el nuevo correo ---
@login_required
def configuracion_new_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    sent_at_timestamp = request.session.get(f"email_new_reset_{user.pk}_sent_at")
    if not sent_at_timestamp or (now().timestamp() - sent_at_timestamp > 300):
        messages.error(request, "El enlace para confirmar tu nuevo correo expiró después de 5 minutos.")
        return redirect("sitio:configuracion")

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "El enlace de activación no es válido o expiró.")
        return redirect("sitio:configuracion")

    nuevo_email = request.session.get("nuevo_email")
    if not nuevo_email:
        messages.error(request, "No se pudo recuperar el nuevo correo.")
        return redirect("sitio:configuracion")

    # Guardar nuevo correo
    user.email = nuevo_email
    user.save()

    # Limpiar sesión
    for key in [f"email_reset_{user.pk}_sent_at", "nuevo_email", "uidb64", "token"]:
        request.session.pop(key, None)

    messages.success(request, "Se ha cambiado el correo exitosamente.")
    return redirect("sitio:dashboard")

# ELIMINAR CUENTA
@login_required
def config_delete_send(request):
    user = request.user
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    delete_link = request.build_absolute_uri(
        reverse("sitio:config_delete_confirm", kwargs={"uidb64": uid, "token": token})
    )

    message = render_to_string("configuracion_delete_email.html", {
        "user": user,
        "delete_link": delete_link,
    })

    email_message = EmailMessage(
        subject="Confirmación de eliminación de cuenta",
        body=message,
        to=[user.email],
    )
    email_message.content_subtype = "html"
    email_message.send()

    request.session[f"delete_request_{user.pk}_sent_at"] = now().timestamp()

    messages.success(request, "Te enviamos un enlace a tu correo (válido por 5 minutos).")
    return redirect("sitio:configuracion")


@login_required
def config_delete_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "El enlace no es válido o expiró.")
        return redirect("sitio:configuracion")

    sent_at = request.session.get(f"delete_request_{user.pk}_sent_at")
    if not sent_at or (now().timestamp() - sent_at > 300):  # 5 minutos
        messages.error(request, "El enlace expiró después de 5 minutos.")
        return redirect("sitio:configuracion")

    # Ahora Django encontrará: sitio/templates/configuracion_delete_confirm.html
    return render(request, "configuracion_delete_confirm.html", {"user": user})


@login_required
def config_delete_final(request):
    user = request.user
    user.delete()
    messages.success(request, "Tu cuenta fue eliminada permanentemente.")
    return redirect("inicio")

@login_required
def autorizacion_view(request):
    if request.method == "POST":
        form = AutorizacionForm(request.POST, user=request.user)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            iglesia = form.cleaned_data['iglesia_id']

            try:
                target_user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                messages.error(request, "No existe ningún usuario con ese correo.")
                return redirect("sitio:autorizacion")

            usuario_iglesias, _ = UsuarioIglesias.objects.get_or_create(usuario=target_user)

            if "add" in request.POST:
                if iglesia in usuario_iglesias.iglesias_admin.all():
                    messages.info(request, f"{target_user.email} ya tiene permiso de edición en {iglesia.nombre}.")
                else:
                    usuario_iglesias.iglesias_admin.add(iglesia)
                    messages.success(request, f"{target_user.email} ahora tiene permisos para modificar {iglesia.nombre}.")
            elif "remove" in request.POST:
                if iglesia in usuario_iglesias.iglesias_admin.all():
                    usuario_iglesias.iglesias_admin.remove(iglesia)
                    messages.success(request, f"Se removieron los permisos de edición de {target_user.email} sobre {iglesia.nombre}.")
                else:
                    messages.info(request, f"{target_user.email} no tenía permisos de edición sobre {iglesia.nombre}.")

            return redirect("sitio:autorizacion")
    else:
        form = AutorizacionForm(user=request.user)

    # Iglesias donde el usuario actual es administrador principal
    admin_iglesias = Iglesia.objects.filter(administrador=request.user)

    # Usuarios que tienen permisos de edición en esas iglesias
    usuarios_con_permisos = UsuarioIglesias.objects.filter(
        iglesias_admin__in=admin_iglesias
    ).distinct().order_by("usuario__email")

    context = {
        "form": form,
        "admin_iglesias": admin_iglesias,
        "usuarios_con_permisos": usuarios_con_permisos,
    }
    return render(request, "autorizacion.html", context)


@login_required
def suscribirse_iglesia(request, iglesia_id):
    iglesia = get_object_or_404(Iglesia, id=iglesia_id)
    user = request.user

    # Buscamos o creamos el registro de UsuarioIglesias para este user
    usuario_iglesias, _ = UsuarioIglesias.objects.get_or_create(usuario=user)

    # Agregamos la iglesia si no estaba ya suscripto
    if iglesia not in usuario_iglesias.iglesias_suscripto.all():
        usuario_iglesias.iglesias_suscripto.add(iglesia)
        messages.success(request, f"Te suscribiste a {iglesia.nombre}.")
    else:
        messages.info(request, f"Ya estabas suscripto a {iglesia.nombre}.")

    # Redirige de vuelta (ajustá la URL al nombre de tu vista de lista de iglesias)
    return redirect("/iglesias/")

@login_required
def desuscribirse_iglesia(request, iglesia_id):
    try:
        iglesia = Iglesia.objects.get(id=iglesia_id)
        request.user.perfil_iglesias.iglesias_suscripto.remove(iglesia)
        messages.success(request, f"Te has desuscripto de {iglesia.nombre}.")
    except Iglesia.DoesNotExist:
        messages.error(request, "La iglesia no existe.")
    return redirect('sitio:dashboard')

@login_required
def check_post_view(request):
    perfil = getattr(request.user, "perfil_iglesias", None)

    mis_publicaciones = Noticia.objects.filter(creador=request.user)

    pendientes = []
    es_moderador = False

    if perfil and perfil.iglesias_admin.exists():
        es_moderador = True
        pendientes = Noticia.objects.filter(
            iglesiaAsociada__in=perfil.iglesias_admin.all(),
            estado="pendiente"
        ).order_by("-fecha")

    return render(request, "check_post.html", {
        "mis_publicaciones": mis_publicaciones,
        "pendientes": pendientes,
        "es_moderador": es_moderador,
    })

def nueva_publicacion_email(noticia, request):
    iglesia = noticia.iglesiaAsociada
    if not iglesia:
        return

    # usuarios suscriptos
    suscriptores = iglesia.suscriptores.all().prefetch_related("usuario")
    emails = [perfil.usuario.email for perfil in suscriptores if perfil.usuario.email]

    if not emails:
        return

    contexto = {
        "iglesia": iglesia,
        "noticia": noticia,
        "inicio_link": request.build_absolute_uri("/")  # link a inicio
    }

    subject = f"📢 Nueva publicación de {iglesia.nombre}"
    html_content = render_to_string("publicacion_email.html", contexto)

    msg = EmailMultiAlternatives(subject, "", settings.DEFAULT_FROM_EMAIL, emails)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
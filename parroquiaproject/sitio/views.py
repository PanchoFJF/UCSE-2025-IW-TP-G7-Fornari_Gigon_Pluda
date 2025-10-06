from collections import defaultdict
from django.utils import timezone
from django.contrib import messages
from sitio.models import Actividades, Iglesia
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404
from .models import Iglesia, Noticia, Actividades, UsuarioIglesias
from .forms import AutorizacionForm, IglesiaForm, EmailChangeForm, ActividadesForm
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.db.models import Q
from django.contrib.auth import logout
from django.contrib.auth.tokens import default_token_generator
from collections import defaultdict
from django.template.defaultfilters import capfirst
from django.core.mail import EmailMessage, EmailMultiAlternatives
from .forms import NoticiaForm, NoticiaEditForm
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.http import JsonResponse, Http404
from .models import Actividades
# Create your views here.
ORDEN_DIAS = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']

def inicio(request):
    # Solo aprobadas
    noticias = Noticia.objects.filter(estado="aprobado").order_by("-fecha")
    form = NoticiaForm()

    if request.user.is_authenticated:
        perfil = getattr(request.user, "perfil_iglesias", None)

        for noticia in noticias:
            noticia.puede_editar = False
            if noticia.creador == request.user:
                noticia.puede_editar = True
            elif noticia.iglesiaAsociada and noticia.iglesiaAsociada.administrador == request.user:
                noticia.puede_editar = True
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
                noticia.estado = "pendiente"
                noticia.save()
                messages.info(request, "Tu publicación ha sido enviada a revisión.")
                return redirect("inicio")

        elif action == "editar":
            noticia = get_object_or_404(Noticia, pk=request.POST.get("noticia_id"))
            noticia.titulo_editado = request.POST.get("titulo", noticia.titulo)
            noticia.descripcion_editada = request.POST.get("descripcion", noticia.descripcion)
            if "imagen" in request.FILES:
                noticia.imagen_editada = request.FILES["imagen"]
            # Resetear estado de edición
            noticia.en_revision_edicion = True
            noticia.estado_edicion = "pendiente"   # siempre vuelve a pendiente
            noticia.motivo_rechazo_edicion = None  # limpiar motivo anterior si lo había
            noticia.fecha_revision_edicion = None  # se seteará cuando el moderador la revise

            noticia.editor = request.user

            noticia.save()
            messages.info(request, "La edición fue enviada a revisión.")
            return redirect("inicio")

        elif action == "eliminar":
            noticia = get_object_or_404(Noticia, pk=request.POST.get("noticia_id"))
            noticia.delete()
            messages.success(request, "La publicación se eliminó correctamente.")
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

def actividades(request):
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    # Crear actividad (desde modal)
    if request.method == "POST":
        form = ActividadesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("sitio:actividades")  # recargar lista
    else:
        form = ActividadesForm()

    # Filtros dinámicos
    dia = request.GET.get("dia")
    categoria = request.GET.get("categoria")
    parroquia_nombre = request.GET.get("parroquia")
    vencimiento = request.GET.get("vencimiento")

    actividades = Actividades.objects.select_related("iglesia").all()

    if dia:
        actividades = actividades.filter(dia__iexact=dia)
    if categoria:
        actividades = actividades.filter(categoria__iexact=categoria)
    if parroquia_nombre:
        actividades = actividades.filter(iglesia__nombre__iexact=parroquia_nombre)
    if vencimiento == "con":
        actividades = actividades.exclude(fechaVencimiento__isnull=True)
    elif vencimiento == "sin":
        actividades = actividades.filter(fechaVencimiento__isnull=True)

    actividades = actividades.order_by("hora")

    # Agrupar por día
    actividades_por_dia = defaultdict(list)
    for act in actividades:
        dia_normalizado = capfirst(act.dia.strip().lower())
        actividades_por_dia[dia_normalizado].append(act)

    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    actividades_por_dia_ordenadas = {dia: actividades_por_dia[dia] for dia in orden_dias if dia in actividades_por_dia}

    # Para selects
    categorias = Actividades.objects.values_list("categoria", flat=True).distinct()
    parroquias = Iglesia.objects.all()

    return render(request, "actividades.html", {
        "form": form,
        "actividades": actividades,   
        "dias": dias,                
        "categorias": categorias,
        "parroquias": parroquias,
        "filtros": {"dia": dia, "categoria": categoria, "parroquia": parroquia_nombre, "vencimiento": vencimiento}
    })

def actividad_detalle_ajax(request, pk):
    try:
        actividad = Actividades.objects.get(pk=pk)
        data = {
            'titulo': actividad.titulo,
            'categoria': actividad.categoria,
            'dia': actividad.dia,
            'hora': actividad.hora.strftime('%H:%M') if actividad.hora else '',
            'texto': actividad.texto,
            'iglesia': actividad.iglesia.nombre if actividad.iglesia else '',
            'fechaVencimiento': actividad.fechaVencimiento.strftime('%Y-%m-%d %H:%M') if actividad.fechaVencimiento else '',
        }
    except Actividades.DoesNotExist:
        data = {'error': 'Actividad no encontrada'}
    return JsonResponse(data)

#def actividad_detalle(request, actividad_id):
    actividad = get_object_or_404(Actividades, id=actividad_id)
    return render(request, 'sitio/actividad_detalle.html', {'actividad': actividad})

def rebuild_index(request):
    from django.core.management import call_command
    from django.http import JsonResponse
    try:
        call_command("rebuild_index", noinput=False)
        result = "Index rebuilt"
    except Exception as err:
        result = f"Error: {err}"

    return JsonResponse({"result": result})

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
    #email_message.send()

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
    #email_message.send()

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
            #email_message.send()

            request.session[f"email_new_reset_{user.pk}_sent_at"] = now().timestamp()
            messages.success(request, "Te enviamos un enlace al nuevo correo para validarlo.")
            return redirect("sitio:configuracion")
    else:
        form = EmailChangeForm()

    return render(request, "configuracion_reset.html", {"form": form})


# --- Confirmar el nuevo correo ---
#@login_required
#def configuracion_new_email(request, uidb64, token):
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
    #email_message.send()

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

    # Mis publicaciones (se verán duplicadas si hay edición pendiente)
    mis_publicaciones = Noticia.objects.filter(
        creador=request.user
    ).order_by("-fecha")

    pendientes = []
    es_moderador = False

    if perfil and perfil.iglesias_admin.exists():
        es_moderador = True
        pendientes = Noticia.objects.filter(
            iglesiaAsociada__in=perfil.iglesias_admin.all()
        ).filter(
            Q(estado="pendiente") | Q(en_revision_edicion=True)
        ).order_by("-fecha")

    # Procesar aprobar/rechazar
    if request.method == "POST":
        action = request.POST.get("action")

        # ---- REINTENTAR (solo creador) ----
        if action == "reintentar":
            noticia = get_object_or_404(Noticia, pk=request.POST.get("noticia_id"), creador=request.user)

            if noticia.estado == "rechazado" and not noticia.en_revision_edicion:
                # El usuario vuelve a intentar la publicación
                noticia.titulo = request.POST.get("titulo", noticia.titulo)
                noticia.descripcion = request.POST.get("descripcion", noticia.descripcion)

                # Manejo de la imagen: si no envía nada, se mantiene la anterior
                if "imagen" in request.FILES:
                    noticia.imagen = request.FILES["imagen"]
                else:
                    # Si no sube nueva imagen → borrar la anterior
                    noticia.imagen.delete(save=False)
                    noticia.imagen = None

                noticia.estado = "pendiente"
                noticia.motivo_rechazo = ""
                noticia.fecha = timezone.now()  # actualizar fecha de creación
                noticia.save()

                messages.info(request, "Has reenviado tu publicación para revisión.")
            else:
                messages.error(request, "Solo puedes reintentar publicaciones rechazadas en creación.")

            return redirect("sitio:check_post")
        
        if es_moderador:
            noticia = get_object_or_404(Noticia, pk=request.POST.get("noticia_id"))

            if action == "aprobar":
                es_edicion = noticia.en_revision_edicion

                if es_edicion:
                    noticia.titulo = noticia.titulo_editado or noticia.titulo
                    noticia.descripcion = noticia.descripcion_editada or noticia.descripcion
                    if noticia.imagen_editada:
                        noticia.imagen = noticia.imagen_editada

                    # limpiar auxiliares
                    noticia.titulo_editado = None
                    noticia.descripcion_editada = None
                    noticia.imagen_editada = None
                    noticia.en_revision_edicion = False

                    noticia.estado_edicion = "aprobado"
                    noticia.fecha_revision_edicion = timezone.now()
                    noticia.ultima_edicion_aprobada = timezone.now() 

                    # correo al editor
                    contexto = {"noticia": noticia, "user": noticia.editor,}
                    html_content = render_to_string("publicacion_edicion_aprobada_email.html", contexto)
                    email = EmailMessage(
                        subject=f"✅ Tu edición de '{noticia.titulo}' fue aprobada",
                        body=html_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[noticia.editor.email] if noticia.editor else [],  # seguridad 
                    )
                else:
                    noticia.estado = "aprobado"
                    noticia.motivo_rechazo = ""
                
                    # correo al creador
                    contexto = {"noticia": noticia, "user": noticia.creador,}
                    html_content = render_to_string("publicacion_aprobada_email.html", contexto)
                    email = EmailMessage(
                        subject=f"✅ Tu publicación '{noticia.titulo}' fue aprobada",
                        body=html_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[noticia.creador.email],
                    )
                noticia.save()
                email.content_subtype = "html"
                if email.to: # solo si hay destinatario
                    #email.send(fail_silently=True)
                    1 == 1 

                # notificar suscriptores SOLO si es nueva publicación
                if not es_edicion:
                    nueva_publicacion_email(noticia, request)

                messages.success(request, "Se ha aprobado la noticia exitosamente.")
                return redirect("sitio:check_post")

            elif action == "rechazar":
                motivo = request.POST.get("motivo", "").strip()

                if noticia.en_revision_edicion:
                    noticia.titulo_editado = None
                    noticia.descripcion_editada = None
                    noticia.imagen_editada = None
                    noticia.en_revision_edicion = False

                    noticia.estado_edicion = "rechazado"
                    noticia.motivo_rechazo_edicion = motivo
                    noticia.fecha_revision_edicion = timezone.now()

                    # correo al editor
                    contexto = {"noticia": noticia, "motivo": motivo, "user": noticia.editor,}
                    html_content = render_to_string("publicacion_edicion_rechazada_email.html", contexto)
                    email = EmailMessage(
                        subject=f"❌ Tu edición de '{noticia.titulo}' fue rechazada",
                        body=html_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[noticia.editor.email] if noticia.editor else [],  # seguridad
                    )
                else:
                    noticia.estado = "rechazado"
                    noticia.motivo_rechazo = motivo

                    # correo al creador
                    contexto = {"noticia": noticia, "motivo": motivo, "user": noticia.creador,}
                    html_content = render_to_string("publicacion_rechazada_email.html", contexto)
                    email = EmailMessage(
                        subject=f"❌ Tu publicación '{noticia.titulo}' fue rechazada",
                        body=html_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[noticia.creador.email],
                    )
                noticia.save()
                email.content_subtype = "html"
                if email.to: # solo si hay destinatario
                    #email.send(fail_silently=True)
                    1 == 1

                messages.success(request, "Se ha rechazado la noticia exitosamente.")
                return redirect("sitio:check_post")

    return render(request, "check_post.html", {
        "mis_publicaciones": mis_publicaciones,
        "pendientes": pendientes,
        "es_moderador": es_moderador,
    })

def nueva_publicacion_email(noticia, request):
    iglesia = noticia.iglesiaAsociada
    if not iglesia:
        return

    suscriptores = iglesia.suscriptores.all().prefetch_related("usuario")

    for perfil in suscriptores:
        usuario = perfil.usuario
        if not usuario.email:
            continue

        contexto = {
            "iglesia": iglesia,
            "noticia": noticia,
            "user": usuario,
            "inicio_link": request.build_absolute_uri("/")
        }

        subject = f"📢 Nueva publicación de {iglesia.nombre}"
        html_content = render_to_string("publicacion_email.html", contexto)

        msg = EmailMultiAlternatives(
            subject,
            "",
            settings.DEFAULT_FROM_EMAIL,
            [usuario.email],
        )
        msg.attach_alternative(html_content, "text/html")
        #msg.send()

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /dashboard/",
        "Disallow: /configuracion/",
        "Disallow: /signup/",
        "Disallow: /login/",
        "Disallow: /logout/",
        "Disallow: /password_reset_custom/",
        "Disallow: /reset/",
        "Disallow: /autorizacion/",
        "Disallow: /suscribirse/",
        "Disallow: /delete_users/",
        "Disallow: /check_post/",
        "Allow: /",
        "Sitemap: https://parroquia-ingweb.onrender.com/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
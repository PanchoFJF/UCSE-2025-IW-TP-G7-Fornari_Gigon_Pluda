from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from sitio.models import Noticia

# python manage.py delete_invalid_users (comando para ejecutar, CronJob en Render)

# Función para eliminar usuarios no verificados
def delete_invalid_users_and_rejected_posts():
    cutoff = now() - timedelta(minutes=15)

    # Usuarios no verificados
    usuarios = User.objects.filter(is_active=False, date_joined__lt=cutoff)
    usuarios_count = usuarios.count()
    usuarios.delete()

    # Publicaciones rechazadas (que no están en revisión de edición)
    rechazadas = Noticia.objects.filter(estado="rechazado", en_revision_edicion=False)
    rechazadas_count = rechazadas.count()
    rechazadas.delete()

    return usuarios_count, rechazadas_count

class Command(BaseCommand):
    help = "Elimina usuarios no verificados después de 15 minutos y publicaciones rechazadas"

    def handle(self, *args, **kwargs):
        usuarios_count, rechazadas_count = delete_invalid_users_and_rejected_posts()
        self.stdout.write(self.style.SUCCESS(
            f"Se eliminaron {usuarios_count} usuarios no verificados y {rechazadas_count} publicaciones rechazadas."
        ))

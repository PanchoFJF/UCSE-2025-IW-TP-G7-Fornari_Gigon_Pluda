from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta

# python manage.py delete_invalid_users (comando para ejecutar, CronJob en Render)

class Command(BaseCommand):
    help = "Elimina usuarios no verificados después de 15 minutos"

    def handle(self, *args, **kwargs):
        cutoff = now() - timedelta(minutes=15)
        # Usuarios inactivos (no activaron mail) y creados hace más de 15 min
        usuarios = User.objects.filter(is_active=False, date_joined__lt=cutoff)
        count = usuarios.count()
        usuarios.delete()
        self.stdout.write(self.style.SUCCESS(f"Se eliminaron {count} usuarios no verificados."))

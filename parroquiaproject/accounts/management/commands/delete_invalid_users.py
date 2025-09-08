from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta

# python manage.py delete_invalid_users (comando para ejecutar, CronJob en Render)

# Función para eliminar usuarios no verificados
def delete_invalid_users():
    cutoff = now() - timedelta(minutes=15)
    usuarios = User.objects.filter(is_active=False, date_joined__lt=cutoff)
    count = usuarios.count()
    usuarios.delete()
    return count

class Command(BaseCommand):
    help = "Elimina usuarios no verificados después de 15 minutos"
    def handle(self, *args, **kwargs):
        count = delete_invalid_users()
        self.stdout.write(self.style.SUCCESS(f"Se eliminaron {count} usuarios no verificados."))

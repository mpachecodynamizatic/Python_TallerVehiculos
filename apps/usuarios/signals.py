from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone


@receiver(user_logged_in)
def actualizar_ultima_conexion(sender, request, user, **kwargs):
    """
    Signal que actualiza el campo ultima_conexion cuando un usuario hace login.

    Args:
        sender: El modelo que envió la señal
        request: El objeto HttpRequest actual
        user: La instancia del usuario que acaba de hacer login
        **kwargs: Argumentos adicionales
    """
    user.ultima_conexion = timezone.now()
    user.save(update_fields=['ultima_conexion'])

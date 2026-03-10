import os
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'

    def ready(self):
        """
        Se ejecuta cuando Django inicia.
        Carga datos de ejemplo si la BD está vacía en el primer despliegue.
        """
        # Solo ejecutar si no estamos en modo migrate/makemigrations
        import sys
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return

        # Solo ejecutar una vez (evitar recargas en desarrollo)
        if os.environ.get('RUN_MAIN') == 'true' and os.environ.get('DJANGO_SETTINGS_MODULE') == 'config.settings.development':
            return

        # Verificar si la BD tiene datos de ejemplo
        try:
            from apps.clientes.models import Cliente
            from django.core.management import call_command

            # Si no hay clientes, cargar datos de ejemplo
            # (Esto permite que el superusuario se cree en entrypoint.sh primero)
            if not Cliente.objects.exists():
                print("\n" + "=" * 60)
                print("  BASE DE DATOS VACÍA DETECTADA")
                print("  Cargando datos de ejemplo automáticamente...")
                print("=" * 60 + "\n")

                call_command('seed_data')

                print("\n" + "=" * 60)
                print("  ✓ Datos de ejemplo cargados correctamente")
                print("  ✓ Clientes, vehículos, citas, órdenes, inventario...")
                print("=" * 60 + "\n")
        except Exception as e:
            # Si hay error (ej: tablas no existen aún), ignorar silenciosamente
            pass

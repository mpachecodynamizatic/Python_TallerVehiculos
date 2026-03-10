#!/bin/sh
set -e

echo "==> Aplicando migraciones..."
python manage.py migrate --noinput

echo "==> Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "==> Creando superusuario por defecto (si no existe)..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@taller.es')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'Admin1234!')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name='Carlos',
        last_name='García López',
        telefono='600111222',
        is_staff=True,
        is_superuser=True
    )
    print(f'Superusuario "{username}" creado correctamente')
else:
    print(f'Superusuario "{username}" ya existe')
EOF

echo "==> Iniciando servidor Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

# ============================================================
#  Dockerfile para TallerVehiculos (Django 6 + Gunicorn)
#  Compatible con Coolify (despliegue automático desde GitHub)
# ============================================================

# --- Etapa 1: dependencias ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Dependencias del sistema necesarias para Pillow y WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements/base.txt requirements/base.txt
COPY requirements/production.txt requirements/production.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements/production.txt

# --- Etapa 2: imagen final ---
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    PORT=5004

WORKDIR /app

# Librerías de runtime (sin build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copiar paquetes Python instalados en la etapa builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código fuente
COPY . .

# Crear usuario sin privilegios
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Carpetas de datos con permisos correctos
RUN mkdir -p staticfiles media static logs data && \
    chown -R appuser:appgroup /app && \
    chmod -R 775 /app/data /app/staticfiles /app/media /app/logs

# Script de arranque
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

EXPOSE 5004

ENTRYPOINT ["/entrypoint.sh"]

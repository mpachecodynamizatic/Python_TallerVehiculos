# 🚀 Despliegue en Coolify

Este documento describe cómo desplegar TallerVehiculos en Coolify.

## Requisitos Previos

- ✅ Cuenta en Coolify
- ✅ Repositorio Git (GitHub/GitLab/Gitea)
- ✅ Dominio configurado (opcional, pero recomendado)

## Configuración en Coolify

### 1. Crear Nueva Aplicación

1. Accede a tu dashboard de Coolify
2. Click en **"New Resource"** → **"Application"**
3. Selecciona tu repositorio Git
4. Elige la rama: `master` o `main`

### 2. Configuración del Build

Coolify detectará automáticamente el `Dockerfile`. Asegúrate de que:

- **Build Pack**: Docker
- **Port**: `5004` (ya configurado en el Dockerfile)
- **Health Check Path**: `/admin/login/` (opcional)

### 3. Variables de Entorno

Configura las siguientes variables en Coolify (Settings → Environment Variables):

```bash
# Django Core
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production

# Hosts (reemplaza con tu dominio)
ALLOWED_HOSTS=taller.tudominio.com,tudominio.com
CSRF_TRUSTED_ORIGINS=https://taller.tudominio.com,https://tudominio.com

# Base de Datos
DB_NAME=db.sqlite3

# Servidor
PORT=5004
GUNICORN_WORKERS=3

# Información del Taller
NOMBRE_TALLER=Mi Taller de Vehículos
DIRECCION_TALLER=Calle Principal 123
TELEFONO_TALLER=+34 123 456 789
EMAIL_TALLER=info@taller.com
CIF_TALLER=B12345678

# Email (Opcional - configura según tu proveedor)
# EMAIL_HOST=smtp.sendgrid.net
# EMAIL_PORT=587
# EMAIL_HOST_USER=apikey
# EMAIL_HOST_PASSWORD=tu-api-key
# DEFAULT_FROM_EMAIL=no-reply@taller.tudominio.com
```

### 4. Persistencia de Datos (Importante)

Para mantener la base de datos SQLite y los archivos media entre deployments:

1. En Coolify, ve a **Storage → Persistent Storage**
2. Añade los siguientes volúmenes:

```
/app/db.sqlite3       →  /data/db.sqlite3
/app/media            →  /data/media
/app/logs             →  /data/logs
```

### 5. Dominio y SSL

1. Ve a **Domains** en tu aplicación
2. Añade tu dominio: `taller.tudominio.com`
3. Coolify generará automáticamente certificados SSL con Let's Encrypt

### 6. Desplegar

1. Click en **Deploy**
2. Espera a que termine el build (2-5 minutos)
3. Coolify ejecutará automáticamente:
   - Migraciones de la base de datos
   - Recolección de archivos estáticos
   - Inicio de Gunicorn

## Post-Despliegue

### Crear Superusuario

Después del primer despliegue, necesitas crear un usuario administrador:

1. En Coolify, ve a **Terminal** o **Execute Command**
2. Ejecuta:

```bash
python manage.py createsuperuser
```

3. Sigue las instrucciones para crear tu usuario admin

### Verificación

Visita tu aplicación en:
- `https://taller.tudominio.com/admin/` - Panel de administración
- `https://taller.tudominio.com/` - Aplicación principal

## Estructura de Archivos

```
TallerVehiculos/
├── Dockerfile              # Configuración Docker multistage
├── docker/
│   └── entrypoint.sh      # Script de arranque (migraciones + collectstatic)
├── requirements/
│   ├── base.txt           # Dependencias base
│   └── production.txt     # Dependencias producción (incluye gunicorn)
├── config/
│   └── settings/
│       └── production.py  # Settings optimizados para producción
└── .env.example           # Plantilla de variables de entorno
```

## Troubleshooting

### Error: "Bad Request (400)"
- **Causa**: El dominio no está en `ALLOWED_HOSTS` o `CSRF_TRUSTED_ORIGINS`
- **Solución**: Añade tu dominio a ambas variables de entorno (incluye `https://`)

### Error: "Static files not found"
- **Causa**: `collectstatic` falló o no se ejecutó
- **Solución**: Verifica los logs del build. El entrypoint.sh ejecuta automáticamente `collectstatic`

### Base de datos se resetea en cada deploy
- **Causa**: Falta configurar volúmenes persistentes
- **Solución**: Configura persistent storage para `/app/db.sqlite3`

### Logs no se guardan
- **Causa**: Carpeta `/app/logs` no es persistente
- **Solución**: Añade volumen persistente para `/app/logs`

## Actualizaciones

Para actualizar la aplicación:

1. Haz push de tus cambios a la rama configurada
2. Coolify detectará automáticamente los cambios
3. O manualmente: Click en **Redeploy** en Coolify

## Seguridad

✅ **Configurado**:
- HTTPS con Let's Encrypt (vía Coolify)
- WhiteNoise para archivos estáticos
- Cookies seguras (CSRF, Session)
- Headers de seguridad (XSS, HSTS, etc.)
- Usuario sin privilegios en el contenedor

⚠️ **Recomendaciones**:
- Genera un `SECRET_KEY` único: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- No uses el `SECRET_KEY` del `.env.example` en producción
- Configura backups regulares de `/data/db.sqlite3`
- Monitorea los logs regularmente

## Backups

### Backup Manual de la Base de Datos

```bash
# Desde el terminal de Coolify
python manage.py dumpdata > backup_$(date +%Y%m%d).json
```

### Restaurar Backup

```bash
python manage.py loaddata backup_20260307.json
```

## Recursos

- [Documentación de Coolify](https://coolify.io/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/)
- [Gunicorn Settings](https://docs.gunicorn.org/en/stable/settings.html)

---

**¿Problemas?** Revisa los logs en Coolify → Logs → Application Logs

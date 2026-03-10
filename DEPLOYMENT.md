# 🚀 Guía de Despliegue - TallerVehiculos

Esta guía describe los diferentes métodos de despliegue del sistema de gestión de taller.

## 📋 Índice

1. [Despliegue Local (Desarrollo)](#despliegue-local-desarrollo)
2. [Despliegue con Docker](#despliegue-con-docker)
3. [Despliegue en Coolify](#despliegue-en-coolify)
4. [Carga Automática de Datos](#carga-automática-de-datos)
5. [Variables de Entorno](#variables-de-entorno)
6. [Troubleshooting](#troubleshooting)

---

## Despliegue Local (Desarrollo)

### Windows

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd Python_TallerVehiculos

# 2. Usar el script automatizado
iniciar.bat
```

El script `iniciar.bat` hace todo automáticamente:
- ✅ Busca/crea entorno virtual
- ✅ Instala dependencias
- ✅ Aplica migraciones
- ✅ Carga datos de ejemplo (si la BD está vacía)
- ✅ Inicia el servidor

### Linux/Mac

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd Python_TallerVehiculos

# 2. Usar el script automatizado
chmod +x run.sh
./run.sh
```

### Acceso al Sistema

Una vez iniciado, accede a:
- **Aplicación**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **Dashboard**: http://localhost:8000/dashboard

**Credenciales**:
- Usuario: `admin`
- Contraseña: `Admin1234!`

---

## Despliegue con Docker

### Construcción de la Imagen

```bash
# Construir la imagen
docker build -t tallervehiculos:latest .

# O usando docker-compose (si tienes el archivo)
docker-compose build
```

### Ejecución del Contenedor

```bash
# Ejecutar con variables de entorno
docker run -d \
  --name tallervehiculos \
  -p 5004:5004 \
  -e DJANGO_SETTINGS_MODULE=config.settings.production \
  -e SECRET_KEY="tu-clave-secreta-muy-larga" \
  -e ALLOWED_HOSTS="tudominio.com,www.tudominio.com" \
  -e CSRF_TRUSTED_ORIGINS="https://tudominio.com" \
  -e USE_HTTPS=True \
  -e DJANGO_SUPERUSER_USERNAME=admin \
  -e DJANGO_SUPERUSER_PASSWORD="Admin1234!" \
  -v tallervehiculos_data:/app/data \
  -v tallervehiculos_media:/app/media \
  tallervehiculos:latest
```

### Verificar Estado

```bash
# Ver logs del contenedor
docker logs -f tallervehiculos

# Acceder al shell del contenedor
docker exec -it tallervehiculos sh
```

### Volúmenes Importantes

- `/app/data` - Base de datos SQLite
- `/app/media` - Archivos multimedia subidos
- `/app/staticfiles` - Archivos estáticos compilados

---

## Despliegue en Coolify

### Configuración Inicial

1. **Conectar Repositorio Git**
   - En Coolify, crea un nuevo proyecto
   - Conecta tu repositorio de GitHub/GitLab
   - Selecciona la rama `main` o `master`

2. **Configurar Variables de Entorno**

En la sección de Environment Variables de Coolify, añade:

```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<genera-una-clave-aleatoria-larga>
ALLOWED_HOSTS=tu-app.coolify.app,tudominio.com
CSRF_TRUSTED_ORIGINS=https://tu-app.coolify.app,https://tudominio.com
USE_HTTPS=True
DB_NAME=db.sqlite3
PORT=5004
GUNICORN_WORKERS=3
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@taller.es
DJANGO_SUPERUSER_PASSWORD=Admin1234!
```

3. **Configurar el Puerto**
   - En Coolify, configura el puerto expuesto: `5004`

4. **Configurar Dominio**
   - Añade tu dominio personalizado o usa el subdominio de Coolify
   - Coolify gestionará automáticamente el certificado SSL

### Proceso de Despliegue

Coolify ejecutará automáticamente:

1. `docker build` - Construye la imagen
2. `docker run` - Inicia el contenedor
3. El `entrypoint.sh` se ejecuta automáticamente:
   - Aplica migraciones
   - Crea el superusuario (si no existe)
   - Recolecta archivos estáticos
   - Inicia Gunicorn

### Persistencia de Datos

Coolify gestiona automáticamente los volúmenes para:
- Base de datos SQLite (`/app/data/`)
- Archivos media (`/app/media/`)

---

## Carga Automática de Datos

### ⭐ Funcionalidad Principal

El sistema **detecta automáticamente** si la base de datos está vacía al iniciar y carga datos de ejemplo.

### ¿Cómo Funciona?

**En Docker/Producción:**
1. **Superusuario**: El `entrypoint.sh` crea primero el usuario admin (si no existe)
2. **Detección**: Al iniciar Django, se verifica si existen clientes en la base de datos
3. **Carga Automática**: Si no hay clientes, se ejecuta automáticamente el comando `seed_data`

**En Desarrollo Local:**
1. **Migraciones**: Ejecutas `python manage.py migrate`
2. **Detección**: Al iniciar el servidor, se verifica si hay clientes
3. **Carga Automática**: Si no hay clientes, carga los datos automáticamente

**Datos Creados:**
   - ✅ 6 usuarios (admin, recepcionistas, mecánicos)
   - ✅ 8 clientes
   - ✅ 10 vehículos
   - ✅ 10 citas
   - ✅ 5 órdenes de trabajo
   - ✅ 25 repuestos en inventario
   - ✅ 4 proveedores
   - ✅ 8 facturas
   - ✅ 5 órdenes de compra

### Usuarios Creados Automáticamente

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | Admin1234! | Administrador |
| recepcion | Admin1234! | Recepcionista |
| recep2 | Admin1234! | Recepcionista |
| mecanico1 | Admin1234! | Mecánico |
| mecanico2 | Admin1234! | Mecánico |
| mecanico3 | Admin1234! | Mecánico |

### Deshabilitar la Carga Automática

Si deseas deshabilitar esta funcionalidad, edita `apps/core/apps.py` y comenta el método `ready()`:

```python
class CoreConfig(AppConfig):
    # ...

    # def ready(self):
    #     # Código comentado
```

### Carga Manual de Datos

También puedes cargar datos manualmente:

```bash
# Cargar datos de ejemplo
python manage.py seed_data

# Borrar todo y recargar (¡CUIDADO!)
python manage.py seed_data --flush
```

---

## Variables de Entorno

### Desarrollo

Copia el archivo de ejemplo y ajusta los valores:

```bash
cp .env.example .env
```

Variables mínimas para desarrollo:

```env
DJANGO_SETTINGS_MODULE=config.settings.development
SECRET_KEY=tu-clave-secreta
```

### Producción

Variables obligatorias:

```env
# Django Core
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<clave-secreta-muy-larga-y-aleatoria>

# Seguridad
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
CSRF_TRUSTED_ORIGINS=https://tudominio.com,https://www.tudominio.com
USE_HTTPS=True

# Superusuario (creado automáticamente al desplegar)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@taller.es
DJANGO_SUPERUSER_PASSWORD=Admin1234!
```

### Generar SECRET_KEY

```bash
# Con Python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Con OpenSSL
openssl rand -base64 50
```

---

## Troubleshooting

### La base de datos no se carga automáticamente

**Problema**: Los datos de ejemplo no se cargan al iniciar.

**Solución**:
1. Verifica que la BD esté realmente vacía:
   ```bash
   python manage.py shell
   >>> from apps.usuarios.models import Usuario
   >>> Usuario.objects.count()
   0  # Debe ser 0 para que se carguen datos
   ```

2. Carga manualmente:
   ```bash
   python manage.py seed_data
   ```

### Error de migraciones

**Problema**: `django.db.utils.OperationalError: no such table`

**Solución**:
```bash
# Aplicar migraciones
python manage.py migrate

# Si el problema persiste, resetear migraciones (desarrollo)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

### Error de permisos en Docker

**Problema**: `PermissionError: [Errno 13] Permission denied: '/app/data'`

**Solución**:
El Dockerfile ya configura los permisos correctamente. Si ves este error:

```bash
# Recrear el contenedor
docker-compose down
docker-compose up --build
```

### El superusuario no se crea en producción

**Problema**: No puedes acceder al admin.

**Solución**:
1. Verifica las variables de entorno:
   ```bash
   docker exec tallervehiculos env | grep DJANGO_SUPERUSER
   ```

2. Crea el superusuario manualmente:
   ```bash
   docker exec -it tallervehiculos python manage.py createsuperuser
   ```

### Error 400 Bad Request en producción

**Problema**: Error 400 al acceder a la aplicación.

**Solución**:
Verifica `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`:

```env
# Deben coincidir con tu dominio
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
CSRF_TRUSTED_ORIGINS=https://tudominio.com,https://www.tudominio.com
```

### La aplicación no responde en el puerto configurado

**Problema**: `curl: (7) Failed to connect to localhost port 5004`

**Solución**:
1. Verifica que el contenedor está corriendo:
   ```bash
   docker ps
   ```

2. Verifica los logs:
   ```bash
   docker logs tallervehiculos
   ```

3. Verifica el mapeo de puertos:
   ```bash
   docker port tallervehiculos
   ```

---

## 📞 Soporte

Si encuentras problemas no documentados aquí:

1. Revisa los logs del servidor:
   ```bash
   # Local
   python manage.py runserver

   # Docker
   docker logs -f tallervehiculos
   ```

2. Verifica la configuración:
   ```bash
   python manage.py check --deploy
   ```

3. Abre un issue en el repositorio con:
   - Descripción del problema
   - Logs relevantes
   - Entorno (local/docker/coolify)
   - Variables de entorno (sin valores sensibles)

---

## ✅ Checklist de Despliegue

Antes de desplegar a producción:

- [ ] `SECRET_KEY` generada y única
- [ ] `DEBUG=False` en producción
- [ ] `ALLOWED_HOSTS` configurado correctamente
- [ ] `CSRF_TRUSTED_ORIGINS` con protocolo https://
- [ ] `USE_HTTPS=True` si usas SSL
- [ ] Contraseña del superusuario cambiada
- [ ] Base de datos respaldada regularmente
- [ ] Variables de email configuradas (si es necesario)
- [ ] Logs monitoreados
- [ ] Volúmenes persistentes configurados

---

**¡Listo para desplegar!** 🎉

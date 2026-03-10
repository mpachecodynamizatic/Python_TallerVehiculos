# TallerVehiculos 🚗

Sistema integral de gestión para talleres mecánicos desarrollado con Django 6.0.

## 🎯 Características

- **Gestión de Clientes**: Registro y seguimiento de clientes
- **Gestión de Vehículos**: Control de vehículos y su historial
- **Citas**: Sistema de programación de citas y servicios
- **Órdenes de Trabajo**: Seguimiento completo de trabajos realizados
- **Inventario**: Control de repuestos y materiales
- **Facturación**: Generación de facturas y control de pagos
- **Compras**: Gestión de proveedores y órdenes de compra
- **Dashboard**: Panel de control con métricas en tiempo real
- **Multi-usuario**: Sistema de roles (Admin, Recepcionista, Mecánico)

## 📋 Requisitos

- Python 3.11+
- pip
- SQLite (incluido en Python)

## 🚀 Instalación Rápida

### Windows

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd Python_TallerVehiculos

# Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements\base.txt

# Aplicar migraciones
python manage.py migrate

# Iniciar servidor de desarrollo
python manage.py runserver
```

### Linux/Mac

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd Python_TallerVehiculos

# Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements/base.txt

# Aplicar migraciones
python manage.py migrate

# Iniciar servidor de desarrollo
python manage.py runserver
```

## 🎨 Carga Automática de Datos de Ejemplo

**¡IMPORTANTE!** El sistema detecta automáticamente si la base de datos está vacía al iniciar y **carga datos de ejemplo** automáticamente.

### ¿Cómo funciona?

1. **Aplicas migraciones** → `python manage.py migrate`
2. **Inicias el servidor** → `python manage.py runserver`
3. **El sistema detecta** que no hay clientes en la BD
4. **Se cargan automáticamente** todos los datos de ejemplo

Los datos incluyen:
- ✅ Usuarios con diferentes roles (admin, recepcionistas, mecánicos)
- ✅ Clientes de prueba
- ✅ Vehículos registrados
- ✅ Citas programadas
- ✅ Órdenes de trabajo
- ✅ Inventario de repuestos
- ✅ Proveedores
- ✅ Facturas de ejemplo

### Credenciales por Defecto

**Usuario Administrador:**
- Usuario: `admin`
- Contraseña: `Admin1234!`

**Otros usuarios disponibles:**
- Recepcionista: `recepcion` / `Admin1234!`
- Mecánico 1: `mecanico1` / `Admin1234!`
- Mecánico 2: `mecanico2` / `Admin1234!`

### Deshabilitar la Carga Automática

Si deseas deshabilitar la carga automática de datos, edita el archivo `apps/core/apps.py` y comenta el método `ready()`.

### Carga Manual de Datos

También puedes cargar o recargar los datos manualmente en cualquier momento:

```bash
# Cargar datos de ejemplo
python manage.py seed_data

# Borrar todo y volver a cargar (¡CUIDADO!)
python manage.py seed_data --flush
```

## 🐳 Despliegue con Docker

El proyecto incluye configuración para despliegue con Docker y es compatible con Coolify.

```bash
# Construir imagen
docker build -t tallervehiculos .

# Ejecutar contenedor
docker run -p 5004:5004 \
  -e DJANGO_SETTINGS_MODULE=config.settings.production \
  -e SECRET_KEY=tu-clave-secreta \
  -e ALLOWED_HOSTS=tudominio.com \
  -e CSRF_TRUSTED_ORIGINS=https://tudominio.com \
  tallervehiculos
```

### Variables de Entorno para Producción

Crea un archivo `.env` con:

```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
CSRF_TRUSTED_ORIGINS=https://tudominio.com,https://www.tudominio.com
USE_HTTPS=True
DB_NAME=db.sqlite3

# Superusuario por defecto (opcional)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@taller.es
DJANGO_SUPERUSER_PASSWORD=Admin1234!
```

## 📁 Estructura del Proyecto

```
Python_TallerVehiculos/
├── apps/                       # Aplicaciones Django
│   ├── core/                   # App principal (carga automática de datos)
│   ├── usuarios/               # Gestión de usuarios y roles
│   ├── clientes/               # Gestión de clientes
│   ├── vehiculos/              # Gestión de vehículos
│   ├── citas/                  # Sistema de citas
│   ├── ordenes/                # Órdenes de trabajo
│   ├── inventario/             # Gestión de inventario
│   ├── compras/                # Compras y proveedores
│   ├── facturacion/            # Facturación
│   └── dashboard/              # Dashboard y métricas
├── config/                     # Configuración Django
│   ├── settings/
│   │   ├── base.py             # Configuración base
│   │   ├── development.py      # Configuración desarrollo
│   │   └── production.py       # Configuración producción
│   ├── urls.py                 # URLs principales
│   └── wsgi.py                 # WSGI para producción
├── templates/                  # Plantillas HTML
├── static/                     # Archivos estáticos (CSS, JS)
├── docker/                     # Archivos Docker
│   └── entrypoint.sh           # Script de inicio para Docker
├── requirements/               # Dependencias
│   ├── base.txt                # Dependencias base
│   ├── development.txt         # Dependencias desarrollo
│   └── production.txt          # Dependencias producción
├── Dockerfile                  # Configuración Docker
├── manage.py                   # CLI de Django
├── probar.bat                  # Script de prueba (Windows)
└── run.sh                      # Script de ejecución (Linux/Mac)
```

## 🧪 Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario manualmente
python manage.py createsuperuser

# Cargar datos de ejemplo
python manage.py seed_data

# Recolectar archivos estáticos (producción)
python manage.py collectstatic

# Verificar problemas del proyecto
python manage.py check

# Abrir shell de Django
python manage.py shell
```

## 🌐 URLs Importantes

- **Página de inicio**: http://localhost:8000/
- **Dashboard**: http://localhost:8000/dashboard/
- **Panel de Administración**: http://localhost:8000/admin/
- **Login**: http://localhost:8000/login/

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 6.0
- **Base de Datos**: SQLite (desarrollo) / compatible con PostgreSQL (producción)
- **Frontend**: HTML5, CSS3, JavaScript
- **Servidor**: Gunicorn (producción)
- **Estilos**: CSS personalizado + componentes modernos
- **Despliegue**: Docker, compatible con Coolify

## 📝 Notas de Desarrollo

- El proyecto usa un modelo de usuario personalizado (`apps.usuarios.Usuario`)
- Los datos se cargan automáticamente en el primer inicio si la BD está vacía
- El sistema detecta si es desarrollo o producción automáticamente
- En producción, usa Gunicorn con 3 workers por defecto
- Los logs se guardan en la carpeta `logs/` en producción

## 🤝 Contribuciones

Este es un proyecto de gestión de taller. Para contribuir:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feat/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'feat(modulo): descripción'`)
4. Push a la rama (`git push origin feat/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

[Especificar licencia aquí]

## 🐛 Reporte de Bugs

Si encuentras algún bug, por favor crea un issue en el repositorio con:
- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs comportamiento actual
- Capturas de pantalla si es posible

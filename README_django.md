# Sistema de Gestión de Taller de Vehículos

Sistema web completo para la gestión integral de un taller de vehículos, desarrollado en Python con Django.

## 🚀 Stack Tecnológico

- **Backend**: Django 6.0
- **Frontend**: Django Templates + HTMX + Alpine.js + Tailwind CSS
- **Database**: SQLite (desarrollo) → PostgreSQL (producción)
- **ORM**: Django ORM
- **Auth**: Django Auth

## 📋 Características Principales

- Gestión de Clientes
- Gestión de Vehículos
- Planificador de Citas
- Órdenes de Trabajo
- Inventario de Repuestos
- Compras a Proveedores
- Facturación y Presupuestos
- Dashboard con KPIs
- Sistema de Notificaciones

## 🛠️ Instalación

### Prerrequisitos

- Python 3.11+
- pip
- virtualenv (opcional)

### Configuración del Entorno de Desarrollo

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd Python_Init
```

2. **Crear y activar el entorno virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements/development.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores
```

5. **Ejecutar migraciones**
```bash
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

7. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

8. **Acceder a la aplicación**
- Aplicación: http://localhost:8000
- Admin: http://localhost:8000/admin

## 📁 Estructura del Proyecto

```
Python_Init/
├── apps/                   # Aplicaciones Django
│   ├── core/              # Funcionalidades base
│   ├── usuarios/          # Gestión de usuarios
│   ├── clientes/          # Gestión de clientes
│   ├── vehiculos/         # Gestión de vehículos
│   ├── citas/             # Sistema de citas
│   ├── ordenes/           # Órdenes de trabajo
│   ├── inventario/        # Gestión de inventario
│   ├── compras/           # Compras a proveedores
│   ├── facturacion/       # Facturación
│   └── dashboard/         # Dashboard y reportes
├── config/                 # Configuración del proyecto
│   ├── settings/          # Settings divididos
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── static/                 # Archivos estáticos
├── templates/              # Plantillas HTML
├── media/                  # Archivos subidos
├── requirements/           # Dependencias
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── venv/                   # Entorno virtual
├── .env                    # Variables de entorno
├── .gitignore
├── manage.py
├── PLAN_PROYECTO_TALLER.md
└── README.md
```

## 🔧 Configuración

### Variables de Entorno

Las siguientes variables de entorno deben configurarse en el archivo `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (para producción)
DB_NAME=taller_db
DB_USER=taller_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con cobertura
pytest --cov=apps

# Ejecutar tests de una app específica
pytest apps/clientes/tests/
```

## 📦 Despliegue

### Producción

1. **Configurar variables de entorno de producción**
2. **Instalar dependencias de producción**
```bash
pip install -r requirements/production.txt
```

3. **Ejecutar migraciones**
```bash
python manage.py migrate --settings=config.settings.production
```

4. **Recolectar archivos estáticos**
```bash
python manage.py collectstatic --settings=config.settings.production
```

5. **Configurar Gunicorn y Nginx**

## 📖 Documentación

- [Plan del Proyecto](PLAN_PROYECTO_TALLER.md) - Plan completo de desarrollo por fases
- [Django Documentation](https://docs.djangoproject.com/)
- [HTMX Documentation](https://htmx.org/docs/)
- [Alpine.js Documentation](https://alpinejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## 👥 Credenciales de Prueba

- **Usuario**: admin
- **Contraseña**: admin123

## 🗺️ Roadmap

### ✅ FASE 0: Configuración Inicial (COMPLETADA)
- Entorno de desarrollo configurado
- Estructura del proyecto creada
- Django instalado y configurado
- Templates base con HTMX, Alpine.js y Tailwind CSS

### 🔜 FASE 1: Autenticación y Usuarios (Próxima)
- Sistema de login/logout
- Gestión de usuarios
- Roles y permisos

### 📅 Fases Futuras
- FASE 2: Clientes y Vehículos
- FASE 3: Sistema de Citas
- FASE 4: Órdenes de Trabajo
- FASE 5: Inventario de Repuestos
- FASE 6: Compras y Proveedores
- FASE 7: Facturación
- FASE 8: Dashboard y Reportes
- FASE 9: Notificaciones
- FASE 10: Testing y Despliegue

## 📝 Licencia

Este proyecto está bajo la licencia MIT.

## 👤 Autor

Desarrollado como parte del plan de desarrollo por fases del Sistema de Gestión de Taller de Vehículos.

---

**Última actualización**: 2026-03-05
**Versión**: 0.1.0 (FASE 0 Completada)

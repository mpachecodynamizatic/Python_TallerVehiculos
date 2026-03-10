# Contexto del Proyecto: TallerVehiculos

Este archivo es leido automaticamente por Claude al comenzar cualquier sesion.

## Que es este proyecto?

Sistema integral de gestión para talleres mecánicos que permite administrar clientes, vehículos, citas, órdenes de trabajo, inventario de repuestos, compras y facturación. Desarrollado con Django 6.0 y diseñado para optimizar la operación diaria de un taller automotriz.

## Stack Tecnologico
- **Backend**: Python 3.11+ + Django 6.0
- **Frontend**: HTML5 + CSS3 + JavaScript (HTMX + Alpine.js)
- **Base de datos**: SQLite (dev) / Compatible PostgreSQL (prod)
- **Servidor**: Gunicorn (producción)
- **Deployment**: Docker, compatible con Coolify
- **Testing**: pytest + Django TestCase

## Convenciones del Equipo
- Commits en espanol, formato: tipo(scope): descripcion
- Ramas: feat/nombre, fix/nombre, refactor/nombre
- Code review requerido antes de merge a main
- Tests obligatorios para nuevos endpoints

## Skills Disponibles
Consulta la carpeta .claude/skills/ para guias detalladas:
- analysis.md      : Analizar codigo y detectar problemas
- planning.md      : Planificar features y sprints
- architecture.md  : Disenar APIs y arquitecturas
- backend.md       : Codigo Python/FastAPI
- frontend.md      : Codigo HTML/CSS/React
- ui-design.md     : Disenar interfaces y sistemas de diseno
- programming.md   : Programacion general y codigo limpio

## Decisiones de Arquitectura

### 1. Framework: Django 6.0
**Razón**: Django proporciona un ORM robusto, panel de administración automático, sistema de autenticación integrado y es ideal para aplicaciones CRUD complejas como un sistema de gestión de taller.

### 2. Base de Datos: SQLite (desarrollo) / Compatible PostgreSQL (producción)
**Razón**: SQLite es simple para desarrollo y despliegue sin dependencias. La estructura está lista para migrar a PostgreSQL en producción si se necesita escalabilidad.

### 3. Carga Automática de Datos de Ejemplo ⭐ NUEVO
**Implementación**: El sistema detecta automáticamente si la base de datos está vacía al iniciar (verificando la existencia de usuarios) y ejecuta el comando `seed_data` automáticamente.

**Archivo**: `apps/core/apps.py` - método `ready()`

**Características**:
- Se ejecuta solo una vez al iniciar Django
- No interfiere con migraciones o comandos de management
- Evita recargas en modo desarrollo
- Crea usuarios, clientes, vehículos, citas, órdenes, inventario, facturas, etc.

**Credenciales por defecto**:
- Admin: `admin` / `Admin1234!`
- Recepcionista: `recepcion` / `Admin1234!`
- Mecánicos: `mecanico1`, `mecanico2` / `Admin1234!`

### 4. Estructura Multi-App
**Razón**: Separación clara de responsabilidades. Cada módulo (clientes, vehículos, citas, etc.) es una app Django independiente, facilitando el mantenimiento y la escalabilidad.

### 5. Sistema de Roles Personalizado
**Razón**: Modelo de usuario extendido (`apps.usuarios.Usuario`) con roles específicos del dominio (ADMIN, RECEPCIONISTA, MECANICO) en lugar de usar solo grupos de Django.

## Estado Actual del Proyecto
> Última actualización: 2026-03-10

- [x] Setup inicial
- [x] Modelos de base de datos (todas las apps creadas)
- [x] Panel de administración completo
- [x] Frontend base con templates
- [x] Sistema de autenticación y roles
- [x] **Carga automática de datos de ejemplo** (al desplegar con BD vacía)
- [x] Deploy con Docker configurado
- [ ] Tests unitarios y de integración
- [ ] Documentación de API completa

## Reglas Específicas
- Siempre usar español para nombres de variables y comentarios
- Validar todos los inputs del usuario
- Incluir logging en operaciones críticas
- Seguir el patrón Repository para acceso a datos

## Preferencias de Estilo
- Usar type hints en todas las funciones
- Docstrings en formato Google Style
- Máximo 80 caracteres por línea
- Nombres descriptivos, evitar abreviaturas
- Las pantallas utilizar el 80% del tamaño de la pantalla
- Los grids/cruds hacerlos con paginacion, con ordenacion de cualquier columna, posibilidad de aplicar filtros sobre las columnas y un buscador global.
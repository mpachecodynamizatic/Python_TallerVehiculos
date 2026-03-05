# Contexto del Proyecto: TallerVehiculos

Este archivo es leido automaticamente por Claude al comenzar cualquier sesion.

## Que es este proyecto?
> [Describe el proposito del proyecto en 2-3 oraciones]

## Stack Tecnologico
- **Backend**: Python + FastAPI/Flask (elige uno) + SQLAlchemy
- **Frontend**: [React/HTML/Vue - por definir]
- **Base de datos**: SQLite (dev) / PostgreSQL (prod)
- **Testing**: pytest

## Opciones de Framework
El proyecto incluye configuracion para:
- **FastAPI**: src/main.py (moderno, async, docs automaticas)
- **Flask**: src/app_flask.py (clasico, simple, probado)
Elige el que mejor se adapte a tus necesidades.

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
> [Registra aqui las decisiones importantes y su justificacion]

## Estado Actual del Proyecto
> [Actualiza esto con el progreso]
- [ ] Setup inicial
- [ ] Modelos de base de datos
- [ ] API endpoints basicos
- [ ] Frontend base
- [ ] Tests
- [ ] Deploy

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
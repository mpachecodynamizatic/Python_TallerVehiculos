#Requires -Version 5.1
<#
.SYNOPSIS
    Inicializa una carpeta de proyecto Python con estructura profesional y skills de Claude.

.DESCRIPTION
    Crea la estructura completa de un proyecto Python incluyendo:
    - Entorno virtual
    - Estructura de carpetas (backend, frontend, tests, docs)
    - Carpeta .claude con skills para analisis, planificacion, diseno, frontend y backend
    - Archivos de configuracion base

.PARAMETER ProjectName
    Nombre del proyecto a crear.

.PARAMETER ProjectPath
    Ruta donde crear el proyecto. Por defecto usa el directorio actual.

.EXAMPLE
    .\init-python-project.ps1 -ProjectName "mi-app"
    .\init-python-project.ps1 -ProjectName "mi-app" -ProjectPath "C:\Proyectos"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectName,

    [Parameter(Mandatory = $false)]
    [string]$ProjectPath = (Get-Location).Path
)

# El directorio raiz es el directorio donde se ejecuta el script
$rootPath = $ProjectPath

# Configurar encoding UTF8 sin BOM
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

# ============================================
#  FUNCIONES AUXILIARES
# ============================================

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Text)
    Write-Host ">>> $Text" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Text)
    Write-Host "[OK] $Text" -ForegroundColor Green
}

function Write-Info {
    param([string]$Text)
    Write-Host "    $Text" -ForegroundColor Gray
}

function New-Directory {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function New-ProjectFile {
    param([string]$Path, [string]$Content = "")
    $dir = Split-Path $Path -Parent
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    # Usar Out-File para evitar problemas de encoding
    $Content | Out-File -FilePath $Path -Encoding utf8 -Force
}

# ============================================
#  INICIO DEL SCRIPT
# ============================================

Write-Header "INICIALIZADOR DE PROYECTO PYTHON"

Write-Success "Directorio de trabajo: $rootPath"

# ============================================
#  1. ESTRUCTURA DE CARPETAS
# ============================================

Write-Step "Creando estructura de carpetas..."

$directories = @(
    "src",
    "src/api",
    "src/models",
    "src/services",
    "src/utils",
    "src/config",
    "frontend",
    "frontend/components",
    "frontend/pages",
    "frontend/styles",
    "frontend/assets",
    "tests",
    "tests/unit",
    "tests/integration",
    "tests/e2e",
    "docs",
    "docs/api",
    "docs/design",
    "scripts",
    ".claude",
    ".claude/skills"
)

foreach ($dir in $directories) {
    New-Directory (Join-Path $rootPath $dir)
}

Write-Success "Estructura de carpetas creada"

# ============================================
#  2. ARCHIVOS BASE DEL PROYECTO
# ============================================

Write-Step "Generando archivos base del proyecto..."

# requirements.txt
$requirementsContent = @"
# Web Framework - FastAPI
fastapi>=0.111.0
uvicorn[standard]>=0.29.0

# Web Framework - Flask
flask>=3.0.0
flask-cors>=4.0.0
flask-sqlalchemy>=3.1.0

# Base de datos
sqlalchemy>=2.0.0
alembic>=1.13.0

# Validacion
pydantic>=2.7.0
pydantic-settings>=2.2.0

# HTTP Client
httpx>=0.27.0
requests>=2.31.0

# Seguridad
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# Utilidades
python-dotenv>=1.0.0
loguru>=0.7.0
"@
New-ProjectFile (Join-Path $rootPath "requirements.txt") $requirementsContent

# requirements-dev.txt
$requirementsDevContent = @"
-r requirements.txt

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=5.0.0

# Linting & Formato
ruff>=0.4.0
black>=24.0.0
mypy>=1.10.0
"@
New-ProjectFile (Join-Path $rootPath "requirements-dev.txt") $requirementsDevContent

# .env.example
$envContent = @"
# Aplicacion
APP_NAME=$ProjectName
APP_ENV=development
DEBUG=true
SECRET_KEY=cambia-esto-en-produccion

# Base de datos
DATABASE_URL=sqlite:///./dev.db

# API
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
"@
New-ProjectFile (Join-Path $rootPath ".env.example") $envContent

# .gitignore
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
*.egg
*.egg-info/
dist/
build/
venv/
.venv/
ENV/
env/

# Variables de entorno
.env
.env.local

# Base de datos local
*.db
*.sqlite3

# Logs
*.log
logs/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
htmlcov/
.pytest_cache/

# Node (frontend)
node_modules/
dist/
.next/
"@
New-ProjectFile (Join-Path $rootPath ".gitignore") $gitignoreContent

# README.md
$readmeContent = @"
# $ProjectName

## Descripcion
Proyecto Python con FastAPI y Flask (elige el que prefieras)

## Requisitos
- Python 3.11+
- pip
- SQLite (incluido en Python)

## Instalacion rapida

``````bash
# Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # Linux/Mac

# Instalar dependencias
pip install -r requirements-dev.txt

# Configurar entorno
cp .env.example .env
``````

## Estructura del Proyecto

- src/              : Codigo fuente backend
  - main.py         : App FastAPI
  - app_flask.py    : App Flask (alternativa)
  - database.py     : Configuracion SQLite/SQLAlchemy
  - models/         : Modelos de base de datos
- frontend/         : Codigo fuente frontend
- tests/            : Tests
- docs/             : Documentacion
- .claude/          : Skills y contexto para Claude

## Inicializar Base de Datos

``````python
# Ejecutar en consola Python
from src.database import init_db
init_db()
``````

## Comandos utiles

### Forma rapida (recomendado):
``````bash
# Desde el directorio padre:
# Windows:
run.bat $ProjectName          # Ejecuta con FastAPI (default)
run.bat $ProjectName fastapi  # Ejecuta con FastAPI
run.bat $ProjectName flask    # Ejecuta con Flask

# Linux/Mac:
./run.sh $ProjectName         # Ejecuta con FastAPI (default)
./run.sh $ProjectName fastapi # Ejecuta con FastAPI
./run.sh $ProjectName flask   # Ejecuta con Flask
``````

### Forma manual:

#### Con FastAPI:
``````bash
# Arrancar servidor de desarrollo
uvicorn src.main:app --reload

# Docs interactivos disponibles en:
# http://localhost:8000/docs
``````

#### Con Flask:
``````bash
# Arrancar servidor de desarrollo
python -m src.app_flask

# O usando flask run:
flask --app src.app_flask run --reload
``````

### Testing y Linting:
``````bash
# Ejecutar tests
pytest

# Lint
ruff check .
black --check .
``````

## Base de Datos SQLite

El proyecto usa SQLite por defecto. La base de datos se crea automaticamente en:
- dev.db (archivo local)

Para cambiar a PostgreSQL u otra BD, modifica DATABASE_URL en .env
``````
"@
New-ProjectFile (Join-Path $rootPath "README.md") $readmeContent

# src/main.py (FastAPI version)
$mainContent = @"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
"@
New-ProjectFile (Join-Path $rootPath "src/main.py") $mainContent

# src/app_flask.py (Flask version)
$flaskContent = @"
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from src.config.settings import settings

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = settings.SECRET_KEY

# Inicializar extensiones
db = SQLAlchemy(app)
CORS(app, origins=settings.ALLOWED_ORIGINS)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'app': settings.APP_NAME
    })


@app.route('/api/v1/example', methods=['GET'])
def example_endpoint():
    return jsonify({
        'message': 'Flask API funcionando',
        'version': '0.1.0'
    })


if __name__ == '__main__':
    app.run(
        host=settings.API_HOST,
        port=settings.API_PORT,
        debug=settings.DEBUG
    )
"@
New-ProjectFile (Join-Path $rootPath "src/app_flask.py") $flaskContent

# src/config/settings.py
$settingsContent = @"
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "$ProjectName"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret"
    DATABASE_URL: str = "sqlite:///./dev.db"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
"@
New-ProjectFile (Join-Path $rootPath "src/config/settings.py") $settingsContent

# src/__init__.py
New-ProjectFile (Join-Path $rootPath "src/__init__.py") ""

# src/database.py (SQLite database setup)
$databaseContent = @"
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config.settings import settings

# Crear engine de SQLite
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necesario para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Crea todas las tablas en la base de datos."""
    Base.metadata.create_all(bind=engine)
"@
New-ProjectFile (Join-Path $rootPath "src/database.py") $databaseContent

# src/models/example.py (Modelo de ejemplo)
$modelContent = @"
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.username}>"


class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Example {self.title}>"
"@
New-ProjectFile (Join-Path $rootPath "src/models/example.py") $modelContent

# src/models/__init__.py
New-ProjectFile (Join-Path $rootPath "src/models/__init__.py") ""

# tests/conftest.py
$conftestContent = @"
import pytest
from httpx import AsyncClient
from src.main import app


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
"@
New-ProjectFile (Join-Path $rootPath "tests/conftest.py") $conftestContent

# run.bat (Script de ejecucion para Windows - en el directorio del script)
$runBatContent = @"
@echo off
REM Script de ejecucion para proyectos Python
REM Uso: run.bat <nombre-proyecto> [fastapi|flask]

if "%1"=="" (
    echo [ERROR] Debes especificar el nombre del proyecto
    echo Uso: run.bat ^<nombre-proyecto^> [fastapi^|flask]
    echo.
    echo Ejemplo:
    echo   run.bat $ProjectName
    echo   run.bat $ProjectName fastapi
    echo   run.bat $ProjectName flask
    pause
    exit /b 1
)

set PROJECT_NAME=%1
set FRAMEWORK=%2

if not exist "%PROJECT_NAME%" (
    echo [ERROR] El proyecto '%PROJECT_NAME%' no existe
    pause
    exit /b 1
)

echo ========================================
echo  Iniciando %PROJECT_NAME%
echo ========================================
echo.

cd %PROJECT_NAME%

REM Activar entorno virtual
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo [OK] Entorno virtual activado
) else (
    echo [ERROR] No se encuentra el entorno virtual .venv
    echo Ejecuta: python -m venv .venv
    pause
    exit /b 1
)

REM Verificar que las dependencias estan instaladas
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo.
    echo [ADVERTENCIA] Dependencias no instaladas
    echo Instalando dependencias...
    pip install -r requirements-dev.txt
)

echo.
if "%FRAMEWORK%"=="" (
    echo Selecciona el framework a usar:
    echo 1. FastAPI (recomendado - moderno, async)
    echo 2. Flask (clasico, simple)
    echo.
    set /p FRAMEWORK="Ingresa 1 o 2 (default 1): "
)

if "%FRAMEWORK%"=="" set FRAMEWORK=1
if "%FRAMEWORK%"=="fastapi" set FRAMEWORK=1
if "%FRAMEWORK%"=="flask" set FRAMEWORK=2

echo.
if "%FRAMEWORK%"=="1" (
    echo [*] Iniciando con FastAPI...
    echo [*] Servidor disponible en: http://localhost:8000
    echo [*] Docs interactivos en: http://localhost:8000/docs
    echo.
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
) else if "%FRAMEWORK%"=="2" (
    echo [*] Iniciando con Flask...
    echo [*] Servidor disponible en: http://localhost:8000
    echo.
    python -m src.app_flask
) else (
    echo [ERROR] Opcion invalida
    pause
    exit /b 1
)
"@
New-ProjectFile (Join-Path $ProjectPath "run.bat") $runBatContent

# run.sh (Script de ejecucion para Linux/Mac - en el directorio del script)
$runShContent = @"
#!/bin/bash
# Script de ejecucion para proyectos Python
# Uso: ./run.sh <nombre-proyecto> [fastapi|flask]

if [ -z "`$1" ]; then
    echo "[ERROR] Debes especificar el nombre del proyecto"
    echo "Uso: ./run.sh <nombre-proyecto> [fastapi|flask]"
    echo ""
    echo "Ejemplo:"
    echo "  ./run.sh $ProjectName"
    echo "  ./run.sh $ProjectName fastapi"
    echo "  ./run.sh $ProjectName flask"
    exit 1
fi

PROJECT_NAME="`$1"
FRAMEWORK="`${2:-1}"

if [ ! -d "`$PROJECT_NAME" ]; then
    echo "[ERROR] El proyecto '`$PROJECT_NAME' no existe"
    exit 1
fi

echo "========================================"
echo "  Iniciando `$PROJECT_NAME"
echo "========================================"
echo ""

cd "`$PROJECT_NAME"

# Activar entorno virtual
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    echo "[OK] Entorno virtual activado"
else
    echo "[ERROR] No se encuentra el entorno virtual .venv"
    echo "Ejecuta: python -m venv .venv"
    exit 1
fi

# Verificar que las dependencias estan instaladas
python -c "import fastapi" 2>/dev/null
if [ `$? -ne 0 ]; then
    echo ""
    echo "[ADVERTENCIA] Dependencias no instaladas"
    echo "Instalando dependencias..."
    pip install -r requirements-dev.txt
fi

echo ""
if [ "`$FRAMEWORK" = "fastapi" ] || [ "`$FRAMEWORK" = "1" ]; then
    echo "[*] Iniciando con FastAPI..."
    echo "[*] Servidor disponible en: http://localhost:8000"
    echo "[*] Docs interactivos en: http://localhost:8000/docs"
    echo ""
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
elif [ "`$FRAMEWORK" = "flask" ] || [ "`$FRAMEWORK" = "2" ]; then
    echo "[*] Iniciando con Flask..."
    echo "[*] Servidor disponible en: http://localhost:8000"
    echo ""
    python -m src.app_flask
else
    echo "[ERROR] Opcion invalida. Usa: ./run.sh <proyecto> [fastapi|flask]"
    exit 1
fi
"@
New-ProjectFile (Join-Path $ProjectPath "run.sh") $runShContent

Write-Success "Archivos base generados"
Write-Info "run.bat y run.sh creados en: $ProjectPath"

# ============================================
#  3. SKILLS DE CLAUDE
# ============================================

Write-Step "Instalando skills de Claude..."

# SKILL: Analisis
$analysisSkill = @"
---
name: analysis
description: Analizar codigo, arquitectura, requisitos y detectar problemas o mejoras.
---

# Skill: Analisis de Proyecto

Eres un experto analizando proyectos Python. Cuando te pidan analizar algo, sigue este proceso:

## Proceso de Analisis

### 1. Analisis de Requisitos
- Identifica el PROBLEMA REAL que se quiere resolver
- Distingue entre requisitos funcionales y no funcionales
- Detecta ambiguedades y solicita aclaraciones si es necesario
- Mapea dependencias entre requisitos

### 2. Analisis de Codigo
- Revisa la estructura y organizacion del codigo
- Identifica code smells y anti-patrones
- Evalua complejidad ciclomatica
- Detecta duplicacion de codigo
- Verifica adherencia a PEP 8 y buenas practicas Python

### 3. Analisis de Arquitectura
- Evalua la separacion de responsabilidades
- Identifica acoplamiento excesivo
- Revisa el flujo de datos
- Detecta cuellos de botella potenciales

### 4. Analisis de Seguridad
- Detecta vulnerabilidades comunes (OWASP Top 10)
- Revisa manejo de datos sensibles
- Evalua autenticacion y autorizacion
- Verifica validacion de inputs

## Formato de Salida

Siempre estructura tu analisis asi:

``````
## Resumen Ejecutivo
[1-3 lineas del estado general]

## Fortalezas
- [Lo que esta bien]

## Problemas Encontrados

### Criticos
- [Problema]: [Impacto] -> [Solucion recomendada]

### Mejoras
- [Area]: [Situacion actual] -> [Situacion deseada]

## Plan de Accion
1. [Accion prioritaria]
2. ...
``````
"@
New-ProjectFile (Join-Path $rootPath ".claude/skills/analysis.md") $analysisSkill

# SKILL: Planificacion
$planningSkill = @"
---
name: planning
description: Planificar sprints, tareas, roadmaps y descomponer features en subtareas.
---

# Skill: Planificacion de Proyecto

Eres un experto en planificacion agil de proyectos de software Python.

## Cuando Usar Este Skill
- Planificar una nueva feature
- Crear un roadmap de producto
- Descomponer una epica en tareas
- Estimar esfuerzo de desarrollo
- Priorizar backlog

## Proceso de Planificacion

### 1. Entender el Scope
- Que se quiere lograr exactamente?
- Quienes son los usuarios afectados?
- Cuales son las restricciones (tiempo, tecnicas, recursos)?

### 2. Descomposicion
Descompone en este orden:
- **Epica**: Feature grande (semanas)
- **Historia de Usuario**: "Como [rol] quiero [accion] para [beneficio]"
- **Tarea Tecnica**: Unidad de trabajo (horas)
- **Subtarea**: Paso concreto (minutos/horas)

### 3. Estimacion
Usa puntos de historia o estimacion en tiempo:
- XS: < 2h
- S: 2-4h
- M: 4-8h (1 dia)
- L: 1-3 dias
- XL: 3+ dias (considera dividir)

### 4. Priorizacion (MoSCoW)
- **Must Have**: Sin esto el MVP no funciona
- **Should Have**: Importante, pero no bloqueante
- **Could Have**: Nice to have
- **Won't Have**: Fuera de scope ahora

## Plantilla de Historia de Usuario

``````markdown
## Historia: [Titulo]
**Como** [tipo de usuario]
**Quiero** [funcionalidad]
**Para** [beneficio/objetivo]

### Criterios de Aceptacion
- [ ] Dado [contexto], cuando [accion], entonces [resultado]

### Tareas Tecnicas
- [ ] [Tarea] (estimacion)

### Definicion de Done
- [ ] Tests escritos y pasando
- [ ] Codigo revisado
- [ ] Documentacion actualizada
``````
"@
New-ProjectFile (Join-Path $rootPath ".claude/skills/planning.md") $planningSkill

# SKILL: Arquitectura y Diseno
$architectureSkill = @"
---
name: architecture
description: Disenar arquitecturas de software, APIs, modelos de datos y sistemas.
---

# Skill: Diseno de Arquitectura

Eres un arquitecto de software senior especializado en Python y sistemas web modernos.

## Principios Guia
- **SOLID**: Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion
- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It
- **12-Factor App**: Para aplicaciones cloud-native

## Patrones Recomendados para Python

### Estructura de Proyecto (FastAPI)
``````
src/
  api/
    routes/      # Endpoints por dominio
    middleware/  # Auth, logging, etc.
  core/
    config.py    # Settings
    security.py  # JWT, hashing
  models/          # SQLAlchemy models
  schemas/         # Pydantic schemas
  services/        # Logica de negocio
  repositories/    # Acceso a datos
  utils/           # Helpers
``````

### Capas de la Aplicacion
``````
API Layer (FastAPI routes)
    |
Service Layer (logica de negocio)
    |
Repository Layer (acceso a datos)
    |
Database (SQLAlchemy)
``````

## Diseno de API REST

### Convenciones
- URLs en kebab-case: /api/v1/user-profiles
- Sustantivos, no verbos: /users no /getUsers
- HTTP verbs semanticos: GET, POST, PUT, PATCH, DELETE
- Versionado en URL: /api/v1/

### Estructura de Respuesta
``````json
{
  "data": {...},
  "meta": { "total": 100, "page": 1 },
  "errors": []
}
``````

## Diseno de Base de Datos

### Checklist
- [ ] Normalizacion adecuada (3NF minimo)
- [ ] Indices en columnas de busqueda frecuente
- [ ] Claves foraneas con cascade correcto
- [ ] Timestamps: created_at, updated_at
- [ ] Soft delete con deleted_at si aplica
- [ ] Migraciones con Alembic

## Formato de Entregable
Cuando disenes una arquitectura, incluye:
1. Diagrama en texto (ASCII o Mermaid)
2. Justificacion de decisiones clave
3. Trade-offs considerados
4. Riesgos identificados
"@
New-ProjectFile (Join-Path $rootPath ".claude/skills/architecture.md") $architectureSkill

# SKILL: Backend / Python
$backendSkill = @"
---
name: backend
description: Escribir, revisar y refactorizar codigo Python/FastAPI para el backend.
---

# Skill: Desarrollo Backend Python

Eres un desarrollador Python senior con expertise en FastAPI, SQLAlchemy y APIs REST.

## Stack Principal
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0 (async)
- **Validacion**: Pydantic v2
- **Auth**: JWT con python-jose
- **Tests**: pytest + pytest-asyncio
- **Migraciones**: Alembic

## Estandares de Codigo

### Estilo
- PEP 8 estricto
- Type hints en todas las funciones
- Docstrings en funciones publicas (Google style)
- f-strings sobre .format() o %

### FastAPI Patterns

``````python
# Estructura de un router
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.schemas.user import UserCreate, UserResponse
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Crea un nuevo usuario."""
    service = UserService(db)
    return await service.create(user_data)
``````

``````python
# Modelo SQLAlchemy
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=func.now())
``````

## Manejo de Errores

``````python
from fastapi import HTTPException, status

# Errores HTTP semanticos
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ya registrado")
``````

## Testing

``````python
@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post("/api/v1/users/", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
``````

## Checklist de Calidad
- [ ] Type hints completos
- [ ] Tests para cada endpoint (happy path + edge cases)
- [ ] Manejo de errores explicito
- [ ] Logging en puntos criticos
- [ ] No secrets en el codigo
- [ ] Validacion de inputs con Pydantic
"@
New-ProjectFile (Join-Path $rootPath ".claude/skills/backend.md") $backendSkill

# SKILL: Frontend
$frontendSkill = @"
---
name: frontend
description: Desarrollar interfaces frontend modernas, componentes y paginas web.
---

# Skill: Desarrollo Frontend

Eres un desarrollador frontend senior con expertise en diseno moderno y experiencia de usuario.

## Stack Recomendado
- **Framework**: React + Vite (o HTML/CSS/JS vanilla)
- **Estilos**: Tailwind CSS o CSS Modules
- **HTTP**: fetch nativo o axios
- **Estado**: useState, useReducer
- **Forms**: react-hook-form + zod

## Principios de Diseno

### Antes de Codear
1. Define la **jerarquia visual** (que es lo mas importante)
2. Elige una **direccion estetica** clara
3. Disena para **movil primero**, luego adapta a escritorio
4. Define la **paleta de colores** y tipografia antes de empezar

### Estetica y UI
- Evita disenos genericos
- Usa tipografias con personalidad
- Espaciado generoso > interfaz abarrotada
- Animaciones sutiles mejoran la percepcion de calidad
- Consistencia en border-radius, sombras y colores

## Estructura de Componentes React

``````jsx
import { useState } from "react"

export function Card({ title, onAction }) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div
      className={`card ${isHovered ? "card--hovered" : ""}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <h3 className="card__title">{title}</h3>
      <button onClick={onAction} className="card__btn">
        Accion
      </button>
    </div>
  )
}
``````

## Comunicacion con API Backend

``````javascript
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"

async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem("token")
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  })
  if (!res.ok) throw new Error(`API Error: ${res.status}`)
  return res.json()
}

export const api = {
  get: (url) => apiRequest(url),
  post: (url, data) => apiRequest(url, { method: "POST", body: JSON.stringify(data) }),
  put: (url, data) => apiRequest(url, { method: "PUT", body: JSON.stringify(data) }),
  delete: (url) => apiRequest(url, { method: "DELETE" }),
}
``````

## Checklist de Calidad Frontend
- [ ] Responsive design (movil, tablet, escritorio)
- [ ] Estados de carga y error manejados
- [ ] Accesibilidad basica (alt texts, roles ARIA, contraste)
- [ ] Validacion de formularios en cliente
- [ ] Tokens/secrets NUNCA en el frontend
- [ ] Performance: imagenes optimizadas, lazy loading
"@
New-ProjectFile (Join-Path $rootPath ".claude/skills/frontend.md") $frontendSkill

# SKILL: Diseno UI/UX
$uiDesignSkill = @"
---
name: ui-design
description: Disenar interfaces, sistemas de diseno, componentes visuales y experiencias de usuario.
---

# Skill: Diseno UI/UX

Eres un disenador UI/UX senior con ojo para interfaces memorables y usables.

## Proceso de Diseno

### 1. Research & Definicion
- Quienes son los usuarios? (personas)
- Que tareas principales realizan?
- Cual es el contexto de uso? (dispositivo, entorno)
- Que emociones debe evocar la interfaz?

### 2. Arquitectura de Informacion
- Mapa de sitio
- Flujos de usuario principales
- Jerarquia de navegacion

### 3. Sistema de Diseno

#### Tokens de Diseno
``````css
:root {
  /* Colores */
  --color-primary: #3b82f6;
  --color-secondary: #8b5cf6;
  --color-accent: #ec4899;
  --color-surface: #ffffff;
  --color-background: #f9fafb;
  --color-text: #111827;
  --color-text-muted: #6b7280;
  --color-error: #ef4444;
  --color-success: #10b981;

  /* Tipografia */
  --font-display: 'Inter', sans-serif;
  --font-body: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Escala tipografica */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;

  /* Espaciado */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --space-8: 2rem;
  --space-16: 4rem;

  /* Bordes */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
  --radius-full: 9999px;

  /* Sombras */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
}
``````

### 4. Componentes Clave
- [ ] Botones (primary, secondary, ghost, danger)
- [ ] Inputs y formularios
- [ ] Cards y contenedores
- [ ] Navegacion (navbar, sidebar, breadcrumbs)
- [ ] Modales y drawers
- [ ] Estados (loading, empty, error)
- [ ] Notificaciones / toasts
- [ ] Tablas y listas

### 5. Principios de Composicion Visual
- **Contraste**: El elemento mas importante debe destacar
- **Alineacion**: Alinea en grids, evita posicionamiento aleatorio
- **Proximidad**: Elementos relacionados juntos
- **Repeticion**: Patrones consistentes crean familiaridad
- **Espacio negativo**: Respira, no llenes todo
- **Jerarquia**: Guia el ojo del usuario

## Entregables Esperados
Cuando disenes UI, entrega:
1. Paleta de colores con hex codes
2. Tipografia seleccionada con escala
3. Mockup en codigo (HTML/CSS o React/Tailwind)
4. Notas sobre interacciones y animaciones
"@
New-ProjectFile (Join-Path $rootPath ".claude/skills/ui-design.md") $uiDesignSkill

# SKILL: Programacion General
$programmingSkill = @"
---
name: programming
description: Escribir codigo limpio, eficiente y mantenible siguiendo mejores practicas.
---

# Skill: Programacion General

Eres un programador senior con expertise en escribir codigo limpio y mantenible.

## Principios de Codigo Limpio

### 1. Nombres Significativos
- Variables y funciones deben revelar su intencion
- Evita abreviaciones crípticas
- Usa nombres buscables

``````python
# Mal
d = 86400  # segundos en un dia

# Bien
SECONDS_PER_DAY = 86400
``````

### 2. Funciones Pequenas
- Una funcion = una responsabilidad
- Maximo 20-30 lineas por funcion
- Extraer hasta que no se pueda mas

``````python
# Mal
def process_user(user_data):
    # validar
    # guardar en db
    # enviar email
    # actualizar cache
    pass

# Bien
def process_user(user_data):
    validated_data = validate_user_data(user_data)
    user = save_user_to_database(validated_data)
    send_welcome_email(user)
    update_user_cache(user)
    return user
``````

### 3. DRY (Don't Repeat Yourself)
- No dupliques logica
- Extrae funciones comunes
- Usa herencia y composicion apropiadamente

### 4. Manejo de Errores
- Maneja errores explicitos
- No uses excepciones para control de flujo
- Loguea errores con contexto

``````python
# Bien
try:
    result = process_data(data)
except ValidationError as e:
    logger.error(f"Validation failed for {data.id}: {e}")
    raise
except DatabaseError as e:
    logger.error(f"Database error processing {data.id}: {e}")
    raise
``````

### 5. Comentarios
- El codigo debe ser auto-explicativo
- Comenta el "por que", no el "que"
- Mantén los comentarios actualizados

``````python
# Mal
# Incrementar i
i += 1

# Bien
# Saltamos el primer elemento porque contiene headers
i += 1
``````

## Patrones de Diseno Utiles

### Singleton
Cuando necesitas una sola instancia (config, logger)

### Factory
Para crear objetos complejos

### Strategy
Para algoritmos intercambiables

### Observer
Para eventos y notificaciones

### Repository
Para acceso a datos

## Checklist de Calidad
- [ ] Codigo auto-explicativo
- [ ] Sin duplicacion
- [ ] Funciones pequenas y enfocadas
- [ ] Manejo de errores apropiado
- [ ] Tests unitarios
- [ ] Type hints (Python)
- [ ] Documentacion actualizada
"@
New-ProjectFile (Join-Path $rootPath ".claude/skills/programming.md") $programmingSkill

Write-Success "Skills de Claude instalados (7 skills)"

# ============================================
#  4. CLAUDE.MD (contexto principal)
# ============================================

Write-Step "Creando CLAUDE.md (contexto principal)..."

$claudeContext = @"
# Contexto del Proyecto: $ProjectName

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
"@
New-ProjectFile (Join-Path $rootPath ".claude/CLAUDE.md") $claudeContext

Write-Success "CLAUDE.md creado"

# ============================================
#  5. ENTORNO VIRTUAL
# ============================================

Write-Step "Verificando Python..."

$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Info "Encontrado: $version"
            break
        }
    }
    catch {
        continue
    }
}

if ($pythonCmd) {
    Write-Step "Creando entorno virtual (.venv)..."
    try {
        & $pythonCmd -m venv (Join-Path $rootPath ".venv")
        Write-Success "Entorno virtual creado en .venv"
    }
    catch {
        Write-Host "[ADVERTENCIA] No se pudo crear el entorno virtual" -ForegroundColor Yellow
        Write-Info "Crea manualmente con: python -m venv $rootPath\.venv"
    }
}
else {
    Write-Host "[ADVERTENCIA] Python no encontrado en PATH" -ForegroundColor Yellow
    Write-Info "Instalalo y ejecuta: python -m venv $rootPath\.venv"
}

# ============================================
#  6. RESUMEN FINAL
# ============================================

Write-Header "PROYECTO CREADO EXITOSAMENTE"

Write-Host ""
Write-Host "Directorio: $rootPath" -ForegroundColor White
Write-Host ""
Write-Host "Estructura creada:" -ForegroundColor Cyan
Write-Host "  + src/            Backend Python (FastAPI + Flask + SQLite)" -ForegroundColor Gray
Write-Host "  + frontend/       Codigo frontend" -ForegroundColor Gray
Write-Host "  + tests/          Tests unitarios e integracion" -ForegroundColor Gray
Write-Host "  + docs/           Documentacion" -ForegroundColor Gray
Write-Host "  + .claude/        Skills y contexto para Claude" -ForegroundColor Gray
Write-Host "    - CLAUDE.md           Contexto principal" -ForegroundColor Gray
Write-Host "    - skills/             7 skills especializados" -ForegroundColor Gray
Write-Host "  + .env.example    Variables de entorno" -ForegroundColor Gray
Write-Host "  + requirements.txt" -ForegroundColor Gray
Write-Host ""
Write-Host "Proximos pasos:" -ForegroundColor Cyan
Write-Host "  1. .venv\Scripts\activate" -ForegroundColor White
Write-Host "  2. pip install -r requirements-dev.txt" -ForegroundColor White
Write-Host "  3. cp .env.example .env" -ForegroundColor White
Write-Host "  4. uvicorn src.main:app --reload   (FastAPI)" -ForegroundColor White
Write-Host "     o python -m src.app_flask       (Flask)" -ForegroundColor White
Write-Host ""
Write-Host "Edita .claude\CLAUDE.md con el contexto de tu proyecto" -ForegroundColor Gray
Write-Host ""
Write-Host "Skills de Claude disponibles:" -ForegroundColor Cyan
Write-Host "  - analysis.md      : Analizar codigo y arquitectura" -ForegroundColor Gray
Write-Host "  - planning.md      : Planificar features y sprints" -ForegroundColor Gray
Write-Host "  - architecture.md  : Disenar APIs y sistemas" -ForegroundColor Gray
Write-Host "  - backend.md       : Codigo Python/FastAPI" -ForegroundColor Gray
Write-Host "  - frontend.md      : Codigo HTML/CSS/React" -ForegroundColor Gray
Write-Host "  - ui-design.md     : Diseno de interfaces" -ForegroundColor Gray
Write-Host "  - programming.md   : Programacion general" -ForegroundColor Gray
Write-Host ""
Write-Host "Listo para empezar a desarrollar!" -ForegroundColor Green
Write-Host ""

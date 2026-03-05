@echo off
REM Script para probar la FASE 0 completa
REM Uso: test_fase0.bat

echo ========================================
echo  PRUEBA DE FASE 0
echo  Sistema de Gestion de Taller
echo ========================================
echo.

REM Activar entorno virtual
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo [OK] Entorno virtual activado
) else (
    echo [X] ERROR: No se encuentra .venv
    pause
    exit /b 1
)

echo.
echo ========================================
echo  1. Verificando Python
echo ========================================
python --version
if errorlevel 1 (
    echo [X] ERROR: Python no encontrado
    pause
    exit /b 1
) else (
    echo [OK] Python instalado
)

echo.
echo ========================================
echo  2. Verificando Django
echo ========================================
python -c "import django; print('Django', django.get_version())"
if errorlevel 1 (
    echo [X] ERROR: Django no instalado
    pause
    exit /b 1
) else (
    echo [OK] Django instalado
)

echo.
echo ========================================
echo  3. Verificando dependencias
echo ========================================
python -c "import django_extensions; print('[OK] django-extensions')" 2>nul && echo [OK] django-extensions || echo [X] django-extensions NO instalado
python -c "import PIL; print('[OK] Pillow')" 2>nul && echo [OK] Pillow || echo [X] Pillow NO instalado
python -c "import dotenv; print('[OK] python-dotenv')" 2>nul && echo [OK] python-dotenv || echo [X] python-dotenv NO instalado
python -c "import environ; print('[OK] django-environ')" 2>nul && echo [OK] django-environ || echo [X] django-environ NO instalado

echo.
echo ========================================
echo  4. Verificando configuracion
echo ========================================
python manage.py check
if errorlevel 1 (
    echo [X] ERROR: Problemas en la configuracion
    pause
    exit /b 1
) else (
    echo [OK] Configuracion correcta
)

echo.
echo ========================================
echo  5. Verificando migraciones
echo ========================================
python manage.py showmigrations --list | findstr /C:"[X]" > nul
if errorlevel 1 (
    echo [X] ADVERTENCIA: Migraciones no aplicadas
) else (
    echo [OK] Migraciones aplicadas
)

echo.
echo ========================================
echo  6. Verificando estructura
echo ========================================
if exist manage.py (echo [OK] manage.py) else (echo [X] manage.py NO ENCONTRADO)
if exist config\settings\base.py (echo [OK] settings/base.py) else (echo [X] settings/base.py NO ENCONTRADO)
if exist config\settings\development.py (echo [OK] settings/development.py) else (echo [X] settings/development.py NO ENCONTRADO)
if exist apps\core (echo [OK] app core) else (echo [X] app core NO ENCONTRADA)
if exist templates\base.html (echo [OK] template base.html) else (echo [X] template base.html NO ENCONTRADO)
if exist templates\dashboard.html (echo [OK] template dashboard.html) else (echo [X] template dashboard.html NO ENCONTRADO)
if exist db.sqlite3 (echo [OK] base de datos) else (echo [X] base de datos NO ENCONTRADA)

echo.
echo ========================================
echo  7. Verificando aplicaciones
echo ========================================
if exist apps\core (echo [OK] core) else (echo [X] core)
if exist apps\usuarios (echo [OK] usuarios) else (echo [X] usuarios)
if exist apps\clientes (echo [OK] clientes) else (echo [X] clientes)
if exist apps\vehiculos (echo [OK] vehiculos) else (echo [X] vehiculos)
if exist apps\citas (echo [OK] citas) else (echo [X] citas)
if exist apps\ordenes (echo [OK] ordenes) else (echo [X] ordenes)
if exist apps\inventario (echo [OK] inventario) else (echo [X] inventario)
if exist apps\compras (echo [OK] compras) else (echo [X] compras)
if exist apps\facturacion (echo [OK] facturacion) else (echo [X] facturacion)
if exist apps\dashboard (echo [OK] dashboard) else (echo [X] dashboard)

echo.
echo ========================================
echo  RESUMEN DE LA PRUEBA
echo ========================================
echo.
echo Todas las verificaciones completadas!
echo.
echo Para iniciar el servidor ejecuta:
echo   run.bat
echo.
echo O manualmente:
echo   python manage.py runserver
echo.
echo Luego accede a:
echo   - Aplicacion: http://localhost:8000
echo   - Admin: http://localhost:8000/admin
echo   - Dashboard: http://localhost:8000/dashboard
echo.
echo Credenciales:
echo   Usuario: admin
echo   Password: admin123
echo.

pause

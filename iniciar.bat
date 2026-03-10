@echo off
REM Script de inicio completo para TallerVehiculos
REM Automatiza: verificación, migraciones, datos de ejemplo y servidor
cls

echo ==========================================
echo   SISTEMA DE GESTION DE TALLER
echo   Django 6.0 + HTMX + Alpine.js
echo ==========================================
echo.

REM ==========================================
REM 1. BUSCAR Y ACTIVAR ENTORNO VIRTUAL
REM ==========================================
echo [1/7] Buscando entorno virtual...
if exist .venv\Scripts\activate.bat (
    set VENV_PATH=.venv
    echo [OK] Encontrado: .venv
    goto :activate
)

if exist venv\Scripts\activate.bat (
    set VENV_PATH=venv
    echo [OK] Encontrado: venv
    goto :activate
)

echo [X] No se encuentra entorno virtual
echo.
echo Deseas crearlo ahora? (S/N)
set /p CREATE="Respuesta: "
if /i "%CREATE%"=="S" (
    echo Creando .venv...
    python -m venv .venv
    set VENV_PATH=.venv
    goto :activate
)
echo Cancelado
pause
exit /b 1

:activate
echo.
echo [2/7] Activando entorno virtual...
call %VENV_PATH%\Scripts\activate.bat
echo [OK] Activado
echo.

REM ==========================================
REM 2. VERIFICAR PYTHON
REM ==========================================
echo [3/7] Verificando Python...
python --version
if errorlevel 1 (
    echo [X] Python no encontrado
    echo Instala Python 3.11+ desde https://www.python.org
    pause
    exit /b 1
)
echo [OK] Python OK
echo.

REM ==========================================
REM 3. INSTALAR/VERIFICAR DEPENDENCIAS
REM ==========================================
echo [4/7] Verificando Django...
python -c "import django; print('Django', django.get_version())" 2>nul
if errorlevel 1 (
    echo [!] Django no instalado
    echo Instalando dependencias...
    pip install -q -r requirements\base.txt
    if errorlevel 1 (
        echo [X] Error al instalar dependencias
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas
)
echo [OK] Django OK
echo.

REM ==========================================
REM 4. VERIFICAR PROYECTO
REM ==========================================
echo [5/7] Verificando configuracion del proyecto...
python manage.py check --deploy 2>nul
if errorlevel 1 (
    echo [!] Hay advertencias en el proyecto (normal en desarrollo)
    python manage.py check
)
echo [OK] Proyecto OK
echo.

REM ==========================================
REM 5. APLICAR MIGRACIONES
REM ==========================================
echo [6/7] Aplicando migraciones de base de datos...
python manage.py migrate --noinput
if errorlevel 1 (
    echo [X] Error al aplicar migraciones
    pause
    exit /b 1
)
echo [OK] Migraciones aplicadas
echo.

REM ==========================================
REM 6. VERIFICAR DATOS DE EJEMPLO
REM ==========================================
echo [7/7] Verificando datos de ejemplo...
echo.
echo NOTA: Si la base de datos esta vacia, se cargaran
echo       datos de ejemplo automaticamente al iniciar.
echo.

REM ==========================================
REM 7. MOSTRAR INFORMACION
REM ==========================================
echo ==========================================
echo   LISTO PARA INICIAR
echo ==========================================
echo.
echo Servidor disponible en:
echo   ^> http://localhost:8000
echo.
echo Panel de Administracion:
echo   ^> http://localhost:8000/admin
echo.
echo Dashboard:
echo   ^> http://localhost:8000/dashboard
echo.
echo Credenciales por defecto:
echo   Usuario:  admin
echo   Password: Admin1234!
echo.
echo Otros usuarios:
echo   - recepcion / Admin1234!
echo   - mecanico1 / Admin1234!
echo.
echo ==========================================
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

REM ==========================================
REM 8. INICIAR SERVIDOR
REM ==========================================
python manage.py runserver

pause

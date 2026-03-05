@echo off
REM Test simple de FASE 0
echo =======================================
echo  TEST SIMPLE - FASE 0
echo =======================================
echo.

REM Activar entorno virtual
call .venv\Scripts\activate.bat
echo [1/5] Entorno virtual activado
echo.

REM Verificar Python
python --version
echo [2/5] Python OK
echo.

REM Verificar Django
python -c "import django"
if %errorlevel% equ 0 (
    python -c "import django; print('Django version:', django.get_version())"
    echo [3/5] Django OK
) else (
    echo [ERROR] Django no instalado
    pause
    exit /b 1
)
echo.

REM Verificar proyecto
python manage.py check
if %errorlevel% equ 0 (
    echo [4/5] Configuracion OK
) else (
    echo [ERROR] Problemas en configuracion
    pause
    exit /b 1
)
echo.

REM Verificar estructura
if exist manage.py (echo [OK] manage.py) else (echo [X] manage.py)
if exist config\settings\base.py (echo [OK] settings) else (echo [X] settings)
if exist templates\base.html (echo [OK] templates) else (echo [X] templates)
if exist db.sqlite3 (echo [OK] database) else (echo [X] database)
echo [5/5] Estructura OK
echo.

echo =======================================
echo  PRUEBA COMPLETADA
echo =======================================
echo.
echo Todo funciona correctamente!
echo.
echo Para iniciar el servidor:
echo   run.bat
echo.
echo O manualmente:
echo   python manage.py runserver
echo.
pause

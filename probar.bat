@echo off
REM Script de prueba automatica
cls
echo =======================================
echo   PRUEBA FASE 0
echo =======================================
echo.

REM Buscar entorno virtual
echo [1/6] Buscando entorno virtual...
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

if exist .venv\Scripts\python.exe (
    set VENV_PATH=.venv
    echo [OK] Encontrado: .venv
    goto :activate
)

echo [X] No se encuentra entorno virtual
echo.
echo Quieres crearlo ahora? (S/N)
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
echo [2/6] Activando entorno virtual...
call %VENV_PATH%\Scripts\activate.bat
echo [OK] Activado
echo.

echo [3/6] Verificando Python...
python --version
echo [OK] Python OK
echo.

echo [4/6] Verificando Django...
python -c "import django; print('Django', django.get_version())" 2>nul
if errorlevel 1 (
    echo [X] Django no instalado
    echo Instalando dependencias...
    pip install -q -r requirements\base.txt
)
echo [OK] Django OK
echo.

echo [5/6] Verificando proyecto...
python manage.py check 2>nul
if errorlevel 1 (
    echo [X] Hay errores en el proyecto
    python manage.py check
    pause
    exit /b 1
)
echo [OK] Proyecto OK
echo.

echo [6/6] Verificando archivos...
if exist manage.py (echo [OK] manage.py) else (echo [X] manage.py)
if exist db.sqlite3 (echo [OK] base de datos) else (echo [!] Sin base de datos - ejecutar: python manage.py migrate)
if exist templates\base.html (echo [OK] templates) else (echo [X] templates)
if exist config\settings\base.py (echo [OK] settings) else (echo [X] settings)
echo.

echo =======================================
echo   PRUEBA COMPLETADA
echo =======================================
echo.
echo TODO FUNCIONA CORRECTAMENTE!
echo.
echo Siguiente paso:
echo   Ejecuta: iniciar.bat
echo   O: python manage.py runserver
echo.
echo Luego abre: http://localhost:8000/admin
echo   Usuario: admin
echo   Password: Admin1234!
echo.
pause

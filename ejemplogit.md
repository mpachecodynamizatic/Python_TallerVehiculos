REM Verificar si Git está instalado
git --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Git no encontrado - no es obligatorio para el funcionamiento
) else (
    echo [OK] Git encontrado
    
    REM Verificar si ya existe un repositorio Git
    if exist ".git" (
        echo [OK] Repositorio Git encontrado
        
        REM Obtener el nombre de la carpeta actual
        for %%I in (.) do set "PROJECT_NAME=%%~nxI"
        
        REM Detectar usuario de GitHub automáticamente
        for /f "tokens=*" %%i in ('gh api user --jq .login 2^>nul') do set "GITHUB_USER=%%i"
        if "!GITHUB_USER!"=="" set "GITHUB_USER=mpacheco@dynamizatic.com"
        
        echo [INFO] Verificando sincronizacion con GitHub...
        echo [INFO] Usuario GitHub: !GITHUB_USER!
        echo [INFO] Repositorio: !PROJECT_NAME!
        
        REM Verificar y sincronizar repositorio existente
        call :sync_github_repo
    ) else (
        echo.
        echo [INFO] No se encontro repositorio Git - creando automaticamente...
        
        REM Crear repositorio automáticamente
        REM Crear repositorio automáticamente
        echo [INFO] Inicializando repositorio Git automaticamente...
        git init
        if errorlevel 1 (
            echo [ERROR] Error inicializando repositorio Git
        ) else (
            echo [OK] Repositorio Git creado exitosamente
            
            REM Crear .gitignore si no existe
            if not exist ".gitignore" (
                echo [INFO] Creando archivo .gitignore...
                (
                    echo # Entorno virtual
                    echo .venv/
                    echo __pycache__/
                    echo *.pyc
                    echo.
                    echo # Archivos de salida
                    echo *.xlsx
                    echo *.csv
                    echo.
                    echo # Archivos del sistema
                    echo .DS_Store
                    echo Thumbs.db
                    echo desktop.ini
                    echo.
                    echo # Archivos temporales
                    echo *.tmp
                    echo *.temp
                    echo ~*
                ) > .gitignore
                echo [OK] Archivo .gitignore creado
            )
            
            echo [INFO] Agregando archivos al repositorio...
            git add .
            git commit -m "Initial commit: ERP Generico - Sistema de Planificacion de Recursos Empresariales"
            if errorlevel 1 (
                echo [WARNING] Error haciendo commit inicial
            ) else (
                echo [OK] Commit inicial realizado
            )
            
            REM Obtener el nombre de la carpeta actual y configurar GitHub
            for %%I in (.) do set "PROJECT_NAME=%%~nxI"
            
            REM Detectar usuario de GitHub automáticamente
            for /f "tokens=*" %%i in ('gh api user --jq .login 2^>nul') do set "GITHUB_USER=%%i"
            if "!GITHUB_USER!"=="" set "GITHUB_USER=mpacheco@dynamizatic.com"
            
            echo.
            echo [INFO] Creando repositorio en GitHub automaticamente...
            echo [INFO] Usuario GitHub: !GITHUB_USER!
            echo [INFO] Nombre del repositorio: !PROJECT_NAME!
            
            REM Crear y sincronizar repositorio
            call :create_github_repo
        )
    )
)
@echo off
REM Script para ejecutar el agente local de investigación de repositorios iOS
REM Windows Batch Script

echo ================================================================================
echo AGENTE LOCAL DE INVESTIGACION DE REPOSITORIOS iOS
echo ================================================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Verificar que el script existe
if not exist "local_repo_research_agent.py" (
    echo [ERROR] local_repo_research_agent.py no encontrado
    pause
    exit /b 1
)

echo [OK] Script encontrado
echo.

REM Cargar variables de entorno desde .env.local o .env
if exist ".env.local" (
    echo [INFO] Cargando variables desde .env.local...
    for /f "tokens=1,2 delims==" %%a in (.env.local) do (
        set "%%a=%%b"
    )
) else if exist ".env" (
    echo [INFO] Cargando variables desde .env...
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        set "%%a=%%b"
    )
)

REM Verificar GITHUB_TOKEN
if "%GITHUB_TOKEN%"=="" (
    echo [ADVERTENCIA] GITHUB_TOKEN no esta configurado
    echo    El agente funcionara pero con capacidades limitadas
    echo.
)

REM Ejecutar agente
echo ================================================================================
echo Ejecutando investigacion...
echo ================================================================================
echo.

python local_repo_research_agent.py --workspace "%CD%"

if errorlevel 1 (
    echo.
    echo [ERROR] La ejecucion fallo
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo [OK] Proceso completado exitosamente
echo ================================================================================
echo.
echo Revisa los archivos generados:
echo   - local_research_report_*.json
echo   - local_execution_*.json
echo.

pause


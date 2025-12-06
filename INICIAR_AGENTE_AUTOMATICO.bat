@echo off
chcp 65001 >nul
echo ========================================
echo   AGENTE AUTOMATICO - BMC URUGUAY
echo ========================================
echo.
echo Iniciando agente de fondo...
echo El agente actualizará productos y precios automáticamente.
echo.
echo Para detener el agente, presiona Ctrl+C
echo.
echo ========================================
echo.

REM Verificar que Python esté instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor, instala Python 3.11 o superior
    pause
    exit /b 1
)

REM Verificar dependencias
echo Verificando dependencias...
python -c "import schedule" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias necesarias...
    pip install schedule
)

REM Iniciar agente
echo Iniciando Background Agent...
echo.
python background_agent.py

pause


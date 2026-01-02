@echo off
REM ⚠️  DEPRECATED: This script is deprecated.
REM    Please use the unified launcher instead:
REM    - launch.bat (recommended)
REM    - python unified_launcher.py --mode chat
REM 
REM This script will continue to work but may be removed in future versions.
REM
setlocal enabledelayedexpansion
chcp 65001 >nul
title BMC Chatbot - Launcher One-Click (DEPRECATED)

echo ========================================
echo   BMC Chatbot - Launcher One-Click (DEPRECATED)
echo ========================================
echo.
echo ⚠️  NOTICE: This launcher is deprecated.
echo    Please use: launch.bat
echo    Or: python unified_launcher.py --mode chat
echo.
timeout /t 3 /nobreak >nul
echo.

set "PYTHON_CMD="
call :find_python
if not defined PYTHON_CMD (
    call :install_python
    call :find_python
    if not defined PYTHON_CMD (
        echo.
        echo No se pudo encontrar Python incluso después de intentar la instalación.
        echo Instala Python 3.11 o superior y vuelve a ejecutar este launcher.
        goto :end
    )
)

echo Usando Python: %PYTHON_CMD%
echo.

call :run_python_script instalar_dependencias_automatico.py "Instalando dependencias"
call :run_python_script configurar_entorno.py "Configurando archivo .env"
call :run_python_script gestionar_servicios.py "Gestionando servicios opcionales"
call :run_python_script verificar_sistema_completo.py "Verificando sistema completo"

echo.
echo ========================================
echo   Iniciando chatbot...
echo ========================================
echo.
"%PYTHON_CMD%" chat_interactivo.py
goto :end


:find_python
for %%P in (python python3 py) do (
    for /f "delims=" %%I in ('%%P -c "import sys; print(sys.executable)" 2^>nul') do (
        set "PYTHON_CMD=%%I"
        goto :eof
    )
)
set "PYTHON_CMD="
goto :eof


:install_python
echo Python 3.11+ no encontrado en el sistema.
set "CHOICE_RESULT=Y"
choice /M "¿Deseas descargar e iniciar el instalador oficial de Python 3.11.7?"
if errorlevel 2 goto :skip_install

set "PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
set "PYTHON_INSTALLER=%TEMP%\python-3.11.7-amd64.exe"

echo Descargando instalador desde %PYTHON_INSTALLER_URL%
powershell -Command "Invoke-WebRequest -Uri '%PYTHON_INSTALLER_URL%' -OutFile '%PYTHON_INSTALLER%'" || (
    echo No se pudo descargar automáticamente el instalador.
    echo Descárgalo manualmente desde: https://www.python.org/downloads/windows/
    goto :skip_install
)

if exist "%PYTHON_INSTALLER%" (
    echo Lanzando instalador. Marca la casilla "Add Python to PATH" durante la instalación.
    start "" "%PYTHON_INSTALLER%"
    echo Completa la instalación y luego regresa a esta ventana.
    pause
) else (
    echo Descarga fallida. Instala Python manualmente desde python.org.
)

:skip_install
goto :eof


:run_python_script
set "SCRIPT=%~1"
set "DESCRIPTION=%~2"
if not defined DESCRIPTION set "DESCRIPTION=Ejecutando %SCRIPT%"

if not exist "%SCRIPT%" (
    echo ❌ No se encontró %SCRIPT%.
    goto :error
)

echo %DESCRIPTION%...
"%PYTHON_CMD%" "%SCRIPT%"
if errorlevel 1 goto :error
echo.
goto :eof


:error
echo.
echo ⚠️  Se produjo un error. Revisa los mensajes anteriores.
pause
exit /b 1


:end
echo.
echo Launcher finalizado.
pause


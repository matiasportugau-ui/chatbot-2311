@echo off
REM Script para construir el instalador del chatbot BMC
chcp 65001 >nul
echo.
echo ========================================
echo   Constructor de Instalador BMC Chatbot
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "chat_interactivo.py" (
    echo ERROR: No se encuentra chat_interactivo.py
    echo Por favor ejecuta este script desde el directorio del proyecto
    pause
    exit /b 1
)

REM Crear directorio de build si no existe
if not exist "build" mkdir build
if not exist "dist" mkdir dist

echo [1/4] Verificando dependencias...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudo instalar PyInstaller
    pause
    exit /b 1
)
echo ✓ PyInstaller instalado

echo.
echo [2/4] Construyendo ejecutable con PyInstaller...
python -m PyInstaller chatbot_installer.spec --clean --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fallo la construccion del ejecutable
    pause
    exit /b 1
)
echo ✓ Ejecutable creado en dist\BMC_Chatbot.exe

echo.
echo [3/4] Verificando Inno Setup...
where iscc >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️  Inno Setup no encontrado en PATH
    echo.
    echo Para crear el instalador completo, necesitas Inno Setup:
    echo 1. Descarga desde: https://jrsoftware.org/isdl.php
    echo 2. Instala Inno Setup (gratis)
    echo 3. Agrega la carpeta de instalacion al PATH o ejecuta manualmente:
    echo    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
    echo.
    echo El ejecutable ya esta listo en: dist\BMC_Chatbot.exe
    echo Puedes distribuirlo directamente o crear el instalador mas tarde.
    echo.
    pause
    exit /b 0
)

echo ✓ Inno Setup encontrado en PATH
echo.
echo [4/4] Creando instalador con Inno Setup...
iscc installer.iss
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fallo la creacion del instalador
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✓ INSTALADOR CREADO EXITOSAMENTE
echo ========================================
echo.
echo El instalador esta en: dist\BMC_Chatbot_Setup.exe
echo.
echo Puedes distribuir este archivo a otros usuarios de Windows.
echo.
pause


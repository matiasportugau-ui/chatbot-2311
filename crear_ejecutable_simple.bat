@echo off
REM Script simple para crear solo el ejecutable .exe
chcp 65001 >nul
echo.
echo ========================================
echo   Creador de Ejecutable BMC Chatbot
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "chat_interactivo.py" (
    echo ERROR: No se encuentra chat_interactivo.py
    echo Por favor ejecuta este script desde el directorio del proyecto
    pause
    exit /b 1
)

REM Crear directorios si no existen
if not exist "build" mkdir build
if not exist "dist" mkdir dist

echo [1/2] Instalando PyInstaller...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudo instalar PyInstaller
    pause
    exit /b 1
)
echo ✓ PyInstaller instalado

echo.
echo [2/2] Construyendo ejecutable...
python -m PyInstaller chatbot_installer.spec --clean --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fallo la construccion del ejecutable
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✓ EJECUTABLE CREADO EXITOSAMENTE
echo ========================================
echo.
echo El ejecutable esta en: dist\BMC_Chatbot.exe
echo.
echo Puedes ejecutarlo directamente o distribuirlo a otros usuarios.
echo Tamaño aproximado: 50-100 MB (incluye Python y dependencias)
echo.
pause


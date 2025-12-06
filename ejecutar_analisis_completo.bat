@echo off
REM Script para ejecutar todos los análisis de integración
chcp 65001 >nul
echo.
echo ========================================
echo   ANÁLISIS COMPLETO DE INTEGRACIÓN
echo ========================================
echo.

REM Refresh PATH to include Python
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SYSTEM_PATH=%%B"
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USER_PATH=%%B"
set "PATH=%SYSTEM_PATH%;%USER_PATH%"

REM Try to find Python
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto :found_python
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python3
    goto :found_python
)

REM Try common Python installation paths
if exist "C:\Python*\python.exe" (
    for /f "delims=" %%i in ('dir /b /ad "C:\Python*"') do set "PYTHON_CMD=C:\%%i\python.exe"
    goto :found_python
)

if exist "%LOCALAPPDATA%\Programs\Python\Python*\python.exe" (
    for /f "delims=" %%i in ('dir /b /ad "%LOCALAPPDATA%\Programs\Python\Python*"') do set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\%%i\python.exe"
    goto :found_python
)

echo ❌ Python no encontrado. Por favor instala Python o agrega Python al PATH.
echo.
echo Puedes instalar Python desde:
echo - Microsoft Store: busca "Python 3.11"
echo - python.org: https://www.python.org/downloads/
echo.
pause
exit /b 1

:found_python
echo ✅ Python encontrado: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

echo ========================================
echo PASO 1: Analizar Conocimiento
echo ========================================
echo.
%PYTHON_CMD% analizar_conocimiento.py
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Error en analizar_conocimiento.py
    pause
)
echo.
echo Presiona cualquier tecla para continuar...
pause >nul

echo.
echo ========================================
echo PASO 2: Analizar Escenarios
echo ========================================
echo.
%PYTHON_CMD% analizar_escenarios.py
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Error en analizar_escenarios.py
    pause
)
echo.
echo Presiona cualquier tecla para continuar...
pause >nul

echo.
echo ========================================
echo PASO 3: Auditar Productos
echo ========================================
echo.
%PYTHON_CMD% auditar_productos.py
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Error en auditar_productos.py
    pause
)
echo.
echo Presiona cualquier tecla para continuar...
pause >nul

echo.
echo ========================================
echo PASO 4: Validar Integración
echo ========================================
echo.
%PYTHON_CMD% validar_integracion.py
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Error en validar_integracion.py
    pause
)
echo.
echo Presiona cualquier tecla para continuar...
pause >nul

echo.
echo ========================================
echo PASO 5: Probar Respuestas
echo ========================================
echo.
%PYTHON_CMD% test_respuestas_chatbot.py
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Error en test_respuestas_chatbot.py
    pause
)

echo.
echo ========================================
echo ✅ ANÁLISIS COMPLETO FINALIZADO
echo ========================================
echo.
echo Reportes generados:
echo - reporte_analisis_conocimiento.json
echo - reporte_analisis_escenarios.json
echo - reporte_auditoria_productos.json
echo - reporte_validacion.json
echo - reporte_pruebas_respuestas.json
echo.
pause


@echo off
REM Batch file to run the BMC chatbot on Windows
REM 
REM ⚠️  DEPRECATED: This script is deprecated.
REM    Please use the unified launcher instead:
REM    - launch.bat (recommended)
REM    - python unified_launcher.py --mode chat
REM 
REM This script will continue to work but may be removed in future versions.
REM
chcp 65001 >nul
echo.
echo ========================================
echo   BMC Chatbot Launcher (DEPRECATED)
echo ========================================
echo.
echo ⚠️  NOTICE: This launcher is deprecated.
echo    Please use: launch.bat
echo    Or: python unified_launcher.py --mode chat
echo.
timeout /t 3 /nobreak >nul
echo.

REM Refresh PATH to include Python from registry
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SYSTEM_PATH=%%B"
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USER_PATH=%%B"
set "PATH=%SYSTEM_PATH%;%USER_PATH%"

REM Try to find Python - check python command
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found Python in PATH
    python --version
    echo.
    echo Starting chatbot...
    echo Press Ctrl+C to exit
    echo.
    python chat_interactivo.py
    goto :end
)

REM Try python3 command
python3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found Python3 in PATH
    python3 --version
    echo.
    echo Starting chatbot...
    echo Press Ctrl+C to exit
    echo.
    python3 chat_interactivo.py
    goto :end
)

REM Try Python Launcher (py) - this is usually available even if python isn't in PATH
py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found Python Launcher (py) in PATH
    py --version
    echo.
    echo Starting chatbot...
    echo Press Ctrl+C to exit
    echo.
    py chat_interactivo.py
    goto :end
)

REM Try common Python installation paths
if exist "%LOCALAPPDATA%\Programs\Python" (
    for /f "delims=" %%i in ('dir /b /ad "%LOCALAPPDATA%\Programs\Python\Python*" 2^>nul') do (
        if exist "%LOCALAPPDATA%\Programs\Python\%%i\python.exe" (
            echo Found Python in: %LOCALAPPDATA%\Programs\Python\%%i
            "%LOCALAPPDATA%\Programs\Python\%%i\python.exe" --version
            echo.
            echo Starting chatbot...
            echo Press Ctrl+C to exit
            echo.
            "%LOCALAPPDATA%\Programs\Python\%%i\python.exe" chat_interactivo.py
            goto :end
        )
    )
)

REM Try C:\Python* paths
for /f "delims=" %%i in ('dir /b /ad "C:\Python*" 2^>nul') do (
    if exist "C:\%%i\python.exe" (
        echo Found Python in: C:\%%i
        "C:\%%i\python.exe" --version
        echo.
        echo Starting chatbot...
        echo Press Ctrl+C to exit
        echo.
        "C:\%%i\python.exe" chat_interactivo.py
        goto :end
    )
)

REM Python not found
echo.
echo ERROR: Python not found!
echo.
echo Please install Python 3.11 or 3.12:
echo 1. Download from: https://www.python.org/downloads/
echo 2. During installation, check "Add Python to PATH"
echo 3. Or install from Microsoft Store: "Python 3.11"
echo.
echo After installing, run this script again.
echo.
pause
exit /b 1

:end
echo.
echo Chatbot closed. Goodbye!
pause


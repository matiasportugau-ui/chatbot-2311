@echo off
REM Batch file to run the BMC chatbot on Windows with UTF-8 encoding
chcp 65001 >nul
echo.
echo ========================================
echo   BMC Chatbot Launcher
echo ========================================
echo.

REM Refresh PATH to include Python
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SYSTEM_PATH=%%B"
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USER_PATH=%%B"
set "PATH=%SYSTEM_PATH%;%USER_PATH%"

REM Try to find Python
where python >nul 2>&1
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

where python3 >nul 2>&1
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


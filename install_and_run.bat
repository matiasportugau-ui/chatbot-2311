@echo off
setlocal EnableDelayedExpansion

echo ================================================================
echo        BMC Chatbot System - Installer & Launcher               
echo ================================================================
echo.

REM Check for Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is required but not found.
    echo Please install Python 3.11 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check python version (simple check)
python --version 2>&1 | findstr "Python 3" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python 3 is required.
    echo Please install Python 3.11 or higher.
    pause
    exit /b 1
)

echo Starting Unified Launcher in Full Stack Mode...
echo This will:
echo 1. Install/Update dependencies
echo 2. Configure environment (.env)
echo 3. Launch API Server
echo 4. Launch Next.js Dashboard
echo.

REM Execute unified launcher with fullstack mode
python unified_launcher.py --mode fullstack

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo System exited with error code %ERRORLEVEL%
    echo Please check the logs in logs/launcher.log
    pause
)

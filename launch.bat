@echo off
REM Unified Launcher Wrapper for Windows
REM This script finds Python and executes the unified launcher

chcp 65001 >nul
title BMC Chatbot - Unified Launcher

REM Try to find Python
for %%P in (python python3 py) do (
    %%P --version >nul 2>&1
    if %%ERRORLEVEL% EQU 0 (
        echo Found Python: %%P
        %%P unified_launcher.py %*
        goto :end
    )
)

REM Python not found
echo.
echo ERROR: Python not found!
echo.
echo Please install Python 3.11+ and try again.
echo Download from: https://www.python.org/downloads/
echo.
pause
exit /b 1

:end
if %ERRORLEVEL% NEQ 0 (
    pause
)


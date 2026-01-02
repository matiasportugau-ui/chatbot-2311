@echo off
REM Script para configurar OpenAI API Key
chcp 65001 >nul
echo.
echo ========================================
echo   Configuracion de OpenAI
echo ========================================
echo.

REM Configurar variables de entorno para esta sesion
set OPENAI_API_KEY=sk-proj-TU-KEY-AQUI
set OPENAI_MODEL=gpt-4o-mini

echo Variables de entorno configuradas para esta sesion.
echo.
echo NOTA: Estas variables solo estan activas en esta ventana.
echo Para hacerlas permanentes, agrega estas lineas a tu archivo .env:
echo.
echo OPENAI_API_KEY=sk-proj-TU-KEY-AQUI
echo OPENAI_MODEL=gpt-4o-mini
echo.
echo Verificando configuracion...
echo.
python verificar_openai.py
echo.
pause


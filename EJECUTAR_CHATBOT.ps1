# PowerShell script para ejecutar el chatbot BMC
# Ejecuta este script con: pwsh EJECUTAR_CHATBOT.ps1
# Requiere PowerShell instalado: brew install --cask powershell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BMC Chatbot Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio del script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Detectar el sistema operativo
$isMacOS = $IsMacOS -or ($PSVersionTable.Platform -eq "Unix" -and (Get-Command uname -ErrorAction SilentlyContinue | ForEach-Object { & $_.Source -s } -ErrorAction SilentlyContinue) -eq "Darwin")
$pythonCmd = if ($isMacOS) { "python3" } else { "py" }

# Verificar Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = & $pythonCmd --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green
        Write-Host ""
        Write-Host "Iniciando chatbot..." -ForegroundColor Yellow
        Write-Host "Presiona Ctrl+C para salir" -ForegroundColor Gray
        Write-Host ""
        
        # Ejecutar chatbot
        & $pythonCmd chat_interactivo.py
    } else {
        throw "Python no encontrado"
    }
} catch {
    Write-Host "ERROR: Python no encontrado!" -ForegroundColor Red
    Write-Host ""
    if ($isMacOS) {
        Write-Host "Por favor instala Python 3.11 o 3.12:" -ForegroundColor Yellow
        Write-Host "1. Con Homebrew: brew install python@3.11" -ForegroundColor White
        Write-Host "2. O descarga desde: https://www.python.org/downloads/" -ForegroundColor White
    } else {
        Write-Host "Por favor instala Python 3.11 o 3.12:" -ForegroundColor Yellow
        Write-Host "1. Descarga desde: https://www.python.org/downloads/" -ForegroundColor White
        Write-Host "2. Durante la instalacion, marca 'Add Python to PATH'" -ForegroundColor White
        Write-Host "3. O instala desde Microsoft Store: 'Python 3.11'" -ForegroundColor White
    }
    Write-Host ""
    Read-Host "Presiona Enter para salir"
}


# PowerShell script to run the BMC chatbot
# This script finds Python and runs the interactive chatbot

Write-Host "BMC Chatbot Launcher" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host ""

# Function to find Python executable
function Find-Python {
    # Try common Python commands first
    $commands = @("python", "python3", "py")
    foreach ($cmd in $commands) {
        try {
            $result = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $result -match "Python 3\.\d+") {
                Write-Host "Found Python: $cmd" -ForegroundColor Green
                Write-Host "Version: $result" -ForegroundColor Gray
                return $cmd
            }
        } catch {
            continue
        }
    }
    
    # Try to find Python in common installation paths
    $paths = @(
        "$env:LOCALAPPDATA\Programs\Python",
        "$env:USERPROFILE\AppData\Local\Programs\Python",
        "C:\Program Files\Python*",
        "C:\Program Files (x86)\Python*"
    )
    
    foreach ($basePath in $paths) {
        $pythonDirs = Get-ChildItem -Path $basePath -Directory -ErrorAction SilentlyContinue
        foreach ($dir in $pythonDirs) {
            $pythonExe = Join-Path $dir.FullName "python.exe"
            if (Test-Path $pythonExe) {
                try {
                    $version = & $pythonExe --version 2>&1
                    if ($LASTEXITCODE -eq 0 -and $version -match "Python 3\.\d+") {
                        Write-Host "Found Python: $pythonExe" -ForegroundColor Green
                        Write-Host "Version: $version" -ForegroundColor Gray
                        return $pythonExe
                    }
                } catch {
                    continue
                }
            }
        }
    }
    
    return $null
}

# Find Python
Write-Host "Searching for Python..." -ForegroundColor Yellow
$pythonExe = Find-Python

if (-not $pythonExe) {
    Write-Host ""
    Write-Host "ERROR: Python 3 not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.11 or 3.12:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "2. During installation, check 'Add Python to PATH'" -ForegroundColor White
    Write-Host "3. Or install from Microsoft Store: 'Python 3.11'" -ForegroundColor White
    Write-Host ""
    Write-Host "After installing, run this script again." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the right directory
$chatbotFile = Join-Path $PSScriptRoot "chat_interactivo.py"
if (-not (Test-Path $chatbotFile)) {
    Write-Host "ERROR: chat_interactivo.py not found" -ForegroundColor Red
    Write-Host "Current directory: $PSScriptRoot" -ForegroundColor Gray
    Write-Host "Please run this script from the project root directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check dependencies
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$requirementsFile = Join-Path $PSScriptRoot "requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "Requirements file found" -ForegroundColor Gray
    $checkDeps = Read-Host "Install/update dependencies? (y/n)"
    if ($checkDeps -eq "y" -or $checkDeps -eq "Y") {
        Write-Host "Installing dependencies..." -ForegroundColor Yellow
        & $pythonExe -m pip install -r $requirementsFile
        if ($LASTEXITCODE -ne 0) {
            Write-Host "WARNING: Some dependencies may have failed to install" -ForegroundColor Yellow
        } else {
            Write-Host "Dependencies installed successfully" -ForegroundColor Green
        }
    }
}

# Run the chatbot
Write-Host ""
Write-Host "Starting chatbot..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to exit" -ForegroundColor Gray
Write-Host ""

try {
    & $pythonExe $chatbotFile
} catch {
    Write-Host ""
    Write-Host "ERROR running chatbot: $_" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Chatbot closed. Goodbye!" -ForegroundColor Cyan

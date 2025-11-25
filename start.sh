#!/bin/bash
# -*- coding: utf-8 -*-
# BMC Chatbot - Launcher for Linux/Codespaces
# Equivalent to INICIAR_CHATBOT.bat for Linux environments

set -e

echo "========================================"
echo "  BMC Chatbot - Launcher One-Click"
echo "========================================"
echo

# Function to find Python 3.11+
find_python() {
    local python_cmd=""
    for cmd in python3 python; do
        if command -v "$cmd" &> /dev/null; then
            version=$("$cmd" -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))" 2>/dev/null)
            major=$(echo "$version" | cut -d. -f1)
            minor=$(echo "$version" | cut -d. -f2)
            # Check for Python 4+ first, then for Python 3.11+
            if [[ "$major" -gt 3 ]] || [[ "$major" -eq 3 && "$minor" -ge 11 ]]; then
                python_cmd="$cmd"
                break
            fi
        fi
    done
    echo "$python_cmd"
}

# Function to run a Python script
run_python_script() {
    local script="$1"
    local description="$2"
    
    if [[ -z "$description" ]]; then
        description="Running $script"
    fi
    
    if [[ ! -f "$script" ]]; then
        echo "❌ Could not find $script."
        exit 1
    fi
    
    echo "$description..."
    "$PYTHON_CMD" "$script"
    echo
}

# Change to script directory
cd "$(dirname "$0")"

# Find Python 3.11+
PYTHON_CMD=$(find_python)

if [[ -z "$PYTHON_CMD" ]]; then
    echo
    echo "Python 3.11 or higher was not found on this system."
    echo
    echo "Please install Python 3.11+ manually:"
    echo "  - Ubuntu/Debian: sudo apt update && sudo apt install python3.11 python3.11-venv python3-pip"
    echo "  - Fedora: sudo dnf install python3.11"
    echo "  - macOS: brew install python@3.11"
    echo "  - Or download from: https://www.python.org/downloads/"
    echo
    echo "After installing Python 3.11+, run this script again."
    exit 1
fi

echo "Using Python: $PYTHON_CMD"
echo

# Run setup scripts in order
run_python_script "instalar_dependencias_automatico.py" "Installing dependencies"
run_python_script "configurar_entorno.py" "Configuring .env file"
run_python_script "gestionar_servicios.py" "Managing optional services"
run_python_script "verificar_sistema_completo.py" "Verifying complete system"

echo
echo "========================================"
echo "  Starting chatbot..."
echo "========================================"
echo

"$PYTHON_CMD" chat_interactivo.py

echo
echo "Launcher finished."

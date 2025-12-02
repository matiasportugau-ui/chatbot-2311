#!/bin/bash
# Alias útiles para gestión de procesos del proyecto BMC
# Agrega estos alias a tu ~/.bashrc o ejecútalos directamente

alias ps-bmc='/workspace/check_processes.sh'
alias status-bmc='cd /workspace && python3 gestionar_procesos.py status'
alias stop-bmc='cd /workspace && python3 gestionar_procesos.py stop'
alias help-bmc='cd /workspace && python3 gestionar_procesos.py help'

# Funciones útiles
kill-bmc() {
    if [ -z "$1" ]; then
        echo "Uso: kill-bmc <PID>"
        echo "Usa 'ps-bmc' para ver los PIDs activos"
    else
        echo "Deteniendo proceso $1..."
        kill "$1" && echo "✅ Proceso detenido" || echo "❌ No se pudo detener el proceso"
    fi
}

# Iniciar servicios comunes
start-chat() {
    cd /workspace && python3 chat_interactivo.py
}

start-api() {
    cd /workspace && python3 api_server.py
}

start-system() {
    cd /workspace && python3 sistema_completo_integrado.py
}

# Información
echo "✅ Aliases cargados para gestión de procesos BMC"
echo ""
echo "Comandos disponibles:"
echo "  ps-bmc       - Ver estado de procesos"
echo "  status-bmc   - Ver estado detallado"
echo "  stop-bmc     - Detener procesos (interactivo)"
echo "  kill-bmc     - Detener proceso por PID"
echo "  start-chat   - Iniciar chat interactivo"
echo "  start-api    - Iniciar API server"
echo "  start-system - Iniciar sistema completo"

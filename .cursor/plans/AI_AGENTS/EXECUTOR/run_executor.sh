#!/bin/bash
# Script de acceso rápido para el Execution AI Agent
# Uso: ./run_executor.sh [mode] [options]

cd "$(dirname "$0")/../.." || exit 1

# Si no se proporciona modo, usar 'full'
MODE="${1:-full}"
shift

# Ejecutar el agente
python AI_AGENTS/EXECUTOR/ejecutor_ai_assisted.py --mode "$MODE" "$@"



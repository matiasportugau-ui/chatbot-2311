#!/bin/bash
# Script de inicio rápido para Gravity Agent

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌌 Gravity Agent - Development Orchestration Specialist${NC}"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Error: python3 no encontrado${NC}"
    exit 1
fi

# Verificar que el script existe
if [ ! -f "$SCRIPT_DIR/gravity_agent.py" ]; then
    echo -e "${YELLOW}Error: gravity_agent.py no encontrado${NC}"
    exit 1
fi

# Función de ayuda
show_help() {
    echo "Uso: $0 [OPCIONES]"
    echo ""
    echo "Opciones:"
    echo "  --pr NUMERO          Analizar PR específico"
    echo "  --local              Analizar cambios locales"
    echo "  --mode MODE          Modo de ejecución (automated|interactive|dry_run|analysis_only)"
    echo "  --start-phase NUM    Fase inicial (default: -8)"
    echo "  --end-phase NUM      Fase final (default: 15)"
    echo "  --help               Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 --pr 87"
    echo "  $0 --local --mode dry_run"
    echo "  $0 --pr 87 --mode analysis_only"
    exit 0
}

# Parsear argumentos
ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done

# Si no hay argumentos, mostrar ayuda
if [ ${#ARGS[@]} -eq 0 ]; then
    show_help
fi

# Ejecutar Gravity Agent
echo -e "${GREEN}Ejecutando Gravity Agent...${NC}"
echo ""

python3 "$SCRIPT_DIR/gravity_agent.py" "${ARGS[@]}"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Gravity Agent completado exitosamente${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠️  Gravity Agent completado con código de salida: $EXIT_CODE${NC}"
fi

exit $EXIT_CODE

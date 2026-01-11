#!/bin/bash
# =============================================================================
# Development Orchestrator Agent - Script de Inicio Rápido
# =============================================================================
# Uso:
#   ./run_orchestrator.sh                    # Ciclo ReAct completo
#   ./run_orchestrator.sh --pr 87            # Analizar PR específico
#   ./run_orchestrator.sh --mode analyze     # Solo análisis
#   ./run_orchestrator.sh --mode plan        # Solo planificación
#   ./run_orchestrator.sh --mode execute     # Solo ejecución
#   ./run_orchestrator.sh --mode status      # Ver estado
# =============================================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🤖 Development Orchestrator Agent${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 no encontrado${NC}"
    exit 1
fi

# Verificar GitHub CLI
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLI (gh) no encontrado - algunas funciones limitadas${NC}"
fi

# Cambiar al directorio del workspace
cd "${WORKSPACE_ROOT}"

echo -e "${GREEN}📂 Workspace: ${WORKSPACE_ROOT}${NC}"
echo -e "${GREEN}✅ Auto-aprobación: Habilitada${NC}"
echo ""

# Ejecutar el agente con los argumentos proporcionados
python3 "${SCRIPT_DIR}/development_orchestrator_agent.py" "$@"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Ejecución completada${NC}"
echo -e "${GREEN}========================================${NC}"

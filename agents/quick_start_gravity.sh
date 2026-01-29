#!/bin/bash
# Quick Start Script for Gravity Orchestrator Agent

set -e

echo "=========================================="
echo "🚀 Gravity Orchestrator Agent - Quick Start"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instala Python 3.8+"
    exit 1
fi

echo -e "${GREEN}✅ Python encontrado${NC}"
echo ""

# Check orchestrator
echo "🔍 Verificando sistema de orquestación..."
if python3 -c "from scripts.orchestrator.main_orchestrator import MainOrchestrator" 2>/dev/null; then
    echo -e "${GREEN}✅ Orchestrator disponible${NC}"
else
    echo -e "${YELLOW}⚠️  Orchestrator no disponible. Algunas funciones pueden estar limitadas.${NC}"
fi
echo ""

# Menu
echo "Selecciona una acción:"
echo "1) Interpretar estado del proyecto"
echo "2) Crear plan de orquestación"
echo "3) Ejecutar orquestación completa (fases 0-15)"
echo "4) Ejecutar fase específica"
echo "5) Ver estado completo"
echo "6) Modo interactivo"
echo ""
read -p "Opción [1-6]: " option

case $option in
    1)
        echo ""
        echo "🔍 Interpretando estado del proyecto..."
        python3 agents/gravity_orchestrator_agent.py --action interpret
        ;;
    2)
        echo ""
        echo "📋 Creando plan de orquestación..."
        python3 agents/gravity_orchestrator_agent.py --action plan
        ;;
    3)
        echo ""
        read -p "¿Auto-aprobar fases? [S/n]: " auto_approve
        if [[ $auto_approve =~ ^[Nn]$ ]]; then
            python3 agents/gravity_orchestrator_agent.py --action execute --no-auto-approve
        else
            python3 agents/gravity_orchestrator_agent.py --action execute
        fi
        ;;
    4)
        echo ""
        read -p "Número de fase a ejecutar: " phase
        python3 agents/gravity_orchestrator_agent.py --action phase --phase $phase
        ;;
    5)
        echo ""
        echo "📊 Obteniendo estado completo..."
        python3 agents/gravity_orchestrator_agent.py --action status | python3 -m json.tool
        ;;
    6)
        echo ""
        echo "🤖 Modo interactivo"
        echo "Usa 'help' para ver comandos disponibles"
        python3 -c "
from agents.gravity_orchestrator_agent import GravityOrchestratorAgent, AgentMode

agent = GravityOrchestratorAgent(mode=AgentMode.HYBRID, auto_approve=True)
print('✅ Agente inicializado. Usa agent.interpret_project_state(), agent.create_orchestration_plan(), etc.')
print('Ejemplo: state = agent.interpret_project_state()')
"
        python3 -i -c "
from agents.gravity_orchestrator_agent import GravityOrchestratorAgent, AgentMode
agent = GravityOrchestratorAgent(mode=AgentMode.HYBRID, auto_approve=True)
"
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "✅ Completado"
echo "=========================================="

#!/bin/bash
# Gravity Training Orchestrator - Quick Commands
# Comandos rápidos para usar el agente

echo "=================================================="
echo "🚀 GRAVITY TRAINING ORCHESTRATOR - Quick Commands"
echo "=================================================="
echo ""

# Function to display menu
show_menu() {
    echo "Selecciona una opción:"
    echo ""
    echo "  1) Analizar PR #87"
    echo "  2) Ejecutar Phase 0 (Planning)"
    echo "  3) Ejecutar integración completa"
    echo "  4) Ver status actual"
    echo "  5) Quick start interactivo"
    echo "  6) Ver outputs generados"
    echo "  7) Ver logs"
    echo "  8) Leer documentación"
    echo "  9) Ver configuración"
    echo "  0) Salir"
    echo ""
}

# Main loop
while true; do
    show_menu
    read -p "Opción: " option
    
    case $option in
        1)
            echo ""
            echo "🔍 Analizando PR #87..."
            python3 AI_AGENTS/gravity_training_orchestrator.py --mode analyze
            echo ""
            read -p "Presiona Enter para continuar..."
            ;;
        2)
            echo ""
            echo "🎯 Ejecutando Phase 0 (Analysis & Planning)..."
            python3 AI_AGENTS/gravity_training_orchestrator.py --mode execute --phase phase_0
            echo ""
            read -p "Presiona Enter para continuar..."
            ;;
        3)
            echo ""
            echo "🚀 Ejecutando integración completa..."
            echo "⚠️  Esto ejecutará todas las fases (4.5 horas estimadas)"
            read -p "¿Continuar? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                python3 AI_AGENTS/gravity_training_orchestrator.py --mode execute
            else
                echo "❌ Cancelado"
            fi
            echo ""
            read -p "Presiona Enter para continuar..."
            ;;
        4)
            echo ""
            echo "📊 Generando status report..."
            python3 AI_AGENTS/gravity_training_orchestrator.py --mode status
            echo ""
            read -p "Presiona Enter para continuar..."
            ;;
        5)
            echo ""
            echo "🎮 Iniciando modo interactivo..."
            python3 AI_AGENTS/run_gravity_orchestrator.py --interactive
            ;;
        6)
            echo ""
            echo "📁 Outputs generados:"
            ls -lh consolidation/training_integration/ 2>/dev/null || echo "No hay outputs aún"
            echo ""
            read -p "Presiona Enter para continuar..."
            ;;
        7)
            echo ""
            echo "📝 Logs de ejecución:"
            ls -lh consolidation/training_integration/logs/ 2>/dev/null || echo "No hay logs aún"
            echo ""
            echo "Ver último log? (yes/no): "
            read show_log
            if [ "$show_log" = "yes" ]; then
                latest_log=$(ls -t consolidation/training_integration/logs/*.log 2>/dev/null | head -1)
                if [ -f "$latest_log" ]; then
                    tail -50 "$latest_log"
                else
                    echo "No hay logs disponibles"
                fi
            fi
            echo ""
            read -p "Presiona Enter para continuar..."
            ;;
        8)
            echo ""
            echo "📚 Documentación disponible:"
            echo ""
            echo "  - AI_AGENTS/GRAVITY_TRAINING_ORCHESTRATOR_README.md"
            echo "  - AI_AGENTS/GRAVITY_AGENT_EXECUTIVE_SUMMARY.md"
            echo "  - AI_AGENTS/gravity_orchestrator_config.json"
            echo ""
            echo "¿Qué documento deseas leer?"
            echo "  1) README completo"
            echo "  2) Executive Summary"
            echo "  3) Configuración"
            echo "  0) Volver"
            read -p "Opción: " doc_option
            
            case $doc_option in
                1)
                    less AI_AGENTS/GRAVITY_TRAINING_ORCHESTRATOR_README.md
                    ;;
                2)
                    less AI_AGENTS/GRAVITY_AGENT_EXECUTIVE_SUMMARY.md
                    ;;
                3)
                    cat AI_AGENTS/gravity_orchestrator_config.json | python3 -m json.tool
                    ;;
                0)
                    ;;
            esac
            echo ""
            read -p "Presiona Enter para continuar..."
            ;;
        9)
            echo ""
            echo "⚙️ Configuración del agente:"
            cat AI_AGENTS/gravity_orchestrator_config.json | python3 -m json.tool | head -50
            echo ""
            read -p "Presiona Enter para continuar..."
            ;;
        0)
            echo ""
            echo "👋 ¡Hasta luego!"
            exit 0
            ;;
        *)
            echo ""
            echo "❌ Opción inválida"
            echo ""
            read -p "Presiona Enter para continuar..."
            ;;
    esac
done

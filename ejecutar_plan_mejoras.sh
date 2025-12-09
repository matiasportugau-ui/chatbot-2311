#!/bin/bash
# Script para generar y ejecutar plan de mejoras con aprobación

echo "================================================================================"
echo "GENERADOR Y EJECUTOR DE PLAN DE MEJORAS"
echo "================================================================================"
echo ""
echo "⚠️  IMPORTANTE: Este script GENERA un plan pero NO lo ejecuta automáticamente."
echo "   Requerirá tu aprobación explícita antes de hacer cualquier cambio."
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ [ERROR] Python3 no está instalado"
    exit 1
fi

echo "✅ [OK] Python encontrado: $(python3 --version)"
echo ""

# Verificar que el script existe
if [ ! -f "repo_improvement_executor.py" ]; then
    echo "❌ [ERROR] repo_improvement_executor.py no encontrado"
    exit 1
fi

echo "✅ [OK] Script encontrado"
echo ""

# Opciones
echo "Opciones:"
echo "  1. Generar plan SOLO (no ejecutar)"
echo "  2. Generar plan y solicitar aprobación"
echo "  3. Ver ayuda"
echo ""

read -p "Selecciona opción [1]: " choice
choice=${choice:-1}

case $choice in
    1)
        echo ""
        echo "📋 Generando plan de ejecución..."
        python3 repo_improvement_executor.py --repo-path "$(pwd)" --plan-only
        ;;
    2)
        echo ""
        echo "📋 Generando plan y solicitando aprobación..."
        python3 repo_improvement_executor.py --repo-path "$(pwd)"
        ;;
    3)
        echo ""
        echo "Ayuda:"
        echo "  --plan-only: Solo genera el plan, no solicita aprobación"
        echo "  --approve-all: Aprobar todo automáticamente (NO recomendado)"
        echo ""
        echo "Ejemplo:"
        echo "  python3 repo_improvement_executor.py --plan-only"
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "================================================================================"
echo "✅ Proceso completado"
echo "================================================================================"


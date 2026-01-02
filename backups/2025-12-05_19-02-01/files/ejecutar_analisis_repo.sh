#!/bin/bash
# Script para ejecutar el agente de análisis del repositorio

echo "================================================================================"
echo "AGENTE DE IA PARA ANÁLISIS Y MEJORA DEL REPOSITORIO"
echo "================================================================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ [ERROR] Python3 no está instalado"
    exit 1
fi

echo "✅ [OK] Python encontrado: $(python3 --version)"
echo ""

# Verificar que el script existe
if [ ! -f "repo_analysis_improvement_agent.py" ]; then
    echo "❌ [ERROR] repo_analysis_improvement_agent.py no encontrado"
    exit 1
fi

echo "✅ [OK] Script encontrado"
echo ""

# Cargar credenciales automáticamente
if [ -f ".env.local" ]; then
    echo "📝 [INFO] Cargando credenciales desde .env.local..."
    export $(cat .env.local | grep -v '^#' | xargs)
elif [ -f ".env" ]; then
    echo "📝 [INFO] Cargando credenciales desde .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Ejecutar agente
echo "================================================================================"
echo "Ejecutando análisis del repositorio..."
echo "================================================================================"
echo ""

python3 repo_analysis_improvement_agent.py --repo-path "$(pwd)" --output "repo_analysis_$(date +%Y%m%d_%H%M%S).json"

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ [ERROR] La ejecución falló con código: $EXIT_CODE"
    exit $EXIT_CODE
fi

echo ""
echo "================================================================================"
echo "✅ [OK] Análisis completado exitosamente"
echo "================================================================================"
echo ""
echo "📄 Revisa el reporte generado:"
echo "   ls -lh repo_analysis_*.json | tail -1"
echo ""


#!/bin/bash
# Script para ejecutar el agente de investigación de repositorios iOS

echo "🚀 Iniciando Agente de Investigación de Repositorios iOS"
echo "========================================================"
echo ""

# Verificar que Python está disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Verificar que el script existe
if [ ! -f "repo_research_agent.py" ]; then
    echo "❌ repo_research_agent.py no encontrado"
    exit 1
fi

# Cargar variables de entorno si existen
if [ -f ".env.local" ]; then
    echo "📝 Cargando variables desde .env.local..."
    export $(cat .env.local | grep -v '^#' | xargs)
elif [ -f ".env" ]; then
    echo "📝 Cargando variables desde .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Verificar GITHUB_TOKEN
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN no está configurado"
    echo "   El agente funcionará pero con capacidades limitadas"
    echo ""
fi

# Ejecutar agente
echo "🔍 Ejecutando investigación..."
echo ""

python3 repo_research_agent.py \
    --workspace "$(pwd)" \
    --github-owner "${GITHUB_OWNER:-matiasportugau-ui}" \
    --output "repo_research_report_$(date +%Y%m%d_%H%M%S).json"

echo ""
echo "✅ Proceso completado"
echo ""
echo "📄 Revisa el reporte generado para ver los resultados"



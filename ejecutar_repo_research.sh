#!/bin/bash
# Script para ejecutar el agente local de investigación de repositorios iOS
# Linux/macOS Shell Script

echo "================================================================================"
echo "AGENTE LOCAL DE INVESTIGACIÓN DE REPOSITORIOS iOS"
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
if [ ! -f "local_repo_research_agent.py" ]; then
    echo "❌ [ERROR] local_repo_research_agent.py no encontrado"
    exit 1
fi

echo "✅ [OK] Script encontrado"
echo ""

# Cargar variables de entorno
if [ -f ".env.local" ]; then
    echo "📝 [INFO] Cargando variables desde .env.local..."
    export $(cat .env.local | grep -v '^#' | xargs)
elif [ -f ".env" ]; then
    echo "📝 [INFO] Cargando variables desde .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Verificar GITHUB_TOKEN
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  [ADVERTENCIA] GITHUB_TOKEN no está configurado"
    echo "   El agente funcionará pero con capacidades limitadas"
    echo ""
fi

# Ejecutar agente
echo "================================================================================"
echo "Ejecutando investigación..."
echo "================================================================================"
echo ""

python3 local_repo_research_agent.py --workspace "$(pwd)"

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ [ERROR] La ejecución falló con código: $EXIT_CODE"
    exit $EXIT_CODE
fi

echo ""
echo "================================================================================"
echo "✅ [OK] Proceso completado exitosamente"
echo "================================================================================"
echo ""
echo "📄 Revisa los archivos generados:"
echo "   - local_research_report_*.json"
echo "   - local_execution_*.json"
echo ""


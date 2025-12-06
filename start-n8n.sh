#!/bin/bash
echo "🚀 Iniciando n8n SIMPLE..."
echo ""

# Verificar Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Abre Docker Desktop primero."
    exit 1
fi

echo "✅ Docker está corriendo"
echo ""

# Iniciar n8n
echo "🐳 Iniciando n8n..."
docker-compose -f docker-compose-simple.yml up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ n8n iniciado!"
    echo ""
    echo "🌐 Acceso:"
    echo "   URL: http://localhost:5678"
    echo "   Usuario: admin"
    echo "   Contraseña: bmc2024"
    echo ""
    echo "📱 Webhook:"
    echo "   URL: http://localhost:5678/webhook/bmc-quote"
    echo "   Método: POST"
    echo ""
    echo "🧪 Probar:"
    echo "   curl -X POST http://localhost:5678/webhook/bmc-quote \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d \"{\\\"body\\\":{\\\"message\\\":\\\"Test Isodec 100mm\\\",\\\"from\\\":\\\"+59812345678\\\"}}\""
    echo ""
else
    echo "❌ Error iniciando n8n"
    exit 1
fi

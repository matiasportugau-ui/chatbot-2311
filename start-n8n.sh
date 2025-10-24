#!/bin/bash

echo "🚀 Iniciando n8n para BMC Quote System..."
echo ""

# Verificar si Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor:"
    echo "   1. Abre Docker Desktop"
    echo "   2. Espera a que esté completamente iniciado"
    echo "   3. Ejecuta este script nuevamente"
    echo ""
    exit 1
fi

echo "✅ Docker está corriendo"
echo ""

# Crear directorio para workflows si no existe
mkdir -p n8n-workflows

echo "📁 Directorio de workflows: $(pwd)/n8n-workflows"
echo ""

# Iniciar n8n con Docker Compose
echo "🐳 Iniciando n8n con Docker Compose..."
docker-compose -f docker-compose.n8n.yml up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ n8n iniciado exitosamente!"
    echo ""
    echo "🌐 URLs disponibles:"
    echo "   - n8n Interface: http://localhost:5678"
    echo "   - Usuario: admin"
    echo "   - Contraseña: bmc2024"
    echo ""
    echo "📊 Webhook URLs:"
    echo "   - WhatsApp Quote: http://localhost:5678/webhook/whatsapp-quote"
    echo ""
    echo "🔧 Comandos útiles:"
    echo "   - Ver logs: docker-compose -f docker-compose.n8n.yml logs -f"
    echo "   - Parar: docker-compose -f docker-compose.n8n.yml down"
    echo "   - Reiniciar: docker-compose -f docker-compose.n8n.yml restart"
    echo ""
    echo "🧪 Para probar el workflow:"
    echo "   - node test-n8n-workflow.js"
    echo "   - node test-n8n-workflow.js --webhook"
    echo ""
    
    # Esperar un momento y mostrar estado
    echo "⏳ Esperando que n8n esté completamente listo..."
    sleep 10
    
    # Verificar que n8n esté respondiendo
    if curl -s http://localhost:5678 > /dev/null; then
        echo "✅ n8n está respondiendo correctamente"
    else
        echo "⚠️  n8n puede estar aún iniciando. Intenta en unos segundos."
    fi
    
else
    echo ""
    echo "❌ Error iniciando n8n"
    echo "Verifica los logs con: docker-compose -f docker-compose.n8n.yml logs"
    exit 1
fi

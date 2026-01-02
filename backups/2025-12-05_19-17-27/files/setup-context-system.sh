#!/bin/bash

echo "🚀 Configurando Sistema de Gestión de Contexto..."

# Crear archivo .env.local si no existe
if [ ! -f .env.local ]; then
    echo "📝 Creando archivo .env.local..."
    cat > .env.local << EOF
# OpenAI API Key para gestión de contexto
OPENAI_API_KEY=tu_clave_openai_aqui

# Configuración del sistema de contexto
MAX_CONTEXT_TOKENS=8000
MAX_MESSAGES_PER_SESSION=20
INACTIVITY_TIMEOUT_MINUTES=30

# URLs de n8n (cuando esté configurado)
N8N_BASE_URL=http://localhost:5678

# Configuración de WhatsApp
WHATSAPP_PHONE_NUMBER_ID=tu_phone_id_aqui
WHATSAPP_ACCESS_TOKEN=tu_access_token_aqui

# Google Sheets
GOOGLE_SHEET_ID=tu_sheet_id_aqui

# MongoDB
MONGODB_URI=tu_mongodb_uri_aqui
EOF
    echo "✅ Archivo .env.local creado"
else
    echo "ℹ️  Archivo .env.local ya existe"
fi

# Verificar que las dependencias estén instaladas
echo "📦 Verificando dependencias..."
if ! npm list ai > /dev/null 2>&1; then
    echo "Instalando dependencias faltantes..."
    npm install ai openai
fi

# Crear directorio para logs si no existe
mkdir -p logs

echo "✅ Configuración completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Edita .env.local y agrega tu OPENAI_API_KEY"
echo "2. Ejecuta: npm run dev"
echo "3. Navega a http://localhost:3000"
echo "4. Ve a la pestaña 'Live Chat' para probar el sistema"
echo ""
echo "🔧 Para configurar n8n:"
echo "1. Instala n8n: npm install -g n8n"
echo "2. Ejecuta: n8n start"
echo "3. Importa los workflows desde /02_implementation/workflows/"
echo ""
echo "🎉 ¡Sistema listo para usar!"

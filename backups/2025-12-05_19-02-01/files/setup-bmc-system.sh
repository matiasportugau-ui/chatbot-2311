#!/bin/bash

echo "🚀 Configurando Sistema BMC de Cotización Inteligente..."

# 1. Crear archivo .env.local si no existe
ENV_FILE=".env.local"
if [ ! -f "$ENV_FILE" ]; then
  echo "📝 Creando archivo .env.local..."
  cat > "$ENV_FILE" << EOF
# BMC Sistema de Cotización Inteligente
# ======================================

# OpenAI API Key (REQUERIDO)
OPENAI_API_KEY=

# Google Sheets API (REQUERIDO)
GOOGLE_SHEET_ID=bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0
GOOGLE_SERVICE_ACCOUNT_EMAIL=
GOOGLE_PRIVATE_KEY=

# MongoDB Atlas (REQUERIDO)
MONGODB_URI=

# WhatsApp Business API (OPCIONAL - para producción)
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_VERIFY_TOKEN=bmc_whatsapp_verify_2024

# n8n Integration (OPCIONAL)
N8N_WEBHOOK_URL=http://localhost:5678/webhook/bmc-quotes
N8N_API_KEY=

# Sistema de Contexto
MAX_CONTEXT_TOKENS=8000
MAX_MESSAGES_PER_SESSION=20
INACTIVITY_TIMEOUT_MINUTES=30

# Configuración de Zona (para cálculo de flete)
DEFAULT_ZONE=montevideo
EOF
  echo "✅ Archivo .env.local creado"
else
  echo "✅ Archivo .env.local ya existe"
fi

# 2. Instalar dependencias
echo "📦 Instalando dependencias..."
npm install googleapis openai mongodb mongoose axios

# 3. Verificar estructura de directorios
echo "📁 Verificando estructura de directorios..."
mkdir -p src/lib
mkdir -p src/models
mkdir -p src/components/chat
mkdir -p src/components/dashboard
mkdir -p src/app/api/chat
mkdir -p src/app/api/quote-engine
mkdir -p src/app/api/sheets
mkdir -p src/app/api/parse-quote
mkdir -p src/app/api/whatsapp

echo "✅ Estructura de directorios verificada"

# 4. Crear archivo de configuración de MongoDB
echo "🗄️ Creando configuración de MongoDB..."
cat > "mongodb-config.json" << EOF
{
  "database": "bmc_quotes",
  "collections": {
    "quotes": "Cotizaciones principales",
    "sessions": "Sesiones de chat",
    "context": "Contexto de conversaciones",
    "products": "Base de conocimiento de productos",
    "analytics": "Métricas y analytics"
  },
  "indexes": [
    {
      "collection": "quotes",
      "fields": ["arg", "telefono", "estado", "fecha"]
    },
    {
      "collection": "sessions",
      "fields": ["session_id", "user_phone", "status"]
    }
  ]
}
EOF

# 5. Crear archivo de configuración de Google Sheets
echo "📊 Creando configuración de Google Sheets..."
cat > "sheets-config.json" << EOF
{
  "spreadsheet_id": "bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0",
  "tabs": {
    "admin": "Admin.",
    "enviados": "Enviados", 
    "confirmado": "Confirmado"
  },
  "columns": {
    "A": "Arg",
    "B": "Estado",
    "C": "Fecha",
    "D": "Cliente",
    "E": "Origen",
    "F": "Telefono",
    "G": "Direccion",
    "H": "Consulta"
  },
  "mapping": {
    "estados": ["Pendiente", "Adjunto", "Listo", "Enviado", "Asignado", "Confirmado"],
    "origenes": ["WA", "LO", "EM", "CL"]
  }
}
EOF

# 6. Crear archivo de configuración de productos BMC
echo "🏗️ Creando configuración de productos BMC..."
cat > "products-config.json" << EOF
{
  "empresa": "BMC Construcciones",
  "productos_principales": [
    {
      "id": "isodec",
      "nombre": "Isodec EPS",
      "descripcion": "Panel aislante de poliestireno expandido",
      "grosor_disponible": [50, 100, 150, 200],
      "precio_base": 45,
      "unidad": "m2"
    },
    {
      "id": "isoroof",
      "nombre": "Isoroof",
      "descripcion": "Panel aislante para techos",
      "grosor_disponible": [30, 50, 80],
      "precio_base": 65,
      "unidad": "m2"
    },
    {
      "id": "isopanel",
      "nombre": "Isopanel",
      "descripcion": "Panel aislante de uso general",
      "grosor_disponible": [50, 100, 150, 200, 250],
      "precio_base": 55,
      "unidad": "m2"
    },
    {
      "id": "isowall",
      "nombre": "Isowall",
      "descripcion": "Panel aislante para paredes exteriores",
      "grosor_disponible": [50, 100, 150],
      "precio_base": 50,
      "unidad": "m2"
    },
    {
      "id": "chapa_galvanizada",
      "nombre": "Chapa Galvanizada",
      "descripcion": "Chapa de acero galvanizado",
      "grosor_disponible": [0.30, 0.41, 0.50],
      "precio_base": 25,
      "unidad": "m2"
    },
    {
      "id": "calameria",
      "nombre": "Calamería",
      "descripcion": "Estructura metálica de soporte",
      "grosor_disponible": [1.5, 2.0, 2.5],
      "precio_base": 15,
      "unidad": "ml"
    }
  ],
  "servicios": {
    "instalacion": {
      "base": 100,
      "por_m2": 15,
      "minimo": 200
    },
    "flete": {
      "base": 50,
      "por_km": 2.5,
      "minimo": 80
    }
  },
  "zonas_flete": {
    "montevideo": {"multiplicador": 1.0, "flete_base": 50},
    "canelones": {"multiplicador": 1.2, "flete_base": 80},
    "maldonado": {"multiplicador": 1.5, "flete_base": 120},
    "rivera": {"multiplicador": 2.0, "flete_base": 200},
    "artigas": {"multiplicador": 2.5, "flete_base": 250}
  }
}
EOF

echo "✅ Configuración completada!"
echo ""
echo "📋 PRÓXIMOS PASOS CRÍTICOS:"
echo ""
echo "1. 🔑 CONFIGURAR CREDENCIALES (.env.local):"
echo "   - OPENAI_API_KEY: Obtener de https://platform.openai.com/api-keys"
echo "   - GOOGLE_SERVICE_ACCOUNT_EMAIL: Crear en Google Cloud Console"
echo "   - GOOGLE_PRIVATE_KEY: Descargar JSON de Service Account"
echo "   - MONGODB_URI: Crear cluster en MongoDB Atlas"
echo ""
echo "2. 📊 CONFIGURAR GOOGLE SHEETS:"
echo "   - Compartir el Sheet con el email del Service Account"
echo "   - Verificar permisos de lectura/escritura"
echo ""
echo "3. 🚀 EJECUTAR SISTEMA:"
echo "   - npm run dev"
echo "   - Navegar a http://localhost:3000"
echo "   - Probar chat en /bmc-chat"
echo ""
echo "4. 🧪 TESTING:"
echo "   - Probar cotizaciones con diferentes productos"
echo "   - Verificar integración con Google Sheets"
echo "   - Validar respuestas del motor de IA"
echo ""
echo "🎉 ¡Sistema BMC de Cotización Inteligente listo para configurar!"

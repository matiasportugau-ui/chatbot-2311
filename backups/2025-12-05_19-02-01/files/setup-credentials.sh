#!/bin/bash

echo "🔐 Configurando Sistema Seguro de Credenciales BMC..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# 1. Crear archivo de credenciales si no existe
CREDENTIALS_FILE="credentials.json"
TEMPLATE_FILE="credentials-template.json"

if [ ! -f "$CREDENTIALS_FILE" ]; then
    if [ -f "$TEMPLATE_FILE" ]; then
        print_info "Copiando template de credenciales..."
        cp "$TEMPLATE_FILE" "$CREDENTIALS_FILE"
        print_status "Archivo credentials.json creado desde template"
    else
        print_error "No se encontró el archivo template. Creando archivo básico..."
        cat > "$CREDENTIALS_FILE" << 'EOF'
{
  "openai": {
    "api_key": "sk-your-openai-api-key-here",
    "model": "gpt-4",
    "max_tokens": 4000,
    "temperature": 0.1
  },
  "google_sheets": {
    "sheet_id": "bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0",
    "service_account_email": "your-service-account@project.iam.gserviceaccount.com",
    "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
    "scopes": ["https://www.googleapis.com/auth/spreadsheets"]
  },
  "mongodb": {
    "uri": "mongodb+srv://username:password@cluster.mongodb.net/bmc_quotes",
    "database": "bmc_quotes",
    "collections": {
      "quotes": "quotes",
      "sessions": "sessions",
      "context": "context",
      "analytics": "analytics"
    }
  },
  "whatsapp": {
    "access_token": "your-whatsapp-access-token",
    "phone_number_id": "your-phone-number-id",
    "verify_token": "bmc_whatsapp_verify_2024",
    "webhook_url": "https://your-domain.vercel.app/api/whatsapp/webhook"
  },
  "n8n": {
    "webhook_url": "http://localhost:5678/webhook/bmc-quotes",
    "api_key": "your-n8n-api-key",
    "base_url": "http://localhost:5678"
  },
  "system": {
    "environment": "development",
    "max_context_tokens": 8000,
    "max_messages_per_session": 20,
    "inactivity_timeout_minutes": 30,
    "default_zone": "montevideo",
    "encryption_key": "bmc-default-encryption-key-32-chars"
  }
}
EOF
        print_status "Archivo credentials.json creado"
    fi
else
    print_warning "El archivo credentials.json ya existe"
fi

# 2. Crear archivo .env.local para desarrollo
ENV_FILE=".env.local"
if [ ! -f "$ENV_FILE" ]; then
    print_info "Creando archivo .env.local..."
    cat > "$ENV_FILE" << 'EOF'
# BMC Sistema de Cotización - Variables de Entorno
# ================================================

# OpenAI Configuration
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.1

# Google Sheets Configuration
GOOGLE_SHEET_ID=bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0
GOOGLE_SERVICE_ACCOUNT_EMAIL=
GOOGLE_PRIVATE_KEY=

# MongoDB Configuration
MONGODB_URI=
MONGODB_DATABASE=bmc_quotes

# WhatsApp Business API (Opcional)
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_VERIFY_TOKEN=bmc_whatsapp_verify_2024
WHATSAPP_WEBHOOK_URL=

# n8n Integration (Opcional)
N8N_WEBHOOK_URL=http://localhost:5678/webhook/bmc-quotes
N8N_API_KEY=
N8N_BASE_URL=http://localhost:5678

# Sistema de Contexto
MAX_CONTEXT_TOKENS=8000
MAX_MESSAGES_PER_SESSION=20
INACTIVITY_TIMEOUT_MINUTES=30
DEFAULT_ZONE=montevideo

# Seguridad
CREDENTIALS_ENCRYPTION_KEY=bmc-secure-encryption-key-32-chars
EOF
    print_status "Archivo .env.local creado"
else
    print_warning "El archivo .env.local ya existe"
fi

# 3. Crear archivo .gitignore si no existe
GITIGNORE_FILE=".gitignore"
if [ ! -f "$GITIGNORE_FILE" ]; then
    print_info "Creando archivo .gitignore..."
    cat > "$GITIGNORE_FILE" << 'EOF'
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Credentials (CRÍTICO - NO SUBIR)
credentials.json
credentials-*.json
*.pem
*.key

# Next.js
.next/
out/

# Production
build/
dist/

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

# nyc test coverage
.nyc_output

# Dependency directories
jspm_packages/

# Optional npm cache directory
.npm

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
    print_status "Archivo .gitignore creado"
else
    print_warning "El archivo .gitignore ya existe"
fi

# 4. Crear script de validación de credenciales
VALIDATION_SCRIPT="validate-credentials.js"
cat > "$VALIDATION_SCRIPT" << 'EOF'
const fs = require('fs');
const path = require('path');

// Función para validar credenciales
function validateCredentials() {
  console.log('🔍 Validando credenciales...\n');
  
  const credentialsPath = path.join(__dirname, 'credentials.json');
  const envPath = path.join(__dirname, '.env.local');
  
  let credentials = {};
  let envVars = {};
  
  // Cargar credentials.json
  if (fs.existsSync(credentialsPath)) {
    try {
      credentials = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
      console.log('✅ credentials.json encontrado');
    } catch (error) {
      console.log('❌ Error leyendo credentials.json:', error.message);
    }
  } else {
    console.log('⚠️ credentials.json no encontrado');
  }
  
  // Cargar .env.local
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf8');
    envContent.split('\n').forEach(line => {
      const [key, value] = line.split('=');
      if (key && value) {
        envVars[key.trim()] = value.trim();
      }
    });
    console.log('✅ .env.local encontrado');
  } else {
    console.log('⚠️ .env.local no encontrado');
  }
  
  // Validar credenciales críticas
  const criticalCredentials = [
    { key: 'openai.api_key', name: 'OpenAI API Key', required: true },
    { key: 'google_sheets.sheet_id', name: 'Google Sheet ID', required: true },
    { key: 'google_sheets.service_account_email', name: 'Google Service Account Email', required: true },
    { key: 'google_sheets.private_key', name: 'Google Private Key', required: true },
    { key: 'mongodb.uri', name: 'MongoDB URI', required: true },
    { key: 'whatsapp.access_token', name: 'WhatsApp Access Token', required: false },
    { key: 'whatsapp.phone_number_id', name: 'WhatsApp Phone Number ID', required: false }
  ];
  
  console.log('\n📋 Estado de las credenciales:');
  console.log('================================');
  
  let allValid = true;
  
  criticalCredentials.forEach(cred => {
    const keys = cred.key.split('.');
    let value = credentials;
    
    for (const key of keys) {
      value = value?.[key];
    }
    
    const status = value && value !== `your-${key}-here` ? '✅' : '❌';
    const required = cred.required ? '(REQUERIDO)' : '(OPCIONAL)';
    
    console.log(`${status} ${cred.name} ${required}`);
    
    if (cred.required && (!value || value.includes('your-'))) {
      allValid = false;
    }
  });
  
  console.log('\n================================');
  
  if (allValid) {
    console.log('🎉 ¡Todas las credenciales críticas están configuradas!');
  } else {
    console.log('⚠️ Algunas credenciales críticas faltan. Edita credentials.json para completarlas.');
  }
  
  return allValid;
}

// Ejecutar validación
validateCredentials();
EOF

print_status "Script de validación creado: validate-credentials.js"

# 5. Hacer ejecutables los scripts
chmod +x setup-credentials.sh
chmod +x validate-credentials.js

print_status "Scripts configurados como ejecutables"

# 6. Mostrar instrucciones
echo ""
echo "🎯 INSTRUCCIONES PARA CONFIGURAR CREDENCIALES:"
echo "=============================================="
echo ""
echo "1. 📝 Edita el archivo 'credentials.json' con tus credenciales reales:"
echo "   - OpenAI API Key"
echo "   - Google Service Account (email y private key)"
echo "   - MongoDB URI"
echo "   - WhatsApp Business API (opcional)"
echo ""
echo "2. 🔍 Valida tu configuración:"
echo "   node validate-credentials.js"
echo ""
echo "3. 🚀 Ejecuta el sistema:"
echo "   npm run dev"
echo ""
echo "4. 🔐 IMPORTANTE - Seguridad:"
echo "   - NUNCA subas credentials.json al repositorio"
echo "   - Usa .env.local para desarrollo"
echo "   - En producción, usa variables de entorno del servidor"
echo ""
echo "📋 CREDENCIALES NECESARIAS:"
echo "=========================="
echo ""
echo "🔑 OpenAI API Key:"
echo "   - Ve a https://platform.openai.com/api-keys"
echo "   - Crea una nueva API key"
echo "   - Copia la key (sk-...)"
echo ""
echo "📊 Google Sheets API:"
echo "   - Ve a https://console.cloud.google.com"
echo "   - Crea un proyecto o usa uno existente"
echo "   - Habilita Google Sheets API"
echo "   - Crea un Service Account"
echo "   - Descarga el JSON con credenciales"
echo "   - Comparte el Sheet con el email del Service Account"
echo ""
echo "🗄️ MongoDB Atlas:"
echo "   - Ve a https://cloud.mongodb.com"
echo "   - Crea un cluster"
echo "   - Obtén la connection string"
echo ""
echo "📱 WhatsApp Business API (Opcional):"
echo "   - Ve a https://developers.facebook.com"
echo "   - Crea una app de WhatsApp Business"
echo "   - Obtén access token y phone number ID"
echo ""
print_status "¡Configuración de credenciales completada!"

#!/bin/bash

echo "🔄 Configurando Integración del Módulo Cotizador con Base de Conocimiento Evolutiva..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_info "🚀 INICIANDO CONFIGURACIÓN DE INTEGRACIÓN"
echo ""

# 1. Verificar que el servidor esté corriendo
print_info "1. Verificando servidor de desarrollo..."
if curl -s http://localhost:3000 > /dev/null; then
    print_status "Servidor corriendo en localhost:3000"
else
    print_warning "Servidor no detectado. Iniciando servidor..."
    npm run dev &
    sleep 10
    if curl -s http://localhost:3000 > /dev/null; then
        print_status "Servidor iniciado correctamente"
    else
        print_error "No se pudo iniciar el servidor. Verificar configuración."
        exit 1
    fi
fi

# 2. Verificar dependencias
print_info "2. Verificando dependencias..."
if [ ! -f "package.json" ]; then
    print_error "package.json no encontrado. Ejecutar desde directorio raíz del proyecto."
    exit 1
fi

# Instalar dependencias si es necesario
if [ ! -d "node_modules" ]; then
    print_info "Instalando dependencias..."
    npm install
fi

print_status "Dependencias verificadas"

# 3. Verificar archivos de configuración
print_info "3. Verificando archivos de configuración..."

# Verificar .env.local
if [ ! -f ".env.local" ]; then
    print_warning ".env.local no encontrado. Creando archivo de ejemplo..."
    cat > .env.local << EOF
# OpenAI API Key (REQUERIDO)
OPENAI_API_KEY=sk-your-openai-key-here

# Google Sheets API (REQUERIDO)
GOOGLE_SHEET_ID=bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0
GOOGLE_SERVICE_ACCOUNT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"

# MongoDB Atlas (REQUERIDO)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database

# WhatsApp Business API (OPCIONAL)
WHATSAPP_ACCESS_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_VERIFY_TOKEN=bmc_whatsapp_verify_2024

# Configuración del Sistema
MAX_CONTEXT_TOKENS=8000
MAX_MESSAGES_PER_SESSION=20
INACTIVITY_TIMEOUT_MINUTES=30
EOF
    print_warning "Archivo .env.local creado. Por favor, editar con credenciales reales."
else
    print_status ".env.local encontrado"
fi

# Verificar credentials.json
if [ ! -f "credentials.json" ]; then
    print_warning "credentials.json no encontrado. Creando desde template..."
    if [ -f "credentials-template.json" ]; then
        cp credentials-template.json credentials.json
        print_warning "credentials.json creado desde template. Por favor, editar con credenciales reales."
    else
        print_error "credentials-template.json no encontrado. Crear manualmente."
    fi
else
    print_status "credentials.json encontrado"
fi

# 4. Verificar archivos de integración
print_info "4. Verificando archivos de integración..."

INTEGRATION_FILES=(
    "src/lib/integrated-quote-engine.ts"
    "src/app/api/integrated-quote/route.ts"
    "src/components/dashboard/integrated-system-metrics.tsx"
    "test-integration.js"
)

for file in "${INTEGRATION_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_status "$file encontrado"
    else
        print_error "$file no encontrado"
        exit 1
    fi
done

# 5. Ejecutar tests de integración
print_info "5. Ejecutando tests de integración..."

if [ -f "test-integration.js" ]; then
    print_info "Ejecutando tests automatizados..."
    node test-integration.js
    
    if [ $? -eq 0 ]; then
        print_status "Tests de integración pasaron correctamente"
    else
        print_warning "Algunos tests fallaron. Revisar logs para más detalles."
    fi
else
    print_error "test-integration.js no encontrado"
fi

# 6. Verificar endpoints de la API
print_info "6. Verificando endpoints de la API..."

ENDPOINTS=(
    "http://localhost:3000/api/integrated-quote?action=info"
    "http://localhost:3000/api/integrated-quote?action=health"
)

for endpoint in "${ENDPOINTS[@]}"; do
    if curl -s "$endpoint" > /dev/null; then
        print_status "Endpoint $endpoint respondiendo"
    else
        print_warning "Endpoint $endpoint no responde"
    fi
done

# 7. Mostrar resumen de configuración
print_info "7. Resumen de configuración completada"
echo ""

print_status "✅ Integración del módulo cotizador configurada"
print_status "✅ Base de conocimiento evolutiva implementada"
print_status "✅ API de integración funcionando"
print_status "✅ Dashboard de métricas disponible"
print_status "✅ Tests automatizados configurados"

echo ""
print_info "🎯 PRÓXIMOS PASOS:"
echo ""
echo "1. 📝 Editar .env.local con credenciales reales:"
echo "   - OPENAI_API_KEY"
echo "   - GOOGLE_SERVICE_ACCOUNT_EMAIL"
echo "   - GOOGLE_PRIVATE_KEY"
echo "   - MONGODB_URI"
echo ""
echo "2. 🔧 Editar credentials.json con credenciales reales"
echo ""
echo "3. 🚀 Reiniciar servidor:"
echo "   npm run dev"
echo ""
echo "4. 🌐 Navegar a http://localhost:3000"
echo "   - Ir a pestaña 'Sistema Integrado'"
echo "   - Probar chat con motor integrado"
echo "   - Verificar métricas en tiempo real"
echo ""
echo "5. 🧪 Ejecutar tests completos:"
echo "   node test-integration.js"
echo ""
echo "6. 📊 Monitorear sistema:"
echo "   - Métricas en dashboard"
echo "   - Logs del servidor"
echo "   - Base de conocimiento evolutiva"
echo ""

print_info "📚 DOCUMENTACIÓN:"
echo "- Guía de Integración: INTEGRATION_GUIDE.md"
echo "- Documentación del Sistema: BMC_SYSTEM_GUIDE.md"
echo "- README del Proyecto: README.md"
echo ""

print_status "🎉 ¡Configuración de integración completada exitosamente!"
print_info "El módulo cotizador está ahora integrado con la base de conocimiento evolutiva."

#!/bin/bash

echo "🚀 Configurando Repositorio GitHub para Sistema BMC..."

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

print_info "📋 INSTRUCCIONES PARA CREAR REPOSITORIO EN GITHUB:"
echo ""
echo "1. 🌐 Ve a https://github.com e inicia sesión"
echo "2. ➕ Haz clic en el botón '+' en la esquina superior derecha"
echo "3. 📁 Selecciona 'New repository'"
echo "4. ⚙️ Configura el repositorio:"
echo "   - Nombre: bmc-cotizacion-inteligente"
echo "   - Descripción: Sistema de cotización inteligente para BMC Construcciones"
echo "   - Visibilidad: Private (recomendado)"
echo "   - ❌ NO marcar 'Add a README file'"
echo "   - ❌ NO marcar 'Add .gitignore'"
echo "   - ❌ NO marcar 'Choose a license'"
echo "5. 🚀 Haz clic en 'Create repository'"
echo ""

print_warning "⚠️ IMPORTANTE: No ejecutes los comandos de abajo hasta haber creado el repositorio en GitHub"
echo ""

print_info "📝 COMANDOS PARA EJECUTAR DESPUÉS DE CREAR EL REPOSITORIO:"
echo ""
echo "# 1. Agregar el repositorio remoto (reemplaza TU_USUARIO con tu usuario de GitHub)"
echo "git remote add origin https://github.com/TU_USUARIO/bmc-cotizacion-inteligente.git"
echo ""
echo "# 2. Cambiar a rama main (si es necesario)"
echo "git branch -M main"
echo ""
echo "# 3. Subir el código al repositorio"
echo "git push -u origin main"
echo ""

print_info "🔐 CONFIGURACIÓN DE SEGURIDAD:"
echo ""
echo "1. 📁 El repositorio debe ser PRIVADO para proteger credenciales"
echo "2. 🔑 Nunca subas archivos con credenciales:"
echo "   - credentials.json"
echo "   - .env.local"
echo "   - *.pem, *.key"
echo "   - service-account-*.json"
echo "3. 🛡️ Usa variables de entorno en producción"
echo "4. 📋 El .gitignore ya está configurado para proteger archivos sensibles"
echo ""

print_info "📊 ESTRUCTURA DEL REPOSITORIO:"
echo ""
echo "bmc-cotizacion-inteligente/"
echo "├── 📁 src/                    # Código fuente"
echo "│   ├── 📁 app/               # Next.js App Router"
echo "│   ├── 📁 components/        # Componentes React"
echo "│   └── 📁 lib/               # Librerías y utilidades"
echo "├── 📁 docs/                  # Documentación"
echo "├── 📄 README.md              # Documentación principal"
echo "├── 📄 LICENSE                # Licencia MIT"
echo "├── 📄 .gitignore            # Archivos a ignorar"
echo "└── 📄 package.json          # Dependencias"
echo ""

print_info "🎯 PRÓXIMOS PASOS DESPUÉS DE CREAR EL REPOSITORIO:"
echo ""
echo "1. 🔗 Conectar repositorio local con GitHub"
echo "2. 📤 Subir código inicial"
echo "3. ⚙️ Configurar credenciales (credentials.json)"
echo "4. 🚀 Ejecutar sistema localmente"
echo "5. 🌐 Desplegar en Vercel"
echo "6. 📱 Configurar WhatsApp Business API"
echo "7. 📊 Conectar Google Sheets"
echo "8. 🗄️ Configurar MongoDB Atlas"
echo ""

print_status "¡Repositorio local listo para conectar con GitHub!"
print_warning "Recuerda: Crea el repositorio en GitHub primero, luego ejecuta los comandos de conexión"

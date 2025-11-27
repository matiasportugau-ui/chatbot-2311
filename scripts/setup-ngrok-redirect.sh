#!/bin/bash

# Script para configurar ngrok como Redirect URI para Mercado Libre OAuth
# Uso: ./scripts/setup-ngrok-redirect.sh

set -e

echo "🔧 Configurando ngrok para Mercado Libre OAuth..."
echo ""

# Verificar que ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok no está instalado."
    echo "📦 Instalando ngrok..."
    brew install ngrok/ngrok/ngrok
    echo ""
    echo "⚠️  Necesitas autenticarte con ngrok:"
    echo "   1. Ve a https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "   2. Copia tu authtoken"
    echo "   3. Ejecuta: ngrok config add-authtoken TU_TOKEN"
    echo ""
    read -p "¿Ya tienes el token y quieres continuar? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verificar que Next.js está corriendo
if ! lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Next.js no está corriendo en el puerto 3000"
    echo "   Inicia el servidor con: npm run dev"
    echo ""
    read -p "¿Quieres que inicie el servidor ahora? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Iniciando Next.js en background..."
        npm run dev > /dev/null 2>&1 &
        sleep 3
    else
        echo "❌ Por favor inicia el servidor manualmente y vuelve a ejecutar este script"
        exit 1
    fi
fi

# Iniciar ngrok
echo "🌐 Iniciando túnel ngrok..."
ngrok http 3000 > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!
sleep 3

# Obtener la URL de ngrok (soporta tanto .ngrok-free.app como .ngrok.io)
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -oE 'https://[^"]*\.ngrok(-free)?\.(app|io)' | head -1)

if [ -z "$NGROK_URL" ]; then
    echo "❌ No se pudo obtener la URL de ngrok"
    echo "   Verifica que ngrok esté corriendo: tail -f /tmp/ngrok.log"
    kill $NGROK_PID 2>/dev/null || true
    exit 1
fi

REDIRECT_URI="${NGROK_URL}/api/mercado-libre/auth/callback"

echo "✅ Túnel ngrok activo: $NGROK_URL"
echo "📍 Redirect URI: $REDIRECT_URI"
echo ""

# Actualizar .env.local
ENV_FILE=".env.local"
if [ -f "$ENV_FILE" ]; then
    # Remover la línea antigua de MERCADO_LIBRE_REDIRECT_URI si existe
    sed -i.bak '/^MERCADO_LIBRE_REDIRECT_URI=/d' "$ENV_FILE"
    echo "✅ Actualizado .env.local"
else
    echo "⚠️  .env.local no existe, creándolo..."
fi

# Agregar la nueva Redirect URI
echo "MERCADO_LIBRE_REDIRECT_URI=$REDIRECT_URI" >> "$ENV_FILE"

echo ""
echo "📋 PRÓXIMOS PASOS MANUALES:"
echo ""
echo "1. Agrega esta URL en developers.mercadolibre.com:"
echo "   $REDIRECT_URI"
echo ""
echo "2. Actualiza Vercel (opcional para desarrollo):"
echo "   vercel env add MERCADO_LIBRE_REDIRECT_URI"
echo "   (pega: $REDIRECT_URI)"
echo ""
echo "3. Reinicia tu servidor Next.js para que tome la nueva variable:"
echo "   npm run dev"
echo ""
echo "4. Prueba el flujo OAuth desde tu dashboard"
echo ""
echo "⚠️  NOTA: Esta URL de ngrok cambiará cada vez que reinicies ngrok."
echo "   Guarda este script para regenerarla fácilmente."
echo ""
echo "🛑 Para detener ngrok: kill $NGROK_PID"
echo "   O simplemente presiona Ctrl+C en la terminal donde corre ngrok"


#!/bin/bash
# Script para generar NEXTAUTH_SECRET

echo "🔑 Generando NEXTAUTH_SECRET..."
SECRET=$(openssl rand -base64 32)
echo ""
echo "✅ Tu NEXTAUTH_SECRET generado:"
echo ""
echo "NEXTAUTH_SECRET=$SECRET"
echo ""
echo "📋 Copia esta línea y reemplázala en tu archivo .env"

#!/usr/bin/env bash
# ===================================================================
# Prompt: Agente Cursor — Instalación + Exportación de Credenciales n8n
# ===================================================================
# Objetivo: instalar n8n (si falta), exportar todas las credenciales
#            cifradas y almacenarlas localmente.
# Entorno: macOS/Linux — CLI o Docker.
# ===================================================================

set -e

echo "🔍 Verificando instalación de n8n..."
if ! command -v n8n &>/dev/null; then
  echo "⚙️  n8n no está instalado. Instalando globalmente con npm..."
  if ! command -v node &>/dev/null; then
    echo "📦 Instalando Node.js con Homebrew..."
    brew install node
  fi
  npm install -g n8n
else
  echo "✅ n8n ya instalado."
fi

echo "🧭 Verificando versión..."
n8n --version

# Crear carpeta de backup
BACKUP_DIR="$HOME/.n8n/backup"
mkdir -p "$BACKUP_DIR"

# Exportar credenciales cifradas
EXPORT_FILE="$BACKUP_DIR/credentials_$(date +%Y%m%d_%H%M%S).json"
echo "📤 Exportando credenciales cifradas a: $EXPORT_FILE"

# Verificar si hay credenciales antes de exportar
CREDENTIAL_COUNT=$(sqlite3 ~/.n8n/database.sqlite "SELECT COUNT(*) FROM credentials_entity;" 2>/dev/null || echo "0")
SHARED_CREDENTIAL_COUNT=$(sqlite3 ~/.n8n/database.sqlite "SELECT COUNT(*) FROM shared_credentials;" 2>/dev/null || echo "0")
TOTAL_CREDENTIALS=$((CREDENTIAL_COUNT + SHARED_CREDENTIAL_COUNT))

if [ "$TOTAL_CREDENTIALS" -eq 0 ]; then
  echo "ℹ️  No se encontraron credenciales para exportar."
  echo "💡 Para crear credenciales, accede a n8n en: http://localhost:5678"
  echo "📝 Una vez creadas las credenciales, ejecuta este script nuevamente."
else
  echo "🔍 Se encontraron $TOTAL_CREDENTIALS credenciales para exportar..."
  n8n export:credentials --all --output="$EXPORT_FILE"
fi

# Verificar variable de cifrado
if [ -z "$N8N_ENCRYPTION_KEY" ]; then
  echo "⚠️  Advertencia: la variable N8N_ENCRYPTION_KEY no está definida."
  echo "🔑 Las credenciales exportadas solo serán reimportables en este entorno."
else
  echo "🔒 Usando clave de cifrado actual: $N8N_ENCRYPTION_KEY"
fi

# Resumen
if [ "$TOTAL_CREDENTIALS" -gt 0 ]; then
  echo "✅ Exportación completa."
  echo "📁 Archivo generado: $EXPORT_FILE"
  echo "💡 Para importar luego: n8n import:credentials --input=$EXPORT_FILE"
else
  echo "✅ Verificación completa."
  echo "📝 No hay credenciales para exportar en este momento."
fi

# ===================================================================
# EXPORT_SEAL v1
# project: sistema-limpieza-mac
# prompt_id: export-n8n-credentials
# version: 1.0.0
# file: export_credentials.sh
# lang: bash
# created_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# author: Mat
# origin: Cursor Agent
# notes: Incluye instalación automática y exportación cifrada.
# ===================================================================

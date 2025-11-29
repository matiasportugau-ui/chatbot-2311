#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
ENV_FILE="${ROOT_DIR}/.env"

echo "🔧 Configurando entorno virtual para el chatbot..."

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 no está instalado. Instálalo antes de continuar."
  exit 1
fi

if [ ! -d "${VENV_DIR}" ]; then
  python3 -m venv "${VENV_DIR}"
  echo "✅ Virtualenv creado en ${VENV_DIR}"
else
  echo "ℹ️  Virtualenv existente encontrado en ${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

echo "📦 Instalando dependencias desde requirements.txt..."
pip install --upgrade pip >/dev/null
pip install -r "${ROOT_DIR}/requirements.txt"

if [ ! -f "${ENV_FILE}" ]; then
  echo "📝 Generando archivo .env con plantilla env.example..."
  cp "${ROOT_DIR}/env.example" "${ENV_FILE}"
  echo "🔐 Recuerda completar valores como OPENAI_API_KEY y MONGODB_URI en ${ENV_FILE}"
else
  echo "ℹ️  Archivo .env ya existe, omitiendo copia."
fi

cat <<'EOF'

✅ Entorno Python listo.
Para activarlo manualmente:
  source .venv/bin/activate

Variables sensibles mínimas esperadas:
  - OPENAI_API_KEY
  - CHAT_USE_FULL_IA (opcional, true/false)
  - MONGODB_URI (opcional, para persistencia)
  - MELI_ACCESS_TOKEN / MELI_SELLER_ID (si sincronizas Mercado Libre)
  - SHOPIFY_SYNC_MAX_AGE_MINUTES (controla el cache local)

EOF


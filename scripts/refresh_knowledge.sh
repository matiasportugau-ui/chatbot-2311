#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
LOG_DIR="${ROOT_DIR}/logs/automation"
mkdir -p "${LOG_DIR}"
INGEST_LOG="${LOG_DIR}/ingestion_$(date +"%Y%m%d_%H%M%S").log"

if [ -d "${VENV_DIR}" ]; then
  echo "🐍 Activando entorno virtual .venv"
  # shellcheck disable=SC1090
  source "${VENV_DIR}/bin/activate"
else
  echo "❌ No se encontró .venv. Ejecuta scripts/setup_chatbot_env.sh antes de continuar."
  exit 1
fi

cd "${ROOT_DIR}"

should_run() {
  local value="${1:-true}"
  value="$(printf '%s' "${value}" | tr '[:upper:]' '[:lower:]')"
  if [[ -z "${value}" || "${value}" == "true" || "${value}" == "1" || "${value}" == "yes" ]]; then
    return 0
  fi
  return 1
}

run_ingestor() {
  local label="$1"
  shift
  echo "🔸 ${label}" | tee -a "${INGEST_LOG}"
  if "$@" >> "${INGEST_LOG}" 2>&1; then
    echo "✅ ${label}" | tee -a "${INGEST_LOG}"
  else
    echo "⚠️  ${label} (ver ${INGEST_LOG})" | tee -a "${INGEST_LOG}"
  fi
}

if should_run "${RUN_SHOPIFY_SYNC:-true}"; then
  echo "🛒 Ejecutando ingestor Shopify..."
  run_ingestor "Shopify catalog sync" python3 python-scripts/fetch_shopify_products.py
else
  echo "⏭️  Shopify sync omitido (RUN_SHOPIFY_SYNC=false)"
fi

if should_run "${RUN_MELI_SYNC:-true}"; then
  if [[ -n "${MELI_ACCESS_TOKEN:-}" && -n "${MELI_SELLER_ID:-}" ]]; then
    echo "🟡 Ejecutando ingestor Mercado Libre..."
    run_ingestor "Mercado Libre questions sync" python3 python-scripts/fetch_mercadolibre_questions.py
  else
    echo "⚠️  Ingestor Mercado Libre omitido (faltan MELI_ACCESS_TOKEN/MELI_SELLER_ID)"
  fi
else
  echo "⏭️  Mercado Libre sync omitido (RUN_MELI_SYNC=false)"
fi

echo "📚 Consolidando conocimiento..."
python3 consolidar_conocimiento.py | tee -a "${INGEST_LOG}"

echo "✅ Validando integración..."
python3 validar_integracion.py | tee -a "${INGEST_LOG}"

echo "🎯 Conocimiento actualizado y validado. Log: ${INGEST_LOG}"

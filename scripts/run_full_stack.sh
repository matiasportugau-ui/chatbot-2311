#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
LOG_DIR="${ROOT_DIR}/logs/automation"
STAMP="$(date +"%Y%m%d_%H%M%S")"
LOG_FILE="${LOG_DIR}/run_${STAMP}.log"

mkdir -p "${LOG_DIR}"

run_step() {
  local title="$1"
  shift
  echo -e "\n🔹 ${title}" | tee -a "${LOG_FILE}"
  "$@" 2>&1 | tee -a "${LOG_FILE}"
}

load_env_file() {
  local env_path="$1"
  set -o allexport
  # shellcheck disable=SC1090
  source "${env_path}"
  local status=$?
  set +o allexport
  return "${status}"
}

if [ ! -d "${VENV_DIR}" ]; then
  echo "⚠️  No se encontró .venv, ejecutando scripts/setup_chatbot_env.sh..." | tee -a "${LOG_FILE}"
  bash "${ROOT_DIR}/scripts/setup_chatbot_env.sh" | tee -a "${LOG_FILE}"
fi

# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

if [ ! -f "${ROOT_DIR}/.env" ]; then
  echo "❌ Falta archivo .env con tus credenciales. Cancela con CTRL+C, complétalo y vuelve a correr este script." | tee -a "${LOG_FILE}"
  exit 1
fi

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "⚠️  OPENAI_API_KEY no está en el entorno actual. Cargando variables desde .env..." | tee -a "${LOG_FILE}"
  if ! load_env_file "${ROOT_DIR}/.env"; then
    echo "❌ No se pudo cargar ${ROOT_DIR}/.env. Revisa el formato y vuelve a intentarlo." | tee -a "${LOG_FILE}"
    exit 1
  fi
  if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "❌ OPENAI_API_KEY sigue sin definirse tras cargar .env. Completa el archivo antes de continuar." | tee -a "${LOG_FILE}"
    exit 1
  fi
fi

run_step "Actualizando conocimiento (Shopify + Mercado Libre + consolidado)" bash "${ROOT_DIR}/scripts/refresh_knowledge.sh"

echo -e "\n🚀 Iniciando API del chatbot (logs en ${LOG_FILE}). Usa CTRL+C para detenerla.\n" | tee -a "${LOG_FILE}"

cd "${ROOT_DIR}"
python3 api_server.py 2>&1 | tee -a "${LOG_FILE}"


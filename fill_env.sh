#!/usr/bin/env bash
set -euo pipefail
TEMPLATE=".env.template"
OUT=".env"
# Convierte {{KEY}} -> ${KEY} y sustituye
sed -E 's/\{\{([A-Za-z0-9_]+)\}\}/\$\{\1\}/g' "$TEMPLATE" | envsubst > "$OUT"
chmod 600 "$OUT"
echo ".env creado: $OUT (perm 600)"

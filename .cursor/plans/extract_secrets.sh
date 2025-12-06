#!/usr/bin/env bash

echo "=== Extrayendo secrets del workspace ==="

# Archivo destino
BACKUP_ENV=".env.backup"
BACKUP_JSON="secrets_dump.json"

# Prefijos relevantes
PREFIXES="OPENAI|MONGO|DATABASE|WHATSAPP|GOOGLE|MELI|SHOPIFY|JWT|API_URL|INTERNAL_API_KEY|LAUNCHER|AGENT|SMTP|VERCEL|NEXT_PUBLIC"

# Limpieza previa
rm -f "$BACKUP_ENV" "$BACKUP_JSON"

# Export a .env.backup
echo "# Backup generado automáticamente $(date)" >> "$BACKUP_ENV"
env | egrep "$PREFIXES" | while IFS='=' read -r key value; do
    echo "${key}=\"${value}\"" >> "$BACKUP_ENV"
done

# Export a JSON
echo "{" >> "$BACKUP_JSON"
COUNT=0
TOTAL=$(env | egrep "$PREFIXES" | wc -l | tr -d ' ')

env | egrep "$PREFIXES" | while IFS='=' read -r key value; do
    COUNT=$((COUNT+1))
    if [ "$COUNT" -lt "$TOTAL" ]; then
        echo "  \"${key}\": \"${value//\"/\\\"}\"," >> "$BACKUP_JSON"
    else
        echo "  \"${key}\": \"${value//\"/\\\"}\"" >> "$BACKUP_JSON"
    fi
done

echo "}" >> "$BACKUP_JSON"

echo "=== DONE ==="
echo "→ Secrets guardados en:"
echo "   - $BACKUP_ENV"
echo "   - $BACKUP_JSON"

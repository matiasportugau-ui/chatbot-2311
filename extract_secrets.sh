#!/usr/bin/env bash

echo "=== Extrayendo secrets del workspace ==="

# Archivo destino
BACKUP_ENV=".env.unified"
BACKUP_JSON="secrets_dump.json"

# Prefijos relevantes
PREFIXES="OPENAI|MONGO|DATABASE|WHATSAPP|GOOGLE|MELI|SHOPIFY|JWT|API_URL|INTERNAL_API_KEY|LAUNCHER|AGENT|SMTP|VERCEL|NEXT_PUBLIC|GROQ|GEMINI|GROK|N8N|MERCADO_LIBRE|NEXTAUTH|SENTRY|ANALYTICS"

# Limpieza previa
rm -f "$BACKUP_ENV" "$BACKUP_JSON"

# Export a .env.unified
echo "# ============================================" >> "$BACKUP_ENV"
echo "# BMC Chatbot - Unified Environment Variables" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
echo "# Backup generado automáticamente $(date)" >> "$BACKUP_ENV"
echo "# DO NOT COMMIT THIS FILE TO GIT!" >> "$BACKUP_ENV"
echo "" >> "$BACKUP_ENV"

# Categorías
echo "# ============================================" >> "$BACKUP_ENV"
echo "# AI Models" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
env | grep -E "^(OPENAI|GROQ|GEMINI|GROK)" | sort | while IFS='=' read -r key value; do
    echo "${key}=${value}" >> "$BACKUP_ENV"
done

echo "" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
echo "# Databases" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
env | grep -E "^(MONGO|DATABASE)" | sort | while IFS='=' read -r key value; do
    echo "${key}=${value}" >> "$BACKUP_ENV"
done

echo "" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
echo "# WhatsApp" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
env | grep -E "^WHATSAPP" | sort | while IFS='=' read -r key value; do
    echo "${key}=${value}" >> "$BACKUP_ENV"
done

echo "" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
echo "# MercadoLibre" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
env | grep -E "^(MELI|MERCADO_LIBRE)" | sort | while IFS='=' read -r key value; do
    echo "${key}=${value}" >> "$BACKUP_ENV"
done

echo "" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
echo "# n8n" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
env | grep -E "^N8N" | sort | while IFS='=' read -r key value; do
    echo "${key}=${value}" >> "$BACKUP_ENV"
done

echo "" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
echo "# Google Services" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
env | grep -E "^GOOGLE" | sort | while IFS='=' read -r key value; do
    echo "${key}=${value}" >> "$BACKUP_ENV"
done

echo "" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
echo "# Other Services" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
env | grep -E "^(NEXTAUTH|SENTRY|ANALYTICS|SHOPIFY|JWT|SMTP|VERCEL)" | sort | while IFS='=' read -r key value; do
    echo "${key}=${value}" >> "$BACKUP_ENV"
done

echo "" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
echo "# Configuration" >> "$BACKUP_ENV"
echo "# ============================================" >> "$BACKUP_ENV"
env | grep -E "^(NEXT_PUBLIC|API_URL|LOG_LEVEL|MODEL_STRATEGY|ENABLE_)" | sort | while IFS='=' read -r key value; do
    echo "${key}=${value}" >> "$BACKUP_ENV"
done

# Export a JSON
echo "{" > "$BACKUP_JSON"
COUNT=0
TOTAL=$(env | grep -E "$PREFIXES" | wc -l | tr -d ' ')

env | grep -E "$PREFIXES" | sort | while IFS='=' read -r key value; do
    COUNT=$((COUNT + 1))
    if [ $COUNT -eq $TOTAL ]; then
        echo "  \"${key}\": \"${value}\"" >> "$BACKUP_JSON"
    else
        echo "  \"${key}\": \"${value}\"," >> "$BACKUP_JSON"
    fi
done

echo "}" >> "$BACKUP_JSON"

# También cargar desde .env si existe
if [ -f .env ]; then
    echo "" >> "$BACKUP_ENV"
    echo "# ============================================" >> "$BACKUP_ENV"
    echo "# Additional from .env file" >> "$BACKUP_ENV"
    echo "# ============================================" >> "$BACKUP_ENV"
    
    # Cargar .env y agregar variables que no estén ya en el archivo
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        
        # Check if key already exists
        if ! grep -q "^${key}=" "$BACKUP_ENV"; then
            echo "${key}=${value}" >> "$BACKUP_ENV"
        fi
    done < .env
fi

# Estadísticas
ENV_COUNT=$(grep -c "=" "$BACKUP_ENV" 2>/dev/null || echo "0")
JSON_COUNT=$(grep -c ":" "$BACKUP_JSON" 2>/dev/null || echo "0")

echo ""
echo "✅ Extracción completada!"
echo "📝 Archivo .env: $BACKUP_ENV ($ENV_COUNT variables)"
echo "📊 Archivo JSON: $BACKUP_JSON ($JSON_COUNT secrets)"
echo ""
echo "💡 Próximos pasos:"
echo "   1. Revisar: cat $BACKUP_ENV"
echo "   2. Subir a GitHub: python upload_secrets_to_github.py --env-file $BACKUP_ENV"
echo "   3. O usar manualmente en Codespaces"
echo ""


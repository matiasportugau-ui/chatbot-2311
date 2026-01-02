#!/bin/bash
# Load secrets from GitHub Codespaces environment
# Merges GitHub Secrets with .env file

set -e

echo "🔐 Loading secrets from GitHub Codespaces..."

# List of secrets to check (from env.example)
SECRETS=(
    "OPENAI_API_KEY"
    "GROQ_API_KEY"
    "GEMINI_API_KEY"
    "GROK_API_KEY"
    "MONGODB_URI"
    "N8N_BASIC_AUTH_PASSWORD"
    "WHATSAPP_ACCESS_TOKEN"
    "WHATSAPP_VERIFY_TOKEN"
    "MERCADO_LIBRE_APP_ID"
    "MERCADO_LIBRE_CLIENT_SECRET"
    "GOOGLE_SHEETS_API_KEY"
)

# Create or update .env file
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    if [ -f "env.example" ]; then
        cp env.example "$ENV_FILE"
        echo "✅ Created .env from env.example"
    else
        touch "$ENV_FILE"
        echo "✅ Created empty .env file"
    fi
fi

# Load secrets from GitHub Codespaces environment
LOADED_COUNT=0
MISSING_COUNT=0

for secret in "${SECRETS[@]}"; do
    # Check if secret exists in environment (GitHub Codespaces secrets)
    if [ -n "${!secret:-}" ]; then
        # Update or add to .env file
        if grep -q "^${secret}=" "$ENV_FILE"; then
            # Update existing value
            sed -i.bak "s|^${secret}=.*|${secret}=${!secret}|" "$ENV_FILE"
        else
            # Add new value
            echo "${secret}=${!secret}" >> "$ENV_FILE"
        fi
        echo "✅ Loaded: $secret"
        ((LOADED_COUNT++))
    else
        # Check if it's already in .env file
        if ! grep -q "^${secret}=" "$ENV_FILE"; then
            echo "⚠️  Missing: $secret (not in GitHub Secrets or .env)"
            ((MISSING_COUNT++))
        fi
    fi
done

# Clean up backup file
rm -f "$ENV_FILE.bak"

echo ""
echo "📊 Summary:"
echo "   ✅ Loaded: $LOADED_COUNT secrets"
echo "   ⚠️  Missing: $MISSING_COUNT secrets"
echo ""

if [ $MISSING_COUNT -gt 0 ]; then
    echo "💡 To add secrets:"
    echo "   1. Go to: Settings → Secrets and variables → Codespaces"
    echo "   2. Add new repository secret"
    echo "   3. Or manually edit .env file"
    echo ""
fi


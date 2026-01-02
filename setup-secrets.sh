#!/bin/bash

# Google Cloud Secret Manager Setup
# This script creates secrets from your .env file

echo "🔐 Setting up Google Cloud Secret Manager..."

GCLOUD_PATH="/Users/matias/google-cloud-sdk/bin/gcloud"

if [ ! -f "$GCLOUD_PATH" ]; then
    echo "❌ gcloud executable not found at $GCLOUD_PATH"
    exit 1
fi

# Check if logged in
$GCLOUD_PATH auth print-access-token >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ You are not logged in. Please run: $GCLOUD_PATH auth login"
    exit 1
fi

# Enable Secret Manager API
echo "📦 Enabling Secret Manager API..."
$GCLOUD_PATH services enable secretmanager.googleapis.com

# List of sensitive environment variables to store as secrets
SENSITIVE_VARS=(
    "OPENAI_API_KEY"
    "OPENAI_SERVICE_ACCOUNT_KEY"
    "XAI_API_KEY"
    "GEMINI_API_KEY"
    "GROQ_API_KEY"
    "MONGODB_PASS"
    "PINECONE_API_KEY"
    "GITHUB_PAT"
    "GOOGLE_API_KEY"
    "GOOGLE_SHEETS_API_KEY"
    "GOOGLE_PRIVATE_KEY"
)

# Read .env file and create secrets
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    exit 1
fi

echo ""
echo "Creating secrets from .env file..."
echo ""

for var_name in "${SENSITIVE_VARS[@]}"; do
    # Extract value from .env
    value=$(grep "^${var_name}=" .env | cut -d'=' -f2- | tr -d '\r')

    if [ -z "$value" ] || [ "$value" = "" ]; then
        echo "⚠️  Skipping $var_name (empty or not found)"
        continue
    fi

    # Convert to lowercase for secret name (Secret Manager requirement)
    secret_name=$(echo "$var_name" | tr '[:upper:]' '[:lower:]' | tr '_' '-')

    echo "📝 Creating secret: $secret_name"

    # Check if secret already exists
    if $GCLOUD_PATH secrets describe "$secret_name" >/dev/null 2>&1; then
        echo "   Secret exists, creating new version..."
        echo -n "$value" | $GCLOUD_PATH secrets versions add "$secret_name" --data-file=-
    else
        echo "   Creating new secret..."
        echo -n "$value" | $GCLOUD_PATH secrets create "$secret_name" --data-file=- --replication-policy="automatic"
    fi
done

echo ""
echo "✅ Secrets created successfully!"
echo ""
echo "To use these secrets in Cloud Run, they will be automatically"
echo "mounted as environment variables during deployment."

#!/bin/bash

# Deployment Script for Google Cloud Run
# --------------------------------------

echo "🚀 Starting Google Cloud Run Deployment..."

# 1. Verify Gcloud Location and Auth
GCLOUD_PATH="/Users/matias/google-cloud-sdk/bin/gcloud"

if [ ! -f "$GCLOUD_PATH" ]; then
    echo "❌ gcloud executable not found at $GCLOUD_PATH"
    echo "Please ensure Google Cloud SDK is installed."
    exit 1
fi

echo "✅ Found gcloud at $GCLOUD_PATH"

# Check authentication
$GCLOUD_PATH auth print-access-token >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  You are not logged in."
    echo "Running login command..."
    $GCLOUD_PATH auth login
else
    echo "✅ Authenticated."
fi

# 2. Project Setup
echo ""
echo "📋 Project Configuration"
echo "-----------------------"
echo "Existing projects:"
$GCLOUD_PATH projects list --format="table(projectId, name)"

echo ""
read -p "Enter the PROJECT ID to use (or type 'new' to create one): " PROJECT_ID

if [ "$PROJECT_ID" == "new" ]; then
    read -p "Enter a unique name for the new project (lowercase, hyphens, e.g., chatbot-project-2025): " NEW_PROJECT_ID
    echo "Creation of new projects via script might require organizational permissions."
    echo "Attempting to create project '$NEW_PROJECT_ID'..."
    $GCLOUD_PATH projects create $NEW_PROJECT_ID --name="Chatbot Project"
    PROJECT_ID=$NEW_PROJECT_ID
fi

echo "✅ Setting active project to: $PROJECT_ID"
$GCLOUD_PATH config set project $PROJECT_ID

# 3. Enable APIs
echo ""
echo "🔌 Enabling required APIs (this may take a minute)..."
$GCLOUD_PATH services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

# 4. Setup Secrets (if not already done)
echo ""
read -p "Have you run ./setup-secrets.sh to create secrets in Secret Manager? (y/n): " SECRETS_SETUP
if [ "$SECRETS_SETUP" != "y" ]; then
    echo "⚠️  Please run ./setup-secrets.sh first to set up secrets, then run this script again."
    exit 1
fi

# 5. Non-sensitive Environment Variables
echo ""
echo "📝 Preparing non-sensitive environment variables..."
NON_SENSITIVE_ENV="XAI_MODEL=grok-4-latest,OPENAI_MODEL=gpt-4o-mini,GEMINI_MODELS=gemini-2.5-flash-lite,MODEL_STRATEGY=balanced,NODE_ENV=production,MONGODB_USER=matiasportugau_db_user,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1"

# 6. Deploy
echo ""
echo "🚀 Deploying to Cloud Run..."
SERVICE_NAME="chatbot-service"
REGION="us-central1"

echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"

# Build secret references for Cloud Run
# Format: ENV_VAR=secret-name:latest
SECRETS=(
    "OPENAI_API_KEY=openai-api-key:latest"
    "OPENAI_SERVICE_ACCOUNT_KEY=openai-service-account-key:latest"
    "XAI_API_KEY=xai-api-key:latest"
    "GEMINI_API_KEY=gemini-api-key:latest"
    "GROQ_API_KEY=groq-api-key:latest"
    "MONGODB_PASS=mongodb-pass:latest"
    "PINECONE_API_KEY=pinecone-api-key:latest"
    "GITHUB_PAT=github-pat:latest"
    "GOOGLE_API_KEY=google-api-key:latest"
    "GOOGLE_SHEETS_API_KEY=google-sheets-api-key:latest"
)

# Deploy command
# --source . builds the container from source using Cloud Build
# --allow-unauthenticated makes it a public website
# --port 3000 matches the port exposed in Dockerfile
echo "Building deployment command..."
CMD="$GCLOUD_PATH run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --port 3000 \
  --set-env-vars=\"$NON_SENSITIVE_ENV\""

# Add secrets
for secret in "${SECRETS[@]}"; do
    CMD="$CMD --set-secrets=\"$secret\""
done

echo "Executing deployment..."
eval $CMD

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "Your chatbot should now be available at the URL shown above."
echo "To view your service: $GCLOUD_PATH run services describe $SERVICE_NAME --region $REGION"

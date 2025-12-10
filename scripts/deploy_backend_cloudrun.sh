#!/bin/bash

# Configuration
SERVICE_NAME="chatbot-backend"
REGION="us-central1"
PROJECT_ID=$(gcloud config get-value project)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ No default project set. Please run 'gcloud config set project YOUR_PROJECT_ID'"
    exit 1
fi

echo "🚀 Deploying $SERVICE_NAME to Cloud Run (Region: $REGION, Project: $PROJECT_ID)..."

# Deploy command
# --source . builds the container from source (Dockerfile) using Cloud Build
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars "SKIP_VENV_CHECK=true"

# Check if deploy was successful
if [ $? -eq 0 ]; then
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --platform managed --region "$REGION" --format 'value(status.url)')
    echo "✅ Backend successfully deployed!"
    echo "🌍 URL: $SERVICE_URL"
    echo ""
    echo "👉 Next Step: Run frontend deployment with this URL:"
    echo "   python3 scripts/deploy_frontend_vercel.py --backend-url $SERVICE_URL"
else
    echo "❌ Deployment failed."
    exit 1
fi

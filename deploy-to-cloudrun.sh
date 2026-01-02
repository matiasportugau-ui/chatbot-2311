#!/bin/bash
#
# Deploy BMC Chatbot Python Backend to Google Cloud Run
# Focuses on Mercado Libre Integration
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}BMC Chatbot - Cloud Run Deployment${NC}"
echo -e "${GREEN}Mercado Libre Integration${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-chatbot-bmc-live}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
SERVICE_NAME="bmc-chatbot-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Service Name: $SERVICE_NAME"
echo "  Image: $IMAGE_NAME"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}Not authenticated. Running gcloud auth login...${NC}"
    gcloud auth login
fi

# Set the project
echo -e "${YELLOW}Setting project to ${PROJECT_ID}...${NC}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo -e "${YELLOW}Enabling required Google Cloud APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    secretmanager.googleapis.com \
    --project=${PROJECT_ID}

# Build the container image
echo -e "${YELLOW}Building container image...${NC}"
gcloud builds submit \
    --tag ${IMAGE_NAME} \
    --dockerfile=Dockerfile.cloudrun \
    --project=${PROJECT_ID} \
    .

# Create secrets if they don't exist
echo -e "${YELLOW}Checking and creating secrets...${NC}"

create_secret_if_not_exists() {
    SECRET_NAME=$1
    SECRET_VALUE=$2

    if gcloud secrets describe ${SECRET_NAME} --project=${PROJECT_ID} &> /dev/null; then
        echo "  ✓ Secret ${SECRET_NAME} already exists"
    else
        echo "  + Creating secret ${SECRET_NAME}"
        echo -n "${SECRET_VALUE}" | gcloud secrets create ${SECRET_NAME} \
            --data-file=- \
            --project=${PROJECT_ID}
    fi
}

# Read from .env file
if [ -f .env ]; then
    echo -e "${YELLOW}Reading secrets from .env file...${NC}"

    # Mercado Libre secrets
    MELI_APP_ID=$(grep MERCADO_LIBRE_APP_ID .env | cut -d '=' -f2)
    MELI_CLIENT_SECRET=$(grep MERCADO_LIBRE_CLIENT_SECRET .env | cut -d '=' -f2)
    MELI_SELLER_ID=$(grep MERCADO_LIBRE_SELLER_ID .env | cut -d '=' -f2)
    MELI_WEBHOOK_SECRET=$(grep MERCADO_LIBRE_WEBHOOK_SECRET .env | cut -d '=' -f2)

    # AI Services
    OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d '=' -f2)
    XAI_API_KEY=$(grep XAI_API_KEY .env | cut -d '=' -f2)
    GEMINI_API_KEY=$(grep GEMINI_API_KEY .env | cut -d '=' -f2)

    # Database
    MONGODB_URI=$(grep MONGODB_URI .env | cut -d '=' -f2)

    # Create secrets
    [ -n "$MELI_APP_ID" ] && create_secret_if_not_exists "mercado-libre-app-id" "$MELI_APP_ID"
    [ -n "$MELI_CLIENT_SECRET" ] && create_secret_if_not_exists "mercado-libre-client-secret" "$MELI_CLIENT_SECRET"
    [ -n "$MELI_SELLER_ID" ] && create_secret_if_not_exists "mercado-libre-seller-id" "$MELI_SELLER_ID"
    [ -n "$MELI_WEBHOOK_SECRET" ] && create_secret_if_not_exists "mercado-libre-webhook-secret" "$MELI_WEBHOOK_SECRET"
    [ -n "$OPENAI_API_KEY" ] && create_secret_if_not_exists "openai-api-key" "$OPENAI_API_KEY"
    [ -n "$XAI_API_KEY" ] && create_secret_if_not_exists "xai-api-key" "$XAI_API_KEY"
    [ -n "$GEMINI_API_KEY" ] && create_secret_if_not_exists "gemini-api-key" "$GEMINI_API_KEY"
    [ -n "$MONGODB_URI" ] && create_secret_if_not_exists "mongodb-uri" "$MONGODB_URI"
else
    echo -e "${RED}Warning: .env file not found. Secrets must be created manually.${NC}"
fi

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --set-env-vars="LOG_LEVEL=INFO,NODE_ENV=production" \
    --set-secrets="MERCADO_LIBRE_APP_ID=mercado-libre-app-id:latest,MERCADO_LIBRE_CLIENT_SECRET=mercado-libre-client-secret:latest,MERCADO_LIBRE_SELLER_ID=mercado-libre-seller-id:latest,MERCADO_LIBRE_WEBHOOK_SECRET=mercado-libre-webhook-secret:latest,OPENAI_API_KEY=openai-api-key:latest,XAI_API_KEY=xai-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest,MONGODB_URI=mongodb-uri:latest" \
    --memory 1Gi \
    --cpu 1 \
    --timeout 60 \
    --concurrency 80 \
    --min-instances 0 \
    --max-instances 10 \
    --project=${PROJECT_ID}

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region ${REGION} \
    --project=${PROJECT_ID} \
    --format='value(status.url)')

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"
echo -e "Service URL: ${GREEN}${SERVICE_URL}${NC}"
echo -e "Health check: ${GREEN}${SERVICE_URL}/health${NC}"
echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Update your Next.js .env with:"
echo "   PY_CHAT_SERVICE_URL=${SERVICE_URL}"
echo ""
echo "2. Redeploy your Next.js app to Vercel with the new environment variable"
echo ""
echo "3. Test the integration:"
echo "   curl ${SERVICE_URL}/health"
echo ""
echo -e "${GREEN}Done!${NC}"

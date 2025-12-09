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

# 4. Environment Variables
echo ""
echo "🔑 Preparing Environment Variables..."
if [ -f ".env" ]; then
    # Extract vars, ignore comments and empty lines
    # Format: KEY=VALUE,KEY2=VALUE2
    ENV_VARS=$(grep -v '^#' .env | grep -v '^$' | tr '\n' ',' | sed 's/,$//')
    echo "✅ Loaded environment variables from .env"
else
    echo "⚠️  .env file not found! Deploying without environment variables."
    ENV_VARS=""
fi

# 5. Deploy
echo ""
echo "🚀 Deploying to Cloud Run..."
SERVICE_NAME="chatbot-service"
REGION="us-central1"

echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"

# Deploy command
# --source . builds the container from source using Cloud Build
# --allow-unauthenticated makes it a public website
CMD="$GCLOUD_PATH run deploy $SERVICE_NAME --source . --region $REGION --allow-unauthenticated --port 8000"

if [ -f ".env" ]; then
    CMD="$CMD --env-vars-file .env"
fi

echo "Executing deployment..."
eval $CMD

echo ""
echo "✅ Deployment Request Sent."

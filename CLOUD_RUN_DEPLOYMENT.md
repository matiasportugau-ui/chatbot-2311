# Google Cloud Run Deployment Guide
## BMC Chatbot - Mercado Libre Integration

This guide explains how to deploy the Python FastAPI backend (AI chatbot service) to Google Cloud Run to support the Mercado Libre integration.

---

## Architecture Overview

```
┌─────────────────────┐
│  Mercado Libre      │
│  (Questions/Orders) │
└──────────┬──────────┘
           │ Webhooks
           ▼
┌─────────────────────┐      ┌──────────────────────┐
│  Next.js App        │◄────►│  Python FastAPI      │
│  (Vercel)           │ HTTP │  (Cloud Run)         │
│                     │      │                      │
│  - OAuth Flow       │      │  - AI Response Gen   │
│  - Webhook Handler  │      │  - OpenAI/Gemini     │
│  - Auto-Answer      │      │  - Knowledge Base    │
└─────────────────────┘      └──────────────────────┘
           │                            │
           └────────────┬───────────────┘
                        ▼
                ┌──────────────┐
                │   MongoDB    │
                │   (Atlas)    │
                └──────────────┘
```

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed ([Install Guide](https://cloud.google.com/sdk/docs/install))
3. **Project ID** (default: `chatbot-bmc-live`)
4. **Environment variables** configured in `.env`

---

## Quick Start

### 1. Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project chatbot-bmc-live
```

### 2. Deploy to Cloud Run

Simply run the deployment script:

```bash
cd chatbot-2311
./deploy-to-cloudrun.sh
```

The script will:
- ✓ Enable required Google Cloud APIs
- ✓ Build the Docker image using Cloud Build
- ✓ Create secrets from your `.env` file
- ✓ Deploy to Cloud Run
- ✓ Output the service URL

### 3. Update Next.js Environment

After deployment, update your Vercel environment variables:

```bash
# Copy the Cloud Run URL from the deployment output
# Then add to Vercel:
PY_CHAT_SERVICE_URL=https://bmc-chatbot-api-<hash>-uc.a.run.app
```

Redeploy your Next.js app on Vercel to apply the changes.

---

## Manual Deployment Steps

### Step 1: Enable Google Cloud APIs

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com
```

### Step 2: Build the Container Image

```bash
PROJECT_ID="chatbot-bmc-live"
SERVICE_NAME="bmc-chatbot-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

gcloud builds submit \
  --tag ${IMAGE_NAME} \
  --dockerfile=Dockerfile.cloudrun \
  --project=${PROJECT_ID}
```

### Step 3: Create Secrets

Create secrets for sensitive environment variables:

```bash
# Mercado Libre secrets
echo -n "742811153438318" | gcloud secrets create mercado-libre-app-id --data-file=-
echo -n "YOUR_CLIENT_SECRET" | gcloud secrets create mercado-libre-client-secret --data-file=-
echo -n "179969104" | gcloud secrets create mercado-libre-seller-id --data-file=-
echo -n "YOUR_WEBHOOK_SECRET" | gcloud secrets create mercado-libre-webhook-secret --data-file=-

# AI API Keys
echo -n "YOUR_OPENAI_KEY" | gcloud secrets create openai-api-key --data-file=-
echo -n "YOUR_XAI_KEY" | gcloud secrets create xai-api-key --data-file=-
echo -n "YOUR_GEMINI_KEY" | gcloud secrets create gemini-api-key --data-file=-

# Database
echo -n "YOUR_MONGODB_URI" | gcloud secrets create mongodb-uri --data-file=-
```

### Step 4: Deploy to Cloud Run

```bash
gcloud run deploy bmc-chatbot-api \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="LOG_LEVEL=INFO,NODE_ENV=production" \
  --set-secrets="MERCADO_LIBRE_APP_ID=mercado-libre-app-id:latest,MERCADO_LIBRE_CLIENT_SECRET=mercado-libre-client-secret:latest,MERCADO_LIBRE_SELLER_ID=mercado-libre-seller-id:latest,MERCADO_LIBRE_WEBHOOK_SECRET=mercado-libre-webhook-secret:latest,OPENAI_API_KEY=openai-api-key:latest,XAI_API_KEY=xai-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest,MONGODB_URI=mongodb-uri:latest" \
  --memory 1Gi \
  --cpu 1 \
  --timeout 60 \
  --concurrency 80 \
  --min-instances 0 \
  --max-instances 10
```

---

## Environment Variables

### Required for Mercado Libre Integration

| Variable | Description | Stored as Secret |
|----------|-------------|------------------|
| `MERCADO_LIBRE_APP_ID` | ML App ID | ✓ |
| `MERCADO_LIBRE_CLIENT_SECRET` | ML Client Secret | ✓ |
| `MERCADO_LIBRE_SELLER_ID` | ML Seller ID | ✓ |
| `MERCADO_LIBRE_WEBHOOK_SECRET` | Webhook HMAC Secret | ✓ |
| `OPENAI_API_KEY` | OpenAI API Key | ✓ |
| `MONGODB_URI` | MongoDB connection string | ✓ |

### Optional AI Services

| Variable | Description | Stored as Secret |
|----------|-------------|------------------|
| `XAI_API_KEY` | X.AI (Grok) API Key | ✓ |
| `GEMINI_API_KEY` | Google Gemini API Key | ✓ |

### Public Environment Variables

Set these directly (not as secrets):

```bash
LOG_LEVEL=INFO
NODE_ENV=production
OPENAI_MODEL=gpt-4o-mini
```

---

## Testing the Deployment

### 1. Health Check

```bash
SERVICE_URL=$(gcloud run services describe bmc-chatbot-api \
  --region us-central1 \
  --format='value(status.url)')

curl ${SERVICE_URL}/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "BMC Quote System API",
  "version": "1.0.0"
}
```

### 2. Test AI Chat Endpoint

```bash
curl -X POST ${SERVICE_URL}/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${INTERNAL_API_KEY}" \
  -d '{
    "message": "¿Cuánto cuesta la lana de roca?",
    "session_id": "test_session"
  }'
```

### 3. Test from Next.js

Update your Next.js `.env`:

```bash
PY_CHAT_SERVICE_URL=https://bmc-chatbot-api-xxxxx-uc.a.run.app
```

Then test the Mercado Libre auto-answer:

```bash
# Trigger a test question on Mercado Libre
# Check logs to verify the integration works
```

---

## Monitoring & Logs

### View Logs

```bash
gcloud run services logs read bmc-chatbot-api \
  --region us-central1 \
  --limit 50 \
  --format json
```

### Stream Logs

```bash
gcloud run services logs tail bmc-chatbot-api \
  --region us-central1
```

### View Metrics

Go to [Cloud Console - Cloud Run](https://console.cloud.google.com/run) and select your service to view:
- Request count
- Request latency
- CPU utilization
- Memory utilization
- Error rate

---

## Updating the Deployment

### Update Code

```bash
# Make your code changes
# Then rebuild and redeploy:
./deploy-to-cloudrun.sh
```

### Update Secrets

```bash
# Update a specific secret
echo -n "NEW_VALUE" | gcloud secrets versions add mercado-libre-client-secret --data-file=-

# Redeploy to pick up new secret version
gcloud run services update bmc-chatbot-api --region us-central1
```

### Rollback

```bash
# List revisions
gcloud run revisions list --service bmc-chatbot-api --region us-central1

# Rollback to a specific revision
gcloud run services update-traffic bmc-chatbot-api \
  --to-revisions REVISION_NAME=100 \
  --region us-central1
```

---

## Cost Optimization

Cloud Run pricing is based on:
- **CPU allocation**: $0.00002400 per vCPU-second
- **Memory allocation**: $0.00000250 per GiB-second
- **Requests**: $0.40 per million requests

Current configuration (1 vCPU, 1 GiB RAM):
- **Min instances**: 0 (scales to zero when idle)
- **Max instances**: 10
- **Estimated cost**: ~$5-20/month depending on traffic

---

## Troubleshooting

### Issue: Build fails

```bash
# Check build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

### Issue: Service won't start

```bash
# Check service logs
gcloud run services logs read bmc-chatbot-api --region us-central1 --limit 100
```

Common causes:
- Missing secrets
- Invalid MongoDB URI
- Missing required files (conocimiento_*.json)

### Issue: 500 errors from API

Check:
1. MongoDB connection is working
2. AI API keys are valid
3. Required environment variables are set

```bash
# Test MongoDB connectivity
curl ${SERVICE_URL}/health
```

---

## Security Best Practices

1. **Never commit secrets** to Git
2. **Use Secret Manager** for all sensitive data
3. **Enable HTTPS only** (Cloud Run default)
4. **Implement rate limiting** in the FastAPI app
5. **Use authentication** for admin endpoints
6. **Monitor logs** for suspicious activity

---

## Next Steps

After deploying the Python backend:

1. ✓ Update Next.js `PY_CHAT_SERVICE_URL` environment variable
2. ✓ Redeploy Next.js app on Vercel
3. ✓ Test the Mercado Libre webhook flow
4. ✓ Enable auto-answer by setting `MELI_AUTO_ANSWER_ENABLED=true` in Next.js
5. ✓ Monitor logs and metrics

---

## Support

For issues or questions:
- Check logs: `gcloud run services logs read bmc-chatbot-api`
- Review [Cloud Run documentation](https://cloud.google.com/run/docs)
- Open an issue in your project repository

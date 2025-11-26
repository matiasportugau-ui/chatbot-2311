# 🚀 Complete Hosting Guide for BMC Chatbot

This guide covers all hosting options for your chatbot system, including both frontend (Next.js) and backend (Python FastAPI) components.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Hosting Options](#hosting-options)
3. [Option 1: Vercel (Recommended)](#option-1-vercel-recommended)
4. [Option 2: Separate Hosting](#option-2-separate-hosting)
5. [Option 3: Docker Deployment](#option-3-docker-deployment)
6. [Option 4: Cloud Platforms](#option-4-cloud-platforms)
7. [Configuration Requirements](#configuration-requirements)
8. [Post-Deployment Setup](#post-deployment-setup)
9. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

Your chatbot system consists of:

1. **Frontend**: Next.js application (`nextjs-app/`)
   - Chat interface
   - Dashboard
   - API routes for frontend

2. **Backend**: Python FastAPI server (`api_server.py`)
   - Chat message processing
   - Quote creation
   - Integration with OpenAI, Google Sheets, MongoDB

3. **Integrations**:
   - OpenAI API (for AI conversations)
   - Google Sheets (for product data)
   - MongoDB (for conversation storage)
   - WhatsApp (optional, for WhatsApp integration)

---

## 🌐 Hosting Options

### Quick Comparison

| Option | Frontend | Backend | Complexity | Cost | Best For |
|--------|----------|---------|------------|------|----------|
| **Vercel** | ✅ | ⚠️ (Serverless) | Low | Free/Paid | Quick deployment |
| **Separate Hosting** | Vercel/Netlify | Railway/Render | Medium | Low-Medium | Production |
| **Docker** | Container | Container | Medium | Medium | Full control |
| **Cloud Platforms** | AWS/GCP/Azure | AWS/GCP/Azure | High | Medium-High | Enterprise |

---

## 🎯 Option 1: Vercel (Recommended)

**Best for**: Quick deployment, serverless architecture, automatic scaling

### Prerequisites

- GitHub account
- Vercel account (free tier available)
- API keys and credentials ready

### Step 1: Prepare Your Repository

```bash
# Ensure your code is committed and pushed to GitHub
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Deploy Frontend to Vercel

#### Method A: Via Vercel Dashboard (Easiest)

1. **Go to Vercel Dashboard**
   - Visit [https://vercel.com](https://vercel.com)
   - Sign in with GitHub

2. **Import Project**
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect Next.js

3. **Configure Project Settings**
   - **Root Directory**: Leave empty (or set to `nextjs-app` if deploying only frontend)
   - **Framework Preset**: Next.js
   - **Build Command**: `npm run build` (or `cd nextjs-app && npm run build`)
   - **Output Directory**: `.next`
   - **Install Command**: `npm install` (or `cd nextjs-app && npm install`)

4. **Set Environment Variables**
   
   Add these in Vercel Dashboard → Settings → Environment Variables:

   ```bash
   # OpenAI
   OPENAI_API_KEY=sk-proj-...
   
   # Google Sheets
   GOOGLE_SHEET_ID=your_sheet_id
   GOOGLE_SERVICE_ACCOUNT_EMAIL=your-service-account@project.iam.gserviceaccount.com
   GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   
   # MongoDB
   MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/database
   
   # Application
   NODE_ENV=production
   NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
   
   # Optional: WhatsApp
   WHATSAPP_ACCESS_TOKEN=your_token
   WHATSAPP_PHONE_NUMBER_ID=your_phone_id
   WHATSAPP_VERIFY_TOKEN=your_verify_token
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Get your deployment URL

#### Method B: Via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Navigate to project root
cd /workspace

# Deploy
vercel --prod

# Or deploy only frontend
cd nextjs-app
vercel --prod
```

### Step 3: Deploy Backend API

Vercel supports Python serverless functions, but for a full FastAPI app, you have two options:

#### Option A: Serverless Functions (Recommended for Vercel)

Create API routes in `nextjs-app/src/app/api/` that proxy to your Python backend or rewrite the logic in TypeScript/JavaScript.

#### Option B: Deploy Backend Separately

Deploy the Python FastAPI backend to a separate service (see Option 2).

### Step 4: Configure API Routes

If using Next.js API routes, create endpoints in `nextjs-app/src/app/api/`:

```typescript
// Example: nextjs-app/src/app/api/chat/process/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const body = await request.json();
  
  // Call your backend API or process directly
  const response = await fetch(`${process.env.BACKEND_URL}/chat/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  
  return NextResponse.json(await response.json());
}
```

### Step 5: Verify Deployment

```bash
# Health check
curl https://your-app.vercel.app/api/health

# Test chat endpoint
curl -X POST https://your-app.vercel.app/api/chat/process \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "Hola", "telefono": "+59812345678"}'
```

---

## 🔧 Option 2: Separate Hosting

**Best for**: Production environments, better control, separate scaling

### Frontend: Vercel/Netlify

Deploy frontend as described in Option 1.

### Backend: Railway/Render/Fly.io

#### Railway (Recommended for Python)

1. **Sign up**: [railway.app](https://railway.app)

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Service**
   - **Root Directory**: `/` (or leave empty)
   - **Start Command**: `python api_server.py` or `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: 3.11+

4. **Set Environment Variables**
   - Same as Vercel (see Configuration Requirements)

5. **Deploy**
   - Railway auto-deploys on git push
   - Get your backend URL (e.g., `https://your-app.railway.app`)

6. **Update Frontend**
   - Add `NEXT_PUBLIC_BACKEND_URL=https://your-app.railway.app` to Vercel env vars

#### Render

1. **Sign up**: [render.com](https://render.com)

2. **Create Web Service**
   - Connect GitHub repository
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables** (same as above)

4. **Deploy**

#### Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Initialize
fly launch

# Deploy
fly deploy
```

---

## 🐳 Option 3: Docker Deployment

**Best for**: Full control, consistent environments, on-premise deployment

### Step 1: Create Dockerfile for Backend

Create `Dockerfile.backend`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Create Dockerfile for Frontend

Create `nextjs-app/Dockerfile`:

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build
RUN npm run build

# Production image
FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

EXPOSE 3000

CMD ["npm", "start"]
```

### Step 3: Create docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_SHEET_ID=${GOOGLE_SHEET_ID}
      - MONGODB_URI=${MONGODB_URI}
    env_file:
      - .env

  frontend:
    build:
      context: ./nextjs-app
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://backend:8000
    depends_on:
      - backend
```

### Step 4: Deploy

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Step 5: Deploy to Cloud

**AWS ECS/Fargate**:
```bash
# Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker build -t chatbot-backend -f Dockerfile.backend .
docker tag chatbot-backend:latest <account>.dkr.ecr.<region>.amazonaws.com/chatbot-backend:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/chatbot-backend:latest
```

**Google Cloud Run**:
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/chatbot-backend
gcloud run deploy chatbot-backend --image gcr.io/PROJECT_ID/chatbot-backend --platform managed
```

---

## ☁️ Option 4: Cloud Platforms

### AWS

1. **Frontend**: AWS Amplify or S3 + CloudFront
2. **Backend**: AWS Lambda (serverless) or ECS/Fargate (containers)
3. **Database**: MongoDB Atlas or AWS DocumentDB

### Google Cloud Platform

1. **Frontend**: Firebase Hosting or Cloud Storage + CDN
2. **Backend**: Cloud Run (containers) or Cloud Functions (serverless)
3. **Database**: MongoDB Atlas or Firestore

### Azure

1. **Frontend**: Azure Static Web Apps
2. **Backend**: Azure Container Apps or Azure Functions
3. **Database**: MongoDB Atlas or Cosmos DB

---

## ⚙️ Configuration Requirements

### Required Environment Variables

#### For Frontend (Next.js)

```bash
# Backend API URL (if separate)
NEXT_PUBLIC_BACKEND_URL=https://your-backend-url.com

# App URL
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app

# Environment
NODE_ENV=production
```

#### For Backend (Python FastAPI)

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...

# Google Sheets
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SERVICE_ACCOUNT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

# MongoDB
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/database

# Server
PORT=8000
HOST=0.0.0.0

# Optional: WhatsApp
WHATSAPP_ACCESS_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_VERIFY_TOKEN=your_verify_token
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/whatsapp-message
```

### Getting API Keys

#### OpenAI API Key
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign in → API Keys → Create new secret key
3. Copy and save securely

#### Google Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project → Enable Google Sheets API
3. Create Service Account → Download JSON key
4. Share Google Sheet with service account email

#### MongoDB Atlas
1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create cluster → Get connection string
3. Set network access (allow your hosting IPs)

---

## 🔐 Post-Deployment Setup

### 1. Google Sheets Access

Ensure your Google Service Account has access:

1. Open your Google Sheet
2. Click "Share"
3. Add service account email: `your-service-account@project.iam.gserviceaccount.com`
4. Grant "Editor" permissions

### 2. MongoDB Network Access

Allow your hosting provider's IPs:

1. Go to MongoDB Atlas → Network Access
2. Add IP Address:
   - **Vercel**: Allow `0.0.0.0/0` (all IPs) or specific Vercel IPs
   - **Railway/Render**: Allow `0.0.0.0/0` or specific IPs
   - **Docker**: Allow your server's IP

### 3. WhatsApp Webhook (Optional)

If using WhatsApp integration:

1. Go to Meta Developer Console
2. Configure webhook URL: `https://your-backend-url.com/api/whatsapp/webhook`
3. Set verify token to match `WHATSAPP_VERIFY_TOKEN`
4. Subscribe to message events

### 4. Custom Domain

**Vercel**:
1. Dashboard → Project → Settings → Domains
2. Add custom domain
3. Configure DNS as instructed

**Railway/Render**:
1. Settings → Custom Domain
2. Add domain and configure DNS

### 5. SSL/HTTPS

Most platforms (Vercel, Railway, Render) provide SSL automatically. For Docker:

```bash
# Use nginx reverse proxy with Let's Encrypt
# Or use Cloudflare for SSL termination
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue 1: Build Fails - "Module not found"

**Solution**:
```bash
# Ensure all dependencies are in package.json
cd nextjs-app
npm install
npm run build
```

#### Issue 2: Backend API Timeout

**Solution**:
- Increase timeout in `vercel.json`:
```json
{
  "functions": {
    "src/app/api/**/*.ts": {
      "maxDuration": 60
    }
  }
}
```

#### Issue 3: Environment Variables Not Working

**Solution**:
- Verify variables are set in hosting dashboard
- Restart deployment after adding variables
- Check variable names match exactly (case-sensitive)
- For Next.js, prefix public vars with `NEXT_PUBLIC_`

#### Issue 4: MongoDB Connection Failed

**Solution**:
- Check MongoDB Atlas network access settings
- Verify `MONGODB_URI` is correct
- Ensure IP whitelist includes hosting provider IPs

#### Issue 5: Google Sheets Permission Denied

**Solution**:
- Verify service account email has access to sheet
- Check `GOOGLE_PRIVATE_KEY` format (include `\n` for newlines)
- Ensure Google Sheets API is enabled

#### Issue 6: OpenAI API Errors

**Solution**:
- Verify `OPENAI_API_KEY` is valid
- Check API quota/limits
- Ensure key has proper permissions

#### Issue 7: CORS Errors

**Solution**:
- Add CORS middleware in FastAPI backend
- Configure allowed origins in hosting platform
- Check `NEXT_PUBLIC_BACKEND_URL` is set correctly

### Health Check Endpoints

Test your deployment:

```bash
# Frontend health
curl https://your-app.vercel.app/api/health

# Backend health
curl https://your-backend-url.com/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2024-11-11T...",
  "service": "bmc-chat-api"
}
```

### Viewing Logs

**Vercel**:
```bash
vercel logs
vercel logs --follow
```

**Railway**:
- Dashboard → Deployments → View Logs

**Render**:
- Dashboard → Service → Logs

**Docker**:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## 📊 Monitoring & Maintenance

### Recommended Tools

1. **Uptime Monitoring**: UptimeRobot, Pingdom
2. **Error Tracking**: Sentry, Rollbar
3. **Analytics**: Google Analytics, Vercel Analytics
4. **Logs**: Vercel Logs, Railway Logs, or CloudWatch

### Regular Maintenance

1. **Update Dependencies**: Monthly
   ```bash
   npm update
   pip install --upgrade -r requirements.txt
   ```

2. **Monitor API Usage**: Check OpenAI, Google Sheets quotas
3. **Review Logs**: Weekly for errors
4. **Backup Data**: MongoDB backups, Google Sheets exports

---

## 🚀 Quick Start Commands

### Deploy to Vercel (Fastest)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy frontend
cd nextjs-app
vercel --prod

# Set environment variables in Vercel dashboard
```

### Deploy Backend to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

### Deploy with Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Render Documentation](https://render.com/docs)
- [Docker Documentation](https://docs.docker.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Next.js Documentation](https://nextjs.org/docs)

---

## 🆘 Need Help?

1. Check deployment logs in your hosting platform
2. Review error messages in this guide
3. Test health check endpoints
4. Verify environment variables
5. Check service status pages

---

**Last Updated**: November 2024  
**Version**: 1.0.0

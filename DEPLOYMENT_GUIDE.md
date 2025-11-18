# 🚀 BMC Cotización Inteligente - Deployment Guide

## Overview

This guide covers the complete deployment process for the BMC Cotización Inteligente application to Vercel.

## Prerequisites

- GitHub account with access to the repository
- Vercel account (can sign up with GitHub)
- Required API keys and credentials:
  - OpenAI API Key
  - Google Service Account credentials
  - MongoDB Atlas connection string
  - (Optional) WhatsApp Business API credentials

## Deployment Options

### Option 1: Deploy via Vercel Dashboard (Recommended)

#### Step 1: Connect Repository to Vercel

1. Go to [https://vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository: `matiasportugau-ui/bmc-cotizacion-inteligente`
4. Vercel will auto-detect Next.js configuration

#### Step 2: Configure Environment Variables

In the Vercel Dashboard, add the following environment variables:

**Required Variables:**

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...

# Google Sheets API
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_SERVICE_ACCOUNT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

# MongoDB
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/database

# Application
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
```

**Optional Variables:**

```bash
# WhatsApp Business API (for WhatsApp integration)
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_verify_token

# N8N Integration (if using n8n workflows)
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/whatsapp-message
```

#### Step 3: Deploy

1. Click "Deploy"
2. Vercel will build and deploy your application
3. Once complete, you'll receive a deployment URL

#### Step 4: Verify Deployment

Test the following endpoints:

- **Health Check**: `https://your-app.vercel.app/api/health`
- **Dashboard**: `https://your-app.vercel.app`

### Option 2: Deploy via Vercel CLI

#### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

#### Step 2: Login to Vercel

```bash
vercel login
```

#### Step 3: Configure Environment Variables

Create a `.env.production` file (do not commit this):

```bash
OPENAI_API_KEY=sk-proj-...
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_SERVICE_ACCOUNT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/database
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
```

#### Step 4: Deploy

```bash
# Production deployment
vercel --prod

# Or preview deployment
vercel
```

### Option 3: Automated Deployment via GitHub Actions

The repository includes a CI/CD pipeline that automatically deploys to Vercel when code is pushed to the `main` branch.

#### Setup GitHub Secrets

Add the following secrets to your GitHub repository (Settings → Secrets and variables → Actions):

1. `VERCEL_TOKEN` - Your Vercel access token
2. `VERCEL_ORG_ID` - Your Vercel organization ID
3. `VERCEL_PROJECT_ID` - Your Vercel project ID

**How to get these values:**

```bash
# Install Vercel CLI
npm install -g vercel

# Link your project
vercel link

# Get your org and project IDs from .vercel/project.json
cat .vercel/project.json

# Get your token from: https://vercel.com/account/tokens
```

#### Trigger Deployment

Push to the `main` branch:

```bash
git push origin main
```

The GitHub Actions workflow will:
1. Run tests
2. Build the application
3. Deploy to Vercel (if on main branch)

## Post-Deployment Configuration

### 1. Google Sheets Setup

Ensure your Google Service Account has access to the target spreadsheet:

1. Open your Google Sheet
2. Click "Share"
3. Add your service account email
4. Grant "Editor" permissions

### 2. MongoDB Atlas Network Access

Allow Vercel's IP addresses:

1. Go to MongoDB Atlas Dashboard
2. Network Access → Add IP Address
3. Add `0.0.0.0/0` (allow from anywhere) **OR** add specific Vercel IPs

### 3. WhatsApp Webhook (Optional)

If using WhatsApp integration:

1. Configure webhook URL in Meta Developer Console
2. Set webhook URL to: `https://your-app.vercel.app/api/whatsapp/webhook`
3. Set verify token to match your `WHATSAPP_VERIFY_TOKEN`

### 4. Custom Domain (Optional)

To use a custom domain:

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed by Vercel

## Monitoring and Debugging

### View Logs

```bash
# View deployment logs
vercel logs

# View function logs
vercel logs --follow
```

### Common Issues

#### Issue: OpenAI API errors

**Solution**: Verify `OPENAI_API_KEY` is set correctly in Vercel environment variables.

#### Issue: Google Sheets permission denied

**Solution**: Ensure the service account has been granted access to the spreadsheet.

#### Issue: MongoDB connection timeout

**Solution**: Check network access settings in MongoDB Atlas.

#### Issue: Build fails with "Module not found"

**Solution**: Ensure all dependencies are in `package.json` and run `npm install` locally.

### Health Check Endpoint

Monitor application health:

```bash
curl https://your-app.vercel.app/api/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2024-11-11T...",
  "environment": "production",
  "services": {
    "openai": { "configured": true, "status": "ready" },
    "googleSheets": { "configured": true, "status": "ready" },
    "mongodb": { "configured": true, "status": "ready" }
  }
}
```

## Rollback

If you need to rollback to a previous deployment:

1. Go to Vercel Dashboard → Deployments
2. Find the previous working deployment
3. Click "..." → "Promote to Production"

Or via CLI:

```bash
vercel rollback
```

## Environment-Specific Configuration

### Development

```bash
npm run dev
```

### Staging

Create a preview deployment:

```bash
vercel
```

### Production

```bash
vercel --prod
```

## Security Best Practices

1. **Never commit** `.env` files or credentials to the repository
2. **Rotate API keys** regularly
3. **Use environment variables** for all sensitive data
4. **Enable** Vercel's authentication for staging environments
5. **Monitor** API usage and set up alerts

## Support

For issues or questions:

- Check Vercel deployment logs
- Review the health check endpoint
- Consult the [Next.js documentation](https://nextjs.org/docs)
- Review the [Vercel documentation](https://vercel.com/docs)

---

**Last Updated**: November 2024  
**Version**: 1.0.0

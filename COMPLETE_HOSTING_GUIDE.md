# 🚀 Complete Hosting Guide for BMC Chatbot

## 📖 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Deployment Options](#deployment-options)
4. [Detailed Guides](#detailed-guides)
5. [Cost Comparison](#cost-comparison)
6. [Troubleshooting](#troubleshooting)

---

## Overview

Your BMC Chatbot system consists of:

- **Python API** (FastAPI) - Backend with AI processing
- **Next.js Frontend** - User interface
- **MongoDB Database** - Data storage
- **WhatsApp Integration** - Customer communication

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                         │
│  Next.js App (Vercel or cPanel)                    │
│  - User interface                                   │
│  - Quote forms                                      │
│  - Dashboard                                        │
└────────────────┬────────────────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────┐
│                   BACKEND API                        │
│  Python/FastAPI (Railway or Render)                │
│  - AI Processing (OpenAI)                          │
│  - Quote calculations                              │
│  - WhatsApp webhooks                               │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│                    DATABASE                          │
│  MongoDB (Railway or Atlas)                        │
│  - Quotes storage                                   │
│  - Customer data                                    │
│  - Chat history                                     │
└─────────────────────────────────────────────────────┘
```

---

## Quick Start

### Automated Deployment (Recommended)

Run the deployment script:

```bash
chmod +x deploy-chatbot.sh
./deploy-chatbot.sh all
```

This interactive script will guide you through the entire deployment process.

### Manual Deployment

Follow the detailed guides for each platform:

1. [Railway Deployment](RAILWAY_DEPLOYMENT_GUIDE.md)
2. [cPanel Deployment](CPANEL_HOSTING_GUIDE.md)

---

## Deployment Options

### ⭐ Option 1: Full Cloud (RECOMMENDED)

**Best for:** Production use, scalability, reliability

```
Frontend:  Vercel (Free)
Backend:   Railway (Free $5/month credit)
Database:  Railway MongoDB (Included)
```

**Advantages:**
- ✅ Completely free (within limits)
- ✅ Automatic deployments from Git
- ✅ SSL certificates included
- ✅ High performance and reliability
- ✅ Easy scaling
- ✅ No server management

**Deployment time:** ~15 minutes

**Steps:**
```bash
# 1. Deploy backend to Railway
./deploy-chatbot.sh railway

# 2. Deploy frontend to Vercel
./deploy-chatbot.sh vercel
```

---

### 🏢 Option 2: Hybrid (Use Your cPanel)

**Best for:** Using existing cPanel hosting, custom domain

```
Frontend:  cPanel Static Files (Your hosting)
Backend:   Railway (Free)
Database:  Railway MongoDB (Included)
```

**Advantages:**
- ✅ Utilize your existing cPanel hosting
- ✅ Keep frontend on your domain
- ✅ Backend on reliable cloud infrastructure
- ✅ Cost-effective

**Deployment time:** ~20 minutes

**Steps:**
```bash
# 1. Deploy backend to Railway
./deploy-chatbot.sh railway

# 2. Prepare static files for cPanel
./deploy-chatbot.sh cpanel

# 3. Upload to cPanel (see generated instructions)
```

---

### 🔧 Option 3: Alternative Cloud (Railway Alternative)

**Best for:** If Railway is not available in your region

```
Frontend:  Vercel (Free)
Backend:   Render.com (Free)
Database:  MongoDB Atlas (Free)
```

**Advantages:**
- ✅ Similar to Option 1
- ✅ Good Railway alternative
- ✅ Free tier available

**Deployment time:** ~20 minutes

**Steps:**
```bash
# 1. Deploy backend to Render
./deploy-chatbot.sh render

# 2. Deploy frontend to Vercel
./deploy-chatbot.sh vercel
```

---

## Detailed Guides

### 1. Railway Deployment

Full guide: [RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md)

**Quick steps:**

1. Create Railway account: https://railway.app
2. Install Railway CLI: `npm i -g @railway/cli`
3. Deploy:
   ```bash
   railway login
   railway init
   railway add mongodb
   railway up
   ```

4. Set environment variables in Railway dashboard:
   ```env
   OPENAI_API_KEY=your-key
   OPENAI_MODEL=gpt-4o-mini
   MONGODB_URI=${{MongoDB.MONGO_URL}}
   ```

5. Get your API URL: `https://your-app.railway.app`

---

### 2. Vercel Deployment

**Quick steps:**

1. Install Vercel CLI: `npm i -g vercel`
2. Navigate to Next.js app:
   ```bash
   cd nextjs-app
   npm install
   ```

3. Deploy:
   ```bash
   vercel --prod
   ```

4. Set environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-app.railway.app
   ```

---

### 3. cPanel Deployment

Full guide: [CPANEL_HOSTING_GUIDE.md](CPANEL_HOSTING_GUIDE.md)

**Your cPanel details:**
- Domain: grow-importa.com.uy
- User: growimpo
- Directory: /homeX/growimpo

**Quick steps:**

1. Build static files:
   ```bash
   cd nextjs-app
   npm run build
   ```

2. Upload `out/` directory to cPanel:
   - Via File Manager: `public_html/`
   - Via FTP: Host: grow-importa.com.uy
   - Via SCP: `scp -r out/* growimpo@grow-importa.com.uy:~/public_html/`

3. Configure SSL in cPanel (free Let's Encrypt)

4. Access: https://grow-importa.com.uy

---

## Cost Comparison

| Item | Option 1 (Full Cloud) | Option 2 (Hybrid) | Option 3 (Alternative) |
|------|----------------------|-------------------|------------------------|
| **Frontend** | Vercel - $0 | cPanel - ~$5-10/mo | Vercel - $0 |
| **Backend** | Railway - $0 ($5 credit) | Railway - $0 | Render - $0 |
| **Database** | Railway MongoDB - $0 | Railway MongoDB - $0 | Atlas - $0 |
| **SSL** | Included - $0 | Let's Encrypt - $0 | Included - $0 |
| **Total/month** | **$0** | **~$5-10** | **$0** |
| **Ease of setup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Scalability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

### Free Tier Limits

**Railway:**
- $5 credit per month
- ~500 hours of usage
- 512MB RAM, 1GB storage
- Perfect for small/medium projects

**Vercel:**
- 100GB bandwidth per month
- Unlimited projects
- Automatic SSL
- CDN included

**Render:**
- 750 hours per month (free tier)
- Auto-sleep after 15min inactivity
- 512MB RAM

**MongoDB Atlas:**
- 512MB storage
- Shared cluster
- Perfect for development/small production

---

## Environment Variables Setup

### Required Variables

Create a `.env` file (DO NOT commit this):

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# MongoDB Connection
MONGODB_URI=your-mongodb-connection-string

# Server Configuration
PORT=8000
HOST=0.0.0.0

# WhatsApp Configuration (Optional)
WHATSAPP_VERIFY_TOKEN=your-verify-token-here
WHATSAPP_ACCESS_TOKEN=your-whatsapp-api-token

# Google Sheets (Optional)
GOOGLE_SHEETS_CREDENTIALS=your-service-account-json
GOOGLE_SHEET_ID=your-google-sheet-id

# Frontend Configuration
NEXT_PUBLIC_API_URL=https://your-api-url.railway.app
```

### Where to Set Variables

**Railway:**
- Dashboard → Project → Variables tab

**Vercel:**
- Dashboard → Project → Settings → Environment Variables

**Render:**
- Dashboard → Service → Environment

**cPanel:**
- Not needed (API is external)

---

## Testing Your Deployment

### 1. Test API Health

```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "api": "online",
    "mongodb": "online",
    "openai": "configured"
  }
}
```

### 2. Test Chat Endpoint

```bash
curl -X POST https://your-app.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola, quiero cotizar Isodec 100mm de 10x5 metros",
    "session_id": "test123"
  }'
```

### 3. Test Frontend

Visit your deployed URL:
- Vercel: Check deployment URL in dashboard
- cPanel: https://grow-importa.com.uy

Verify:
- ✅ Page loads without errors
- ✅ Chat interface works
- ✅ Quote form submits successfully
- ✅ API connection works

---

## WhatsApp Integration

### Configure Webhook

After deploying your API:

1. Get your webhook URL:
   ```
   https://your-app.railway.app/api/whatsapp/webhook
   ```

2. Go to Meta Business Suite:
   - https://developers.facebook.com
   - Select your app
   - WhatsApp → Configuration

3. Set webhook:
   - **URL:** `https://your-app.railway.app/api/whatsapp/webhook`
   - **Verify Token:** (same as `WHATSAPP_VERIFY_TOKEN` in env)

4. Subscribe to webhook events:
   - messages
   - messaging_postbacks

### Test WhatsApp

1. Send a message to your WhatsApp Business number
2. Check Railway logs for webhook events
3. Verify response is sent back

---

## Troubleshooting

### Build Fails

**Issue:** Deployment fails during build

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version  # Should be 3.9+
   ```

2. **Test build locally:**
   ```bash
   pip install -r requirements.txt
   python sistema_completo_integrado.py
   ```

3. **Check dependencies:**
   - Ensure all imports are available
   - Verify `requirements.txt` is complete

### Database Connection Fails

**Issue:** Cannot connect to MongoDB

**Solutions:**

1. **Verify connection string:**
   - Railway: Use `${{MongoDB.MONGO_URL}}`
   - Atlas: Get from cluster connect button

2. **Check network access:**
   - Atlas: Allow all IPs (0.0.0.0/0)
   - Railway: Automatic

3. **Test connection:**
   ```python
   from pymongo import MongoClient
   client = MongoClient("your-connection-string")
   print(client.list_database_names())
   ```

### API Not Responding

**Issue:** API returns 503 or doesn't respond

**Solutions:**

1. **Check logs:**
   - Railway: Dashboard → Logs
   - Render: Dashboard → Logs

2. **Verify environment variables:**
   - All required vars are set
   - No typos in variable names

3. **Check service status:**
   - Railway: Dashboard shows "Running"
   - Render: Service is not sleeping

### Frontend Can't Connect to API

**Issue:** Frontend shows connection errors

**Solutions:**

1. **Verify API URL:**
   ```javascript
   console.log(process.env.NEXT_PUBLIC_API_URL)
   ```

2. **Check CORS:**
   - API allows your frontend domain
   - Update `allow_origins` in `sistema_completo_integrado.py`

3. **Test API directly:**
   ```bash
   curl https://your-api-url.railway.app/health
   ```

### cPanel Upload Issues

**Issue:** Files don't work after upload to cPanel

**Solutions:**

1. **Check file permissions:**
   - Files: 644
   - Directories: 755

2. **Verify .htaccess:**
   - Should be in root directory
   - Check rewrite rules

3. **Check subdirectory:**
   - If in subdirectory, update base path
   - Update `NEXT_PUBLIC_API_URL`

---

## Monitoring & Maintenance

### Logs

**Railway:**
```bash
railway logs
```

**Vercel:**
- Dashboard → Deployments → Select deployment → Function logs

**Render:**
- Dashboard → Logs (real-time)

### Metrics

Monitor in dashboards:
- Request count
- Response times
- Error rates
- Resource usage (CPU, memory)

### Alerts

Set up alerts for:
- Deployment failures
- High error rates
- Resource limits
- Downtime

**Railway:**
- Settings → Notifications → Add webhook

**Vercel:**
- Settings → Integrations → Add Slack/Discord

---

## Scaling

### When to Scale

Scale up when you see:
- High response times (>2 seconds)
- Memory usage >80%
- CPU usage >80%
- Free tier limits exceeded

### How to Scale

**Railway:**
1. Upgrade to Hobby plan ($5/mo)
2. Increase replicas
3. Add more resources

**Vercel:**
- Automatic scaling included
- Upgrade for higher limits

**Database:**
- Railway: Add more storage
- Atlas: Upgrade cluster tier

---

## Security Checklist

- [ ] Environment variables not in Git
- [ ] `.env` in `.gitignore`
- [ ] API keys rotated regularly
- [ ] CORS configured for production domains only
- [ ] SSL certificates installed
- [ ] WhatsApp webhook signature verified
- [ ] Rate limiting enabled
- [ ] Database backups configured
- [ ] Admin endpoints protected

---

## Next Steps After Deployment

1. **Test thoroughly:**
   - All endpoints work
   - Chat is responsive
   - Quotes calculate correctly
   - WhatsApp integration works

2. **Configure domain:**
   - Point custom domain to services
   - Set up SSL
   - Update CORS settings

3. **Set up monitoring:**
   - Error tracking (Sentry)
   - Analytics (Google Analytics)
   - Uptime monitoring (UptimeRobot)

4. **Document for team:**
   - Deployment process
   - Environment variables
   - Troubleshooting steps

5. **Plan backups:**
   - Database backups
   - Code in version control
   - Environment variables documented

---

## Support & Resources

### Documentation
- [Railway Docs](https://docs.railway.app)
- [Vercel Docs](https://vercel.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Next.js Docs](https://nextjs.org/docs)

### Your Project Guides
- [Railway Deployment Guide](RAILWAY_DEPLOYMENT_GUIDE.md)
- [cPanel Hosting Guide](CPANEL_HOSTING_GUIDE.md)

### Get Help
- Check deployment logs
- Review this guide
- Test locally first
- Check service status pages

---

## Quick Reference

### Deployment Commands

```bash
# Full automated deployment
./deploy-chatbot.sh all

# Deploy to Railway only
./deploy-chatbot.sh railway

# Deploy to Vercel only
./deploy-chatbot.sh vercel

# Prepare cPanel files
./deploy-chatbot.sh cpanel

# Deploy to Render
./deploy-chatbot.sh render
```

### Your URLs (After Deployment)

```
API:      https://your-app.railway.app
Frontend: https://grow-importa.com.uy (cPanel)
          or
          https://your-app.vercel.app
Docs:     https://your-app.railway.app/docs
Health:   https://your-app.railway.app/health
```

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] OpenAI API key obtained
- [ ] Code tested locally
- [ ] Environment variables documented
- [ ] Git repository up to date
- [ ] `.env` not in Git

### Railway Deployment
- [ ] Railway account created
- [ ] Railway CLI installed
- [ ] MongoDB added
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] Health check passes

### Frontend Deployment
- [ ] Next.js builds successfully
- [ ] API URL configured
- [ ] Deployment successful
- [ ] Site loads correctly
- [ ] API connection works

### Post-Deployment
- [ ] All endpoints tested
- [ ] WhatsApp webhook configured
- [ ] SSL certificates active
- [ ] Monitoring set up
- [ ] Team documented
- [ ] Backup plan in place

---

**🎉 Congratulations! Your chatbot is now hosted and ready to serve customers!**

**Recommended: Start with Option 1 (Full Cloud) for the easiest deployment experience.**

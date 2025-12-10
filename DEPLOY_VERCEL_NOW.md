# 🎨 Vercel Frontend Deployment Guide

## Overview

Deploy the Next.js frontend dashboard to Vercel for the chatbot-2311 system.

---

## Pre-Deployment Checklist

- [ ] Railway backend deployed and working
- [ ] Next.js build succeeds locally (`npm run build`)
- [ ] Have Vercel account (free tier works)
- [ ] Have required environment variables ready

---

## Option 1: Vercel Dashboard Deployment ⭐ RECOMMENDED

### Step 1: Create Vercel Account (if needed)

1. Go to: https://vercel.com/signup
2. Sign up with GitHub (recommended)
3. Authorize Vercel to access your repositories

### Step 2: Import Project

1. Go to: https://vercel.com/new
2. Click **"Import Git Repository"**
3. Find: `matiasportugau-ui/chatbot-2311`
4. Click **"Import"**

### Step 3: Configure Project

**Framework Preset:** Next.js (auto-detected)

**Root Directory:** Leave as `.` (project root)

**Build Command:** `npm run build` (auto-filled)

**Output Directory:** `.next` (auto-filled)

### Step 4: Add Environment Variables

Click "Environment Variables" and add:

| Name | Value | Notes |
|------|-------|-------|
| `NEXT_PUBLIC_API_URL` | `https://web-production-b896.up.railway.app` | Railway backend URL |
| `MONGODB_URI` | `mongodb+srv://...` | Your MongoDB Atlas connection string |
| `OPENAI_API_KEY` | `sk-...` | Your OpenAI key |
| `NODE_ENV` | `production` | Auto-set, verify |

**For all environments:** Select "Production", "Preview", and "Development"

### Step 5: Deploy

1. Click **"Deploy"**
2. Wait for build to complete (~2-3 minutes)
3. Get your deployment URL: `https://chatbot-2311.vercel.app` (or similar)

---

## Option 2: Vercel CLI Deployment

### Install Vercel CLI

```bash
npm install -g vercel
```

### Login to Vercel

```bash
vercel login
```
Follow the authentication flow.

### Link Project

```bash
cd /Users/matias/chatbot-2311
vercel link
```

**Follow prompts:**
- Set up and deploy? Yes
- Scope: (select your account)
- Link to existing project? No
- Project name: chatbot-2311
- Directory: `./` (current)

### Configure Environment Variables

```bash
# Add Railway backend URL
vercel env add NEXT_PUBLIC_API_URL
# When prompted, enter: https://web-production-b896.up.railway.app
# Select: Production, Preview, Development

# Add MongoDB URI
vercel env add MONGODB_URI
# Enter your MongoDB connection string
# Select: Production, Preview, Development  

# Add OpenAI Key
vercel env add OPENAI_API_KEY
# Enter: your OpenAI API key
# Select: Production, Preview, Development
```

### Deploy to Production

```bash
vercel --prod
```

**Expected output:**
```
🔍  Inspect: https://vercel.com/...
✅  Production: https://chatbot-2311.vercel.app
```

---

## Verification Steps

### 1. Check Deployment Status

In Vercel Dashboard:
- Go to your project
- Check deployment status: ✅ "Ready"
- Note the production URL

### 2. Test Frontend Load

```bash
curl -I https://your-app.vercel.app
```

**Expected:** `HTTP/2 200`

### 3. Test Chat Integration

1. Open: `https://your-app.vercel.app/chat` (or similar)
2. Send test message: "Hola"
3. Verify response from backend

### 4. Check API Routes

```bash
# Test Next.js API route
curl https://your-app.vercel.app/api/health
```

### 5. Verify Frontend-Backend Connection

Open browser console (F12) and check for CORS errors:
- Should connect to Railway backend successfully
- No CORS errors
- API calls complete successfully

---

## Troubleshooting

### Build Fails - TypeScript Errors

```bash
# Run build locally first
cd /Users/matias/chatbot-2311
npm run build

# Fix any errors shown
npm run lint
npm run type-check
```

Then redeploy to Vercel.

### Environment Variables Not Working

1. In Vercel Dashboard → Settings → Environment Variables
2. Verify all variables are set for **Production**
3. **Trigger redeploy** after changing variables
4. Variables only apply to new deployments, not existing ones

### CORS Errors

Update Railway backend to allow Vercel domain:

1. Edit Railway environment variable: `ALLOWED_ORIGINS`
2. Add your Vercel URL: `https://your-app.vercel.app`
3. Redeploy Railway backend

### Next.js Build Timeout

In Vercel Dashboard → Settings → Functions:
- Increase "Max Duration": 30s → 60s
- Enable "Edge Runtime" if applicable

---

## Post-Deployment Configuration

### 1. Custom Domain (Optional)

In Vercel Dashboard → Settings → Domains:
1. Add custom domain: `chatbot.yourdomain.com`
2. Configure DNS records as shown
3. Wait for SSL certificate provisioning

### 2. Update Railway CORS

Add Vercel URL to Railway's allowed origins:

```bash
# In Railway Dashboard
ALLOWED_ORIGINS=https://your-app.vercel.app,https://chatbot.yourdomain.com
```

### 3. Configure Analytics

Vercel automatically tracks:
- Page views
- Performance metrics
- Error rates

View in: Dashboard → Analytics

---

## Vercel Deployment URLs

After deployment, you'll have:

| Environment | URL Pattern |
|-------------|-------------|
| **Production** | `https://chatbot-2311.vercel.app` |
| **Preview** | `https://chatbot-2311-git-branch.vercel.app` |
| **Development** | Local: `http://localhost:3000` |

---

## Next Steps

After successful Vercel deployment:

1. ✅ Update task.md - mark Vercel deployment complete
2. 🧪 Run end-to-end integration tests
3. 📱 Test WhatsApp integration (if configured)
4. 📊 Set up monitoring and alerts
5. 📝 Document final deployment URLs

---

## Quick Reference Commands

```bash
# Check deployment status
vercel ls

# View logs
vercel logs

# Rollback deployment
vercel rollback

# Open project in dashboard
vercel open
```

---

**Ready to deploy?** Start with Option 1 (Dashboard) for the easiest experience!

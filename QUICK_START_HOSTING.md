# ⚡ Quick Start: Host Your Chatbot in 5 Minutes

This is a condensed guide to get your chatbot hosted quickly. For detailed information, see [HOSTING_GUIDE.md](./HOSTING_GUIDE.md).

## 🎯 Fastest Option: Vercel (Recommended)

### Prerequisites Checklist

- [ ] GitHub account
- [ ] Vercel account (sign up at [vercel.com](https://vercel.com))
- [ ] OpenAI API key
- [ ] Google Sheets API credentials (optional)
- [ ] MongoDB connection string (optional)

### Step-by-Step (5 minutes)

#### 1. Push Code to GitHub (if not already)

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2. Deploy to Vercel

**Option A: Via Dashboard (Easiest)**
1. Go to [vercel.com](https://vercel.com) → Sign in
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Root Directory**: Leave empty (or `nextjs-app` if deploying only frontend)
   - **Framework**: Next.js (auto-detected)
5. Add Environment Variables (see below)
6. Click "Deploy"

**Option B: Via CLI**
```bash
npm install -g vercel
vercel login
vercel --prod
```

#### 3. Set Environment Variables

In Vercel Dashboard → Settings → Environment Variables, add:

```bash
# Required
OPENAI_API_KEY=sk-proj-your-key-here
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app

# Optional but recommended
GOOGLE_SHEET_ID=your-sheet-id
GOOGLE_SERVICE_ACCOUNT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/database
```

#### 4. Verify Deployment

```bash
# Test your deployment
curl https://your-app.vercel.app/api/health

# Expected response:
# {"status":"healthy","timestamp":"...","service":"bmc-chat-api"}
```

#### 5. Access Your Chatbot

Open: `https://your-app.vercel.app`

---

## 🔧 Alternative: Backend on Railway (If you need Python FastAPI)

If your chatbot uses the Python FastAPI backend (`api_server.py`):

### Deploy Backend to Railway

1. **Sign up**: [railway.app](https://railway.app)
2. **New Project** → Deploy from GitHub
3. **Configure**:
   - Root Directory: `/`
   - Start Command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
4. **Add Environment Variables** (same as above)
5. **Get Backend URL**: `https://your-backend.railway.app`

### Update Frontend

In Vercel, add:
```bash
NEXT_PUBLIC_BACKEND_URL=https://your-backend.railway.app
```

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] Code is committed to Git
- [ ] `.env` files are NOT committed (check `.gitignore`)
- [ ] All dependencies are in `package.json` (frontend) or `requirements.txt` (backend)
- [ ] Build works locally: `npm run build` (frontend) or `python api_server.py` (backend)
- [ ] API keys are ready
- [ ] Google Sheet is shared with service account email (if using)
- [ ] MongoDB network access allows your hosting IPs (if using)

---

## 🚀 Using the Deployment Script

You have an automated deployment script:

```bash
# Full deployment
./scripts/deploy-ai-agent.sh --full-deployment --json

# Check only (no deployment)
./scripts/deploy-ai-agent.sh --check-only --json

# Deploy only
./scripts/deploy-ai-agent.sh --deploy vercel --json
```

---

## 🐛 Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Build fails | Run `npm install` in `nextjs-app/` |
| Environment variables not working | Restart deployment after adding vars |
| MongoDB connection failed | Add `0.0.0.0/0` to MongoDB Atlas network access |
| Google Sheets permission denied | Share sheet with service account email |
| CORS errors | Check `NEXT_PUBLIC_BACKEND_URL` is set correctly |

---

## 📞 Need More Help?

- **Detailed Guide**: See [HOSTING_GUIDE.md](./HOSTING_GUIDE.md)
- **Deployment Guide**: See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Troubleshooting**: Check logs in your hosting platform dashboard

---

## ✅ Post-Deployment Checklist

After deployment:

- [ ] Health check endpoint works: `/api/health`
- [ ] Chat interface loads: `/`
- [ ] Test sending a message
- [ ] Check logs for errors
- [ ] Set up custom domain (optional)
- [ ] Configure monitoring/analytics (optional)

---

**Time to deploy**: ~5 minutes  
**Cost**: Free tier available on Vercel  
**Difficulty**: ⭐ Easy

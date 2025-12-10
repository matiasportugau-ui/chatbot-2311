# 🚀 Railway Deployment Guide - Quick Fix

## Current Issue

Railway backend is deployed but `/api/chat` endpoint returns 404 errors.

**Root Cause:** Railway is running an outdated version of the code.

**Solution:** Trigger a redeploy to use the latest `sistema_completo_integrado.py`.

---

## Option 1: Manual Redeploy (Railway Dashboard) ⭐ RECOMMENDED

1. **Open Railway Dashboard:**
   - Go to: https://railway.app/dashboard
   - Select project: **zesty-art**
   - Navigate to environment: **production**

2. **Find Your Service:**
   - Look for the service with domain: `web-production-b896.up.railway.app`
   - Click on the service

3. **Trigger Redeploy:**
   - Click on the **"Deployments"** tab
   - Find the most recent deployment
   - Click the **⋯** (three dots menu)
   - Select **"Redeploy"**
   - Confirm the redeploy

4. **Wait for Build:**
   - Watch the build logs in real-time
   - Wait for status: **"Success"** ✅
   - Deployment takes ~3-5 minutes

5. **Verify Deployment:**
   ```bash
   # Run this command to test:
   bash test_railway.sh
   ```
   
   **Expected:** Chat endpoint should return a response (not 404)

---

## Option 2: Git Push Trigger

If Railway is connected to GitHub auto-deploy:

```bash
cd /Users/matias/chatbot-2311

# Create empty commit to trigger deployment
git commit --allow-empty -m "Trigger Railway redeploy"

# Push to main branch
git push origin main
```

**Wait 2-3 minutes** for Railway to detect the push and redeploy automatically.

---

## Option 3: Railway CLI (Non-Interactive)

Since Railway CLI requires TTY, use this workaround:

```bash
# If you have access to the service name:
railway redeploy --service "web" --yes

# Or use environment variable:
RAILWAY_SERVICE="web" railway redeploy --yes
```

---

## Verification Steps

After redeploy completes:

### 1. Test Health Endpoint
```bash
curl https://web-production-b896.up.railway.app/health | jq .
```

**Expected:**
```json
{
  "status": "healthy",
  "services": {
    "mongodb": "online",
    "openai": "configured"
  }
}
```

### 2. Test Chat Endpoint (Critical!)
```bash
curl -X POST https://web-production-b896.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hola","session_id":"test123"}' | jq .
```

**Expected:**
```json
{
  "response": "Hola! Soy el asistente...",
  "session_id": "test123"
}
```

**NOT Expected:** `{"detail":"Not Found"}` ❌

### 3. Run Full Test Suite
```bash
bash test_railway.sh
```

---

## Troubleshooting

### If Chat Endpoint Still Returns 404

1. **Check Railway Logs:**
   ```bash
   railway logs --project zesty-art
   ```
   
   Look for:
   - Import errors (missing dependencies)
   - MongoDB connection failures
   - OpenAI API key issues

2. **Verify Environment Variables:**
   - In Railway Dashboard → Service → Variables
   - Required variables:
     - `OPENAI_API_KEY`
     - `MONGODB_URI`
     - `PORT` (should be auto-set)

3. **Check Start Command:**
   - In Railway Dashboard → Service → Settings
   - Should be: `uvicorn sistema_completo_integrado:app --host 0.0.0.0 --port $PORT`
   - Verify it matches `railway.json`

4. **Rebuild from Scratch:**
   - In Deployments tab
   - Click ⋯ on latest deployment
   - Select "Rebuild"

### If MongoDB Connection Fails

```bash
# From Railway Dashboard:
# 1. Check MongoDB service is running
# 2. Verify MONGODB_URI variable is set correctly
# 3. Check network access in MongoDB Atlas
```

---

## Next Steps After Successful Redeploy

1. ✅ Mark Railway deployment as complete
2. 🔄 Move to Vercel frontend deployment
3. 🧪 Run integration tests
4. 📊 Set up monitoring

---

## Quick Reference

| Item | Value |
|------|-------|
| **Project** | zesty-art |
| **Environment** | production |
| **URL** | https://web-production-b896.up.railway.app |
| **Health** | /health |
| **Chat API** | /api/chat |
| **Docs** | /docs |

---

**Need Help?** Check Railway deployment logs or run `bash test_railway.sh` for diagnostics.

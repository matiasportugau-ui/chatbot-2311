# 🚀 Quick Start: Host Your Chatbot NOW

## 🎯 Choose Your Path (2-3 options)

Based on your cPanel hosting at **grow-importa.com.uy**, here are the best options:

---

## ⭐ Option 1: Full Cloud (FASTEST & EASIEST)

**Time:** 15 minutes | **Cost:** FREE | **Difficulty:** ⭐⭐

Deploy everything to free cloud services - no cPanel needed!

### What you'll get:
- ✅ Professional hosting on Railway & Vercel
- ✅ Automatic SSL certificates
- ✅ Auto-deploy from Git
- ✅ 99.9% uptime
- ✅ Free tier (enough for most needs)

### Quick Steps:

```bash
# 1. Run the automated deployment script
chmod +x deploy-chatbot.sh
./deploy-chatbot.sh all

# 2. Follow the interactive prompts
# - Choose Railway for API
# - Choose Vercel for frontend
# - Done!
```

**Your URLs:**
- API: `https://your-app.railway.app`
- App: `https://your-app.vercel.app`

---

## 🏢 Option 2: Use Your cPanel (UTILIZE EXISTING HOSTING)

**Time:** 20 minutes | **Cost:** ~$0-5/month | **Difficulty:** ⭐⭐⭐

Use your existing cPanel hosting + free Railway for backend.

### What you'll get:
- ✅ Frontend on your domain (grow-importa.com.uy)
- ✅ Backend on reliable Railway
- ✅ Utilize your existing hosting
- ✅ Professional setup

### Quick Steps:

```bash
# 1. Deploy backend to Railway
./deploy-chatbot.sh railway

# 2. Build and prepare frontend
./deploy-chatbot.sh cpanel

# 3. Upload to your cPanel
# Files are ready in: deployment/cpanel/
# Follow instructions in: deployment/UPLOAD_TO_CPANEL.txt
```

**cPanel Upload:**
1. Log into cPanel
2. File Manager → public_html/
3. Upload files from `deployment/cpanel/`

**Your URLs:**
- API: `https://your-app.railway.app`
- App: `https://grow-importa.com.uy`

---

## 📊 Comparison Table

| Feature | Option 1 (Full Cloud) | Option 2 (cPanel Hybrid) |
|---------|----------------------|-------------------------|
| **Setup time** | 15 min | 20 min |
| **Cost** | $0 | $0-5/mo |
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Ease** | Very Easy | Moderate |
| **Your domain** | New domain | Your existing domain |
| **SSL** | Auto included | Manual setup in cPanel |
| **Updates** | Auto deploy on Git push | Manual upload |

---

## 🎬 Step-by-Step: Option 1 (Recommended)

### Prerequisites (One-time setup)

1. **Create accounts** (free, 2 minutes each):
   - Railway: https://railway.app
   - Vercel: https://vercel.com
   - Both support GitHub login

2. **Get OpenAI API Key** (if you don't have one):
   - Visit: https://platform.openai.com/api-keys
   - Create new key
   - Copy it (you'll need it soon)

### Deployment Steps

#### Step 1: Deploy Backend to Railway (8 minutes)

```bash
# Open terminal in your project directory
cd /workspace

# Option A: Use automated script (easiest)
./deploy-chatbot.sh railway

# Option B: Manual deployment
npm install -g @railway/cli
railway login
railway init
railway add mongodb
```

**Set environment variables in Railway dashboard:**
1. Go to https://railway.app/dashboard
2. Select your project
3. Click "Variables" tab
4. Add these:
   ```
   OPENAI_API_KEY = your-openai-key-here
   OPENAI_MODEL = gpt-4o-mini
   MONGODB_URI = ${{MongoDB.MONGO_URL}}
   PORT = 8000
   HOST = 0.0.0.0
   ```

5. Copy your Railway URL (e.g., `https://your-app.railway.app`)

#### Step 2: Deploy Frontend to Vercel (5 minutes)

```bash
# Option A: Use automated script
./deploy-chatbot.sh vercel

# Option B: Manual deployment
npm install -g vercel
cd nextjs-app
npm install
vercel --prod
```

**When prompted:**
- Project name: `bmc-chatbot`
- Framework: `Next.js`
- Build command: (leave default)
- Output directory: (leave default)

**Set environment variable:**
1. In Vercel dashboard
2. Settings → Environment Variables
3. Add:
   ```
   NEXT_PUBLIC_API_URL = https://your-app.railway.app
   ```

#### Step 3: Test Your Deployment (2 minutes)

1. **Test API:**
   ```bash
   curl https://your-app.railway.app/health
   ```
   
   Should return:
   ```json
   {"status": "healthy"}
   ```

2. **Test Frontend:**
   - Visit your Vercel URL
   - Try the chat interface
   - Create a test quote

3. **Done!** 🎉

---

## 🎬 Step-by-Step: Option 2 (cPanel)

### Prerequisites

1. **Deploy backend first** (Railway - same as Option 1 Step 1)
2. **cPanel access ready**:
   - URL: Your hosting provider's cPanel
   - User: `growimpo`
   - Password: Your cPanel password

### Deployment Steps

#### Step 1: Deploy Backend to Railway (8 minutes)

Same as Option 1, Step 1 above.

#### Step 2: Build Static Files (5 minutes)

```bash
# Run automated build
./deploy-chatbot.sh cpanel

# This will:
# - Configure Next.js for static export
# - Build optimized files
# - Create deployment package
# - Generate upload instructions
```

Files will be ready in: `deployment/cpanel/`

#### Step 3: Upload to cPanel (7 minutes)

**Method A: cPanel File Manager (Easiest)**

1. Log into cPanel
2. Click "File Manager"
3. Navigate to `public_html/`
4. Click "Upload"
5. Select all files from `deployment/cpanel/`
6. Wait for upload to complete
7. Set permissions:
   - Files: 644
   - Directories: 755

**Method B: FTP (Faster for many files)**

1. Open FileZilla (or any FTP client)
2. Connect:
   - Host: `grow-importa.com.uy`
   - User: `growimpo`
   - Password: Your cPanel password
   - Port: 21
3. Navigate to `/public_html/`
4. Upload all files from `deployment/cpanel/`

**Method C: SSH/SCP (Fastest)**

```bash
# If SSH is enabled on your hosting
scp -r deployment/cpanel/* growimpo@grow-importa.com.uy:~/public_html/
```

#### Step 4: Configure SSL (2 minutes)

1. In cPanel, go to "SSL/TLS Status"
2. Find your domain
3. Click "Install AutoSSL" (free Let's Encrypt)
4. Wait for installation

#### Step 5: Test (2 minutes)

1. Visit: https://grow-importa.com.uy
2. Test the chatbot
3. Verify API connection works

---

## 🔧 Environment Variables

### Required Variables

You need to set these in Railway (for both options):

```env
# OpenAI (REQUIRED)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Database (Auto-set by Railway MongoDB)
MONGODB_URI=${{MongoDB.MONGO_URL}}

# Server (REQUIRED)
PORT=8000
HOST=0.0.0.0
```

### Optional Variables (WhatsApp, Google Sheets)

```env
# WhatsApp Business API
WHATSAPP_VERIFY_TOKEN=your-verify-token
WHATSAPP_ACCESS_TOKEN=your-whatsapp-token

# Google Sheets Integration
GOOGLE_SHEETS_CREDENTIALS={"type":"service_account",...}
GOOGLE_SHEET_ID=your-sheet-id
```

---

## ✅ Verification Checklist

After deployment, verify:

### Backend (Railway)
- [ ] Deployment shows "Running" status
- [ ] Health check passes: `curl https://your-app.railway.app/health`
- [ ] API docs accessible: `https://your-app.railway.app/docs`
- [ ] MongoDB connected (check logs)
- [ ] Environment variables set correctly

### Frontend
- [ ] Site loads without errors
- [ ] Chat interface works
- [ ] Can submit quote form
- [ ] API connection successful (check browser console)
- [ ] SSL certificate valid (https://)

### Integration
- [ ] Chat sends messages to backend
- [ ] Quotes are created successfully
- [ ] Responses are displayed correctly
- [ ] No CORS errors in console

---

## 🐛 Common Issues & Quick Fixes

### Issue: "Build failed" on Railway

**Fix:**
```bash
# Test locally first
pip install -r requirements.txt
python sistema_completo_integrado.py
```

If works locally, check:
- Python version in Railway (should be 3.9+)
- All dependencies in requirements.txt

### Issue: Frontend can't connect to API

**Fix:**
1. Check API URL is correct in Vercel environment variables
2. Verify CORS settings in `sistema_completo_integrado.py`
3. Test API directly: `curl https://your-app.railway.app/health`

### Issue: "MongoDB connection failed"

**Fix:**
1. Verify MongoDB addon is added in Railway
2. Check `MONGODB_URI` is set to `${{MongoDB.MONGO_URL}}`
3. Restart the deployment

### Issue: cPanel upload - files not showing

**Fix:**
1. Verify you uploaded to `public_html/` (not subdirectory)
2. Check file permissions (644 for files, 755 for dirs)
3. Check `.htaccess` file is present

---

## 📱 WhatsApp Integration (Optional)

After deployment, to enable WhatsApp:

### 1. Configure Webhook in Meta Business Suite

1. Go to https://developers.facebook.com
2. Select your app → WhatsApp → Configuration
3. Set webhook:
   - **URL:** `https://your-app.railway.app/api/whatsapp/webhook`
   - **Verify Token:** (create one, add to Railway env vars)

### 2. Test Webhook

```bash
# Test verification
curl "https://your-app.railway.app/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=123"

# Should return: 123
```

### 3. Send Test Message

Send a WhatsApp message to your business number and check Railway logs.

---

## 💰 Cost Breakdown

### Option 1: Full Cloud

| Service | Free Tier | Typical Usage | Cost |
|---------|-----------|---------------|------|
| Railway | $5 credit/mo | ~$0-3/mo | **$0** |
| Vercel | 100GB bandwidth | ~5GB/mo | **$0** |
| MongoDB | 512MB storage | ~50MB | **$0** |
| **Total** | | | **$0/month** |

### Option 2: cPanel Hybrid

| Service | Free Tier | Typical Usage | Cost |
|---------|-----------|---------------|------|
| Railway | $5 credit/mo | ~$0-3/mo | **$0** |
| cPanel | Paid hosting | N/A | **~$5-10/mo** |
| **Total** | | | **$5-10/month** |

*Note: Most usage stays within free tiers for small-medium traffic*

---

## 🚀 What's Next?

After successful deployment:

1. **Test thoroughly** - Try all features
2. **Configure domain** - Add custom domain (optional)
3. **Set up monitoring** - Enable alerts
4. **Document access** - Save URLs and credentials
5. **Share with team** - Provide access to dashboard

---

## 📚 Additional Resources

- **Complete Guide:** [COMPLETE_HOSTING_GUIDE.md](COMPLETE_HOSTING_GUIDE.md)
- **Railway Details:** [RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md)
- **cPanel Details:** [CPANEL_HOSTING_GUIDE.md](CPANEL_HOSTING_GUIDE.md)

---

## 🆘 Need Help?

### Quick Troubleshooting

1. **Check logs:**
   - Railway: Dashboard → Logs
   - Vercel: Dashboard → Deployments → Function Logs

2. **Test locally:**
   ```bash
   python sistema_completo_integrado.py
   # Visit: http://localhost:8000/docs
   ```

3. **Verify environment variables:**
   - Railway: Dashboard → Variables
   - Vercel: Dashboard → Settings → Environment Variables

4. **Review guides:**
   - Read the relevant deployment guide
   - Check troubleshooting sections

---

## 🎯 Summary: Pick Your Option

### Choose Option 1 if you want:
- ✅ Fastest deployment (15 min)
- ✅ Best performance
- ✅ Automatic updates
- ✅ No server management
- ✅ Professional hosting for free

### Choose Option 2 if you want:
- ✅ Use your existing cPanel
- ✅ Keep your domain
- ✅ More control over frontend
- ✅ Traditional hosting approach

---

**🎬 Ready to start? Run this command:**

```bash
./deploy-chatbot.sh all
```

**This will launch an interactive wizard to guide you through deployment!**

---

**Questions? Check the [Complete Hosting Guide](COMPLETE_HOSTING_GUIDE.md) for detailed information.**

# 🌐 Hosting Your Chatbot on cPanel

## 📋 Overview

Your hosting details:
- **Domain:** grow-importa.com.uy
- **IP:** 179.27.153.55
- **User:** growimpo
- **Directory:** /homeX/growimpo
- **Available Space:** ~30 GB remaining

## ⚠️ Important Limitations of cPanel Shared Hosting

cPanel shared hosting has several limitations for this chatbot system:

1. **❌ No Docker Support** - Docker containers cannot run on shared hosting
2. **❌ Limited Python Support** - No long-running processes (FastAPI/Flask won't work continuously)
3. **❌ No Node.js Service** - Next.js development server cannot run 24/7
4. **❌ No MongoDB** - Cannot host MongoDB on shared hosting
5. **✅ Static Files** - Can host static HTML/JS files
6. **✅ PHP Support** - Full PHP support available

## 🎯 Best Deployment Strategy

### **Option A: Hybrid Deployment (RECOMMENDED)**

Use cPanel for static frontend + External services for backend

```
┌─────────────────────────────────────────────┐
│ Your cPanel (grow-importa.com.uy)           │
│ - Static Next.js build (HTML/CSS/JS)       │
│ - Contact forms                             │
│ - Landing page                              │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ External Services (FREE)                    │
│ - Railway/Render: Python API + MongoDB     │
│ - Vercel: Next.js (alternative)            │
│ - N8N Cloud: Workflow automation           │
└─────────────────────────────────────────────┘
```

### **Option B: Full External Hosting (EASIEST)**

Deploy everything on free cloud platforms (no cPanel needed)

### **Option C: cPanel with External API (PARTIAL)**

Use cPanel for landing page + webhook redirects to external API

---

## 📦 Option A: Hybrid Deployment (Detailed)

### Step 1: Deploy Backend Services (Free Cloud)

#### 1.1 Deploy Python API to Railway

**Why Railway?**
- ✅ Free tier ($5 credit monthly)
- ✅ Supports Python/FastAPI
- ✅ Includes MongoDB addon
- ✅ Easy deployment

**Deployment Steps:**

1. **Create Railway Account**
   ```bash
   # Visit: https://railway.app
   # Sign up with GitHub
   ```

2. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

3. **Deploy Python API**
   ```bash
   cd /workspace
   
   # Create railway project
   railway init
   
   # Add MongoDB plugin
   railway add mongodb
   
   # Deploy
   railway up
   ```

4. **Set Environment Variables** (in Railway dashboard)
   ```env
   OPENAI_API_KEY=your-openai-key
   OPENAI_MODEL=gpt-4o-mini
   MONGODB_URI=${{MONGODB.MONGODB_URI}}
   PORT=8000
   HOST=0.0.0.0
   ```

5. **Get Your API URL**
   - Railway will provide: `https://your-app.railway.app`
   - Save this URL for later!

#### 1.2 Alternative: Deploy to Render.com

**Render Deployment:**

1. Visit https://render.com and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn sistema_completo_integrado:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3
5. Add MongoDB (separate service or MongoDB Atlas)

### Step 2: Build Static Next.js for cPanel

#### 2.1 Configure Next.js for Static Export

Create/update `nextjs-app/next.config.ts`:

```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'export', // Enable static export
  trailingSlash: true,
  images: {
    unoptimized: true, // Required for static export
  },
  env: {
    NEXT_PUBLIC_API_URL: 'https://your-app.railway.app', // Your Railway URL
  },
};

export default nextConfig;
```

#### 2.2 Build Static Files

```bash
cd /workspace/nextjs-app
npm install
npm run build
```

This creates a `out/` directory with static files.

#### 2.3 Upload to cPanel

**Via cPanel File Manager:**

1. Log into cPanel at your hosting provider
2. Open **File Manager**
3. Navigate to `public_html/` directory
4. Create a subdirectory (optional): `public_html/chatbot/`
5. Upload all files from `nextjs-app/out/` directory
6. Set permissions: 644 for files, 755 for directories

**Via FTP (Recommended for large files):**

```bash
# Install FileZilla or use command line FTP
ftp grow-importa.com.uy

# Login with your credentials
user: growimpo
password: [your-cpanel-password]

# Navigate to public_html
cd public_html

# Upload files
mput nextjs-app/out/*
```

**Via SSH (if available):**

```bash
# Connect via SSH
ssh growimpo@grow-importa.com.uy

# Navigate to web directory
cd public_html

# Upload using scp from your local machine
scp -r nextjs-app/out/* growimpo@grow-importa.com.uy:~/public_html/chatbot/
```

#### 2.4 Configure Domain/Subdomain

**Option 1: Main Domain**
- Upload to `public_html/` → https://grow-importa.com.uy

**Option 2: Subdomain**
1. In cPanel, go to **Subdomains**
2. Create: `chat.grow-importa.com.uy`
3. Point to `public_html/chatbot/`

### Step 3: Set Up WhatsApp Webhooks

Your WhatsApp webhook URL will be:
```
https://your-app.railway.app/api/whatsapp/webhook
```

Configure in Meta Business Suite:
1. Go to https://developers.facebook.com
2. Select your app → WhatsApp → Configuration
3. Set webhook URL: `https://your-app.railway.app/api/whatsapp/webhook`
4. Set verify token (same as in your env vars)

---

## 📦 Option B: Full External Hosting (No cPanel)

### Deploy Everything to Vercel + Railway

**Advantages:**
- ✅ Completely free (within limits)
- ✅ Automatic deployments
- ✅ Better performance
- ✅ No cPanel restrictions

**Deployment:**

1. **Deploy Next.js to Vercel**
   ```bash
   cd /workspace
   npx vercel --prod
   ```

2. **Deploy Python API to Railway** (same as Option A Step 1.1)

3. **Configure Environment Variables** in Vercel:
   - Go to Vercel dashboard → Settings → Environment Variables
   - Add:
     ```
     NEXT_PUBLIC_API_URL=https://your-app.railway.app
     ```

---

## 📦 Option C: cPanel Landing Page + API Redirect

Use your cPanel hosting only for a landing page and redirect API calls.

### Step 1: Create Landing Page on cPanel

Create `public_html/index.html`:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BMC Uruguay - Chatbot de Cotizaciones</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        
        .logo {
            font-size: 60px;
            margin-bottom: 20px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 32px;
        }
        
        p {
            color: #666;
            margin-bottom: 30px;
            font-size: 18px;
        }
        
        .features {
            text-align: left;
            margin: 30px 0;
        }
        
        .feature {
            display: flex;
            align-items: center;
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .feature-icon {
            font-size: 30px;
            margin-right: 15px;
        }
        
        .feature-text {
            text-align: left;
        }
        
        .feature-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .feature-desc {
            color: #666;
            font-size: 14px;
        }
        
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 18px 40px;
            border-radius: 50px;
            text-decoration: none;
            font-size: 18px;
            font-weight: bold;
            margin: 10px;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .whatsapp-button {
            background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        }
        
        .whatsapp-button:hover {
            box-shadow: 0 10px 30px rgba(37, 211, 102, 0.4);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🤖</div>
        <h1>BMC Uruguay</h1>
        <p>Sistema Inteligente de Cotizaciones</p>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">⚡</div>
                <div class="feature-text">
                    <div class="feature-title">Cotizaciones Instantáneas</div>
                    <div class="feature-desc">Recibe tu cotización en segundos</div>
                </div>
            </div>
            
            <div class="feature">
                <div class="feature-icon">💬</div>
                <div class="feature-text">
                    <div class="feature-title">Chat Inteligente</div>
                    <div class="feature-desc">Asistente con IA disponible 24/7</div>
                </div>
            </div>
            
            <div class="feature">
                <div class="feature-icon">📊</div>
                <div class="feature-text">
                    <div class="feature-title">Productos Isodec</div>
                    <div class="feature-desc">Cotiza paneles aislantes térmicos</div>
                </div>
            </div>
        </div>
        
        <a href="https://wa.me/59899123456?text=Hola%20quiero%20cotizar" class="cta-button whatsapp-button">
            📱 Cotizar por WhatsApp
        </a>
        
        <a href="https://your-app.railway.app" class="cta-button">
            💻 Abrir Sistema Web
        </a>
    </div>
</body>
</html>
```

### Step 2: Upload to cPanel

1. Log into cPanel File Manager
2. Navigate to `public_html/`
3. Upload `index.html`
4. Access: https://grow-importa.com.uy

---

## 🔧 Complete Setup Script for Option A

Save this as `deploy-to-cpanel.sh`:

```bash
#!/bin/bash

echo "🚀 BMC Chatbot - Deployment to cPanel + Railway"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Build Next.js
echo -e "${BLUE}Step 1: Building Next.js application...${NC}"
cd nextjs-app

# Check if next.config.ts has static export
if ! grep -q "output: 'export'" next.config.ts; then
    echo -e "${RED}⚠️  Warning: next.config.ts not configured for static export${NC}"
    echo "Please add output: 'export' to next.config.ts"
    exit 1
fi

npm install
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Next.js build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

cd ..

# Step 2: Prepare files for upload
echo -e "${BLUE}Step 2: Preparing files for upload...${NC}"

# Create deployment directory
mkdir -p deployment/cpanel

# Copy static files
cp -r nextjs-app/out/* deployment/cpanel/

echo -e "${GREEN}✓ Files prepared in deployment/cpanel/${NC}"

# Step 3: Instructions for Railway
echo ""
echo -e "${BLUE}Step 3: Deploy Python API to Railway${NC}"
echo "1. Visit: https://railway.app"
echo "2. Create new project"
echo "3. Add MongoDB plugin"
echo "4. Run: railway up"
echo "5. Copy your Railway URL"
echo ""

# Step 4: Upload instructions
echo -e "${BLUE}Step 4: Upload to cPanel${NC}"
echo "Option A - File Manager:"
echo "  1. Log into cPanel"
echo "  2. Open File Manager"
echo "  3. Navigate to public_html/"
echo "  4. Upload files from deployment/cpanel/"
echo ""
echo "Option B - FTP:"
echo "  Host: grow-importa.com.uy"
echo "  User: growimpo"
echo "  Directory: /public_html/"
echo ""
echo "Option C - SCP (if SSH enabled):"
echo "  scp -r deployment/cpanel/* growimpo@grow-importa.com.uy:~/public_html/"
echo ""

echo -e "${GREEN}✓ Deployment preparation complete!${NC}"
echo ""
echo "📁 Static files ready in: deployment/cpanel/"
echo "🌐 After upload, access: https://grow-importa.com.uy"
```

Make it executable:
```bash
chmod +x deploy-to-cpanel.sh
./deploy-to-cpanel.sh
```

---

## 📊 Cost Comparison

| Service | Option A (Hybrid) | Option B (Full Cloud) | Option C (Landing) |
|---------|-------------------|------------------------|-------------------|
| **Frontend** | cPanel (Paid) | Vercel (Free) | cPanel (Paid) |
| **API** | Railway (Free $5/mo) | Railway (Free $5/mo) | Railway (Free $5/mo) |
| **Database** | Railway MongoDB (Free) | Railway MongoDB (Free) | Railway MongoDB (Free) |
| **N8N** | N8N Cloud (Free) | N8N Cloud (Free) | N8N Cloud (Free) |
| **Total** | ~$0-10/mo | $0 | ~$0-10/mo |

---

## 🎯 Recommended Choice

### **For Production: Option B (Full Cloud)**
- ✅ Best performance
- ✅ Easiest deployment
- ✅ Automatic scaling
- ✅ SSL included
- ✅ CI/CD integration

### **To Use Your cPanel: Option A (Hybrid)**
- ✅ Utilize existing hosting
- ✅ Keep static frontend on your domain
- ✅ Backend on reliable infrastructure

### **For Testing: Option C (Landing Page)**
- ✅ Quick setup
- ✅ Minimal configuration
- ✅ Easy to maintain

---

## 🚀 Quick Start Command

I'll create an automated deployment script for you. Which option do you prefer?

1. **Option A** - Hybrid (cPanel + Railway)
2. **Option B** - Full Cloud (Vercel + Railway)
3. **Option C** - Landing Page only

Let me know, and I'll create the complete setup!

---

## 📞 Support

If you encounter issues:
1. Check Railway/Vercel logs
2. Verify environment variables
3. Test API endpoints
4. Check cPanel error logs (if using)

---

## 🔐 Security Notes

1. **Never commit API keys** to Git
2. **Use environment variables** for all secrets
3. **Enable SSL** on cPanel (free via Let's Encrypt)
4. **Set proper CORS** headers on API
5. **Validate webhook signatures** from WhatsApp

---

## ✅ Checklist Before Deployment

- [ ] OpenAI API key obtained
- [ ] Railway account created
- [ ] MongoDB configured
- [ ] WhatsApp Business API set up
- [ ] cPanel credentials ready
- [ ] Domain DNS configured
- [ ] SSL certificate installed
- [ ] Environment variables set
- [ ] Build tested locally
- [ ] Backup existing cPanel files

---

**Ready to deploy? I can execute the deployment for you! Just tell me which option you prefer.**

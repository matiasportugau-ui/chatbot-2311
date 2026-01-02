# 🚂 Railway.app Deployment Guide

## Complete Guide to Deploy Your Chatbot on Railway

Railway.app is perfect for hosting your Python chatbot API with these advantages:
- ✅ **Free $5 credit monthly** (enough for small projects)
- ✅ **Automatic deployments** from GitHub
- ✅ **Built-in MongoDB** addon
- ✅ **Environment variables** management
- ✅ **SSL certificates** included
- ✅ **Easy scaling**

---

## 🚀 Quick Deployment (5 minutes)

### Prerequisites
- GitHub account
- Railway account (free)
- Your chatbot code pushed to GitHub

### Step 1: Create Railway Account

1. Visit: https://railway.app
2. Click **"Start a New Project"**
3. Sign up with GitHub
4. Authorize Railway to access your repositories

### Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `bmc-cotizacion-inteligente`
4. Railway will detect Python and start building

### Step 3: Add MongoDB Database

1. Click **"New"** → **"Database"** → **"Add MongoDB"**
2. Railway creates MongoDB instance automatically
3. Connection string is available as `${{MongoDB.MONGO_URL}}`

### Step 4: Configure Environment Variables

In Railway dashboard → Variables tab:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# MongoDB Connection
MONGODB_URI=${{MongoDB.MONGO_URL}}

# Server Configuration
PORT=8000
HOST=0.0.0.0

# WhatsApp Configuration (if using)
WHATSAPP_VERIFY_TOKEN=your-verify-token
WHATSAPP_ACCESS_TOKEN=your-whatsapp-token

# Google Sheets (if using)
GOOGLE_SHEETS_CREDENTIALS=your-credentials-json
GOOGLE_SHEET_ID=your-sheet-id
```

### Step 5: Create Railway Configuration

Create `railway.json` in your project root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "uvicorn sistema_completo_integrado:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Step 6: Create Procfile (Alternative)

Or create a `Procfile`:

```
web: uvicorn sistema_completo_integrado:app --host 0.0.0.0 --port $PORT
```

### Step 7: Deploy!

1. Push changes to GitHub:
   ```bash
   git add railway.json
   git commit -m "Add Railway configuration"
   git push
   ```

2. Railway auto-deploys on push
3. Get your URL: `https://your-app.railway.app`

---

## 🔧 Detailed Setup

### Create FastAPI Entry Point

Create `sistema_completo_integrado.py` if not exists:

```python
#!/usr/bin/env python3
"""
FastAPI application for BMC Quote System
Deploys on Railway.app
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BMC Quote System API",
    description="Intelligent quotation system for BMC Uruguay",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class QuoteRequest(BaseModel):
    customer_name: str
    phone: str
    product: str
    thickness: str
    length: float
    width: float
    
class ChatMessage(BaseModel):
    message: str
    session_id: str = None

# Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "BMC Quote System",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """
    Chat endpoint for conversational quotes
    """
    try:
        # Import here to avoid circular imports
        from ia_conversacional_integrada import procesar_mensaje_usuario
        
        response = procesar_mensaje_usuario(
            message.message, 
            message.session_id
        )
        
        return {
            "response": response,
            "session_id": message.session_id
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/quotes")
async def create_quote(quote: QuoteRequest):
    """
    Create a new quote
    """
    try:
        # Import your quote system
        from sistema_cotizaciones import SistemaCotizacionesBMC, Cliente, EspecificacionCotizacion
        from decimal import Decimal
        
        sistema = SistemaCotizacionesBMC()
        
        cliente = Cliente(
            nombre=quote.customer_name,
            telefono=quote.phone
        )
        
        especificaciones = EspecificacionCotizacion(
            producto=quote.product,
            espesor=quote.thickness,
            largo_metros=Decimal(str(quote.length)),
            ancho_metros=Decimal(str(quote.width))
        )
        
        cotizacion = sistema.crear_cotizacion(cliente, especificaciones)
        
        return {
            "quote_id": cotizacion.id,
            "total": float(cotizacion.precio_total),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error creating quote: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """
    WhatsApp webhook endpoint
    """
    try:
        data = await request.json()
        logger.info(f"WhatsApp webhook received: {data}")
        
        # Process WhatsApp message
        # Add your WhatsApp processing logic here
        
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error in WhatsApp webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/whatsapp/webhook")
async def whatsapp_verify(request: Request):
    """
    WhatsApp webhook verification
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
    
    if mode == "subscribe" and token == verify_token:
        logger.info("WhatsApp webhook verified")
        return int(challenge)
    else:
        raise HTTPException(status_code=403, detail="Verification failed")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### Update requirements.txt

Ensure all dependencies are listed:

```txt
# Core dependencies
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
python-dotenv>=1.0.0

# Database
pymongo>=4.5.0

# AI
openai>=1.0.0

# Utilities
requests>=2.25.1
python-multipart>=0.0.6
```

---

## 🔄 Automatic Deployments

Railway automatically deploys when you push to GitHub:

1. Make changes locally
2. Commit and push:
   ```bash
   git add .
   git commit -m "Update chatbot"
   git push
   ```
3. Railway detects push and redeploys
4. Check logs in Railway dashboard

---

## 📊 Monitor Your Deployment

### View Logs

In Railway dashboard:
1. Select your project
2. Click on **"View Logs"**
3. Monitor real-time logs

### Check Metrics

Railway provides:
- CPU usage
- Memory usage
- Network traffic
- Request count

### Set Up Alerts

1. Go to **Settings** → **Notifications**
2. Add email or Discord webhook
3. Get notified on deployment failures

---

## 🧪 Test Your Deployment

### Test API Health

```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy"
}
```

### Test Chat Endpoint

```bash
curl -X POST https://your-app.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola, quiero cotizar Isodec",
    "session_id": "test123"
  }'
```

### Test Quote Creation

```bash
curl -X POST https://your-app.railway.app/api/quotes \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Juan Perez",
    "phone": "099123456",
    "product": "isodec",
    "thickness": "100mm",
    "length": 10,
    "width": 5
  }'
```

---

## 🔐 Security Best Practices

### 1. Environment Variables

Never commit secrets to Git:
- Add `.env` to `.gitignore`
- Use Railway's environment variables
- Rotate API keys regularly

### 2. CORS Configuration

Update CORS for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://grow-importa.com.uy",
        "https://your-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting

Add rate limiting:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat(request: Request, message: ChatMessage):
    # ... existing code
```

---

## 💰 Cost Management

### Free Tier Limits

Railway free tier includes:
- **$5 credit per month**
- ~500 hours of usage
- Enough for small projects

### Optimize Costs

1. **Use sleep mode:** Railway sleeps inactive apps
2. **Optimize queries:** Efficient database queries
3. **Cache responses:** Reduce API calls
4. **Monitor usage:** Check Railway metrics

### Upgrade Options

If you exceed free tier:
- **Hobby Plan:** $5/month
- **Pro Plan:** $20/month
- **Pay as you go:** Usage-based

---

## 🐛 Troubleshooting

### Build Fails

**Issue:** Build fails with dependency errors

**Solution:**
```bash
# Test locally first
pip install -r requirements.txt
python sistema_completo_integrado.py

# Check Python version
python --version  # Should be 3.9+
```

### App Crashes on Start

**Issue:** App starts but crashes immediately

**Solution:**
- Check logs in Railway dashboard
- Verify environment variables are set
- Ensure PORT is read from environment:
  ```python
  port = int(os.getenv("PORT", 8000))
  ```

### Database Connection Fails

**Issue:** Cannot connect to MongoDB

**Solution:**
- Verify `MONGODB_URI` is set to `${{MongoDB.MONGO_URL}}`
- Check MongoDB service is running
- Test connection:
  ```python
  from pymongo import MongoClient
  client = MongoClient(os.getenv("MONGODB_URI"))
  print(client.list_database_names())
  ```

### WhatsApp Webhook Not Working

**Issue:** WhatsApp messages not received

**Solution:**
- Verify webhook URL in Meta Business Suite
- Check `WHATSAPP_VERIFY_TOKEN` matches
- Test webhook:
  ```bash
  curl "https://your-app.railway.app/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=123"
  ```

---

## 🔄 Custom Domain (Optional)

### Add Your Domain

1. In Railway dashboard, go to **Settings**
2. Click **Domains**
3. Click **Add Domain**
4. Enter: `api.grow-importa.com.uy`
5. Add CNAME record to your DNS:
   ```
   Type: CNAME
   Name: api
   Value: [railway-provided-value]
   ```

### Update CORS

After adding custom domain:

```python
allow_origins=[
    "https://grow-importa.com.uy",
    "https://api.grow-importa.com.uy"
]
```

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [MongoDB Atlas (alternative)](https://www.mongodb.com/atlas)

---

## ✅ Deployment Checklist

- [ ] Railway account created
- [ ] GitHub repository connected
- [ ] MongoDB addon added
- [ ] Environment variables configured
- [ ] `sistema_completo_integrado.py` created
- [ ] `railway.json` or `Procfile` added
- [ ] Code pushed to GitHub
- [ ] Deployment successful
- [ ] API health check passes
- [ ] Chat endpoint tested
- [ ] WhatsApp webhook configured (if using)
- [ ] Monitoring set up

---

**Your Railway deployment URL will be:**
```
https://your-project-name.railway.app
```

**Use this URL in your Next.js frontend and WhatsApp webhook configuration!**

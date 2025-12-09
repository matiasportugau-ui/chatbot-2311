# 🔐 Complete .env Credentials Guide

This document provides a comprehensive overview of all environment variables needed for the BMC Chatbot system.

---

## 📋 Quick Setup

```bash
# 1. Copy the example file
cp .env.example .env

# 2. Edit with your actual credentials
nano .env
```

---

## 🔑 Required Credentials

### 1. OpenAI API Configuration

**REQUIRED for chatbot functionality**

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
```

**How to get:**
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new API key
3. Copy and paste into `.env`

**Models available:**
- `gpt-4o-mini` - Recommended (cost-effective)
- `gpt-4o` - More powerful
- `gpt-3.5-turbo` - Budget option

---

### 2. MongoDB Database

**REQUIRED for data persistence**

```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/bmc_chat
```

**Options:**

#### Option A: MongoDB Atlas (Recommended for production)
1. Visit [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create free cluster
3. Get connection string from "Connect" button
4. Format: `mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>`

#### Option B: Railway MongoDB
```bash
MONGODB_URI=${{MongoDB.MONGO_URL}}
```

#### Option C: Local Development
```bash
MONGODB_URI=mongodb://localhost:27017/bmc_chat
```

---

## 🌐 Server Configuration

### Basic Server Settings

```bash
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=production
```

**Environments:**
- `development` - Local testing with debug enabled
- `staging` - Pre-production testing
- `production` - Live deployment

---

### Frontend API URL

```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

**Deployment-specific values:**
- **Railway:** `https://<your-service>.railway.app`
- **Render:** `https://<your-service>.onrender.com`
- **Vercel:** `https://<your-project>.vercel.app`
- **Cloud Run:** `https://<service>-<hash>-<region>.run.app`
- **Local:** `http://localhost:8000`

---

## 📱 Optional Integrations

### 3. WhatsApp Business API

**For WhatsApp bot integration**

```bash
WHATSAPP_VERIFY_TOKEN=your-custom-verify-token-123
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
```

**How to get:**
1. Visit [Meta Business Suite](https://developers.facebook.com)
2. Create app > Add WhatsApp product
3. Get Phone Number ID from Dashboard
4. Generate Access Token
5. Create custom Verify Token (any secure string)

**Setup webhook:**
- Callback URL: `https://your-api.com/webhook/whatsapp`
- Verify Token: (your custom token above)

---

### 4. Google Sheets Integration

**For CRM/lead management**

```bash
GOOGLE_SHEETS_CREDENTIALS={"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...@....iam.gserviceaccount.com","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}

GOOGLE_SHEET_ID=1AbC123XyZ_your-sheet-id-here
```

**How to get:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project
3. Enable Google Sheets API
4. Create Service Account
5. Generate JSON key
6. Copy entire JSON as single line to `.env`
7. Share your Google Sheet with service account email

**Get Sheet ID:**
- From URL: `https://docs.google.com/spreadsheets/d/`**`<SHEET_ID>`**`/edit`

---

## 🔒 Security Settings

### CORS Configuration

```bash
ALLOWED_ORIGINS=https://grow-importa.com.uy,https://your-app.vercel.app,https://your-frontend.com
```

**Format:** Comma-separated list (no spaces)

---

### Admin Protection

```bash
ADMIN_PASSWORD=your-super-secure-password-here-123!
```

**Use for:** Protected admin endpoints, system management

**Best practices:**
- Minimum 16 characters
- Mix of letters, numbers, symbols
- Use password manager

---

## 📊 Optional Services

### Error Tracking (Sentry)

```bash
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
```

**How to get:**
1. Create account at [sentry.io](https://sentry.io)
2. Create project
3. Copy DSN from project settings

---

### Payment Processing (Stripe)

```bash
STRIPE_SECRET_KEY=sk_test_PLACEHOLDER_KEY
STRIPE_PUBLISHABLE_KEY=pk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**How to get:**
1. Create account at [stripe.com](https://stripe.com)
2. Get keys from Dashboard > Developers > API keys
3. Use `sk_test_` for testing, `sk_live_` for production

---

## 🛠️ Development Settings

### Debug Mode

```bash
DEBUG=false
RELOAD=false
```

**Settings:**
- `DEBUG=true` - Show detailed error messages (development only)
- `RELOAD=true` - Enable hot reload for code changes
- `DEBUG=false` - Production setting (hide sensitive errors)

---

## 📝 Complete .env Template

Here's a complete example with all variables:

```bash
# ============================================================================
# OpenAI (REQUIRED)
# ============================================================================
OPENAI_API_KEY=sk-proj-your-actual-key-here
OPENAI_MODEL=gpt-4o-mini

# ============================================================================
# Database (REQUIRED)
# ============================================================================
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/bmc_chat

# ============================================================================
# Server Configuration
# ============================================================================
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=production

# ============================================================================
# Frontend
# ============================================================================
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# ============================================================================
# WhatsApp (Optional)
# ============================================================================
WHATSAPP_VERIFY_TOKEN=my-secure-token-123
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345

# ============================================================================
# Google Sheets (Optional)
# ============================================================================
GOOGLE_SHEETS_CREDENTIALS={"type":"service_account"...}
GOOGLE_SHEET_ID=1AbC123XyZ-your-sheet-id

# ============================================================================
# Security
# ============================================================================
ALLOWED_ORIGINS=https://grow-importa.com.uy,https://app.vercel.app
ADMIN_PASSWORD=super-secure-password-123

# ============================================================================
# Optional Services
# ============================================================================
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx

# ============================================================================
# Development
# ============================================================================
DEBUG=false
RELOAD=false
```

---

## 🚀 Platform-Specific Configuration

### Railway Deployment

```bash
# Use Railway's internal services
MONGODB_URI=${{MongoDB.MONGO_URL}}
PORT=${{PORT}}
NEXT_PUBLIC_API_URL=https://${{RAILWAY_SERVICE_NAME}}.railway.app
```

### Vercel Deployment

```bash
# Add all variables in Vercel dashboard
# Settings > Environment Variables
# IMPORTANT: Prefix frontend vars with NEXT_PUBLIC_
```

### Cloud Run Deployment

```bash
# Use Secret Manager for sensitive data
# Set via gcloud:
gcloud secrets create openai-key --data-file=- <<< "sk-..."
```

---

## ✅ Validation Checklist

Use this checklist to verify your setup:

- [ ] **OpenAI API Key** - Tested and working
- [ ] **MongoDB URI** - Connection successful
- [ ] **PORT** - Set correctly (8000 default)
- [ ] **NEXT_PUBLIC_API_URL** - Points to deployed backend
- [ ] **CORS Origins** - Includes all frontend URLs
- [ ] **Admin Password** - Strong and secure
- [ ] WhatsApp tokens (if using)
- [ ] Google Sheets credentials (if using)
- [ ] Error tracking configured (optional)
- [ ] Payment gateway configured (optional)

---

## 🧪 Testing Your Configuration

Run the credential test script:

```bash
python test_credenciales_env.py
```

This will verify:
- ✅ All required variables are set
- ✅ OpenAI API key is valid
- ✅ MongoDB connection works
- ✅ Optional services are configured

---

## 🔐 Security Best Practices

1. **Never commit `.env` to git**
   - Already in `.gitignore`
   - Use `.env.example` for templates

2. **Use different values per environment**
   - Development: Test API keys
   - Staging: Separate credentials
   - Production: Live credentials

3. **Rotate credentials regularly**
   - Change admin passwords quarterly
   - Rotate API keys annually
   - Update tokens if compromised

4. **Use secret management tools**
   - Railway: Built-in secrets
   - Vercel: Environment variables
   - Cloud Run: Secret Manager
   - Local: `.env` file (never commit)

5. **Limit credential access**
   - Use read-only keys where possible
   - Restrict IP addresses
   - Enable 2FA on all accounts

---

## 🆘 Troubleshooting

### OpenAI API Errors

**Error:** `401 Unauthorized`
- **Fix:** Check API key is correct and active
- **Verify:** Has billing enabled on OpenAI account

**Error:** `429 Rate Limit`
- **Fix:** Upgrade OpenAI plan or reduce requests

---

### MongoDB Connection Issues

**Error:** `Connection timeout`
- **Fix:** Check network access in MongoDB Atlas
- **Verify:** Allow all IPs (0.0.0.0/0) or add specific IPs

**Error:** `Authentication failed`
- **Fix:** Verify username/password in connection string
- **Check:** User has correct database permissions

---

### CORS Errors

**Error:** `Access-Control-Allow-Origin`
- **Fix:** Add frontend URL to `ALLOWED_ORIGINS`
- **Format:** `https://example.com,https://app.com` (no spaces)

---

## 📞 Need Help?

1. Check deployment guides:
   - [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
   - [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md)
   - [AGENT_DEPLOYMENT_PLAN_TEAM_INSTRUCTIONS.md](./AGENT_DEPLOYMENT_PLAN_TEAM_INSTRUCTIONS.md)

2. Test credentials:
   ```bash
   python test_credenciales_env.py
   ```

3. Verify setup:
   ```bash
   python verify_setup.py
   ```

---

## 📚 Related Documentation

- [Setup Complete Guide](./SETUP_COMPLETE_GUIDE.md)
- [Setup Credentials Guide](./SETUP_CREDENTIALS_GUIDE.md)
- [How to Run](./HOW_TO_RUN.md)
- [Start Here Deployment](./START_HERE_DEPLOYMENT.md)

---

**Last Updated:** 2025-12-09  
**Version:** 2.0  
**Maintained by:** BMC Development Team

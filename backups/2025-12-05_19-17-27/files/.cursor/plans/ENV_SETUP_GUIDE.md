# Unified .env Setup Guide

Complete guide for creating and uploading your unified .env file with all keys and tokens.

## 🚀 Quick Start

### Option 1: Interactive Setup (Recommended)

```bash
# Step 1: Create .env file interactively
python setup_unified_env.py

# Step 2: Upload to GitHub Codespaces
python upload_secrets_to_github.py
```

### Option 2: Manual Setup

```bash
# Step 1: Create .env from template
cp env.example .env

# Step 2: Edit .env with your keys
nano .env  # or use your preferred editor

# Step 3: Upload to GitHub (automatic or manual)
python upload_secrets_to_github.py
```

## 📋 What's Included

The unified .env includes all required keys organized by category:

### AI Models (Required: OpenAI)
- `OPENAI_API_KEY` ⭐ **REQUIRED**
- `GROQ_API_KEY` (optional, free tier available)
- `GEMINI_API_KEY` (optional)
- `GROK_API_KEY` (optional)
- `OPENAI_ORGANIZATION_ID` (optional)
- `OPENAI_PROJECT_ID` (optional)

### Databases (Required: MongoDB)
- `MONGODB_URI` ⭐ **REQUIRED**
- `DATABASE_URL` (optional, PostgreSQL)

### WhatsApp (Optional)
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_VERIFY_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_BUSINESS_ID`
- `WHATSAPP_APP_SECRET`

### MercadoLibre (Optional)
- `MERCADO_LIBRE_APP_ID`
- `MERCADO_LIBRE_CLIENT_SECRET`
- `MELI_ACCESS_TOKEN`
- `MELI_REFRESH_TOKEN`
- `MELI_SELLER_ID`

### n8n (Optional)
- `N8N_BASIC_AUTH_PASSWORD`
- `N8N_API_KEY`

### Google (Optional)
- `GOOGLE_SHEETS_API_KEY`

### Other (Optional)
- `NEXTAUTH_SECRET`
- `SENTRY_DSN`

## 🔧 Detailed Instructions

### Step 1: Create .env File

**Interactive Mode (Recommended):**
```bash
python setup_unified_env.py
```

This will:
- ✅ Load existing .env values if present
- ✅ Prompt for each variable with descriptions
- ✅ Show where to get each key
- ✅ Create organized .env file
- ✅ Create backup of existing .env

**Non-Interactive Mode:**
```bash
python setup_unified_env.py --non-interactive
```

This creates .env from existing environment variables only.

### Step 2: Upload to GitHub

**Automatic Upload (Requires GitHub CLI):**
```bash
# Install GitHub CLI if not installed
# macOS: brew install gh
# Linux: See https://cli.github.com/

# Authenticate
gh auth login

# Upload secrets
python upload_secrets_to_github.py
```

**Manual Upload:**
```bash
# Show manual instructions
python upload_secrets_to_github.py --manual
```

Then follow the instructions to upload via GitHub web interface.

## 📤 Upload Methods

### Method 1: GitHub CLI (Automatic)

**Prerequisites:**
- GitHub CLI installed: `gh --version`
- Authenticated: `gh auth login`

**Steps:**
```bash
python upload_secrets_to_github.py
```

The script will:
- ✅ Read all secrets from .env
- ✅ Upload to GitHub Repository Secrets
- ✅ Show progress for each secret
- ✅ Verify upload success

### Method 2: GitHub Web Interface (Manual)

1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/codespaces`
2. Click "New repository secret"
3. For each secret:
   - Name: `OPENAI_API_KEY` (example)
   - Value: `sk-...` (from your .env)
   - Click "Add secret"

**Quick Reference:**
```bash
# See all secrets to upload
python upload_secrets_to_github.py --manual
```

### Method 3: GitHub CLI Manual

```bash
# For each secret
gh secret set OPENAI_API_KEY --repo YOUR_USERNAME/YOUR_REPO
# Enter value when prompted
```

## 🔐 Security Best Practices

1. ✅ **Never commit .env to Git** - Already in `.gitignore`
2. ✅ **Use GitHub Secrets** - Encrypted and secure
3. ✅ **Rotate keys regularly** - Every 90 days recommended
4. ✅ **Use strong passwords** - For NEXTAUTH_SECRET, etc.
5. ✅ **Limit access** - Only share with trusted team members

## 📝 Example Workflow

```bash
# 1. Create .env file
python setup_unified_env.py

# 2. Review created file
cat .env

# 3. Upload to GitHub
python upload_secrets_to_github.py

# 4. Verify in GitHub
# Go to: Settings → Secrets and variables → Codespaces

# 5. Use in Codespaces
# Secrets are automatically available in Codespaces!
```

## 🆘 Troubleshooting

### "GitHub CLI not found"
```bash
# Install GitHub CLI
# macOS
brew install gh

# Linux
# See: https://cli.github.com/manual/installation
```

### "Not authenticated"
```bash
gh auth login
# Follow the prompts
```

### "Repository not found"
- Check git remote: `git remote -v`
- Or provide manually when prompted

### "Secret upload failed"
- Check GitHub CLI authentication: `gh auth status`
- Verify repository access
- Try manual upload method

### ".env file not found"
```bash
# Create it first
python setup_unified_env.py
```

## 📚 Additional Resources

- **GitHub Secrets Docs**: https://docs.github.com/en/codespaces/managing-your-codespaces/managing-secrets-for-your-codespaces
- **GitHub CLI Docs**: https://cli.github.com/manual/
- **Security Guide**: `CODESPACES_SECURITY.md`

## ✅ Verification

After uploading, verify secrets are available:

1. **In GitHub:**
   - Go to: Settings → Secrets and variables → Codespaces
   - Should see all uploaded secrets

2. **In Codespaces:**
   ```bash
   # Secrets are automatically available as environment variables
   echo $OPENAI_API_KEY
   
   # Or load from .env
   bash .devcontainer/load-secrets.sh
   ```

---

**You're all set!** Your secrets are now securely stored and ready to use in Codespaces. 🚀


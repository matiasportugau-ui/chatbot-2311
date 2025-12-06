# Quick .env Setup - 2 Steps

## 🚀 Setup Your Unified .env File

### Step 1: Create .env File
```bash
python setup_unified_env.py
```

This interactive script will:
- ✅ Guide you through all required keys
- ✅ Show where to get each key
- ✅ Create organized .env file
- ✅ Load existing values if present

### Step 2: Upload to GitHub (Choose One)

**Option A: Automatic (Requires GitHub CLI)**
```bash
# Install GitHub CLI first: brew install gh
# Authenticate: gh auth login
secrets.json.
# Upload from .env file
python upload_secrets_to_github.py

# Or upload from .env.unified (if you have one)
python upload_secrets_to_github.py --env-file .env.unified
```

**Option B: Manual Upload**
```bash
# Get instructions
python upload_secrets_to_github.py --manual

# Or for .env.unified
python upload_secrets_to_github.py --env-file .env.unified --manual

# Then go to GitHub:
# Settings → Secrets and variables → Codespaces → New repository secret
```

**📤 Full Upload Guide**: See `GITHUB_SECRETS_UPLOAD.md` for detailed instructions.

## 📋 Required Keys (Minimum)

- `OPENAI_API_KEY` ⭐ **REQUIRED**
- `MONGODB_URI` ⭐ **REQUIRED**

All others are optional but recommended for full functionality.

## ✅ Done!

After uploading, secrets are automatically available in Codespaces!

---

**Full Guide**: See `ENV_SETUP_GUIDE.md` for detailed instructions.




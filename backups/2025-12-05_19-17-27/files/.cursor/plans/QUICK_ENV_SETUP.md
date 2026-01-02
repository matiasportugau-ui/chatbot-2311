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
python upload_secrets_to_github.py
```

**Option B: Manual Upload**
```bash
# Get instructions
python upload_secrets_to_github.py --manual

# Then go to GitHub:
# Settings → Secrets and variables → Codespaces → New repository secret
```

## 📋 Required Keys (Minimum)

- `OPENAI_API_KEY` ⭐ **REQUIRED**
- `MONGODB_URI` ⭐ **REQUIRED**

All others are optional but recommended for full functionality.

## ✅ Done!

After uploading, secrets are automatically available in Codespaces!

---

**Full Guide**: See `ENV_SETUP_GUIDE.md` for detailed instructions.


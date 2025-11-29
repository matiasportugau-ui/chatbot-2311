# Complete Setup Guide - BMC Chatbot System

## Overview

This guide provides step-by-step instructions to set up the BMC Chatbot System from scratch, ensuring all components are properly configured and validated.

## Quick Start

### One-Command Setup (Recommended)

```bash
# Windows
launch.bat

# Linux/Mac
./launch.sh

# Or directly
python unified_launcher.py
```

The unified launcher will:
- Check prerequisites
- Install dependencies
- Configure environment
- Validate setup
- Consolidate knowledge base
- Run integration tests

## Prerequisites

### Required
- **Python 3.11+** - Download from https://www.python.org/downloads/
- **Internet connection** - For downloading dependencies

### Optional
- **Node.js 18+** - For Next.js dashboard (download from https://nodejs.org/)
- **Docker** - For MongoDB (download from https://www.docker.com/)
- **Git** - For cloning repository

## Step-by-Step Setup

### Step 1: Clone/Download Repository

```bash
git clone <repository-url>
cd chatbot-2311
```

### Step 2: Run Unified Launcher

```bash
python unified_launcher.py
```

Or use the wrapper scripts:
- Windows: `launch.bat`
- Linux/Mac: `./launch.sh`

### Step 3: Interactive Setup Wizard (First Time)

If this is your first time, the launcher will guide you through setup. Alternatively, run the wizard manually:

```bash
python scripts/setup_environment_wizard.py
```

The wizard will:
- Guide you through required variables
- Help configure optional variables
- Validate inputs in real-time
- Create `.env` file automatically

### Step 4: Verify Setup

After setup, verify everything is configured correctly:

```bash
# Comprehensive verification
python verificar_sistema_completo.py

# Environment validation
python scripts/validate_environment.py

# Integration tests
python scripts/test_integration.py
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | `sk-...` |

### Optional Variables

#### API Configuration
- `PY_CHAT_SERVICE_URL` - Python API URL (default: `http://localhost:8000`)
- `NEXT_PUBLIC_API_URL` - Next.js API URL (default: `http://localhost:3001/api`)

#### Database
- `MONGODB_URI` - MongoDB connection string (default: `mongodb://localhost:27017/bmc_chat`)

#### WhatsApp Integration
- `WHATSAPP_ACCESS_TOKEN` - WhatsApp Business API access token
- `WHATSAPP_PHONE_NUMBER_ID` - WhatsApp phone number ID
- `WHATSAPP_VERIFY_TOKEN` - Webhook verification token
- `WHATSAPP_APP_SECRET` - App secret for signature verification

#### NextAuth.js
- `NEXTAUTH_URL` - Base URL (default: `http://localhost:3000`)
- `NEXTAUTH_SECRET` - Session encryption secret (auto-generated if missing)

#### MercadoLibre
- `MELI_ACCESS_TOKEN` - MercadoLibre API access token
- `MELI_SELLER_ID` - MercadoLibre seller ID

#### Google Sheets
- `GOOGLE_SHEETS_API_KEY` - Google Sheets API key

## Validation Tools

### Environment Validator

Comprehensive validation of all environment variables:

```bash
python scripts/validate_environment.py
```

**Features:**
- Validates required vs optional variables
- Tests API keys with actual requests
- Checks MongoDB connectivity
- Validates URL formats
- Provides clear error messages with fixes

**Options:**
```bash
# JSON output
python scripts/validate_environment.py --json

# Save report
python scripts/validate_environment.py --save-report
```

### WhatsApp Credential Validator

Validates WhatsApp Business API credentials:

```bash
python scripts/verify_whatsapp_credentials.py
```

**Features:**
- Tests access token with API calls
- Verifies phone number ID
- Checks webhook URL accessibility
- Tests signature verification

### Integration Test Suite

Comprehensive integration testing:

```bash
python scripts/test_integration.py
```

**Tests:**
- API server health
- Knowledge base loading
- MongoDB connectivity
- OpenAI API connectivity
- WhatsApp webhook (if configured)
- n8n workflow (if configured)
- Next.js frontend (if running)

**Options:**
```bash
# JSON output
python scripts/test_integration.py --json

# Save report
python scripts/test_integration.py --save-report
```

## Setup Recovery

If setup fails or you need to recover:

```bash
python scripts/recover_setup.py
```

**Features:**
- Detects partial setup states
- Offers to continue from last step
- Creates backups before fixes
- Auto-fixes common issues
- Restores from backup if needed

**Options:**
```bash
# Auto-fix critical issues
python scripts/recover_setup.py --auto-fix

# Restore from backup
python scripts/recover_setup.py --restore latest

# List available backups
python scripts/recover_setup.py --list-backups
```

## n8n Workflow Setup

### Automatic Import

If n8n is running, the unified launcher can import workflows automatically:

```bash
python unified_launcher.py
# When prompted, answer 'y' to import n8n workflows
```

### Manual Import

```bash
python scripts/import_n8n_workflow.py
```

**Options:**
```bash
# Import specific workflow
python scripts/import_n8n_workflow.py --workflow n8n_workflows/workflow-whatsapp.json

# Don't activate workflows
python scripts/import_n8n_workflow.py --no-activate

# Custom n8n URL
python scripts/import_n8n_workflow.py --n8n-url http://your-n8n-instance:5678
```

## Knowledge Base Setup

The unified launcher automatically consolidates knowledge files during setup. To manually consolidate:

```bash
python consolidar_conocimiento.py
```

This creates `conocimiento_consolidado.json` from all available knowledge files.

## Verification Checklist

After setup, verify:

- [ ] Python 3.11+ installed and in PATH
- [ ] All Python dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file exists and configured
- [ ] `OPENAI_API_KEY` is set and valid
- [ ] Knowledge base files exist (at least one)
- [ ] MongoDB is running (if using)
- [ ] API server can start (`python api_server.py`)
- [ ] Integration tests pass (`python scripts/test_integration.py`)

## Troubleshooting

### Common Issues

#### 1. Python Not Found

**Problem:** `python: command not found`

**Solution:**
- Install Python 3.11+ from https://www.python.org/downloads/
- During installation, check "Add Python to PATH"
- Or use `python3` instead of `python`

#### 2. Dependencies Installation Fails

**Problem:** `pip install` fails

**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then install requirements
python -m pip install -r requirements.txt
```

#### 3. Environment Variables Not Loading

**Problem:** Variables in `.env` not being read

**Solution:**
- Ensure `.env` file is in project root
- Check file format (KEY=VALUE, no spaces around =)
- Restart the application after changing `.env`

#### 4. OpenAI API Key Invalid

**Problem:** OpenAI API returns 401 error

**Solution:**
- Get a new API key from https://platform.openai.com/api-keys
- Update `OPENAI_API_KEY` in `.env`
- Run: `python scripts/validate_environment.py`

#### 5. MongoDB Connection Failed

**Problem:** Cannot connect to MongoDB

**Solution:**
```bash
# Start MongoDB with Docker
docker start bmc-mongodb

# Or check if MongoDB is running
docker ps | grep mongodb

# Or install MongoDB locally
```

#### 6. Port Already in Use

**Problem:** Port 8000 (or 3000) already in use

**Solution:**
```bash
# Find process using port
lsof -ti :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 $(lsof -ti :8000)  # Mac/Linux
```

#### 7. Knowledge Base Not Loading

**Problem:** No knowledge base files found

**Solution:**
```bash
# Consolidate knowledge files
python consolidar_conocimiento.py

# Or create a basic knowledge file
# The system will work without it, but with limited knowledge
```

### Getting Help

1. **Check Logs:**
   ```bash
   # Launcher logs
   cat logs/launcher.log
   
   # API server logs
   cat logs/api_server.log
   
   # Validation reports
   cat logs/environment_validation.json
   ```

2. **Run Diagnostics:**
   ```bash
   # System verification
   python verificar_sistema_completo.py
   
   # Environment validation
   python scripts/validate_environment.py
   
   # Integration tests
   python scripts/test_integration.py
   ```

3. **Recovery:**
   ```bash
   # Detect and fix issues
   python scripts/recover_setup.py --auto-fix
   ```

## Next Steps After Setup

1. **Start the System:**
   ```bash
   python unified_launcher.py --mode fullstack
   ```

2. **Test the Chatbot:**
   ```bash
   python unified_launcher.py --mode chat
   ```

3. **Run Simulator:**
   ```bash
   python unified_launcher.py --mode simulator
   ```

4. **Access Dashboard:**
   - Start Next.js: `python unified_launcher.py --mode dashboard`
   - Open: http://localhost:3000

## Advanced Configuration

### Custom API Port

```bash
python unified_launcher.py --port 9000 --mode api
```

### Production Mode

```bash
python unified_launcher.py --production --mode fullstack
```

### Development Mode

```bash
python unified_launcher.py --dev --mode api
```

### Skip Setup

If already configured:

```bash
python unified_launcher.py --skip-setup --mode chat
```

## Maintenance

### Update Knowledge Base

```bash
# Refresh knowledge from sources
bash scripts/refresh_knowledge.sh

# Or manually consolidate
python consolidar_conocimiento.py
```

### Update Dependencies

```bash
# Python
pip install --upgrade -r requirements.txt

# Node.js
npm update
```

### Backup Configuration

```bash
# Backup .env
cp .env .env.backup

# Backup knowledge
cp conocimiento_consolidado.json conocimiento_consolidado.json.backup
```

## Support

For issues or questions:

1. Check logs in `logs/` directory
2. Run validation: `python scripts/validate_environment.py`
3. Run recovery: `python scripts/recover_setup.py`
4. Review documentation in project root

## Summary

The setup process is now fully automated:

1. ✅ **Unified Launcher** - Single entry point for everything
2. ✅ **Environment Wizard** - Interactive setup guide
3. ✅ **Comprehensive Validation** - Validates all components
4. ✅ **Integration Testing** - Tests everything works together
5. ✅ **Recovery Tools** - Fixes common issues automatically
6. ✅ **Clear Documentation** - Step-by-step guides

**Result:** Setup time reduced from ~30 minutes to ~5 minutes with automated validation and testing.

---

**Last Updated:** Complete setup enhancement implementation
**Status:** ✅ All setup tools implemented and ready to use


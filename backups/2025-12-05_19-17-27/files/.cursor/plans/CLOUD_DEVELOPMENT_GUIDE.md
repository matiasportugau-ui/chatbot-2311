# Cloud Development Guide - GitHub Codespaces

Complete guide for developing the BMC Chatbot project in GitHub Codespaces, accessible from any device.

## 🚀 Quick Start

### Step 1: Create Codespace

1. Go to your GitHub repository: `https://github.com/matiasportugau-ui/chatbot-2311`
2. Click the green **"Code"** button
3. Select **"Codespaces"** tab
4. Click **"Create codespace on main"** (or your branch)
5. Wait 2-3 minutes for automatic setup

### Step 2: Access Your Environment

Once created, you'll see:
- **VS Code in browser** - Full IDE experience
- **Terminal** - Integrated terminal
- **Port forwarding** - Automatic URLs for your services

The setup script runs automatically and installs all dependencies.

### Step 3: Configure Secrets

**Option A: GitHub Repository Secrets (Recommended)**
1. Go to: Settings → Secrets and variables → Codespaces → New repository secret
2. Add your secrets:
   - `OPENAI_API_KEY`
   - `GROQ_API_KEY`
   - `GEMINI_API_KEY`
   - `MONGODB_URI`
   - `N8N_BASIC_AUTH_PASSWORD`
   - `WHATSAPP_ACCESS_TOKEN`
   - And others from `env.example`

**Option B: Manual Entry in Codespaces**
1. In Codespaces terminal, edit `.env`:
   ```bash
   nano .env
   ```
2. Add your API keys manually

### Step 4: Start Services

**Automated (Recommended):**
```bash
bash scripts/codespaces-start.sh
```

**Manual:**
```bash
# Start Docker services
docker-compose up -d

# Start Next.js (in one terminal)
npm run dev

# Start FastAPI (in another terminal)
source venv/bin/activate
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 Accessing Your Apps

After starting services, Codespaces will show you public URLs in the "Ports" tab:

- **Next.js Dashboard**: `https://xxxx-3000-xxxx.preview.app.github.dev`
- **FastAPI API**: `https://xxxx-8000-xxxx.preview.app.github.dev`
- **n8n Workflows**: `https://xxxx-5678-xxxx.preview.app.github.dev`

These URLs:
- ✅ Work from any browser (desktop, tablet, phone)
- ✅ Can be shared with your team
- ✅ Are HTTPS secure
- ✅ No VPN needed

## 👥 Sharing with Team

### Method 1: Repository Access (Best for Development)
1. Add team members as collaborators in GitHub
2. Each person creates their own Codespace
3. Everyone works independently
4. Changes sync via Git

**Steps:**
1. Repository → Settings → Collaborators
2. Add team members
3. They can create their own Codespaces

### Method 2: Share Public URLs (Best for Demos)
1. Make ports public in Codespaces (right-click port → "Change Port Visibility" → "Public")
2. Share the public URLs with your team
3. Team can access web apps without Codespace access

**Example:**
```
Share this URL with your team:
https://matiasportugau-ui-xxxx-3000.preview.app.github.dev
```

### Method 3: Share Codespace (Temporary)
1. Right-click on Codespace → "Share"
2. Generate shareable link
3. Team can access your running environment
4. ⚠️ Only one person should edit at a time

## 💰 Cost Information

### Free Tier
- **60 hours/month** (2-core, 4GB RAM)
- Perfect for development and testing
- Resets monthly

### Paid Tiers
- **2-core**: $0.18/hour
- **4-core**: $0.36/hour
- **8-core**: $0.72/hour
- **Storage**: 20GB included, $0.07/GB/month additional

### Cost Optimization Tips
1. **Stop Codespaces when not in use** - Saves hours
2. **Use smaller machines** - 2-core is usually enough for development
3. **Monitor usage** - Check hours used in Settings → Billing
4. **Auto-stop** - Codespaces auto-stop after 30 minutes of inactivity

## 🔧 Troubleshooting

### Ports Not Forwarding?
1. Check "Ports" tab in VS Code
2. Right-click port → "Change Port Visibility" → "Public"
3. Verify service is running: `bash scripts/codespaces-health.sh`

### Services Not Starting?
```bash
# Check Docker
docker-compose ps

# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Full restart
docker-compose down && docker-compose up -d
```

### Environment Variables Not Working?
```bash
# Verify .env exists
ls -la .env

# Check if variables are loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY')[:10] + '...' if os.getenv('OPENAI_API_KEY') else 'Not set')"

# Reload secrets
bash .devcontainer/load-secrets.sh
```

### Setup Script Failed?
```bash
# Run setup manually
bash .devcontainer/setup.sh

# Check logs
cat .devcontainer/setup.log
```

### Can't Access Services?
1. Verify services are running: `bash scripts/codespaces-health.sh`
2. Check port forwarding: `bash scripts/codespaces-ports.sh`
3. Verify firewall/network settings
4. Try accessing via public URL from Ports tab

## 📱 Access from Any Device

You can access Codespaces from:
- ✅ Desktop computers (Windows, Mac, Linux)
- ✅ Tablets (iPad, Android)
- ✅ Phones (iPhone, Android)
- ✅ Any device with a modern browser

Just open: `https://github.com/codespaces`

## 🎯 Daily Workflow

### Starting Work
1. **Resume Codespace**: Go to GitHub → Codespaces → Click "Resume"
2. **Pull latest changes**: `git pull origin main` (or your branch)
3. **Start services**: `bash scripts/codespaces-start.sh`
4. **Check health**: `bash scripts/codespaces-health.sh`

### During Work
- Edit code in VS Code
- Test in browser using public URLs
- Commit changes: `git add . && git commit -m "..." && git push`

### Ending Work
1. **Commit and push** your changes
2. **Stop Codespace** (optional, saves money):
   - Click Codespace name → "Stop"
   - Or let it auto-stop after 30 minutes

## 🔐 Security Best Practices

1. ✅ **Use GitHub Secrets** for API keys (not .env in repo)
2. ✅ **Don't commit `.env` files** - Already in `.gitignore`
3. ✅ **Use private repositories** for sensitive projects
4. ✅ **Review port visibility** - Make public only if needed
5. ✅ **Stop Codespaces when not in use** - Reduces attack surface
6. ✅ **Regularly rotate secrets** - Update API keys periodically
7. ✅ **Use branch protection** - Prevent accidental commits

## 📚 Additional Resources

- [GitHub Codespaces Docs](https://docs.github.com/en/codespaces)
- [VS Code in Browser](https://code.visualstudio.com/docs/remote/codespaces)
- [Port Forwarding Guide](https://docs.github.com/en/codespaces/developing-in-codespaces/forwarding-ports-in-your-codespace)
- [Codespaces Pricing](https://github.com/features/codespaces/pricing)

## 🆘 Getting Help

1. Check this guide first
2. Review `CODESPACES_QUICK_START.md` for quick reference
3. Check service health: `bash scripts/codespaces-health.sh`
4. Review logs: `cat .devcontainer/setup.log`
5. GitHub Support: [GitHub Support](https://support.github.com)

---

**Last Updated**: December 2025  
**Project**: BMC Chatbot System  
**Repository**: `https://github.com/matiasportugau-ui/chatbot-2311`


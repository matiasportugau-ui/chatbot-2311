# Codespaces Quick Start - 5 Minute Guide

Get your BMC Chatbot running in GitHub Codespaces in 5 minutes.

## ⚡ Quick Setup

### 1. Create Codespace (2 minutes)
```
GitHub → Your Repo → Code → Codespaces → Create codespace
```

### 2. Wait for Setup (2 minutes)
Setup runs automatically. Watch the terminal for progress.

### 3. Configure Secrets (1 minute)
```bash
# Option A: GitHub Secrets (recommended)
Settings → Secrets → Codespaces → Add secrets

# Option B: Manual
nano .env  # Edit with your API keys
```

### 4. Start Services
```bash
bash scripts/codespaces-start.sh
```

## 🌐 Access Your Apps

Check the **"Ports"** tab in VS Code for public URLs:
- Next.js: `https://xxxx-3000-xxxx.preview.app.github.dev`
- FastAPI: `https://xxxx-8000-xxxx.preview.app.github.dev`
- n8n: `https://xxxx-5678-xxxx.preview.app.github.dev`

## 📋 Essential Commands

```bash
# Start everything
bash scripts/codespaces-start.sh

# Check health
bash scripts/codespaces-health.sh

# View ports
bash scripts/codespaces-ports.sh

# View logs
docker-compose logs -f
tail -f /tmp/nextjs.log
tail -f /tmp/fastapi.log
```

## 🔑 Required Secrets

Add these in GitHub → Settings → Secrets → Codespaces:
- `OPENAI_API_KEY`
- `GROQ_API_KEY` (optional)
- `GEMINI_API_KEY` (optional)
- `MONGODB_URI` (if using external MongoDB)

## 🆘 Quick Troubleshooting

**Services not starting?**
```bash
docker-compose restart
bash scripts/codespaces-health.sh
```

**Ports not accessible?**
- Check "Ports" tab
- Right-click port → "Change Port Visibility" → "Public"

**Secrets not loading?**
```bash
bash .devcontainer/load-secrets.sh
```

## 💡 Pro Tips

1. **Stop Codespace when done** - Saves money (free tier: 60 hours/month)
2. **Use public URLs** - Share with team for demos
3. **Auto-setup** - Everything installs automatically on first start
4. **Multiple terminals** - Open multiple terminals for different services

## 📚 More Help

- Full guide: `CLOUD_DEVELOPMENT_GUIDE.md`
- Team collaboration: `CODESPACES_TEAM_COLLABORATION.md`
- Security: `CODESPACES_SECURITY.md`

---

**That's it!** You're ready to develop in the cloud. 🚀


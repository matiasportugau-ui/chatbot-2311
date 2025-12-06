# Quick Sync Reference Card

## 🚀 Your Repository
**GitHub:** `https://github.com/matiasportugau-ui/chatbot-2311.git`

---

## 📋 Daily Workflow (3 Steps)

### Before Starting Work:
```bash
git pull origin main
```

### After Making Changes:
```bash
git add .
git commit -m "Description of changes"
git push origin main
```

### If Conflicts Occur:
```bash
# Git will show conflicted files
# 1. Open files, resolve conflicts (remove <<<<<<< markers)
# 2. Then:
git add .
git commit -m "Resolved conflicts"
git push origin main
```

---

## 🖥️ Setting Up Second Computer

### Quick Setup (Linux/Mac):
```bash
cd ~/Projects
# You can use ANY folder name - it's safe!
git clone https://github.com/matiasportugau-ui/chatbot-2311.git
# OR with custom name:
# git clone https://github.com/matiasportugau-ui/chatbot-2311.git my-chatbot
cd chatbot-2311
./setup_new_computer.sh
```

**💡 Folder name doesn't matter - it's just for organizing files locally!**

### Manual Setup:
```bash
# 1. Clone
git clone https://github.com/matiasportugau-ui/chatbot-2311.git
cd chatbot-2311

# 2. Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Node.js
npm install

# 4. Environment
cp env.example .env
# Edit .env with your credentials (from secure backup)
```

---

## 🔐 Secrets Management

**NEVER commit `.env` to Git!**

### Transfer .env Securely:
1. **From Computer A:** Copy `.env` to secure location
   - Password manager (1Password, Bitwarden)
   - Encrypted USB
   - Encrypted cloud storage

2. **To Computer B:** Place `.env` in project root
   ```bash
   # Verify it's not tracked:
   git status  # .env should NOT appear
   ```

---

## ✅ Verification Checklist

- [ ] Git remote configured: `git remote -v`
- [ ] Can pull: `git pull origin main`
- [ ] Can push: `git push origin main`
- [ ] Python venv active: `which python` shows `venv/bin/python`
- [ ] Dependencies installed: `pip list | grep openai`
- [ ] Node modules: `ls node_modules | head`
- [ ] `.env` exists and is NOT in git: `git status` doesn't show `.env`

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Your branch is behind" | `git pull origin main` |
| "Permission denied" | Set up SSH keys for GitHub |
| ".env not found" | `cp env.example .env` then edit |
| "Module not found" | `pip install -r requirements.txt` |
| "node_modules missing" | `npm install` |

---

## 📞 Need More Help?

See full guide: `WORKSPACE_SYNC_GUIDE.md`


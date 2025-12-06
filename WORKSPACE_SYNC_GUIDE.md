# Workspace Sync Guide - Working Across Multiple Computers

This guide explains how to sync your workspace between multiple computers and work on the same version from both machines.

## 🎯 Recommended Approach: Git Version Control

The best way to keep your workspace synchronized is using **Git** (which is already set up in this project). This ensures:
- ✅ Version history and change tracking
- ✅ Conflict resolution
- ✅ Same codebase on both computers
- ✅ Easy rollback if something breaks

---

## 📋 Quick Start: Sync to Second Computer

### Step 1: Prepare Current Computer (First Machine)

1. **Commit your current changes:**
   ```bash
   cd /Users/matias/chatbot2511/chatbot-2311
   git add .
   git commit -m "Sync workspace before moving to second computer"
   ```

2. **Push to remote repository:**
   ```bash
   # Your repository is already configured:
   git push origin main
   
   # If you need to set up a new remote (unlikely):
   # git remote add origin https://github.com/matiasportugau-ui/chatbot-2311.git
   # git branch -M main
   # git push -u origin main
   ```

3. **Export your environment variables:**
   ```bash
   # Create a backup of your .env file (keep it secure!)
   # IMPORTANT: Never commit .env to git - it contains secrets
   cp .env .env.backup
   # Store .env.backup securely (password manager, encrypted USB, etc.)
   ```

### Step 2: Set Up Second Computer

1. **Clone the repository:**
   ```bash
   cd ~/Projects  # or wherever you want the project
   git clone https://github.com/matiasportugau-ui/chatbot-2311.git chatbot-2311
   cd chatbot-2311
   ```

2. **Set up Python environment:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up Node.js environment:**
   ```bash
   # Install Node.js dependencies
   npm install
   ```

4. **Configure environment variables:**
   ```bash
   # Copy the example file
   cp env.example .env
   
   # Edit .env with your actual credentials
   # Use the .env.backup from your first computer (securely transferred)
   nano .env  # or use your preferred editor
   ```

5. **Verify setup:**
   ```bash
   # Test that everything works
   python -m pytest  # if you have tests
   npm run dev  # if you want to test the Next.js app
   ```

---

## 🔄 Daily Workflow: Working on Both Computers

### When Starting Work on Computer A:

```bash
cd /path/to/chatbot-2311
git pull origin main  # Get latest changes from Computer B
# Work on your changes...
git add .
git commit -m "Description of changes"
git push origin main
```

### When Starting Work on Computer B:

```bash
cd /path/to/chatbot-2311
git pull origin main  # Get latest changes from Computer A
# Work on your changes...
git add .
git commit -m "Description of changes"
git push origin main
```

### ⚠️ Handling Conflicts

If both computers have uncommitted changes:

```bash
git pull origin main
# If conflicts occur:
# 1. Git will mark conflicted files
# 2. Open files and resolve conflicts (look for <<<<<<< markers)
# 3. After resolving:
git add .
git commit -m "Resolved merge conflicts"
git push origin main
```

---

## 🔐 Managing Secrets and Environment Variables

### Important: Never Commit Secrets!

Your `.gitignore` already excludes `.env` files. Here's how to handle secrets:

### Method 1: Manual Transfer (Most Secure)

1. **On Computer A:** Export your `.env` file securely
   - Use a password manager (1Password, Bitwarden, etc.)
   - Use encrypted USB drive
   - Use secure cloud storage with encryption (Dropbox, Google Drive with encryption)

2. **On Computer B:** Import the `.env` file
   ```bash
   # Place .env file in project root
   # Verify it's not tracked by git:
   git status  # .env should NOT appear
   ```

### Method 2: Environment Variable Template

1. Keep `env.example` updated with all required variables (without values)
2. On new computer, copy `env.example` to `.env` and fill in values
3. Use a password manager to store actual values

### Method 3: Secrets Manager (Advanced)

For production setups, consider using:
- **AWS Secrets Manager**
- **HashiCorp Vault**
- **1Password Secrets Automation**
- **GitHub Secrets** (for CI/CD)

---

## 🚀 Alternative Sync Methods

### Option 2: Cloud Storage Sync (Simpler, Less Recommended)

**Pros:**
- ✅ Automatic sync
- ✅ No Git knowledge needed

**Cons:**
- ❌ No version history
- ❌ Conflict resolution is manual
- ❌ Can sync sensitive files accidentally
- ❌ Slower for large projects

**Setup:**
1. Install Dropbox, Google Drive, or iCloud on both computers
2. Move project folder to synced directory
3. **IMPORTANT:** Ensure `.gitignore` excludes:
   - `node_modules/`
   - `__pycache__/`
   - `.env`
   - `venv/`
   - `*.log`

### Option 3: Remote Development (VS Code Remote / SSH)

**Best for:** Working on one computer from another

1. **Set up SSH access to Computer A from Computer B:**
   ```bash
   # On Computer B:
   ssh user@computer-a-ip
   ```

2. **Use VS Code Remote SSH:**
   - Install "Remote - SSH" extension
   - Connect to Computer A
   - Edit files directly on Computer A

### Option 4: Docker + Cloud Storage

For consistent environments:

1. Create `Dockerfile` (you may already have one)
2. Use Docker Compose for services
3. Sync code via Git
4. Run same Docker containers on both computers

---

## 📦 What Gets Synced vs. What Doesn't

### ✅ Synced via Git (Recommended):
- All source code (`.py`, `.js`, `.ts`, `.json`, etc.)
- Configuration files (except `.env`)
- Documentation (`.md` files)
- Project structure

### ❌ NOT Synced (Should be excluded):
- `.env` files (secrets)
- `node_modules/` (install via `npm install`)
- `__pycache__/` (Python cache)
- `venv/` (Python virtual environment)
- `*.log` (log files)
- `.DS_Store` (macOS)
- IDE settings (`.vscode/`, `.idea/`)

### ⚠️ Manual Sync Required:
- `.env` files (secrets - use secure transfer)
- Database files (if using local SQLite)
- Local backups

---

## 🛠️ Setup Script for Second Computer

Create this script to automate setup on a new computer:

```bash
#!/bin/bash
# setup_new_computer.sh

echo "🚀 Setting up chatbot-2311 on new computer..."

   # Clone repository
   echo "📥 Cloning repository..."
   git clone https://github.com/matiasportugau-ui/chatbot-2311.git chatbot-2311
   cd chatbot-2311

# Python setup
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Node.js setup
echo "📦 Setting up Node.js dependencies..."
npm install

# Environment setup
echo "⚙️  Setting up environment..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "⚠️  IMPORTANT: Edit .env file with your credentials!"
    echo "   Use the .env.backup from your other computer."
fi

echo "✅ Setup complete!"
echo "📝 Next steps:"
echo "   1. Edit .env file with your credentials"
echo "   2. Test: python -m pytest"
echo "   3. Test: npm run dev"
```

Make it executable:
```bash
chmod +x setup_new_computer.sh
```

---

## 🔍 Verify Your Setup

### Checklist for Both Computers:

- [ ] Git is installed and configured
- [ ] Python 3.x is installed
- [ ] Node.js and npm are installed
- [ ] Virtual environment is created and activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Node modules installed (`npm install`)
- [ ] `.env` file exists and is configured
- [ ] `.env` is NOT tracked by git (`git status` should not show it)
- [ ] Can pull/push to remote repository
- [ ] Project runs successfully on both computers

### Test Commands:

```bash
# Test Git sync
git pull origin main
git status

# Test Python
python --version
python -c "import openai; print('Python deps OK')"

# Test Node.js
node --version
npm --version
npm list --depth=0
```

---

## 🆘 Troubleshooting

### Problem: "Your branch is behind 'origin/main'"

**Solution:**
```bash
git pull origin main
# Resolve any conflicts, then:
git push origin main
```

### Problem: "Permission denied (publickey)" when pushing

**Solution:**
```bash
# Set up SSH keys for GitHub
ssh-keygen -t ed25519 -C "your_email@example.com"
# Add public key to GitHub: Settings > SSH and GPG keys
```

### Problem: Different Python/Node versions on computers

**Solution:**
- Use version managers:
  - Python: `pyenv` or `conda`
  - Node.js: `nvm` (Node Version Manager)
- Document required versions in `README.md`

### Problem: Environment variables not working

**Solution:**
```bash
# Verify .env file exists
ls -la .env

# Check if variables are loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY')[:10] + '...')"
```

---

## 📚 Additional Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Environment Variables Best Practices](https://12factor.net/config)
- [VS Code Remote Development](https://code.visualstudio.com/docs/remote/remote-overview)

---

## 🎯 Recommended Workflow Summary

1. **Primary Method:** Use Git + GitHub/GitLab for code sync
2. **Secrets:** Manually transfer `.env` securely (password manager)
3. **Daily:** Always `git pull` before starting work, `git push` when done
4. **Conflicts:** Resolve immediately, don't let them accumulate
5. **Backup:** Regular commits = automatic backup

---

**Need Help?** Check your project's `README.md` for specific setup instructions.


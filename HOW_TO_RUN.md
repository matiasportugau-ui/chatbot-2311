# 🚀 How to Run the BMC Chatbot System

## ⭐ Recommended: Unified Launcher

The **Unified Launcher** is the easiest way to run the system. It handles everything automatically.

### Quick Start

**Windows:**
```batch
launch.bat
```

**Linux/Mac:**
```bash
./launch.sh
```

**Direct Python:**
```bash
python unified_launcher.py
```

### What It Does

- ✅ Checks prerequisites (Python 3.11+, Node.js)
- ✅ Installs dependencies automatically
- ✅ Configures environment (.env file)
- ✅ Shows interactive menu with all modes
- ✅ Manages services (API, MongoDB, Next.js)

### Direct Mode Execution

Run specific modes without the menu:

```bash
# Interactive Chatbot
python unified_launcher.py --mode chat

# API Server
python unified_launcher.py --mode api

# Chat Simulator
python unified_launcher.py --mode simulator

# Full Stack (API + Dashboard)
python unified_launcher.py --mode fullstack

# Setup only (no execution)
python unified_launcher.py --setup-only

# Skip setup (assume configured)
python unified_launcher.py --skip-setup --mode chat
```

For complete documentation, see **[UNIFIED_LAUNCHER.md](./UNIFIED_LAUNCHER.md)**

---

## Alternative: Simulation Script

If you prefer the simulation script approach:

**Use a dot-slash (relative path):**

```bash
./run_simulation.sh
```

**NOT:**
```bash
/run_simulation.sh    # ❌ Wrong - absolute path
run_simulation.sh     # ❌ Wrong - missing ./
```

### Quick Steps

1. **Navigate to the directory:**
   ```bash
   cd /path/to/chatbot-2311
   ```

2. **Run the script:**
   ```bash
   ./run_simulation.sh
   ```

3. **That's it!** The script will:
   - Install dependencies if needed
   - Start MongoDB (if Docker is running)
   - Start API server
   - Launch the simulator

## If Docker is Not Running

The script will continue without MongoDB. You'll see:

```
⚠️  Docker daemon is not running
   To start MongoDB: start Docker Desktop or run 'docker start bmc-mongodb'
   Continuing without MongoDB (no conversation persistence)
```

**This is OK!** The chatbot will work, but conversations won't be saved.

**To enable MongoDB:**
1. Start Docker Desktop
2. Run the script again

## Troubleshooting

### "Permission denied"
```bash
chmod +x run_simulation.sh
./run_simulation.sh
```

### "No such file or directory"
Make sure you're in the correct directory:
```bash
pwd
# Should show: .../05_dashboard_ui
ls -la run_simulation.sh
# Should show the file
```

### Script stops at API server
Check the logs:
```bash
cat logs/api_server.log
```

## Alternative: Manual Start

If you prefer manual control:

```bash
# Terminal 1: Start API server
python api_server.py

# Terminal 2: Start simulator
python simulate_chat_cli.py
```

Or use the unified launcher in manual mode:
```bash
python unified_launcher.py --mode api    # Terminal 1
python unified_launcher.py --mode simulator  # Terminal 2
```

---

## Summary

**Recommended approach:**
- Use `unified_launcher.py` for the best experience
- It handles setup, dependencies, and service management automatically

**Alternative approaches:**
- Use `./run_simulation.sh` for quick simulation testing
- Manual start for development/debugging

For more details, see:
- **[UNIFIED_LAUNCHER.md](./UNIFIED_LAUNCHER.md)** - Complete unified launcher guide
- **[START_HERE.md](./START_HERE.md)** - Quick start guide
- **[QUICK_RUN.md](./QUICK_RUN.md)** - Quick run reference


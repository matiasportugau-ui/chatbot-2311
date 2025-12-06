# ⚡ Quick Access Guide - Unified Launcher

## 🚀 Start the System (One Command)

### Windows
```batch
launch.bat
```

### Linux/Mac
```bash
./launch.sh
```

### Direct Python
```bash
python unified_launcher.py
```

## 📋 Common Commands

### Interactive Chat
```bash
python unified_launcher.py --mode chat
```

### API Server Only
```bash
python unified_launcher.py --mode api
```

### Full Stack (API + Dashboard)
```bash
python unified_launcher.py --mode fullstack
```

### Simulator
```bash
python unified_launcher.py --mode simulator
```

### Setup Only (No Execution)
```bash
python unified_launcher.py --setup-only
```

### Skip Setup (Already Configured)
```bash
python unified_launcher.py --skip-setup --mode chat
```

## 📚 Documentation Quick Links

- **[START_HERE.md](./START_HERE.md)** - ⭐ Start here for quick setup
- **[UNIFIED_LAUNCHER.md](./UNIFIED_LAUNCHER.md)** - Complete unified launcher guide
- **[HOW_TO_RUN.md](./HOW_TO_RUN.md)** - Detailed running instructions
- **[QUICK_RUN.md](./QUICK_RUN.md)** - Quick run reference
- **[README.md](./README.md)** - Main project documentation

## 🎯 All Available Modes

1. **chat** - Interactive Chatbot (`chat_interactivo.py`)
2. **api** - API Server (`api_server.py`)
3. **simulator** - Chat Simulator (`simulate_chat.py`)
4. **dashboard** - Next.js Dashboard (dev mode)
5. **fullstack** - API + Dashboard together
6. **agent** - Automated Agent System
7. **system** - Complete Integrated System

## 🔧 Development Tools (From Menu)

When you run `python unified_launcher.py` (without --mode), you get an interactive menu with:

- **s** - System Status
- **t** - Run Tests
- **c** - Check Configuration
- **r** - Reset Setup
- **l** - View Logs

## 📝 What Changed

All documentation has been updated to feature the **Unified Launcher** as the primary entry point:

✅ **Updated Files:**
- START_HERE.md
- HOW_TO_RUN.md
- QUICK_RUN.md
- README.md
- UNIFIED_LAUNCHER.md
- RUN_CHATBOT_WINDOWS.md
- QUICK_START_CHATBOT.md
- START_CHATBOT_NOW.md
- AUTOPILOT.md
- QUICK_REFERENCE.md
- INSTALAR_Y_EJECUTAR.md (Spanish)

✅ **Legacy scripts** are marked as deprecated but still work
✅ **Consistent documentation** across all guides
✅ **Clear migration path** from old methods

## 🆘 Troubleshooting

### Python Not Found
```bash
# Install Python 3.11+ from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH"
```

### Dependencies Missing
The unified launcher installs them automatically, or:
```bash
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Check what's using port 8000
lsof -ti :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
python unified_launcher.py --port 9000 --mode api
```

## 💡 Pro Tips

1. **First time?** Just run `launch.bat` or `./launch.sh` - it handles everything
2. **Already configured?** Use `--skip-setup` to save time
3. **Development?** Use `--dev` for verbose logging
4. **Production?** Use `--production` for optimized settings
5. **Need help?** Check `UNIFIED_LAUNCHER.md` for complete documentation

---

**Last Updated:** Documentation review and unified launcher integration complete
**Commit:** `068ce69` - docs: Update all documentation to feature Unified Launcher


# 🚀 Chatbot Execution Commands

Quick reference guide for executing your BMC Chatbot system.

## ⭐ Recommended: Complete Executor (Best Option)

The **Complete Executor** (`ejecutor_completo.py`) is the most comprehensive option. It handles:
- ✅ System review and verification
- ✅ Automatic dependency installation
- ✅ Service configuration (MongoDB, etc.)
- ✅ Multiple execution modes
- ✅ Auto-repair of issues
- ✅ AI-powered diagnostics

### Basic Usage

```bash
# Navigate to project directory
cd /Users/matias/chatbot2511/chatbot-2311

# Run the complete executor
python ejecutor_completo.py
```

### Execution Modes

When you run `ejecutor_completo.py`, you'll be prompted to select a mode:

1. **unified** - Unified Launcher (recommended)
2. **chat** - Interactive chat
3. **api** - API Server only
4. **interactive** - Interactive mode with AI assistant (if AI available)
5. **diagnostic** - Intelligent system diagnosis (if AI available)

---

## 🎯 Unified Launcher (Alternative)

The **Unified Launcher** provides an interactive menu with all system options.

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

### Direct Mode Execution

Run specific modes without the interactive menu:

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

---

## 💬 Direct Script Execution

### Interactive Chat

```bash
python chat_interactivo.py
```

### API Server

```bash
python api_server.py
```

The API server will start on `http://localhost:8000` by default.

### Chat Simulator

```bash
python simulate_chat_cli.py
```

---

## 🧪 Simulation Script

For quick testing with automatic setup:

```bash
./run_simulation.sh
```

This script will:
- ✅ Check Python version
- ✅ Create .env file if needed
- ✅ Install missing dependencies
- ✅ Start MongoDB (via Docker if available)
- ✅ Start API server
- ✅ Launch interactive CLI simulator

---

## 🔧 Manual Multi-Terminal Setup

If you prefer manual control, run each component in separate terminals:

### Terminal 1: API Server
```bash
python api_server.py
```

### Terminal 2: Interactive Chat
```bash
python chat_interactivo.py
```

### Terminal 3: MongoDB (if needed)
```bash
docker start mongodb
# or
docker-compose up mongodb
```

---

## 📋 Prerequisites

Before running, ensure you have:

1. **Python 3.8+** (3.11+ recommended)
   ```bash
   python --version
   ```

2. **Dependencies installed**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment variables configured**
   - `.env` or `.env.local` file with API keys
   - Or use `load_secrets_automatically.py` for encrypted secrets

4. **MongoDB (optional)**
   - Docker with MongoDB container
   - Or MongoDB running locally

---

## 🎛️ Execution Modes Comparison

| Mode | Command | Description |
|------|---------|-------------|
| **Complete Executor** | `python ejecutor_completo.py` | Full system with auto-setup and diagnostics |
| **Unified Launcher** | `python unified_launcher.py` | Interactive menu with all options |
| **Interactive Chat** | `python chat_interactivo.py` | Direct chat interface |
| **API Server** | `python api_server.py` | REST API server only |
| **Simulator** | `python simulate_chat_cli.py` | CLI-based chat simulator |
| **Simulation Script** | `./run_simulation.sh` | Automated setup and simulation |

---

## 🚨 Troubleshooting

### Permission Denied (Linux/Mac)
```bash
chmod +x launch.sh
chmod +x run_simulation.sh
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -ti :8000

# Kill it
kill -9 $(lsof -ti :8000)
```

### MongoDB Not Running
The system will work without MongoDB, but conversations won't persist.

To start MongoDB:
```bash
docker start mongodb
# or
docker-compose up -d mongodb
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Environment Variables Not Loaded
```bash
# Check if .env exists
ls -la .env .env.local

# Or use automatic secrets loader
python load_secrets_automatically.py
```

---

## 📚 Additional Resources

- **[HOW_TO_RUN.md](./HOW_TO_RUN.md)** - Detailed running instructions
- **[QUICK_RUN.md](./QUICK_RUN.md)** - Quick run reference
- **[START_HERE.md](./START_HERE.md)** - Quick start guide
- **[README.md](./README.md)** - Main documentation

---

## 🎯 Quick Reference

**Most Common Commands:**

```bash
# Full system with auto-setup (RECOMMENDED)
python ejecutor_completo.py

# Quick chat interface
python chat_interactivo.py

# API server only
python api_server.py

# Interactive menu
python unified_launcher.py
```

---

**Last Updated:** Based on current codebase structure
**Project Path:** `/Users/matias/chatbot2511/chatbot-2311`


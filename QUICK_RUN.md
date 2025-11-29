# 🚀 Quick Run Reference

## ⭐ Recommended: Unified Launcher

For the best experience, use the **Unified Launcher**:

**Windows:**
```batch
launch.bat
```

**Linux/Mac:**
```bash
./launch.sh
```

**Direct:**
```bash
python unified_launcher.py
```

The unified launcher provides:
- ✅ Interactive menu with all modes
- ✅ Automatic setup and dependency installation
- ✅ Service management (API, MongoDB, Next.js)
- ✅ Multiple execution modes

See **[UNIFIED_LAUNCHER.md](./UNIFIED_LAUNCHER.md)** for complete documentation.

---

## Alternative: Simulation Script

For quick simulation testing, you can use:

```bash
./run_simulation.sh
```

That's it! The script will:

1. ✅ Check Python version
2. ✅ Create .env file if needed
3. ✅ Install missing dependencies
4. ✅ Start MongoDB (via Docker if available)
5. ✅ Start API server
6. ✅ Launch interactive CLI simulator

## What It Does

The `run_simulation.sh` script automatically:

- **Checks prerequisites**: Python 3.8+, dependencies
- **Sets up environment**: Creates .env from template if missing
- **Installs dependencies**: Automatically installs from requirements.txt
- **Starts MongoDB**: Uses Docker if available, or continues without it
- **Starts API server**: Runs in background, waits for it to be ready
- **Launches simulator**: Opens interactive CLI for testing

## Usage

### Basic Usage

```bash
cd Dashboard-bmc/proyecto-cotizacion-whatsapp/05_dashboard_ui
./run_simulation.sh
```

### What You'll See

```
🚀 BMC Chatbot Simulator - One-Command Setup
==============================================

📋 Step 1: Checking Python...
✅ Python 3.11.0 found

📋 Step 2: Checking environment configuration...
✅ .env file exists

📋 Step 3: Checking Python dependencies...
✅ All required dependencies installed

📋 Step 4: Checking MongoDB...
✅ MongoDB is accessible

📋 Step 5: Setting up logs...
✅ Logs directory ready

📋 Step 6: Checking API server...
✅ API server started (PID: 12345)
   Waiting for server to be ready...
✅ API server is ready!

📋 Step 7: Verifying setup...
✅ API server module can be imported

✅ Setup complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Starting Interactive CLI Simulator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Tips:
   - Type messages to chat with the bot
   - Use /help to see all commands
   - Use /exit to quit

📊 Status:
   API Server: http://localhost:8000
   MongoDB: Connected
   API PID: 12345 (will stop when you exit)

🚀 BMC Chat Simulator
📱 Phone: +59891234567
💬 Type a message or /help for commands
>
```

## Features

### Automatic Setup

- No manual configuration needed
- Handles missing dependencies
- Starts required services
- Creates necessary files

### Smart Detection

- Detects if services are already running
- Reuses existing MongoDB containers
- Checks port availability
- Validates connections

### Clean Exit

- Stops API server when you exit
- Preserves logs
- Clean shutdown

## Troubleshooting

### Script Fails to Run

```bash
# Make sure it's executable
chmod +x run_simulation.sh

# Or run with bash
bash run_simulation.sh
```

### Dependencies Not Installing

```bash
# Install manually first
pip3 install -r requirements.txt

# Then run script
./run_simulation.sh
```

### MongoDB Issues

The script will:
- Try to start MongoDB with Docker
- Continue without MongoDB if Docker unavailable
- System works without MongoDB (no persistence)

### Port Already in Use

The script will:
- Detect port 8000 in use
- Attempt to free it
- If that fails, show error message

**Manual fix:**
```bash
# Find process using port 8000
lsof -ti :8000

# Kill it
kill -9 $(lsof -ti :8000)

# Run script again
./run_simulation.sh
```

## Alternative: Manual Steps

If you prefer manual control:

```bash
# Terminal 1: Start API server
python api_server.py

# Terminal 2: Start simulator
python simulate_chat_cli.py
```

## Next Steps

After the simulator starts:

1. **Test basic conversation:**
   ```
   > Hola
   > Necesito información sobre Isodec
   ```

2. **Test quote request:**
   ```
   > Quiero cotizar Isodec 10x5 100mm blanco
   ```

3. **Use CLI commands:**
   ```
   > /help
   > /history
   > /stats
   > /export
   ```

4. **Exit when done:**
   ```
   > /exit
   ```

## See Also

- **[UNIFIED_LAUNCHER.md](./UNIFIED_LAUNCHER.md)** - ⭐ Complete unified launcher guide (recommended)
- **[START_HERE.md](./START_HERE.md)** - Quick start guide
- **[HOW_TO_RUN.md](./HOW_TO_RUN.md)** - Detailed running instructions
- **TESTING_GUIDE.md** - Comprehensive testing guide
- **README_SIMULATOR.md** - Simulator documentation
- **start_simulator.sh** - Alternative start script (requires API running)

---

**Quick Summary:**
- **Best option:** Use `unified_launcher.py` for full system access
- **Quick test:** Use `./run_simulation.sh` for simulation only


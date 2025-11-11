# 🚀 How to Run the Simulation

## Correct Command

**Use a dot-slash (relative path):**

```bash
./run_simulation.sh
```

**NOT:**
```bash
/run_simulation.sh    # ❌ Wrong - absolute path
run_simulation.sh     # ❌ Wrong - missing ./
```

## Quick Steps

1. **Navigate to the directory:**
   ```bash
   cd Dashboard-bmc/proyecto-cotizacion-whatsapp/05_dashboard_ui
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

If the script doesn't work:

```bash
# Terminal 1: Start API server
python api_server.py

# Terminal 2: Start simulator
python simulate_chat_cli.py
```

---

**Remember: Always use `./run_simulation.sh` (with the dot-slash)!** ✅


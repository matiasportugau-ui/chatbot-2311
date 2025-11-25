# 🚀 How to Run the Chatbot on Windows

## Quick Start

### Option 1: Use the Batch File (Easiest)

Double-click `run_chatbot.bat` or run in PowerShell:

```powershell
.\run_chatbot.bat
```

### Option 2: Use the PowerShell Script

```powershell
.\run_chatbot.ps1
```

### Option 3: Run Directly (if Python is installed)

```powershell
python chat_interactivo.py
```

## Prerequisites

### Python Installation Required

The chatbot requires **Python 3.8 or higher**. 

**If Python is not installed:**

1. **Download Python:**
   - Go to: https://www.python.org/downloads/
   - Download Python 3.11 or 3.12
   - ⚠️ **IMPORTANT:** During installation, check **"Add Python to PATH"**

2. **Or install from Microsoft Store:**
   - Open Microsoft Store
   - Search for "Python 3.11"
   - Click "Install"

3. **Verify installation:**
   ```powershell
   python --version
   ```
   Should show: `Python 3.11.x` or similar

### Install Dependencies

After Python is installed, install required packages:

```powershell
pip install -r requirements.txt
```

Or let the launcher script handle it (it will ask you).

## Running the Chatbot

### Interactive Chat Mode

The simplest way to test the chatbot:

```powershell
python chat_interactivo.py
```

This starts an interactive terminal chat where you can:
- Ask about products (Isodec, Poliestireno, Lana de Roca)
- Request quotes
- Get product information

### Example Conversation

```
👤 Tú: Hola
🤖 Agente: ¡Hola! 👋 Soy tu agente de cotizaciones...

👤 Tú: Quiero cotizar
🤖 Agente: ¡Perfecto! 🎯 Vamos a crear tu cotización...

👤 Tú: Juan Perez
🤖 Agente: ¡Hola Juan Perez! 👋

👤 Tú: 099123456
🤖 Agente: ✅ Teléfono registrado...

... (continue with the quote process)
```

### Exit the Chat

Type `salir`, `exit`, `chau`, `adios`, or `bye` to exit.

## Alternative: Full System with API Server

For the complete system with API server and enhanced features:

### Terminal 1 - Start API Server:
```powershell
python api_server.py
```

### Terminal 2 - Start Enhanced CLI:
```powershell
python simulate_chat_cli.py
```

## Troubleshooting

### "Python not found" or "python no se reconoce"

**Solution:** Python is not in your PATH or not installed.

1. Reinstall Python and check "Add Python to PATH"
2. Or manually add Python to PATH:
   - Find Python installation (usually `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX`)
   - Add to System PATH in Environment Variables

### "ModuleNotFoundError"

**Solution:** Dependencies not installed.

```powershell
pip install -r requirements.txt
```

### "ImportError: cannot import name..."

**Solution:** Missing local modules. Make sure you're in the project root directory.

```powershell
cd "C:\Users\usuario\Clone repo coti inteligente\bmc-cotizacion-inteligente"
python chat_interactivo.py
```

### PowerShell Execution Policy Error

If you get an execution policy error:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try running the script again.

## What the Chatbot Can Do

✅ **Product Information:**
- Isodec (Panel Aislante Térmico)
- Poliestireno Expandido
- Lana de Roca

✅ **Quote Generation:**
- Step-by-step quote process
- Collects: name, phone, address, product, dimensions, thickness, color, finishes
- Calculates total price automatically

✅ **Interactive Conversation:**
- Natural language understanding
- Multi-step conversations
- Context awareness

## Files

- `chat_interactivo.py` - Standalone interactive chatbot
- `run_chatbot.bat` - Windows batch launcher
- `run_chatbot.ps1` - PowerShell launcher script
- `sistema_cotizaciones.py` - Quote system core
- `utils_cotizaciones.py` - Utility functions

## Next Steps

Once the chatbot is running:
1. Test different conversation flows
2. Try various product combinations
3. Test edge cases and error handling
4. Review the quote generation logic

For more advanced features, see:
- `START_HERE.md` - Full system guide
- `README_SIMULATOR.md` - Simulator documentation
- `HOW_TO_RUN.md` - Detailed run instructions


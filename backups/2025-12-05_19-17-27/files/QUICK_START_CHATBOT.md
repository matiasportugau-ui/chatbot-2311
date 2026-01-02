# 🚀 Quick Start - Run the Chatbot

## ⭐ Recommended: Unified Launcher

The **Unified Launcher** is the easiest way to run the chatbot. It handles everything automatically.

### Quick Start (Windows)

**Double-click:**
```batch
launch.bat
```

**Or in PowerShell:**
```powershell
.\launch.bat
```

**Or directly:**
```powershell
python unified_launcher.py --mode chat
```

### Quick Start (Linux/Mac)

```bash
./launch.sh
```

**Or directly:**
```bash
python unified_launcher.py --mode chat
```

The unified launcher will:
- ✅ Check prerequisites
- ✅ Install dependencies
- ✅ Configure environment
- ✅ Start the chatbot

For complete documentation, see **[UNIFIED_LAUNCHER.md](./UNIFIED_LAUNCHER.md)**

---

## Alternative: Manual Execution

If you prefer to run manually, the chatbot needs an **interactive terminal** where you can type messages.

### Step 1: Open a Terminal

**Windows - PowerShell:**
- Press `Win + X`
- Select "Windows PowerShell" or "Terminal"
- Navigate to the project folder

**Windows - Command Prompt:**
- Press `Win + R`
- Type `cmd` and press Enter
- Navigate to the project folder

### Step 2: Run the Chatbot

**Legacy batch file (deprecated):**
- Double-click `run_chatbot.bat` in Windows Explorer
- ⚠️ Note: Use `launch.bat` instead (unified launcher)

**Or run manually:**

**PowerShell:**
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
python chat_interactivo.py
```

**Command Prompt:**
```cmd
python chat_interactivo.py
```

### Step 3: Start Chatting!

You'll see:
```
======================================================================
🤖 CHAT INTERACTIVO - AGENTE DE COTIZACIONES BMC URUGUAY
======================================================================
Escribe 'salir' para terminar la conversación
======================================================================

🤖 Agente: ¡Hola! 👋
...
```

Then type your messages when you see:
```
👤 Tú: 
```

### Example Conversation

```
👤 Tú: Hola
🤖 Agente: ¡Hola! 👋 Soy tu agente de cotizaciones...

👤 Tú: Quiero cotizar
🤖 Agente: ¡Perfecto! 🎯 Vamos a crear tu cotización...

👤 Tú: Juan Perez
🤖 Agente: ¡Hola Juan Perez! 👋

... (continue the conversation)
```

### To Exit

Type: `salir`, `exit`, `chau`, `adios`, or `bye`

Or press `Ctrl + C`

---

**Note:** The chatbot must run in YOUR terminal window where you can type. It cannot run automatically - it needs your input!


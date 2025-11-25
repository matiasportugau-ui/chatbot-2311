# 🚀 Quick Start - Run the Chatbot

## Run in Your Own Terminal

The chatbot needs an **interactive terminal** where you can type messages. Here's how:

### Step 1: Open a Terminal

**Option A: PowerShell**
- Press `Win + X`
- Select "Windows PowerShell" or "Terminal"
- Navigate to the project folder:
  ```powershell
  cd "C:\Users\usuario\Clone repo coti inteligente\bmc-cotizacion-inteligente"
  ```

**Option B: Command Prompt**
- Press `Win + R`
- Type `cmd` and press Enter
- Navigate to the project folder:
  ```cmd
  cd "C:\Users\usuario\Clone repo coti inteligente\bmc-cotizacion-inteligente"
  ```

### Step 2: Run the Chatbot

**Easiest way - Double-click:**
- Double-click `run_chatbot.bat` in Windows Explorer
- A terminal window will open automatically

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


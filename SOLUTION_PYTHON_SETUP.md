# 🔧 Solution: Python Installation Required

## Problem Identified

The chatbot cannot run because **Python is not properly installed** on your system. 

Windows has a Python "stub" that redirects to the Microsoft Store, but Python itself is not installed.

## ✅ Solution: Install Python

### Step 1: Install Python 3.11 or 3.12

**Option A: Official Python Installer (Recommended)**

1. Go to: **https://www.python.org/downloads/**
2. Download **Python 3.11** or **Python 3.12** for Windows
3. Run the installer
4. ⚠️ **CRITICAL:** Check the box **"Add Python to PATH"** during installation
5. Click "Install Now"
6. Wait for installation to complete

**Option B: Microsoft Store**

1. Open **Microsoft Store**
2. Search for **"Python 3.11"**
3. Click **"Get"** or **"Install"**
4. Wait for installation

### Step 2: Verify Installation

Open PowerShell and run:

```powershell
python --version
```

You should see: `Python 3.11.x` or `Python 3.12.x`

If you see an error, Python is not in PATH. Reinstall and make sure to check "Add Python to PATH".

### Step 3: Run the Chatbot

Once Python is installed, you can run the chatbot using any of these methods:

**Method 1: Batch File (Easiest)**
```powershell
.\run_chatbot.bat
```

**Method 2: PowerShell Script**
```powershell
.\run_chatbot.ps1
```

**Method 3: Direct Python Command**
```powershell
python chat_interactivo.py
```

## 📋 What the Chatbot Needs

The chatbot (`chat_interactivo.py`) only requires:
- ✅ **Python 3.8+** (standard library only - no external packages needed for basic functionality)
- ✅ Local files: `sistema_cotizaciones.py` and `utils_cotizaciones.py`

**Optional dependencies** (in `requirements.txt`) are only needed for:
- API server features
- MongoDB integration
- OpenAI integration
- PDF generation
- Web interface

The **basic interactive chatbot works with just Python installed!**

## 🚀 Quick Test After Installation

Once Python is installed, test it:

```powershell
# Navigate to project directory
cd "C:\Users\usuario\Clone repo coti inteligente\bmc-cotizacion-inteligente"

# Run the chatbot
python chat_interactivo.py
```

You should see:
```
🤖 Agente de Cotizaciones BMC Uruguay iniciado
📋 Sistema cargado y listo para atenderte

🤖 Agente: ¡Hola! 👋
...
```

## 📝 Files Created to Help You

I've created these files to make it easier:

1. **`run_chatbot.bat`** - Windows batch file launcher
2. **`run_chatbot.ps1`** - PowerShell script launcher  
3. **`RUN_CHATBOT_WINDOWS.md`** - Complete Windows guide
4. **`SOLUTION_PYTHON_SETUP.md`** - This file (troubleshooting guide)

## 🆘 Still Having Issues?

### Issue: "python no se reconoce" after installation

**Solution:** Python is not in PATH

1. Find your Python installation:
   - Usually: `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX`
   - Or: `C:\Program Files\Python3XX`

2. Add to PATH manually:
   - Press `Win + X` → System → Advanced system settings
   - Click "Environment Variables"
   - Under "User variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX`
   - Click "New" again and add: `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX\Scripts`
   - Click OK on all dialogs
   - **Restart PowerShell/CMD** for changes to take effect

### Issue: PowerShell execution policy error

**Solution:** Run this in PowerShell (as Administrator):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: ModuleNotFoundError for local files

**Solution:** Make sure you're in the correct directory:

```powershell
cd "C:\Users\usuario\Clone repo coti inteligente\bmc-cotizacion-inteligente"
python chat_interactivo.py
```

## ✅ Verification Checklist

Before running the chatbot, verify:

- [ ] Python 3.11 or 3.12 is installed
- [ ] `python --version` works in PowerShell
- [ ] You're in the project root directory
- [ ] Files exist: `chat_interactivo.py`, `sistema_cotizaciones.py`, `utils_cotizaciones.py`

## 🎯 Next Steps

1. **Install Python** (follow Step 1 above)
2. **Verify installation** (follow Step 2)
3. **Run the chatbot** (follow Step 3)
4. **Start chatting!** Try: "Hola", "Quiero cotizar", etc.

---

**Once Python is installed, the chatbot will work immediately - no additional setup needed!**


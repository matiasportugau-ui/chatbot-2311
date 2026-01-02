# 🐍 Install Python 3.14.0 for Windows

## Direct Download Links

Based on the [official Python 3.14.0 release page](https://www.python.org/downloads/release/python-3140/):

### Recommended: Windows 64-bit Installer
**Download:** [python-3.14.0-amd64.exe](https://www.python.org/ftp/python/3.14.0/python-3.14.0-amd64.exe)
- **File Size:** 28.5 MB
- **MD5:** cf642108b97545a30ac055b94657a0e6
- **Recommended for:** Most Windows 10/11 systems (64-bit)

### Alternative Options:
- **32-bit:** [python-3.14.0.exe](https://www.python.org/ftp/python/3.14.0/python-3.14.0.exe) (27.1 MB)
- **ARM64:** [python-3.14.0-arm64.exe](https://www.python.org/ftp/python/3.14.0/python-3.14.0-arm64.exe) (27.8 MB) - Experimental

## Installation Steps

1. **Download the installer:**
   - Click the link above for the 64-bit version (recommended)
   - Or visit: https://www.python.org/downloads/release/python-3140/
   - Click "Windows installer (64-bit)" under the Files section

2. **Run the installer:**
   - Double-click the downloaded `.exe` file
   - ⚠️ **CRITICAL:** Check the box **"Add Python to PATH"** at the bottom
   - Click "Install Now" (or "Customize installation" if you want to change location)
   - Wait for installation to complete

3. **Verify installation:**
   - Open PowerShell
   - Run: `python --version`
   - Should show: `Python 3.14.0`

## What's New in Python 3.14

- Free-threaded Python support
- Template string literals (t-strings)
- Multiple interpreters in stdlib
- Zstandard compression support
- Improved error messages
- Experimental JIT compiler (included in Windows binaries)

## After Installation

Once Python 3.14.0 is installed, you can run the chatbot:

```powershell
python chat_interactivo.py
```

Or use the launcher:
```powershell
.\run_chatbot.bat
```

## Troubleshooting

### If "Add Python to PATH" was missed:
1. Reinstall Python and check the box this time
2. Or manually add to PATH:
   - Find: `C:\Users\YourName\AppData\Local\Programs\Python\Python314`
   - Add to System PATH in Environment Variables

### Verify Installation:
```powershell
python --version
pip --version
```

Both should work after installation.


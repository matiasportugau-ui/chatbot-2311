@echo off
REM setup_new_computer.bat
REM Quick setup script for syncing workspace to a new computer (Windows)

echo 🚀 Setting up chatbot-2311 on new computer...
echo.

REM Check if we're in the right directory or need to clone
if not exist ".git" (
    echo 📥 Repository not found. Please provide the repository URL:
    set /p REPO_URL="Git repository URL (or press Enter to skip): "
    
    if not "%REPO_URL%"=="" (
        echo Cloning repository...
        git clone "%REPO_URL%" chatbot-2311
        cd chatbot-2311
    ) else (
        echo ⚠️  Skipping Git clone. Make sure you're in the project directory.
    )
)

REM Check Python
echo 🐍 Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ first.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo ✅ Python found

REM Check Node.js
echo 📦 Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Node.js not found. Some features may not work.
    echo    Install from: https://nodejs.org/
) else (
    node --version
    echo ✅ Node.js found
)

REM Python setup
echo.
echo 🐍 Setting up Python environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

call venv\Scripts\activate.bat
echo ✅ Virtual environment activated

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install Python dependencies
echo 📦 Installing Python dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Python dependencies installed
) else (
    echo ⚠️  requirements.txt not found
)

REM Node.js setup
where npm >nul 2>&1
if not errorlevel 1 (
    echo.
    echo 📦 Setting up Node.js dependencies...
    if exist "package.json" (
        call npm install
        echo ✅ Node.js dependencies installed
    ) else (
        echo ⚠️  package.json not found
    )
)

REM Environment setup
echo.
echo ⚙️  Setting up environment...
if not exist ".env" (
    if exist "env.example" (
        copy env.example .env >nul
        echo ✅ Created .env from env.example
        echo ⚠️  IMPORTANT: Edit .env file with your actual credentials!
        echo    Use the .env.backup from your other computer (securely transferred).
    ) else (
        echo ⚠️  env.example not found. Create .env manually.
    )
) else (
    echo ✅ .env file already exists
)

REM Verify .env is not tracked by git
echo.
echo 🔍 Verifying Git configuration...
git ls-files --error-unmatch .env >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  WARNING: .env is tracked by Git! This is a security risk.
    echo    Run: git rm --cached .env
    echo    Then add .env to .gitignore
) else (
    echo ✅ .env is not tracked by Git (good!)
)

echo.
echo ✅ Setup complete!
echo.
echo 📝 Next steps:
echo    1. Edit .env file with your credentials (from secure backup)
echo    2. Activate virtual environment: venv\Scripts\activate.bat
echo    3. Test Python: python -c "import openai; print('OK')"
if exist "package.json" (
    echo    4. Test Node.js: npm run dev (if available)
)
echo    5. Pull latest changes: git pull origin main
echo.
echo 💡 Tip: Always run 'git pull' before starting work and 'git push' when done!
echo.
pause


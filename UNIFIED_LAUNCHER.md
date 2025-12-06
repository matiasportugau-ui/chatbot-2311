# Unified Launcher System

## Overview

The Unified Launcher is a single entry point for the entire BMC Chatbot System. It consolidates all execution modes, setup procedures, and development tools into one cross-platform launcher.

## Quick Start

### Windows

### Mac/Linux
```bash
./install_and_run.sh
```

### Windows
Double click `install_and_run.bat` or run:
```batch
install_and_run.bat
```

### Manual Method (Advanced)
```bash
python unified_launcher.py --mode fullstack
```

## Features

- **Single Entry Point**: One command to access all system modes
- **Auto-Setup**: Automatically configures dependencies and environment
- **Cross-Platform**: Works on Windows, Linux, and Mac
- **Smart Detection**: Finds Python, Node.js, Docker automatically
- **Unified Menu**: All execution modes in one place
- **Service Management**: Handles background services (API, MongoDB, Next.js)
- **Error Recovery**: Graceful handling of missing components
- **Development Tools**: Built-in utilities for debugging

## Execution Modes

### Python Backend Modes

1. **Interactive Chatbot** (`chat_interactivo.py`)

   - Real-time conversation interface
   - Step-by-step quote creation
   - Product information queries

2. **API Server** (`api_server.py`)

   - FastAPI REST API
   - Endpoints for chat processing and quotes
   - Runs on port 8000 by default

3. **Chat Simulator** (`simulate_chat.py`)

   - Simulates chat conversations
   - Tests chatbot logic without WhatsApp
   - Requires API server running
   - Available via menu or `--mode simulator`

4. **Enhanced CLI Simulator** (`simulate_chat_cli.py`)

   - Enhanced simulator with better formatting
   - Interactive CLI interface
   - Available via menu (option 4)
   - Note: Not available as direct `--mode` option, use menu or run directly

5. **Main System Menu** (`main.py`)

   - Menu-driven system
   - Quote creation, search, reports
   - Data export functionality

6. **Automated Agent System** (`automated_agent_system.py`)

   - Orchestrates agent components
   - Workflow execution
   - Background follow-ups

7. **System Complete** (`sistema_completo_integrado.py`)
   - Complete integrated system
   - All features combined

### Next.js Frontend Modes

8. **Next.js Dashboard (Dev)**

   - Development server with hot reload
   - Available at http://localhost:3000
   - Auto-reloads on code changes

9. **Next.js Dashboard (Production)**
   - Production build and server
   - Optimized for performance
   - Requires build step

### Combined Modes

10. **Full Stack (API + Dashboard)**
    - Starts API server in background
    - Starts Next.js dashboard
    - Health checks for both services
    - Graceful shutdown on exit

## Command-Line Options

### Basic Usage

```bash
python unified_launcher.py
```

Shows interactive menu

### Direct Mode Execution

```bash
python unified_launcher.py --mode chat
python unified_launcher.py --mode api
python unified_launcher.py --mode simulator
python unified_launcher.py --mode dashboard
python unified_launcher.py --mode fullstack
python unified_launcher.py --mode agent
python unified_launcher.py --mode system
```

### Setup Options

```bash
# Only run setup, don't start anything
python unified_launcher.py --setup-only

# Skip setup steps (assume already configured)
python unified_launcher.py --skip-setup --mode chat
```

### Mode Options

```bash
# Production mode (optimized settings)
python unified_launcher.py --production --mode fullstack

# Development mode (verbose logging)
python unified_launcher.py --dev --mode api

# Custom API port
python unified_launcher.py --port 9000 --mode api
```

## Development Tools

Access from the main menu:

- **System Status** (`s`): Check Python modules, environment, and services
- **Run Tests** (`t`): Run system tests (coming soon)
- **Check Configuration** (`c`): Validate system configuration
- **Reset Setup** (`r`): Reset environment and re-run setup
- **View Logs** (`l`): View launcher log file

## Setup Process

The launcher automatically runs these setup steps:

1. **Check Prerequisites**

   - Python 3.11+ detection
   - Node.js detection (optional)
   - npm/yarn detection

2. **Install Python Dependencies**

   - Upgrades pip
   - Installs from `requirements.txt`

3. **Configure Environment**

   - Creates/updates `.env` file
   - Prompts for missing API keys
   - Sets default values

4. **Manage Services**

   - Checks/starts MongoDB (Docker)
   - Verifies service availability

5. **Install Node.js Dependencies**

   - Auto-detects `package.json`
   - Installs npm dependencies
   - Supports both root and `nextjs-app/` directories

6. **Verify System**
   - Checks all critical modules
   - Validates configuration
   - Reports system status

## Environment Variables

The launcher checks for these environment variables:

### Required

- `OPENAI_API_KEY` - OpenAI API key (required for AI features)

### Optional

- `MONGODB_URI` - MongoDB connection string
- `PORT` - API server port (default: 8000)
- `HOST` - API server host (default: 0.0.0.0)
- `OPENAI_MODEL` - OpenAI model (default: gpt-4o-mini)

### WhatsApp Integration (Optional)

- `WHATSAPP_VERIFY_TOKEN`
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`

### Google Sheets Integration (Optional)

- `GOOGLE_SERVICE_ACCOUNT_EMAIL`
- `GOOGLE_PRIVATE_KEY`

## Logging

All operations are logged to `logs/launcher.log`:

- Setup operations
- Service starts/stops
- Errors with stack traces (in dev mode)
- System status checks

View logs from the menu or directly:

```bash
tail -f logs/launcher.log
```

## Service Management

### Background Services

The launcher can manage these background services:

1. **API Server** (FastAPI)

   - Port: 8000 (configurable)
   - Health check: `http://localhost:8000/health`
   - Logs: `logs/api_server.log`

2. **MongoDB** (Docker)

   - Container: `bmc-mongodb`
   - Port: 27017
   - Auto-starts if Docker available

3. **Next.js Dashboard**
   - Development: Port 3000
   - Production: Port 3000
   - Auto-detects directory

### Health Checks

The launcher performs health checks for:

- API server availability
- MongoDB connection
- Next.js server (when running)

## Troubleshooting

### Python Not Found

```bash
# Install Python 3.11+ from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation
```

### Node.js Not Found

```bash
# Install Node.js from https://nodejs.org/
# Or skip Next.js features (they're optional)
```

### Dependencies Installation Fails

```bash
# Try upgrading pip first
python -m pip install --upgrade pip

# Then install requirements
python -m pip install -r requirements.txt
```

### MongoDB Connection Issues

```bash
# Check if Docker is running
docker ps

# Start MongoDB container manually
docker start bmc-mongodb

# Or install MongoDB locally
```

### API Server Won't Start

```bash
# Check if port 8000 is available
netstat -an | grep 8000  # Linux/Mac
netstat -an | findstr 8000  # Windows

# Check logs
cat logs/api_server.log
```

## Migration from Old Scripts

The unified launcher replaces these scripts:

- `run_chatbot.bat` → Use `launch.bat` or `python unified_launcher.py --mode chat`
- `start.sh` → Use `./launch.sh` or `python unified_launcher.py`
- `INICIAR_CHATBOT.bat` → Use `launch.bat`
- `run_chatbot.ps1` → Use `launch.bat` or `python unified_launcher.py`

Old scripts are still available but deprecated. They will show a deprecation notice.

## Examples

### Development Workflow

```bash
# Start full stack for development
python unified_launcher.py --dev --mode fullstack
```

### Production Deployment

```bash
# Setup only
python unified_launcher.py --setup-only

# Start production mode
python unified_launcher.py --production --mode fullstack
```

### Quick Testing

```bash
# Skip setup and run simulator
python unified_launcher.py --skip-setup --mode simulator
```

### API Only

```bash
# Run just the API server
python unified_launcher.py --mode api
```

## File Structure

```
.
├── unified_launcher.py    # Main launcher script
├── launch.bat             # Windows wrapper
├── launch.sh              # Linux/Mac wrapper
├── logs/                  # Log files
│   └── launcher.log      # Main launcher log
└── UNIFIED_LAUNCHER.md   # This documentation
```

## Contributing

When adding new execution modes:

1. Add mode to `show_menu()` method
2. Add mode mapping in `mode_map` dictionary
3. Implement execution logic in `_execute_mode()`
4. Update this documentation

## Support

For issues or questions:

1. Check logs in `logs/launcher.log`
2. Run system status check from menu
3. Verify prerequisites are met
4. Review error messages for specific guidance

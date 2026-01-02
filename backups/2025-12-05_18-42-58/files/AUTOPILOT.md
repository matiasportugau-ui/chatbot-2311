## 🧠 Autopilot – End-to-End Runbook

Use this checklist to spin up every major component without manual guesswork.

### 1. Environment Prep
- Copy credentials into env (they can live in `.env.local` for Next and standard env vars for Python). No `credentials.json` is required—the loaders fall back to environment variables automatically now.
- Export the sensitive vars once (example):
  ```bash
  export OPENAI_API_KEY="sk-..."
  export MONGODB_URI="mongodb://localhost:27017/bmc-cotizaciones"
  export GOOGLE_SHEET_ID="..."
  ```

### 2. Start Python Back-end + Simulator

**Recommended: Unified Launcher (All-in-One)**
```bash
# Start everything together
python unified_launcher.py --mode fullstack
```

**Or use menu:**
```bash
python unified_launcher.py
# Then select option 'a' for Full Stack
```

**Alternative: Manual Setup**
```bash
python -m venv .venv && source .venv/bin/activate      # optional but recommended
pip install -r requirements.txt
python api_server.py                                   # terminal 1
python simulate_chat_cli.py                            # terminal 2 (interactive)
```

> **Note:** The unified launcher (`launch.bat` / `launch.sh`) handles all of this automatically. Legacy scripts (`run_simulation.sh`, `INICIAR_CHATBOT.bat`) still work but are deprecated.

### 3. Start the Next.js Dashboard/API Routes
```bash
./scripts/dev.sh
```
- This script installs dependencies (if needed), bootstraps `.env.local`, and runs `npm run dev`.
- API routes (`src/app/api/*`) now auto-initialize the secure configuration the first time they are hit.

### 4. Optional: Full Simulation Script

**Recommended: Unified Launcher**
```bash
# Windows
launch.bat

# Linux/Mac
./launch.sh

# Or directly
python unified_launcher.py --mode simulator
```

**Legacy: Simulation Script (Deprecated)**
```bash
./run_simulation.sh
```
- ⚠️ **Note:** This script is deprecated. Use unified launcher instead.
- Detects Docker/MongoDB, installs Python deps, configures env, verifies services, and launches `chat_interactivo.py`.

### 5. Health Checks
- FastAPI: `curl http://localhost:8000/health`
- Next.js APIs: `curl http://localhost:3000/api/health`
- MongoDB: `mongosh --eval "db.runCommand({ ping: 1 })"`

Once those pass, the chatbot, dashboard, simulator, and background workflows are ready for QA. No manual wiring beyond the commands above is required.

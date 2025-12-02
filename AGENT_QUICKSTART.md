# ⚡ AGENT QUICK START - Immediate Actions

## 🚦 START HERE

### Step 1: Identify Your Role
Read this first, then go to your section:

| If you are... | Go to Section |
|---------------|---------------|
| Coordinating the team | [ORCHESTRATOR](#orchestrator-quick-start) |
| Working on Python API | [BACKEND](#backend-quick-start) |
| Working on Next.js | [FRONTEND](#frontend-quick-start) |
| Setting up WhatsApp/Sheets | [INTEGRATION](#integration-quick-start) |
| Managing MongoDB | [DATABASE](#database-quick-start) |
| Setting up CI/CD | [DEVOPS](#devops-quick-start) |
| Running tests | [QA](#qa-quick-start) |

---

## 🎯 ORCHESTRATOR Quick Start

```bash
# 1. Check project status
cd /workspace
git status

# 2. Verify main files exist
ls -la AGENT_DEPLOYMENT_PLAN.md AGENT_INSTRUCTIONS.md

# 3. Check for .env file
if [ -f .env ]; then echo "✅ .env exists"; else echo "⚠️ .env MISSING"; fi

# 4. List agents' key files
echo "=== Key Files Status ==="
ls -la api_server.py sistema_final_integrado.py package.json vercel.json Procfile
```

### Your First Task:
1. ✅ Read `AGENT_DEPLOYMENT_PLAN.md`
2. ✅ Assign tasks from Phase 1 table
3. ✅ Create communication channel (comment in this file or create AGENT_STATUS.md)

---

## 🔧 BACKEND Quick Start

```bash
# 1. Go to workspace
cd /workspace

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate it
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Check if .env exists, create if not
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
OPENAI_API_KEY=sk-YOUR-KEY-HERE
MONGODB_URI=mongodb://localhost:27017/bmc
PORT=8000
HOST=0.0.0.0
EOF
    echo "⚠️ Please edit .env with your actual keys!"
fi

# 6. Test the API
python api_server.py &
sleep 3
curl http://localhost:8000/health
```

### Your First Task:
1. ✅ Verify Python 3.10+ is installed
2. ✅ Install dependencies successfully
3. ✅ Get `/health` endpoint working
4. 📢 Report status to ORCHESTRATOR

---

## 🎨 FRONTEND Quick Start

```bash
# 1. Go to workspace
cd /workspace

# 2. Check Node version (need 18+)
node --version

# 3. Install dependencies
npm install

# 4. Check for build errors
npm run build

# 5. If build passes, try dev server
npm run dev
```

### Your First Task:
1. ✅ Verify Node 18+ is installed
2. ✅ Run `npm install` successfully
3. ✅ Run `npm run build` without errors
4. 📢 Report status to ORCHESTRATOR

---

## 🔗 INTEGRATION Quick Start

```bash
# 1. Check integration files exist
cd /workspace
ls -la n8n_integration.py integracion_whatsapp.py integracion_google_sheets.py

# 2. Check n8n workflows
ls n8n_workflows/*.json | head -5

# 3. Check API integration routes
ls -la src/app/api/whatsapp/ src/app/api/sheets/ src/app/api/mercado-libre/

# 4. Verify environment variable placeholders
grep -E "(WHATSAPP|GOOGLE|MERCADO)" .env.example 2>/dev/null || echo "Check .env for integration vars"
```

### Your First Task:
1. ✅ List all integration files
2. ✅ Identify which integrations are configured
3. ✅ Document missing environment variables
4. 📢 Report status to ORCHESTRATOR

---

## 🗄️ DATABASE Quick Start

```bash
# 1. Check MongoDB connection variable
grep MONGODB .env 2>/dev/null || echo "⚠️ MONGODB_URI not in .env"

# 2. Check for data files
ls -la *.json | grep -E "(conocimiento|base)" | head -5

# 3. If MongoDB URI exists, test connection
if grep -q MONGODB_URI .env 2>/dev/null; then
    python3 -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
uri = os.getenv('MONGODB_URI')
if uri:
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        print('✅ MongoDB connection successful!')
    except Exception as e:
        print(f'❌ MongoDB connection failed: {e}')
else:
    print('⚠️ MONGODB_URI not set')
"
fi
```

### Your First Task:
1. ✅ Check if MongoDB URI is configured
2. ✅ Test database connection
3. ✅ List existing data files
4. 📢 Report status to ORCHESTRATOR

---

## 🔄 DEVOPS Quick Start

```bash
# 1. Check CI/CD files
cd /workspace
ls -la .github/workflows/*.yml

# 2. Check deployment configs
ls -la Procfile vercel.json railway.json 2>/dev/null

# 3. Check scripts
ls scripts/*.sh

# 4. Verify git status
git status

# 5. Check current branch
git branch --show-current
```

### Your First Task:
1. ✅ List all workflow files
2. ✅ Verify Procfile exists
3. ✅ Check vercel.json configuration
4. 📢 Report status to ORCHESTRATOR

---

## 🧪 QA Quick Start

```bash
# 1. Check test files
cd /workspace
ls -la tests/ test_scenarios/ 2>/dev/null
ls -la test*.js test*.py 2>/dev/null

# 2. Check if test script exists
ls scripts/test.sh 2>/dev/null || echo "⚠️ No test.sh found"

# 3. Quick smoke test - check if main files parse
python3 -c "import api_server; print('✅ api_server.py parses OK')" 2>/dev/null || echo "❌ api_server.py has errors"
python3 -c "import sistema_final_integrado; print('✅ sistema_final_integrado.py parses OK')" 2>/dev/null || echo "❌ sistema_final_integrado.py has errors"

# 4. Check Node/TypeScript
npm run lint 2>/dev/null || echo "Check npm lint"
```

### Your First Task:
1. ✅ List all test files
2. ✅ Verify Python files parse correctly
3. ✅ Run lint check on frontend
4. 📢 Report status to ORCHESTRATOR

---

## 📊 STATUS REPORTING TEMPLATE

Copy this and fill in for your agent:

```markdown
## 🔄 AGENT STATUS REPORT

**Agent ID:** [AGENT-00X]
**Role:** [Your Role]
**Time:** [Timestamp]

### Completed ✅
- [ ] Task 1
- [ ] Task 2

### In Progress 🔄
- [ ] Current task

### Blocked ⚠️
- Issue: [Description]
- Need: [What you need]

### Next Steps ⏭️
1. [Next action]
2. [After that]

### Notes 📝
[Any additional observations]
```

---

## 🚀 PARALLEL EXECUTION PLAN

Agents can work simultaneously on these independent tasks:

### Wave 1 (All agents, parallel)
```
ORCHESTRATOR: Review plan, setup tracking
BACKEND: Install Python deps, test locally  ──┐
FRONTEND: Install Node deps, test build    ──┤── Can run simultaneously
DATABASE: Test MongoDB connection          ──┤
INTEGRATION: List integration configs      ──┤
DEVOPS: Check CI/CD files                  ──┤
QA: List test files, run lint              ──┘
```

### Wave 2 (After Wave 1)
```
DEVOPS: Setup Railway (depends on BACKEND ✅)
DEVOPS: Setup Vercel (depends on FRONTEND ✅)
DATABASE: Import data (depends on connection ✅)
INTEGRATION: Configure webhooks (depends on DEVOPS ✅)
```

### Wave 3 (After Wave 2)
```
BACKEND: Deploy to Railway
FRONTEND: Deploy to Vercel
QA: Run E2E tests
```

---

## 🎬 LET'S GO!

1. Each agent: Run your Quick Start section above
2. Report status using the template
3. Coordinate with ORCHESTRATOR for next steps

**TIME TO DEPLOY! 🚀**

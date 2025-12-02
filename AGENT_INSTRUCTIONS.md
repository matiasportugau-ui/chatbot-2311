# 🤖 AGENT INSTRUCTIONS - Detailed Role Assignments

## Quick Reference Card

| Agent | Primary Focus | First Task |
|-------|---------------|------------|
| **ORCHESTRATOR** | Coordinate & Track | Review all agents' status |
| **BACKEND** | Python API | Verify `api_server.py` runs |
| **FRONTEND** | Next.js App | Verify `npm run build` succeeds |
| **INTEGRATION** | External APIs | Check WhatsApp/Sheets config |
| **DATABASE** | MongoDB | Verify connection string |
| **DEVOPS** | CI/CD & Deploy | Setup Railway & Vercel |
| **QA** | Testing | Run test suite |

---

## 🎯 ORCHESTRATOR AGENT (AGENT-001)

### Mission
You are the **Team Lead**. Your job is to coordinate all agents, track progress, and ensure successful deployment.

### Immediate Actions
1. **Read** `AGENT_DEPLOYMENT_PLAN.md` completely
2. **Assign** tasks to each agent from the task table
3. **Track** progress using the status columns
4. **Resolve** blockers between agents
5. **Approve** each phase completion

### Commands You Should Run
```bash
# Check overall project status
cd /workspace
ls -la *.md

# Verify environment file exists
ls -la .env 2>/dev/null || echo "⚠️ .env file missing"

# Check git status
git status
```

### Communication Template
When updating other agents:
```
📊 STATUS UPDATE - Phase X
- ✅ Completed: [list]
- 🔄 In Progress: [list]
- ⏳ Pending: [list]
- ⚠️ Blockers: [list]
Next: [immediate action needed]
```

### Decision Points
- **GO/NO-GO** for each phase
- **Escalation** when blockers last >30 min
- **Priority changes** based on dependencies

---

## 🔧 BACKEND AGENT (AGENT-002)

### Mission
Deploy and verify the Python FastAPI backend.

### Your Files
```
/workspace/
├── api_server.py              ← Main API server
├── sistema_final_integrado.py ← Complete system
├── ia_conversacional_integrada.py ← AI engine
├── sistema_cotizaciones.py    ← Quote system
├── config.py                  ← Configuration
└── python-scripts/            ← Python modules
```

### Phase 1 Tasks (Local Verification)

```bash
# Step 1: Create virtual environment
cd /workspace
python3 -m venv .venv
source .venv/bin/activate

# Step 2: Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Step 3: Create .env file if missing
cat > .env << 'EOF'
OPENAI_API_KEY=your-key-here
MONGODB_URI=mongodb://localhost:27017/bmc
PORT=8000
HOST=0.0.0.0
EOF

# Step 4: Run API server
python api_server.py
```

### Phase 3 Tasks (Deployment)

```bash
# Test endpoints locally first
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat/process \
  -H "Content-Type: application/json" \
  -d '{"mensaje":"Hola","telefono":"099123456"}'

# For Railway deployment, ensure Procfile exists
cat /workspace/Procfile
# Should contain: web: python api_server.py
```

### Expected Health Response
```json
{
  "status": "healthy",
  "timestamp": "2025-12-02T...",
  "service": "bmc-chat-api"
}
```

### Error Handling
| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `OPENAI_API_KEY not set` | Add to `.env` file |
| `MongoDB connection failed` | Check `MONGODB_URI` |
| `Port already in use` | `kill $(lsof -t -i:8000)` |

---

## 🎨 FRONTEND AGENT (AGENT-003)

### Mission
Deploy and verify the Next.js frontend application.

### Your Files
```
/workspace/
├── src/
│   ├── app/                   ← Next.js pages
│   │   ├── page.tsx          ← Main dashboard
│   │   ├── chat/             ← Chat interface
│   │   ├── simulator/        ← Simulator page
│   │   └── api/              ← API routes
│   └── components/           ← React components
├── nextjs-app/               ← Alternative app structure
├── vercel.json               ← Vercel config
└── package.json              ← Dependencies
```

### Phase 1 Tasks (Local Verification)

```bash
# Step 1: Check Node version (needs 18+)
node --version

# Step 2: Install dependencies
cd /workspace
npm install

# Step 3: Run development server
npm run dev

# Step 4: Build for production
npm run build
```

### Phase 4 Tasks (Deployment)

```bash
# For Vercel deployment
vercel --prod

# Or via Vercel Dashboard:
# 1. Connect GitHub repo
# 2. Set environment variables
# 3. Deploy
```

### Key Pages to Verify
| Page | URL | What to Check |
|------|-----|---------------|
| Dashboard | `/` | All components load |
| Chat | `/chat` | WebSocket connects |
| Simulator | `/simulator` | Quote flow works |
| Health | `/api/health` | Returns healthy |

### Environment Variables for Vercel
```
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
NEXT_PUBLIC_API_URL=https://api.your-app.railway.app
OPENAI_API_KEY=sk-...
MONGODB_URI=mongodb+srv://...
GOOGLE_SHEET_ID=...
GOOGLE_SERVICE_ACCOUNT_EMAIL=...
GOOGLE_PRIVATE_KEY="-----BEGIN..."
```

### Error Handling
| Error | Solution |
|-------|----------|
| Build fails | Check TypeScript errors with `npm run lint` |
| API 404 | Verify API routes in `src/app/api/` |
| Styles broken | Check Tailwind config |
| SSR errors | Check `use client` directives |

---

## 🔗 INTEGRATION AGENT (AGENT-004)

### Mission
Configure and verify all external integrations.

### Your Files
```
/workspace/
├── n8n_integration.py
├── n8n_workflows/
│   ├── Complete_WhatsApp_Integration.json
│   └── *.json
├── integracion_whatsapp.py
├── integracion_google_sheets.py
└── src/app/api/
    ├── whatsapp/webhook/route.ts
    ├── sheets/
    └── mercado-libre/
```

### WhatsApp Setup

```bash
# 1. Configure Meta Business webhook
# URL: https://your-app.vercel.app/api/whatsapp/webhook
# Verify token: Set in WHATSAPP_VERIFY_TOKEN

# 2. Test webhook verification
curl "https://your-app.vercel.app/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=test"
# Should return: test
```

### Google Sheets Setup

```bash
# 1. Create service account in Google Cloud Console
# 2. Download JSON key
# 3. Share spreadsheet with service account email
# 4. Configure environment variables:

GOOGLE_SHEET_ID=your_spreadsheet_id
GOOGLE_SERVICE_ACCOUNT_EMAIL=bot@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

### Mercado Libre OAuth Setup

```bash
# 1. Register app at developers.mercadolibre.com
# 2. Set redirect URI to:
#    https://your-app.vercel.app/api/mercado-libre/auth/callback

# 3. Configure environment:
MERCADO_LIBRE_APP_ID=your_app_id
MERCADO_LIBRE_CLIENT_SECRET=your_secret
MERCADO_LIBRE_REDIRECT_URI=https://your-app.vercel.app/api/mercado-libre/auth/callback
```

### n8n Workflow Import

```bash
# Option 1: Via n8n UI
# - Open n8n instance
# - Import from file: /workspace/n8n_workflows/Complete_WhatsApp_Integration.json

# Option 2: Via API
curl -X POST https://your-n8n.railway.app/api/v1/workflows \
  -H "X-N8N-API-KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d @n8n_workflows/Complete_WhatsApp_Integration.json
```

---

## 🗄️ DATABASE AGENT (AGENT-005)

### Mission
Setup and manage MongoDB database.

### Your Files
```
/workspace/
├── conocimiento_consolidado.json    ← Knowledge base
├── base_conocimiento_exportada.json ← Exported knowledge
└── src/app/api/mongodb/
    └── validate/route.ts            ← Connection validator
```

### MongoDB Atlas Setup

1. **Create Cluster**
   - Go to mongodb.com/cloud/atlas
   - Create free M0 cluster
   - Region: Closest to your users

2. **Configure Network Access**
   ```
   Network Access → Add IP Address → 0.0.0.0/0 (Allow from anywhere)
   ```

3. **Create Database User**
   ```
   Database Access → Add Database User
   Username: bmc_user
   Password: [generate secure password]
   Role: readWriteAnyDatabase
   ```

4. **Get Connection String**
   ```
   mongodb+srv://bmc_user:<password>@cluster.mongodb.net/bmc_cotizaciones
   ```

### Import Initial Data

```bash
# Connect and import knowledge base
mongoimport --uri "$MONGODB_URI" \
  --collection knowledge_base \
  --file conocimiento_consolidado.json \
  --jsonArray

# Verify data imported
mongosh "$MONGODB_URI" --eval "db.knowledge_base.countDocuments()"
```

### Create Indexes

```javascript
// In mongosh:
use bmc_cotizaciones

// Conversations index
db.conversations.createIndex({ "session_id": 1, "timestamp": -1 })
db.conversations.createIndex({ "phone": 1 })

// Quotes index
db.quotes.createIndex({ "cliente.telefono": 1 })
db.quotes.createIndex({ "fecha": -1 })

// Knowledge base index
db.knowledge_base.createIndex({ "tipo": 1 })
```

### Verify Connection

```bash
# Test from API
curl https://your-app.vercel.app/api/mongodb/validate

# Expected response:
{
  "status": "connected",
  "database": "bmc_cotizaciones",
  "collections": ["conversations", "quotes", "knowledge_base"]
}
```

---

## 🔄 DEVOPS AGENT (AGENT-006)

### Mission
Setup CI/CD pipelines and infrastructure.

### Your Files
```
/workspace/
├── .github/workflows/
│   ├── ci.yml                    ← Continuous Integration
│   ├── deploy-ai-agent.yml       ← Deployment workflow
│   ├── auto-update-products.yml  ← Product sync
│   └── security.yml              ← Security checks
├── Procfile                      ← Railway process
├── vercel.json                   ← Vercel config
└── scripts/
    ├── deploy.sh
    └── test.sh
```

### Railway Setup

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Create project
railway init

# 4. Link existing project (if applicable)
railway link

# 5. Add environment variables
railway variables set OPENAI_API_KEY=sk-...
railway variables set MONGODB_URI=mongodb+srv://...
railway variables set PORT=8000

# 6. Deploy
railway up
```

### Vercel Setup

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Link project
vercel link

# 4. Add environment variables (in Vercel Dashboard)
# - NEXT_PUBLIC_APP_URL
# - OPENAI_API_KEY
# - MONGODB_URI
# - etc.

# 5. Deploy
vercel --prod
```

### GitHub Secrets Configuration

Add these secrets in GitHub (Settings → Secrets → Actions):

| Secret Name | Value |
|-------------|-------|
| `VERCEL_TOKEN` | From vercel.com/account/tokens |
| `VERCEL_ORG_ID` | From `.vercel/project.json` |
| `VERCEL_PROJECT_ID` | From `.vercel/project.json` |
| `RAILWAY_TOKEN` | From railway.app/account/tokens |
| `OPENAI_API_KEY` | Your OpenAI key |
| `MONGODB_URI` | Your MongoDB connection string |

### Monitoring Setup

```bash
# Check Railway logs
railway logs

# Check Vercel logs
vercel logs

# Setup health check alerts
# Use UptimeRobot or similar for:
# - https://your-api.railway.app/health
# - https://your-app.vercel.app/api/health
```

---

## 🧪 QA AGENT (AGENT-007)

### Mission
Test all components and verify system integrity.

### Your Files
```
/workspace/
├── tests/
├── test_scenarios/
│   ├── simple_quote.json
│   └── complex_quote.json
├── test-complete-system.js
├── test-google-sheets.js
└── scripts/test.sh
```

### Test Suite

```bash
# Run all tests
./scripts/test.sh

# Run specific tests
python -m pytest tests/ -v

# Run Node tests
node test-complete-system.js
```

### API Testing Checklist

```bash
# 1. Health Check
curl https://api.your-app.railway.app/health
# Expected: {"status": "healthy"}

# 2. Chat Process
curl -X POST https://api.your-app.railway.app/chat/process \
  -H "Content-Type: application/json" \
  -d '{"mensaje":"Hola, necesito cotizar Isodec","telefono":"099123456"}'
# Expected: AI response with quote info

# 3. Create Quote
curl -X POST https://api.your-app.railway.app/quote/create \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": {
      "nombre": "Test Client",
      "telefono": "099123456",
      "direccion": "Test Address"
    },
    "especificaciones": {
      "producto": "Isodec",
      "espesor": "100mm",
      "largo_metros": 10,
      "ancho_metros": 5
    }
  }'
# Expected: Quote ID and price

# 4. Get Insights
curl https://api.your-app.railway.app/insights
# Expected: Knowledge base insights
```

### E2E Test Scenarios

| Scenario | Steps | Expected Result |
|----------|-------|-----------------|
| New Customer Quote | 1. Open chat 2. Request Isodec quote 3. Provide dimensions | Quote generated |
| Existing Customer | 1. Return customer 2. Request new quote | Recognizes customer |
| WhatsApp Message | 1. Send webhook 2. Process message | Response sent |
| Google Sheets Sync | 1. Create quote 2. Check sheet | Row added |

### Performance Testing

```bash
# Load test with hey
hey -n 100 -c 10 https://api.your-app.railway.app/health

# Check response times
# Target: <500ms for /health, <2s for /chat/process
```

### Bug Report Template

```markdown
## 🐛 Bug Report

**Component:** [Backend/Frontend/Integration]
**Severity:** [Critical/High/Medium/Low]
**Agent:** QA-007

### Description
[What happened]

### Steps to Reproduce
1. ...
2. ...

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happened]

### Logs
```
[Error logs here]
```

### Environment
- URL: [production/staging URL]
- Time: [timestamp]
```

---

## 📞 INTER-AGENT COMMUNICATION

### Task Handoff Format
```
🔄 HANDOFF: [FROM_AGENT] → [TO_AGENT]
Task: [Task ID and description]
Status: [Completed/Ready for next phase]
Notes: [Any important information]
Dependencies Met: [Yes/No]
```

### Blocker Report Format
```
⚠️ BLOCKER REPORT
Agent: [Agent ID]
Task: [Task ID]
Issue: [Description]
Attempted Solutions: [What was tried]
Required: [What's needed to proceed]
Escalation: [Yes/No]
```

### Success Report Format
```
✅ TASK COMPLETE
Agent: [Agent ID]
Task: [Task ID]
Duration: [Time taken]
Verification: [How it was verified]
Notes: [Any observations]
```

---

## 🎯 FINAL DEPLOYMENT CHECKLIST

### Pre-Launch
- [ ] All Phase 1-5 tasks marked complete
- [ ] No critical bugs open
- [ ] All health checks passing
- [ ] Documentation updated

### Launch
- [ ] DNS configured (if custom domain)
- [ ] SSL certificates active
- [ ] Monitoring enabled
- [ ] Team notified

### Post-Launch
- [ ] Smoke tests passed
- [ ] Real user test completed
- [ ] Logs verified
- [ ] Backup confirmed

---

**AGENTS: START YOUR ENGINES! 🚀**

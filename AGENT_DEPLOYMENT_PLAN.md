# 🚀 AGENT DEPLOYMENT PLAN - BMC Cotización Inteligente

## Phase 0: Orchestration Review & Team Setup

**Date:** December 2, 2025  
**Project:** BMC Uruguay Intelligent Quote System  
**Status:** READY FOR DEPLOYMENT

---

## 📊 System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BMC COTIZACIÓN INTELIGENTE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   FRONTEND   │───▶│   BACKEND    │───▶│   DATABASE   │                   │
│  │   Next.js    │    │   FastAPI    │    │   MongoDB    │                   │
│  │   Vercel     │    │   Railway    │    │   Atlas      │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│         │                   │                   │                           │
│         ▼                   ▼                   ▼                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   CHAT UI    │    │   AI ENGINE  │    │  INTEGRATIONS│                   │
│  │   Dashboard  │    │   OpenAI     │    │  WhatsApp    │                   │
│  │   Simulator  │    │   NLP        │    │  Sheets      │                   │
│  └──────────────┘    └──────────────┘    │  MercadoLibre│                   │
│                                          └──────────────┘                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │                    AUTOMATION LAYER                              │        │
│  │   GitHub Actions │ n8n Workflows │ Background Agent             │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 👥 AGENT TEAM ORGANIZATION

### 🎯 **ORCHESTRATOR AGENT** (Team Lead)
**Role:** `AGENT-ORCHESTRATOR-001`  
**Responsibilities:**
- Coordinate all other agents
- Track progress across all tasks
- Handle blockers and escalations
- Ensure quality standards
- Final deployment approval

**Key Files:**
- `/workspace/AGENT_DEPLOYMENT_PLAN.md` (this file)
- All status tracking documents

---

### 🔧 **BACKEND AGENT** 
**Role:** `AGENT-BACKEND-002`  
**Responsibilities:**
- Python API deployment (`api_server.py`)
- Sistema integrado (`sistema_final_integrado.py`)
- IA conversacional module
- Quote engine system
- Health checks & monitoring

**Key Files:**
- `/workspace/api_server.py`
- `/workspace/sistema_final_integrado.py`
- `/workspace/ia_conversacional_integrada.py`
- `/workspace/sistema_cotizaciones.py`
- `/workspace/python-scripts/*`

**Environment Variables Required:**
```bash
OPENAI_API_KEY=sk-...
MONGODB_URI=mongodb+srv://...
PORT=8000
HOST=0.0.0.0
```

---

### 🎨 **FRONTEND AGENT**
**Role:** `AGENT-FRONTEND-003`  
**Responsibilities:**
- Next.js application deployment
- Chat interface components
- Dashboard components
- UI/UX optimizations
- Vercel configuration

**Key Files:**
- `/workspace/src/app/*`
- `/workspace/src/components/*`
- `/workspace/nextjs-app/*`
- `/workspace/vercel.json`

**Environment Variables Required:**
```bash
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
NEXT_PUBLIC_API_URL=https://api.your-app.com
```

---

### 🔗 **INTEGRATION AGENT**
**Role:** `AGENT-INTEGRATION-004`  
**Responsibilities:**
- WhatsApp Business API setup
- Google Sheets synchronization
- Mercado Libre OAuth & webhooks
- n8n workflow automation
- External API connections

**Key Files:**
- `/workspace/n8n_integration.py`
- `/workspace/n8n_workflows/*`
- `/workspace/integracion_whatsapp.py`
- `/workspace/integracion_google_sheets.py`
- `/workspace/src/app/api/mercado-libre/*`

**Environment Variables Required:**
```bash
# WhatsApp
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_VERIFY_TOKEN=...

# Google Sheets
GOOGLE_SHEET_ID=...
GOOGLE_SERVICE_ACCOUNT_EMAIL=...
GOOGLE_PRIVATE_KEY="..."

# Mercado Libre
MERCADO_LIBRE_APP_ID=...
MERCADO_LIBRE_CLIENT_SECRET=...
MERCADO_LIBRE_REDIRECT_URI=...
```

---

### 🗄️ **DATABASE AGENT**
**Role:** `AGENT-DATABASE-005`  
**Responsibilities:**
- MongoDB Atlas setup
- Data migration
- Index optimization
- Backup configuration
- Connection pooling

**Key Files:**
- `/workspace/src/app/api/mongodb/*`
- `/workspace/conocimiento_consolidado.json`
- `/workspace/base_conocimiento_exportada.json`

**Environment Variables Required:**
```bash
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/bmc
```

---

### 🔄 **DEVOPS AGENT**
**Role:** `AGENT-DEVOPS-006`  
**Responsibilities:**
- GitHub Actions workflows
- CI/CD pipelines
- Monitoring & logging
- Security hardening
- Performance optimization

**Key Files:**
- `/workspace/.github/workflows/*`
- `/workspace/scripts/*`
- `/workspace/Procfile`
- `/workspace/vercel.json`

---

### 🧪 **QA AGENT**
**Role:** `AGENT-QA-007`  
**Responsibilities:**
- End-to-end testing
- API testing
- Integration testing
- Performance testing
- Bug reporting & tracking

**Key Files:**
- `/workspace/tests/*`
- `/workspace/test_scenarios/*`
- `/workspace/scripts/test.sh`

---

## 📋 DEPLOYMENT TASKS BREAKDOWN

### 🟢 **PHASE 1: Pre-Deployment Verification** (Priority: CRITICAL)

| Task ID | Task Description | Assigned Agent | Status | Dependencies |
|---------|-----------------|----------------|--------|--------------|
| T1.1 | Verify all environment variables | ORCHESTRATOR | ⏳ PENDING | None |
| T1.2 | Test Python backend locally | BACKEND | ⏳ PENDING | T1.1 |
| T1.3 | Test Next.js frontend locally | FRONTEND | ⏳ PENDING | T1.1 |
| T1.4 | Verify MongoDB connection | DATABASE | ⏳ PENDING | T1.1 |
| T1.5 | Validate API integrations | INTEGRATION | ⏳ PENDING | T1.2, T1.4 |
| T1.6 | Run test suite | QA | ⏳ PENDING | T1.2, T1.3 |

---

### 🟡 **PHASE 2: Infrastructure Setup** (Priority: HIGH)

| Task ID | Task Description | Assigned Agent | Status | Dependencies |
|---------|-----------------|----------------|--------|--------------|
| T2.1 | Setup MongoDB Atlas cluster | DATABASE | ⏳ PENDING | T1.4 |
| T2.2 | Configure Railway project | DEVOPS | ⏳ PENDING | T2.1 |
| T2.3 | Configure Vercel project | DEVOPS | ⏳ PENDING | None |
| T2.4 | Setup GitHub secrets | DEVOPS | ⏳ PENDING | T2.2, T2.3 |
| T2.5 | Configure n8n instance | INTEGRATION | ⏳ PENDING | T2.2 |

---

### 🟠 **PHASE 3: Backend Deployment** (Priority: HIGH)

| Task ID | Task Description | Assigned Agent | Status | Dependencies |
|---------|-----------------|----------------|--------|--------------|
| T3.1 | Deploy Python API to Railway | BACKEND | ⏳ PENDING | T2.2, T2.4 |
| T3.2 | Verify /health endpoint | BACKEND | ⏳ PENDING | T3.1 |
| T3.3 | Test /chat/process endpoint | BACKEND | ⏳ PENDING | T3.2 |
| T3.4 | Test /quote/create endpoint | BACKEND | ⏳ PENDING | T3.2 |
| T3.5 | Verify MongoDB connectivity | DATABASE | ⏳ PENDING | T3.1 |
| T3.6 | Import initial knowledge base | DATABASE | ⏳ PENDING | T3.5 |

---

### 🔵 **PHASE 4: Frontend Deployment** (Priority: HIGH)

| Task ID | Task Description | Assigned Agent | Status | Dependencies |
|---------|-----------------|----------------|--------|--------------|
| T4.1 | Deploy Next.js to Vercel | FRONTEND | ⏳ PENDING | T2.3, T2.4 |
| T4.2 | Verify main dashboard | FRONTEND | ⏳ PENDING | T4.1 |
| T4.3 | Test chat interface | FRONTEND | ⏳ PENDING | T4.1, T3.3 |
| T4.4 | Test simulator page | FRONTEND | ⏳ PENDING | T4.1 |
| T4.5 | Verify API connections | FRONTEND | ⏳ PENDING | T3.2, T4.1 |

---

### 🟣 **PHASE 5: Integration Testing** (Priority: MEDIUM)

| Task ID | Task Description | Assigned Agent | Status | Dependencies |
|---------|-----------------|----------------|--------|--------------|
| T5.1 | Test WhatsApp webhook | INTEGRATION | ⏳ PENDING | T3.1 |
| T5.2 | Test Google Sheets sync | INTEGRATION | ⏳ PENDING | T3.1 |
| T5.3 | Configure Mercado Libre OAuth | INTEGRATION | ⏳ PENDING | T3.1 |
| T5.4 | Import n8n workflows | INTEGRATION | ⏳ PENDING | T2.5 |
| T5.5 | End-to-end quote flow test | QA | ⏳ PENDING | T4.3, T5.2 |
| T5.6 | Full system integration test | QA | ⏳ PENDING | T5.1-T5.5 |

---

### ⚪ **PHASE 6: Production Readiness** (Priority: MEDIUM)

| Task ID | Task Description | Assigned Agent | Status | Dependencies |
|---------|-----------------|----------------|--------|--------------|
| T6.1 | Configure custom domain | DEVOPS | ⏳ PENDING | T4.5 |
| T6.2 | Setup SSL certificates | DEVOPS | ⏳ PENDING | T6.1 |
| T6.3 | Enable GitHub Actions CI/CD | DEVOPS | ⏳ PENDING | T2.4 |
| T6.4 | Configure monitoring/alerts | DEVOPS | ⏳ PENDING | T3.1, T4.1 |
| T6.5 | Document API endpoints | ORCHESTRATOR | ⏳ PENDING | T3.4, T4.5 |
| T6.6 | Final security review | DEVOPS | ⏳ PENDING | T6.1-T6.4 |

---

## 🎯 CRITICAL PATH

```
┌─────────────────────────────────────────────────────────────────────────┐
│ CRITICAL PATH TO PRODUCTION                                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   [T1.1] Verify Env → [T2.1] MongoDB → [T2.2] Railway → [T3.1] Deploy  │
│                            │              │               Backend      │
│                            ▼              ▼                  │         │
│   [T1.3] Test Frontend → [T2.3] Vercel → [T4.1] Deploy ─────────┐     │
│                                           Frontend              │      │
│                                              │                  │      │
│                                              ▼                  ▼      │
│                                        [T5.5] E2E Test → [T6.6] Go Live│
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ QUICK START COMMANDS

### For Backend Agent:
```bash
# Test locally
cd /workspace
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python api_server.py

# Verify health
curl http://localhost:8000/health
```

### For Frontend Agent:
```bash
# Test locally
cd /workspace/nextjs-app
npm install
npm run dev

# Build for production
npm run build
```

### For DevOps Agent:
```bash
# Deploy to Railway
railway up

# Deploy to Vercel
vercel --prod
```

### For QA Agent:
```bash
# Run tests
./scripts/test.sh

# E2E test
node test-complete-system.js
```

---

## 📊 SUCCESS CRITERIA

### Phase 1 Complete When:
- [ ] All environment variables verified
- [ ] Local tests pass (Python & Node)
- [ ] MongoDB connection confirmed
- [ ] No critical errors in logs

### Phase 2 Complete When:
- [ ] Railway project created with env vars
- [ ] Vercel project created with env vars
- [ ] GitHub secrets configured
- [ ] MongoDB Atlas accessible

### Phase 3 Complete When:
- [ ] `/health` returns `{"status": "healthy"}`
- [ ] `/chat/process` responds correctly
- [ ] `/quote/create` works end-to-end
- [ ] MongoDB receiving data

### Phase 4 Complete When:
- [ ] Dashboard loads at production URL
- [ ] Chat interface connects to backend
- [ ] Simulator works correctly
- [ ] No console errors

### Phase 5 Complete When:
- [ ] WhatsApp messages processed
- [ ] Google Sheets syncing
- [ ] Mercado Libre OAuth works
- [ ] Full quote flow tested

### Phase 6 Complete When:
- [ ] Custom domain working
- [ ] SSL active (HTTPS)
- [ ] CI/CD pipeline active
- [ ] Monitoring active
- [ ] Documentation complete

---

## 🚨 ESCALATION PROTOCOL

### Level 1: Agent Self-Resolution
- Agent attempts to resolve within scope
- Documents solution for team

### Level 2: Cross-Agent Collaboration
- Agent requests help from related agent
- Shared debugging session

### Level 3: Orchestrator Intervention
- Orchestrator takes over coordination
- May reassign tasks or pause deployment

### Level 4: External Escalation
- Requires human intervention
- Platform support (Railway, Vercel, MongoDB)

---

## 📅 ESTIMATED TIMELINE

| Phase | Duration | Start | End |
|-------|----------|-------|-----|
| Phase 1: Verification | 2-3 hours | Day 1 | Day 1 |
| Phase 2: Infrastructure | 2-3 hours | Day 1 | Day 1 |
| Phase 3: Backend Deploy | 1-2 hours | Day 1 | Day 1 |
| Phase 4: Frontend Deploy | 1-2 hours | Day 1 | Day 1 |
| Phase 5: Integration | 3-4 hours | Day 1-2 | Day 2 |
| Phase 6: Production | 2-3 hours | Day 2 | Day 2 |

**Total Estimated Time:** 12-18 hours (1-2 working days)

---

## ✅ READY TO START

### Pre-Flight Checklist:
- [ ] All agents have read this document
- [ ] Environment variables documented
- [ ] Access credentials confirmed
- [ ] Communication channels established
- [ ] Backup plan understood

### GO/NO-GO Decision:
- **Orchestrator Approval:** ⏳ PENDING
- **Backend Ready:** ⏳ PENDING
- **Frontend Ready:** ⏳ PENDING
- **Database Ready:** ⏳ PENDING
- **Integrations Ready:** ⏳ PENDING

---

## 📝 AGENT ASSIGNMENT CONFIRMATION

| Agent Role | Assigned | Confirmed | Ready |
|------------|----------|-----------|-------|
| ORCHESTRATOR | AGENT-001 | ⏳ | ⏳ |
| BACKEND | AGENT-002 | ⏳ | ⏳ |
| FRONTEND | AGENT-003 | ⏳ | ⏳ |
| INTEGRATION | AGENT-004 | ⏳ | ⏳ |
| DATABASE | AGENT-005 | ⏳ | ⏳ |
| DEVOPS | AGENT-006 | ⏳ | ⏳ |
| QA | AGENT-007 | ⏳ | ⏳ |

---

**Document Version:** 1.0  
**Last Updated:** December 2, 2025  
**Status:** READY FOR TEAM DEPLOYMENT

---

## 🎬 LET'S DEPLOY! 🚀

```
    ____  __  __  ______   __  __  ____   __  __  _____  __  __  ___  __  __ 
   / __ )/ / / / / ____/  / / / / / __ \ / / / / / ___/ / / / / /   |/  |/  |
  / __  / /_/ / / /      / / / / / /_/ // / / / / __ \ / /_/ / / /| / /|_/ / 
 / /_/ / __  / / /___   / /_/ / / _, _// /_/ / / /_/ // __  / / ___ / /  / /  
/_____/_/ /_/  \____/   \____/ /_/ |_| \____/  \____//_/ /_/ /_/  |_/_/  /_/   
                                                                              
                    DEPLOYMENT READY - ALL AGENTS STANDBY
```

# 🗺️ Workspace Visual Summary - Complete Architecture

**Quick visual reference for the BMC Chatbot workspace architecture**  
**Status:** ✅ **100% COMPLETE**

---

## 🏗️ Complete System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACES                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Next.js      │  │ WhatsApp     │  │ Chat CLI     │  │ Simulator    │  │
│  │ Dashboard    │  │ Business API │  │ Interface    │  │              │  │
│  │ (Port 3000)  │  │              │  │              │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │                │           │
│         └─────────────────┴──────────────────┴────────────────┘           │
│                            │                                                │
│                            ▼                                                │
└────────────────────────────┼────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DUAL API GATEWAY LAYER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────┐  ┌────────────────────────────────┐ │
│  │  FastAPI Server                  │  │  Next.js API Routes              │ │
│  │  (api_server.py)                 │  │  /api/* (25 endpoints)           │ │
│  │  Port: 8000                      │  │                                  │ │
│  │                                  │  │  • /api/chat/stream             │ │
│  │  Endpoints:                      │  │  • /api/quote-engine            │ │
│  │  • POST /chat/process            │  │  • /api/integrated-quote         │ │
│  │  • POST /quote/create            │  │  • /api/sheets/*                 │ │
│  │  • GET  /health                 │  │  • /api/mercado-libre/*          │ │
│  │  • GET  /insights                │  │  • /api/whatsapp/webhook         │ │
│  │                                  │  │  • /api/search                  │ │
│  │                                  │  │  • /api/export, /api/import     │ │
│  │                                  │  │  • /api/settings, notifications │ │
│  │                                  │  │  • /api/recovery                 │ │
│  └──────────────────────────────────┘  └────────────────────────────────┘ │
│                                                                              │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AI PROCESSING ENGINE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │         IA Conversacional Integrada                                   │  │
│  │         (ia_conversacional_integrada.py)                              │  │
│  │                                                                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │  │
│  │  │ OpenAI GPT-4 │  │   Pattern    │  │   Language   │             │  │
│  │  │ Integration  │  │  Matching    │  │  Processor   │             │  │
│  │  │  (Primary)   │  │  (Fallback)  │  │  (NLP)       │             │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Knowledge    │    │  Quote        │    │  Context      │
│  Base         │    │  System       │    │  Manager      │
│               │    │               │    │               │
│  • Dynamic    │    │  • Pricing    │    │  • Sessions   │
│  • Learning   │    │  • Products    │    │  • History    │
│  • Patterns   │    │  • Clients    │    │  • State      │
└───────────────┘    └───────────────┘    └───────────────┘
        │                       │                       │
        └───────────────────────┴───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   MongoDB Database     │
                    │   (10 Collections)    │
                    │                        │
                    │  • conversations      │
                    │  • quotes             │
                    │  • sessions           │
                    │  • context            │
                    │  • products           │
                    │  • analytics          │
                    │  • settings           │
                    │  • notifications      │
                    │  • search_history     │
                    │  • mercado_libre_grants│
                    └───────────────────────┘
```

---

## 📦 Complete Module Organization Tree

```
workspace/
│
├── 🐍 CORE PYTHON BACKEND (35+ files)
│   ├── AI Engine
│   │   ├── ia_conversacional_integrada.py ⭐ CORE
│   │   ├── base_conocimiento_dinamica.py ⭐ CORE
│   │   ├── motor_analisis_conversiones.py
│   │   └── language_processor.py
│   │
│   ├── Quote System
│   │   ├── sistema_cotizaciones.py ⭐ CORE
│   │   └── utils_cotizaciones.py
│   │
│   ├── API Server
│   │   └── api_server.py ⭐ CORE
│   │
│   ├── Tools & Testing
│   │   ├── chat_interactivo.py
│   │   ├── simulate_chat_cli.py
│   │   └── test_drive_chatbot.py
│   │
│   └── Learning & Feedback
│       ├── learning_engine.py
│       ├── learning_pipeline.py
│       └── feedback_collector.py
│
├── ⚛️ NEXT.JS FRONTEND (60+ files)
│   ├── Pages
│   │   ├── src/app/page.tsx (Dashboard)
│   │   ├── src/app/chat/page.tsx
│   │   ├── src/app/chat-evolved/page.tsx
│   │   ├── src/app/bmc-chat/page.tsx
│   │   └── src/app/simulator/page.tsx
│   │
│   ├── Components
│   │   ├── src/components/chat/*.tsx (3 files)
│   │   ├── src/components/dashboard/*.tsx (20+ files)
│   │   └── src/components/ui/*.tsx (7 files)
│   │
│   └── API Routes (25 endpoints)
│       ├── src/app/api/chat/stream/route.ts ⭐ MAIN
│       ├── src/app/api/quote-engine/route.ts
│       ├── src/app/api/integrated-quote/route.ts
│       ├── src/app/api/sheets/*/route.ts (2 files)
│       ├── src/app/api/mercado-libre/*/route.ts (6 files)
│       ├── src/app/api/whatsapp/webhook/route.ts
│       ├── src/app/api/search/route.ts
│       ├── src/app/api/export/route.ts
│       ├── src/app/api/import/route.ts
│       ├── src/app/api/settings/route.ts
│       ├── src/app/api/notifications/route.ts
│       ├── src/app/api/trends/route.ts
│       ├── src/app/api/analytics/quotes/route.ts
│       ├── src/app/api/recovery/route.ts
│       └── src/app/api/health/route.ts
│
├── 📥 DATA INGESTION (15+ files)
│   ├── python-scripts/fetch_shopify_products.py
│   ├── python-scripts/fetch_mercadolibre_questions.py
│   ├── consolidar_conocimiento.py
│   └── conocimiento_consolidado.json ⭐ MAIN KNOWLEDGE
│
├── 🔧 AUTOMATION SCRIPTS (30+ files)
│   ├── scripts/refresh_knowledge.sh ⭐ MAIN
│   ├── scripts/run_full_stack.sh
│   ├── start_chatbot.sh
│   └── scripts/recover_conversations.py
│
├── 🔄 N8N WORKFLOWS (12+ files)
│   └── n8n_workflows/workflow-whatsapp-complete.json
│
├── ⚙️ CONFIGURATION (25+ files)
│   ├── config_conocimiento.json
│   ├── matriz_precios.json
│   ├── env.example
│   └── docker-compose.yml
│
└── 📚 DOCUMENTATION (50+ files)
    ├── README.md
    ├── DEPLOYMENT_GUIDE.md
    └── TROUBLESHOOTING_GUIDE.md
```

---

## 🔄 Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION FLOW                                   │
└─────────────────────────────────────────────────────────────────────────┘

External Sources:
  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐
  │  Shopify    │  │ Mercado Libre│  │  WhatsApp   │  │ Google Sheets│
  │  API        │  │  API          │  │  Exports    │  │  API         │
  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                │                  │                  │
         ▼                ▼                  ▼                  ▼
  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐
  │ fetch_      │  │ fetch_       │  │ fetch_      │  │ Next.js API  │
  │ shopify_    │  │ mercadolibre │  │ whatsapp_   │  │ /api/sheets  │
  │ products.py │  │ _questions.py│  │ chats.py    │  │              │
  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                │                  │                  │
         └────────────────┴──────────────────┴──────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ consolidar_           │
              │ conocimiento.py       │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ conocimiento_          │ ⭐ MAIN FILE
              │ consolidado.json       │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ validar_integracion.py │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Loaded by AI System    │
              │ at startup             │
              │ (via config_conocimiento)│
              └───────────────────────┘
```

---

## 🎯 Complete Integration Status Matrix

| Component | Backend | Frontend | n8n | MongoDB | Status |
|-----------|---------|----------|-----|---------|--------|
| **Chat Processing** | ✅ | ✅ | ✅ | ✅ | 🟢 **Active** |
| **Quote Generation** | ✅ | ✅ | ⚠️ | ✅ | 🟢 **Active** |
| **Knowledge Base** | ✅ | ✅ | ❌ | ⚠️ | 🟢 **Active** |
| **WhatsApp** | ✅ | ✅ | ✅ | ✅ | 🟢 **Active** |
| **Mercado Libre** | ✅ | ✅ | ❌ | ✅ | 🟢 **Active** |
| **Shopify** | ✅ | ⚠️ | ❌ | ⚠️ | 🟡 **Partial** |
| **Google Sheets** | ✅ | ✅ | ✅ | ⚠️ | 🟢 **Active** |
| **Learning System** | ✅ | ✅ | ❌ | ✅ | 🟢 **Active** |
| **Search** | ❌ | ✅ | ❌ | ✅ | 🟢 **Active** |
| **Export/Import** | ❌ | ✅ | ❌ | ✅ | 🟢 **Active** |
| **Settings** | ❌ | ✅ | ❌ | ✅ | 🟢 **Active** |
| **Notifications** | ❌ | ✅ | ❌ | ✅ | 🟢 **Active** |
| **Recovery** | ✅ | ✅ | ❌ | ✅ | 🟢 **Active** |

**Legend:**
- ✅ Fully integrated
- ⚠️ Partially integrated
- ❌ Not integrated

---

## 📊 Complete File Count by Module

```
┌─────────────────────────────────────────────────────────────────────┐
│  Module                  │  Files  │  Status           │  Priority │
├─────────────────────────────────────────────────────────────────────┤
│  Core Python Backend     │   35+   │  ✅ Active         │  🔴 High  │
│  Next.js Frontend        │   60+   │  ✅ Active         │  🔴 High  │
│  API Routes (Next.js)    │   25    │  ✅ Active         │  🔴 High  │
│  Data Ingestion          │   15+   │  ✅ Active         │  🟡 Medium│
│  Automation Scripts      │   30+   │  ✅ Active         │  🟡 Medium│
│  n8n Workflows           │   12+   │  ✅ Active         │  🟡 Medium│
│  Configuration           │   25+   │  ✅ Active         │  🔴 High  │
│  Documentation           │   50+   │  ✅ Complete        │  🟢 Low   │
│  Legacy Files            │   25+   │  ⚠️  Legacy         │  🟢 Low   │
└─────────────────────────────────────────────────────────────────────┘

Total: ~200+ files
Active: ~150 files
Legacy: ~25 files
Documentation: 50+ files
```

---

## 🗄️ MongoDB Collections Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MongoDB Collections (10)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ conversations   │  │ quotes          │  │ sessions        │  │
│  │ • Chat history  │  │ • Quote records │  │ • Active sessions│  │
│  │ • Messages      │  │ • Customer data │  │ • Context state  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ context         │  │ products        │  │ analytics       │  │
│  │ • Shared data   │  │ • Product catalog│  │ • Metrics       │  │
│  │ • Cross-session│  │ • Knowledge base│  │ • Statistics    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ settings        │  │ notifications   │  │ search_history  │  │
│  │ • User config   │  │ • Alerts        │  │ • Search logs   │  │
│  │ • System config │  │ • Messages      │  │ • Queries       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                     │
│  ┌─────────────────┐                                               │
│  │ mercado_libre_  │                                               │
│  │ grants          │                                               │
│  │ • OAuth tokens  │                                               │
│  │ • API grants    │                                               │
│  └─────────────────┘                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Paths

### **For Developers:**
1. Read `WORKSPACE_MAPPING.md` for detailed file mapping
2. Check `README.md` for setup instructions
3. Use `scripts/refresh_knowledge.sh` to update knowledge
4. Run `api_server.py` for backend (port 8000)
5. Run `npm run dev` for frontend (port 3000)
6. Use `docker-compose up` for full stack

### **For Users:**
1. Read `START_HERE.md`
2. Follow `QUICK_START_CHATBOT.md`
3. Check `HOW_TO_USE.md` for usage guide

### **For Deployment:**
1. Read `DEPLOYMENT_GUIDE.md`
2. Check `VERCEL_DEPLOY_GUIDE.md` for Vercel
3. Review `SETUP_CREDENTIALS_GUIDE.md` for credentials

### **For Data Recovery:**
1. Use `scripts/recover_conversations.py`
2. Or call `/api/recovery` endpoint
3. Check `RECOVERY_SUMMARY.md` for details

---

## 🔍 Finding Files by Functionality

**Need to modify chat behavior?**
→ `ia_conversacional_integrada.py`

**Need to change quote calculations?**
→ `sistema_cotizaciones.py`

**Need to update knowledge base?**
→ `scripts/refresh_knowledge.sh`

**Need to modify API endpoints?**
→ `api_server.py` (Python) or `src/app/api/*/route.ts` (Next.js)

**Need to change UI?**
→ `src/components/dashboard/*.tsx` or `src/components/chat/*.tsx`

**Need to add new data source?**
→ Create new script in `python-scripts/` and add to `scripts/refresh_knowledge.sh`

**Need to add new API endpoint?**
→ Create new file in `src/app/api/[name]/route.ts`

**Need to modify database schema?**
→ Check MongoDB collections section, update models in `src/models/`

**Need to add new n8n workflow?**
→ Create JSON file in `n8n_workflows/` and import to n8n

---

## 📈 API Endpoints Quick Reference

### **Chat & Quotes**
- `POST /api/chat/stream` - Streaming chat with AI
- `POST /api/quote-engine` - Generate quotes
- `POST /api/integrated-quote` - Full quote pipeline
- `POST /api/parse-quote` - Parse quote from text

### **Data Management**
- `POST /api/search` - Full-text search
- `POST /api/export` - Export data (CSV/JSON)
- `POST /api/import` - Import data (CSV/JSON)
- `GET /api/recovery` - Data recovery

### **Integrations**
- `GET|POST /api/sheets/sync` - Google Sheets sync
- `GET|POST /api/sheets/enhanced-sync` - Enhanced sync
- `GET|POST /api/mercado-libre/*` - Mercado Libre API
- `GET|POST /api/whatsapp/webhook` - WhatsApp webhook

### **System**
- `GET /api/health` - Health check
- `GET|POST /api/context` - Context management
- `GET|POST /api/settings` - Settings management
- `GET|POST|PUT|DELETE /api/notifications` - Notifications
- `GET /api/trends` - Trend analysis
- `GET /api/analytics/quotes` - Quote analytics

**Total:** 25 API endpoints

---

## 🐳 Docker Services Quick Reference

```
Services:
  • n8n (Port 5678) - Workflow orchestration
  • chat-api (Port 8000) - FastAPI Python backend
  • mongodb (Port 27017) - Database

Network: bmc-network (bridge)
Volumes: n8n_data, chat_data, mongodb_data
```

---

**Last Updated:** 2025-01-XX  
**Status:** ✅ **100% COMPLETE**  
**See:** `WORKSPACE_MAPPING.md` for detailed information


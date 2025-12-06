# 📋 BMC Repository Inventory - Reference Guide

**Purpose:** Quick reference for AI agents analyzing the BMC ecosystem  
**Last Updated:** 2024-12-28  
**Organization:** `matiasportugau-ui`

---

## 🗂️ Repository Catalog

### Tier 1: Core Repositories (High Priority)

#### 1. bmc-cotizacion-inteligente
- **Purpose:** Advanced AI-powered quotation system
- **Tech Stack:** TypeScript, Python, OpenAI, MongoDB, Google Sheets
- **Maturity:** ⭐⭐⭐⭐⭐ (85% - Most Evolved)
- **Key Modules:**
  - `src/lib/quote-engine.ts` - Core quotation engine
  - `src/lib/integrated-quote-engine.ts` - Integrated quotation system
  - Knowledge base with learning capabilities
  - WhatsApp → Google Sheets automation
- **Unique Features:**
  - Multi-query type detection (cotización/información/pregunta)
  - Dynamic knowledge base evolution
  - Zone-based pricing (Montevideo, Canelones, Maldonado, Rivera)
  - Export seal versioning system
- **Integration Points:**
  - WhatsApp Business API
  - Google Sheets CRM
  - OpenAI GPT-4
  - MongoDB for knowledge storage

#### 2. Ultimate-CHATBOT
- **Purpose:** Comprehensive conversational AI platform
- **Tech Stack:** Rasa, n8n, Qdrant, Chatwoot, PostgreSQL, Redis
- **Maturity:** ⭐⭐⭐⭐⭐ (70% - High)
- **Key Modules:**
  - Rasa NLU (15+ intents, 10+ entities)
  - n8n workflow orchestration
  - Qdrant vector database
  - Chatwoot multi-channel integration
- **Unique Features:**
  - 6-layer microservices architecture
  - Context management with token optimization
  - Pattern recognition and evaluation framework
  - Full documentation
- **Integration Points:**
  - Multiple messaging channels
  - Vector database for RAG
  - Workflow automation

#### 3. chatbot-2311
- **Purpose:** Integrated quotation chatbot with learning
- **Tech Stack:** Python, FastAPI, WhatsApp, Google Sheets, MongoDB
- **Maturity:** ⭐⭐⭐⭐ (65% - High)
- **Key Modules:**
  - `api_server.py` - FastAPI main entry point
  - `ia_conversacional_integrada.py` - Conversational AI
  - `sistema_cotizaciones.py` - Quotation engine
  - `base_conocimiento_dinamica.py` - Dynamic knowledge base
  - `integracion_whatsapp.py` - WhatsApp integration
- **Unique Features:**
  - Continuous learning from interactions
  - Pattern recognition
  - Dual processing mode (OpenAI + pattern matching)
  - Background agents for follow-ups
- **Integration Points:**
  - WhatsApp Business API
  - Google Sheets
  - MongoDB
  - n8n workflows

#### 4. Dashboard-bmc
- **Purpose:** Financial dashboard & prompt library
- **Tech Stack:** Python, Looker Studio, Google Sheets, Master Prompts
- **Maturity:** ⭐⭐⭐⭐ (50% - Medium-High)
- **Key Modules:**
  - Master Prompts library
  - Multi-agent orchestration
  - Financial analytics
- **Unique Features:**
  - AU1/AU2 governance patterns
  - Role-based agent decomposition
  - Phase-based workflow management
- **Integration Points:**
  - Google Sheets
  - Data Studio
  - Prompt templates

### Tier 2: Support Repositories (Medium Priority)

#### 5. ChatBOT
- **Purpose:** Self-hosted auto-ATC chatbot
- **Tech Stack:** Rasa, PostgreSQL, Qdrant, n8n, Chatwoot
- **Maturity:** ⭐⭐⭐ (60% - Medium)
- **Key Modules:**
  - Rasa configuration
  - Docker setup
  - AUTO-ATC Playbook v3
- **Status:** Solid foundation, needs integration with other repos

#### 6. background-agents
- **Purpose:** Autonomous background agent framework
- **Tech Stack:** JavaScript, Node.js, Cron
- **Maturity:** ⭐⭐⭐ (80% - High for framework)
- **Key Modules:**
  - `src/core/BaseAgent.js` - Abstract base agent
  - `src/core/AgentManager.js` - Agent lifecycle management
  - CLI tools
  - Dashboard integration
- **Status:** Good CLI, needs expansion and integration

### Tier 3: Developing Repositories (Lower Priority)

#### 7. bmc-chatbot-pro
- **Purpose:** Integrated BMC Chatbot Pro
- **Tech Stack:** TypeScript
- **Maturity:** ⭐⭐ (20% - Low)
- **Status:** Needs content analysis and integration

#### 8. vmc-chatbot-pro
- **Purpose:** VMC Chatbot variant
- **Tech Stack:** TypeScript 100%
- **Maturity:** ⭐⭐ (10% - Low)
- **Status:** Pure TypeScript, needs integration

#### 9. BMC---Uruguay
- **Purpose:** JavaScript-based BMC system
- **Tech Stack:** JavaScript, HTML, Docker
- **Maturity:** ⭐⭐ (40% - Low)
- **Status:** Basic structure, needs development

### Tier 4: Specialized Repositories

#### 10. bmc-theme
- **Purpose:** Shopify/Liquid theme
- **Tech Stack:** Liquid, JavaScript, CSS
- **Maturity:** ⭐ (90% - High for theme)
- **Status:** Specialized, not core to chatbot system

---

## 🔗 Known Integration Patterns

### Pattern 1: Quotation Flow
```
User Message (WhatsApp/Web)
  → chatbot-2311/ia_conversacional_integrada.py
  → sistema_cotizaciones.py
  → bmc-cotizacion-inteligente/quote-engine (if advanced features needed)
  → Google Sheets (CRM)
  → Response to User
```

### Pattern 2: Knowledge Base Learning
```
User Interaction
  → chatbot-2311/base_conocimiento_dinamica.py
  → MongoDB Storage
  → Pattern Recognition
  → Knowledge Evolution
  → Future Response Improvement
```

### Pattern 3: Multi-Channel Orchestration
```
WhatsApp/Web/Chatwoot
  → Ultimate-CHATBOT (orchestration)
  → n8n Workflows
  → Background Agents
  → Response Delivery
```

### Pattern 4: Background Processing
```
Scheduled Task
  → background-agents/BaseAgent
  → Process Queue
  → Update Google Sheets
  → Send Notifications
```

---

## 📊 Maturity Comparison Matrix

| Repository | Code Quality | Features | Scalability | Security | Docs | Testing | Integration | Learning | Deployment | Innovation | **Total** |
|------------|--------------|----------|-------------|----------|------|---------|-------------|----------|------------|------------|-----------|
| bmc-cotizacion-inteligente | 9 | 9 | 8 | 7 | 8 | 7 | 9 | 9 | 8 | 9 | **84/100** |
| Ultimate-CHATBOT | 8 | 8 | 9 | 8 | 9 | 7 | 9 | 7 | 9 | 8 | **81/100** |
| chatbot-2311 | 7 | 8 | 7 | 6 | 7 | 6 | 8 | 9 | 7 | 7 | **72/100** |
| Dashboard-bmc | 7 | 6 | 6 | 6 | 8 | 5 | 7 | 6 | 6 | 8 | **65/100** |
| ChatBOT | 6 | 6 | 7 | 7 | 6 | 5 | 6 | 5 | 8 | 6 | **58/100** |
| background-agents | 7 | 7 | 7 | 6 | 6 | 6 | 7 | 5 | 7 | 7 | **60/100** |

---

## 🎯 Key Files Reference

### Quotation Systems
- `bmc-cotizacion-inteligente/src/lib/quote-engine.ts` - Most evolved
- `chatbot-2311/sistema_cotizaciones.py` - Integrated version
- `chatbot-2311/utils_cotizaciones.py` - Validation utilities

### Knowledge Bases
- `chatbot-2311/base_conocimiento_dinamica.py` - Dynamic learning
- `Ultimate-CHATBOT/Qdrant` - Vector storage (to be configured)

### Integrations
- `chatbot-2311/integracion_whatsapp.py` - WhatsApp Business API
- `chatbot-2311/integracion_google_sheets.py` - Google Sheets sync
- `chatbot-2311/n8n_integration.py` - n8n workflows

### Background Agents
- `background-agents/src/core/BaseAgent.js` - Base framework
- `chatbot-2311/background_agent.py` - Python implementation
- `chatbot-2311/automated_agent_system.py` - Automated system

### Orchestration
- `Ultimate-CHATBOT/n8n/workflows/` - Workflow definitions
- `chatbot-2311/n8n_workflows/` - Workflow JSON files

---

## 🔍 Search Keywords by Domain

### Quotation/Cotización
- `quote`, `quotation`, `cotizacion`, `cotizar`
- `price`, `pricing`, `precio`
- `calculate`, `calcular`
- `product`, `producto`
- `espesor`, `dimension`, `dimensiones`

### Lead/CRM
- `lead`, `client`, `cliente`, `customer`
- `ingest`, `ingestion`, `ingesta`
- `crm`, `sheets`, `google`
- `createLead`, `insertLead`

### Knowledge Base
- `knowledge`, `conocimiento`, `kb`
- `base_conocimiento`, `knowledge_base`
- `qdrant`, `vector`, `embedding`
- `learn`, `learning`, `aprender`

### WhatsApp
- `whatsapp`, `wa`
- `webhook`, `message`, `mensaje`
- `sendMessage`, `send_message`

### Background Agents
- `agent`, `background`, `automated`
- `cron`, `schedule`, `scheduled`
- `BaseAgent`, `AgentManager`

### Orchestration
- `n8n`, `workflow`, `orchestration`
- `chatwoot`, `multi-channel`
- `integration`, `integracion`

---

## 📝 Notes for AI Agents

1. **Start with Tier 1 repos** for most comprehensive analysis
2. **Use exemplar modules** from `bmc-cotizacion-inteligente` and `Ultimate-CHATBOT` as references
3. **Look for Spanish comments/variables** - this is a Uruguayan business
4. **Check for export_seal** in generated files
5. **Focus on integration opportunities** between repos
6. **Prioritize quotation system** improvements (core business value)

---

**Export Seal:**
```json
{
  "export_seal": {
    "project": "Ultimate-CHATBOT",
    "prompt_id": "bmc-repository-inventory",
    "version": "v1.0",
    "created_at": "2024-12-28T00:00:00Z",
    "author": "BMC",
    "origin": "ArchitectBot"
  }
}
```


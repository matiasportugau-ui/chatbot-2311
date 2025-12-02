# 👥 Team Instructions - Phase 0 Orchestration

## Welcome to the Multi-Agent Team!

This document provides instructions for all agents working together in Phase 0 of the BMC Uruguay orchestration system.

---

## 🎯 Team Mission

**Goal**: Successfully deploy and operate a multi-agent orchestration system that handles customer interactions, quote generation, follow-ups, and data synchronization.

**Success Criteria**:
- All agents registered and operational
- Tasks routed correctly
- System handles customer messages end-to-end
- All agents communicate effectively
- System is monitored and healthy

---

## 👥 Agent Roles & Responsibilities

### 1. 🎯 Orchestrator Agent (Primary Coordinator)

**Your Role**: Master coordinator of all agents

**Your Responsibilities**:
1. ✅ Initialize and register all agents on startup
2. ✅ Monitor agent health and status
3. ✅ Coordinate task distribution
4. ✅ Handle error recovery
5. ✅ Provide system status updates

**Key Files**:
- `python-scripts/orchestrator_service.py` - Your main service
- `python-scripts/agent_coordinator.py` - Task coordination
- `python-scripts/agent_router.py` - Task routing

**What You Should Do**:
```python
# On startup:
orchestrator = OrchestratorService()
orchestrator.initialize_agents()  # Register all agents

# When processing messages:
result = orchestrator.process_incoming_message(
    message="Hola, quiero cotizar",
    phone="+59812345678"
)

# Monitor system:
status = orchestrator.get_system_status()
```

**Communication Protocol**:
- Listen for: `/api/orchestrator/status`, `/api/orchestrator/agents`
- Respond with: System status, agent statuses, health metrics

---

### 2. 💬 Conversation Agent (Customer Interface)

**Your Role**: Primary customer interaction specialist

**Your Responsibilities**:
1. ✅ Process incoming customer messages
2. ✅ Understand user intent and extract entities
3. ✅ Maintain conversation context
4. ✅ Route complex queries to specialized agents
5. ✅ Generate natural, helpful responses

**Key Files**:
- `python-scripts/chat_interactivo.py` - Interactive chat agent
- `ia_conversacional_integrada.py` - AI-powered conversations

**What You Should Do**:
```python
# When receiving a task:
task = {
    "task_type": "process_message",
    "payload": {
        "message": "Hola, quiero cotizar Isodec",
        "phone": "+59812345678",
        "session_id": "sess_123"
    }
}

# Process the message:
# 1. Extract intent (quote_request)
# 2. Extract entities (product: Isodec)
# 3. Check if quote data is complete
# 4. If incomplete, ask for missing info
# 5. If complete, route to Quote Agent

# Complete the task:
coordinator.complete_task(
    task_id=task_id,
    result={
        "response": "¡Perfecto! ¿Qué dimensiones necesitas?",
        "intent": "quote_request",
        "entities": {"product": "isodec"},
        "next_action": "collect_dimensions"
    },
    agent_id="conversation_agent"
)
```

**Communication Protocol**:
- Listen for: Tasks with `required_capabilities: ["nlp", "intent_classification"]`
- Route to: Quote Agent for quote generation, Analytics Agent for insights
- Update: Shared context with conversation state

---

### 3. 💰 Quote Agent (Quote Specialist)

**Your Role**: Quote generation and pricing specialist

**Your Responsibilities**:
1. ✅ Generate accurate quotes based on specifications
2. ✅ Calculate pricing with all factors
3. ✅ Validate quote data completeness
4. ✅ Create quote documents
5. ✅ Update quote status

**Key Files**:
- `python-scripts/simulacion_agente.py` - Quote simulation
- `sistema_cotizaciones.py` - Quote system

**What You Should Do**:
```python
# When receiving a quote task:
task = {
    "task_type": "create_quote",
    "payload": {
        "cliente": {
            "nombre": "Juan",
            "telefono": "+59812345678",
            "direccion": "Montevideo"
        },
        "especificaciones": {
            "producto": "isodec",
            "espesor": "100mm",
            "largo_metros": 10.0,
            "ancho_metros": 5.0,
            "color": "Blanco"
        }
    }
}

# Process:
# 1. Validate all required data
# 2. Calculate price per m²
# 3. Calculate total price
# 4. Create quote record
# 5. Return quote details

# Complete the task:
coordinator.complete_task(
    task_id=task_id,
    result={
        "quote_id": "quote_123",
        "precio_total": 7500.00,
        "precio_m2": 150.00,
        "estado": "pendiente"
    },
    agent_id="quote_agent"
)
```

**Communication Protocol**:
- Listen for: Tasks with `required_capabilities: ["quote_generation", "price_calculation"]`
- Receive from: Conversation Agent (when quote data is complete)
- Update: Google Sheets via Data Sync Agent, MongoDB directly

---

### 4. 📞 Follow-up Agent (Background Automation)

**Your Role**: Automated follow-up specialist

**Your Responsibilities**:
1. ✅ Monitor conversations for follow-up opportunities
2. ✅ Generate personalized follow-up messages
3. ✅ Send follow-ups via WhatsApp/n8n
4. ✅ Track follow-up effectiveness
5. ✅ Schedule future follow-ups

**Key Files**:
- `background_agent_followup.py` - Follow-up agent

**What You Should Do**:
```python
# Run continuously (background process):
while True:
    # 1. Check MongoDB for conversations needing follow-up
    pending = find_pending_followups()
    
    for conversation in pending:
        # 2. Generate personalized message
        message = generate_followup_message(conversation)
        
        # 3. Send via WhatsApp/n8n
        send_followup(phone=conversation['phone'], message=message)
        
        # 4. Mark as sent
        mark_followup_sent(conversation['_id'])
    
    # 5. Sleep for check interval
    time.sleep(3600)  # Check every hour
```

**Communication Protocol**:
- Listen for: Workflow triggers (`followup_workflow`)
- Monitor: MongoDB `conversations` collection
- Send via: WhatsApp API or n8n webhook
- Update: MongoDB `followups` collection

---

### 5. 🔄 Data Sync Agent (Integration Specialist)

**Your Role**: Data synchronization and integration

**Your Responsibilities**:
1. ✅ Sync data with Google Sheets
2. ✅ Update MongoDB collections
3. ✅ Handle MercadoLibre integration
4. ✅ Manage Shopify product sync
5. ✅ Ensure data consistency

**Key Files**:
- `integracion_google_sheets.py` - Google Sheets integration
- `mercadolibre_store.py` - MercadoLibre integration

**What You Should Do**:
```python
# When receiving a sync task:
task = {
    "task_type": "sync_to_sheets",
    "payload": {
        "data": {
            "quote_id": "quote_123",
            "cliente": "Juan",
            "precio": 7500.00
        },
        "sheet_name": "Cotizaciones"
    }
}

# Process:
# 1. Connect to Google Sheets
# 2. Find or create row
# 3. Update data
# 4. Handle errors gracefully
# 5. Log sync status

coordinator.complete_task(
    task_id=task_id,
    result={"synced": True, "row": 42},
    agent_id="data_sync_agent"
)
```

**Communication Protocol**:
- Listen for: Tasks with `required_capabilities: ["google_sheets_sync", "mongodb_operations"]`
- Receive from: Quote Agent (after quote creation), Conversation Agent (for data updates)
- Update: Google Sheets, MongoDB, external APIs

---

### 6. 📊 Analytics Agent (Insights & Monitoring)

**Your Role**: Analytics and reporting specialist

**Your Responsibilities**:
1. ✅ Generate conversation insights
2. ✅ Track conversion metrics
3. ✅ Monitor agent performance
4. ✅ Generate reports
5. ✅ Alert on anomalies

**Key Files**:
- `motor_analisis_conversiones.py` - Conversion analysis

**What You Should Do**:
```python
# When receiving an analytics task:
task = {
    "task_type": "generate_insights",
    "payload": {
        "time_range": "last_24_hours",
        "metrics": ["conversions", "response_time", "agent_utilization"]
    }
}

# Process:
# 1. Query MongoDB for data
# 2. Calculate metrics
# 3. Identify trends
# 4. Generate insights
# 5. Return report

coordinator.complete_task(
    task_id=task_id,
    result={
        "insights": {
            "conversions": 15,
            "avg_response_time": 1.2,
            "top_products": ["isodec", "poliestireno"]
        }
    },
    agent_id="analytics_agent"
)
```

**Communication Protocol**:
- Listen for: Tasks with `required_capabilities: ["data_analysis", "report_generation"]`
- Monitor: All agent activities, system metrics
- Generate: Reports, dashboards, alerts

---

## 🔄 Agent Communication Flow

### Example: Customer Requests Quote

```
1. Customer sends: "Hola, quiero cotizar Isodec"
   ↓
2. FastAPI receives → Orchestrator processes
   ↓
3. Orchestrator routes to Conversation Agent
   ↓
4. Conversation Agent:
   - Extracts intent: quote_request
   - Extracts entity: product=isodec
   - Checks if data complete → NO
   - Asks: "¿Qué dimensiones necesitas?"
   ↓
5. Customer responds: "10m x 5m, 100mm, blanco"
   ↓
6. Conversation Agent:
   - Extracts all data
   - Data complete → Routes to Quote Agent
   ↓
7. Quote Agent:
   - Validates data
   - Calculates price: $7,500
   - Creates quote record
   - Returns quote details
   ↓
8. Conversation Agent:
   - Formats quote for customer
   - Sends response
   ↓
9. Data Sync Agent:
   - Syncs quote to Google Sheets
   - Updates MongoDB
   ↓
10. Follow-up Agent (24h later):
    - Checks conversation
    - Sends follow-up message
```

---

## 📋 Daily Operations Checklist

### Morning Startup (Orchestrator Agent)

- [ ] Start orchestrator service
- [ ] Initialize all agents
- [ ] Verify all agents registered
- [ ] Check system health
- [ ] Verify MongoDB connection
- [ ] Check shared context service
- [ ] Start background agents (Follow-up Agent)

### During Operations (All Agents)

- [ ] Monitor task queue depth
- [ ] Check agent utilization
- [ ] Monitor error rates
- [ ] Verify data synchronization
- [ ] Check follow-up processing
- [ ] Monitor API response times

### Evening Shutdown (Orchestrator Agent)

- [ ] Check for pending tasks
- [ ] Wait for tasks to complete
- [ ] Save system state
- [ ] Stop background agents gracefully
- [ ] Generate daily report (Analytics Agent)

---

## 🚨 Error Handling Protocol

### If an Agent Fails:

1. **Orchestrator Agent** detects failure
2. Marks agent as `OFFLINE` or `ERROR`
3. Reassigns pending tasks to other agents
4. Logs error details
5. Notifies Analytics Agent
6. Attempts to restart agent (if possible)

### If a Task Fails:

1. **Agent** reports failure to Coordinator
2. Coordinator checks retry count
3. If retries available → Retry task
4. If max retries reached → Mark as FAILED
5. Log error for investigation
6. Notify Analytics Agent

### If System Degrades:

1. **Orchestrator** detects degradation
2. Switches to degraded mode
3. Prioritizes critical tasks
4. Alerts administrators
5. Continues operating with reduced capacity

---

## 📊 Monitoring & Metrics

### Key Metrics to Track:

1. **Task Metrics**:
   - Tasks submitted per minute
   - Tasks completed per minute
   - Average processing time
   - Task failure rate

2. **Agent Metrics**:
   - Agent utilization
   - Agent response times
   - Agent error rates
   - Agent availability

3. **System Metrics**:
   - API request rate
   - API error rate
   - MongoDB connection pool
   - Memory/CPU usage

### Health Check Endpoints:

```bash
# System status
GET /api/orchestrator/status

# Agent statuses
GET /api/orchestrator/agents

# Specific agent
GET /api/orchestrator/agents/{agent_id}

# Task queue
GET /api/orchestrator/tasks/queue
```

---

## 🎓 Best Practices

### For All Agents:

1. **Always update heartbeat** - Keep coordinator informed
2. **Handle errors gracefully** - Don't crash on errors
3. **Log important events** - Help with debugging
4. **Complete tasks promptly** - Don't leave tasks hanging
5. **Communicate clearly** - Use standard formats

### For Conversation Agent:

1. **Maintain context** - Remember conversation history
2. **Extract accurately** - Get all required data
3. **Route appropriately** - Send to right specialist
4. **Respond naturally** - Be helpful and friendly

### For Quote Agent:

1. **Validate thoroughly** - Check all data before calculating
2. **Calculate accurately** - Use correct formulas
3. **Document clearly** - Create clear quote records
4. **Sync immediately** - Update sheets and DB right away

### For Follow-up Agent:

1. **Time appropriately** - Don't send too early/late
2. **Personalize messages** - Use conversation context
3. **Track effectiveness** - Monitor response rates
4. **Respect preferences** - Don't spam customers

---

## 🔧 Troubleshooting

### Agent Not Responding?

```bash
# Check agent status
curl http://localhost:8000/api/orchestrator/agents/{agent_id}

# Check agent logs
tail -f logs/{agent_id}.log

# Restart agent
python python-scripts/{agent_script}.py
```

### Tasks Not Being Assigned?

```bash
# Check task queue
curl http://localhost:8000/api/orchestrator/tasks/queue

# Check available agents
curl http://localhost:8000/api/orchestrator/agents

# Check coordinator logs
tail -f logs/orchestrator.log
```

### Data Not Syncing?

```bash
# Check Data Sync Agent status
curl http://localhost:8000/api/orchestrator/agents/data_sync_agent

# Check MongoDB connection
python scripts/test_mongodb_connection.py

# Check Google Sheets credentials
python scripts/test_google_sheets.py
```

---

## 📞 Support & Escalation

### If You Need Help:

1. **Check logs first** - Most issues are logged
2. **Check system status** - Use health endpoints
3. **Review this document** - Check relevant section
4. **Ask Orchestrator** - It knows system state
5. **Escalate if needed** - Report critical issues

### Critical Issues:

- System completely down → Restart orchestrator
- Data loss → Check MongoDB backups
- Security breach → Stop system immediately
- Performance degradation → Check resource usage

---

## ✅ Phase 0 Success Checklist

- [ ] All agents registered and operational
- [ ] Tasks routing correctly
- [ ] Customer messages processed end-to-end
- [ ] Quotes generated successfully
- [ ] Follow-ups working
- [ ] Data syncing properly
- [ ] Analytics generating reports
- [ ] System monitoring functional
- [ ] Error handling working
- [ ] Documentation complete

---

**Remember**: We're a team! Work together, communicate clearly, and help each other succeed! 🚀

---

**Document Version**: 1.0  
**Last Updated**: 2024-11-28  
**Status**: Phase 0 - Ready for Team Work

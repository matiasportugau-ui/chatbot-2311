# 🎯 Phase 0: Multi-Agent Orchestration Deployment Plan

## Executive Summary

This document outlines the Phase 0 orchestration setup for the BMC Uruguay multi-agent system. The system will coordinate multiple specialized agents to handle customer interactions, quote generation, follow-ups, and data synchronization.

**Status**: Phase 0 - Initial Orchestration Setup  
**Target Date**: Immediate  
**Team Size**: Multi-agent team (all agents in this chat)

---

## 🏗️ System Architecture Overview

### Current System Components

1. **FastAPI Server** (`api_server.py`) - Main API endpoint
2. **Shared Context Service** (`shared_context_service.py`) - MongoDB-based context management
3. **Workflow Engine** (`agent_workflows.py`) - Workflow execution engine
4. **Background Follow-up Agent** (`background_agent_followup.py`) - Automated follow-ups
5. **Interactive Chat Agent** (`chat_interactivo.py`) - Customer interaction agent
6. **Quote Simulation Agent** (`simulacion_agente.py`) - Quote generation agent
7. **IA Conversational System** (`ia_conversacional_integrada.py`) - AI-powered conversations

### Missing Components (To Be Created)

1. **Agent Coordinator** (`agent_coordinator.py`) - Task distribution and agent management
2. **Agent Router** (`agent_router.py`) - Intelligent routing of tasks to agents
3. **Orchestrator Service** (`orchestrator_service.py`) - Main orchestration controller

---

## 👥 Agent Roles & Responsibilities

### 1. **Orchestrator Agent** (Primary Coordinator)
**Role**: Master Orchestrator  
**Responsibilities**:
- Coordinate all agent activities
- Manage task queues and priorities
- Monitor agent health and performance
- Route tasks to appropriate agents
- Handle error recovery and retries

**Capabilities**:
- Task distribution
- Load balancing
- Health monitoring
- Workflow orchestration

---

### 2. **Conversation Agent** (Customer Interaction)
**Role**: Primary Customer Interface  
**Responsibilities**:
- Handle incoming customer messages
- Process natural language queries
- Extract intent and entities
- Maintain conversation context
- Route complex queries to specialized agents

**Capabilities**:
- Natural language understanding
- Intent classification
- Entity extraction
- Context management
- Multi-turn conversations

**Files**: `chat_interactivo.py`, `ia_conversacional_integrada.py`

---

### 3. **Quote Agent** (Quote Generation)
**Role**: Quote Specialist  
**Responsibilities**:
- Generate accurate quotes
- Calculate pricing based on specifications
- Validate quote data completeness
- Create quote documents
- Update quote status

**Capabilities**:
- Quote calculation
- Price validation
- Product knowledge
- Specification parsing
- Document generation

**Files**: `simulacion_agente.py`, `sistema_cotizaciones.py`

---

### 4. **Follow-up Agent** (Background Automation)
**Role**: Automated Follow-up Specialist  
**Responsibilities**:
- Monitor conversations for follow-up opportunities
- Generate personalized follow-up messages
- Send follow-up messages via WhatsApp/n8n
- Track follow-up effectiveness
- Schedule future follow-ups

**Capabilities**:
- Conversation monitoring
- Message generation
- Scheduling
- Channel integration (WhatsApp, n8n)
- Analytics tracking

**Files**: `background_agent_followup.py`

---

### 5. **Data Sync Agent** (Integration Specialist)
**Role**: Data Synchronization  
**Responsibilities**:
- Sync data with Google Sheets
- Update MongoDB collections
- Handle MercadoLibre integration
- Manage Shopify product sync
- Ensure data consistency

**Capabilities**:
- Google Sheets API
- MongoDB operations
- External API integration
- Data transformation
- Error handling

**Files**: `integracion_google_sheets.py`, `mercadolibre_store.py`

---

### 6. **Analytics Agent** (Insights & Monitoring)
**Role**: Analytics & Reporting  
**Responsibilities**:
- Generate conversation insights
- Track conversion metrics
- Monitor agent performance
- Generate reports
- Alert on anomalies

**Capabilities**:
- Data analysis
- Report generation
- Performance metrics
- Anomaly detection
- Dashboard updates

**Files**: `motor_analisis_conversiones.py`

---

## 🔧 Orchestration Architecture

### Orchestrator Selection: **Centralized Orchestrator Pattern**

**Rationale**:
- Single point of control for easier debugging
- Simplified task distribution
- Better resource management
- Easier to scale individual agents
- Clear separation of concerns

### Communication Pattern: **Message Queue + Shared Context**

```
┌─────────────────┐
│   FastAPI API   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Orchestrator   │ ◄─── Coordinates all agents
│    Service      │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Convers │ │ Quote  │ │Follow- │ │  Data   │ │Analytics│
│ Agent  │ │ Agent  │ │  up    │ │  Sync   │ │ Agent   │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
    │         │          │          │          │
    └─────────┴──────────┴──────────┴──────────┘
                    │
                    ▼
         ┌──────────────────┐
         │ Shared Context    │
         │   (MongoDB)       │
         └──────────────────┘
```

---

## 📋 Phase 0 Implementation Tasks

### Task 1: Create Agent Coordinator ✅ Priority: CRITICAL
**Owner**: Orchestrator Agent  
**Estimated Time**: 2 hours

**Deliverables**:
- `python-scripts/agent_coordinator.py`
- Task queue management
- Agent registration system
- Task assignment logic
- Health monitoring

**Key Features**:
```python
class AgentCoordinator:
    - register_agent(agent_id, capabilities, status)
    - submit_task(task_type, payload, priority)
    - assign_task_to_agent(task_id, agent_id)
    - get_task_status(task_id)
    - get_agent_status(agent_id)
    - health_check()
```

---

### Task 2: Create Agent Router ✅ Priority: CRITICAL
**Owner**: Orchestrator Agent  
**Estimated Time**: 1.5 hours

**Deliverables**:
- `python-scripts/agent_router.py`
- Intelligent routing logic
- Capability matching
- Load balancing
- Fallback mechanisms

**Key Features**:
```python
class AgentRouter:
    - route_task(task_type, payload, required_capabilities)
    - find_best_agent(capabilities, current_load)
    - get_available_agents(capabilities)
    - update_agent_load(agent_id, load)
```

---

### Task 3: Create Orchestrator Service ✅ Priority: CRITICAL
**Owner**: Orchestrator Agent  
**Estimated Time**: 2 hours

**Deliverables**:
- `python-scripts/orchestrator_service.py`
- Main orchestration controller
- Integration with FastAPI
- Workflow coordination
- Error handling

**Key Features**:
```python
class OrchestratorService:
    - initialize_agents()
    - process_incoming_message(message, context)
    - coordinate_workflow(workflow_id, data)
    - handle_error(error, context)
    - get_system_status()
```

---

### Task 4: Update API Server Integration ✅ Priority: HIGH
**Owner**: Conversation Agent  
**Estimated Time**: 1 hour

**Deliverables**:
- Update `api_server.py` to use orchestrator
- Route messages through orchestrator
- Integrate with agent coordinator
- Add orchestration endpoints

**Changes**:
- Import orchestrator service
- Replace direct IA calls with orchestrator routing
- Add `/api/orchestrator/status` endpoint
- Add `/api/orchestrator/agents` endpoint

---

### Task 5: Register All Agents ✅ Priority: HIGH
**Owner**: Orchestrator Agent  
**Estimated Time**: 1 hour

**Deliverables**:
- Agent registration script
- Capability definitions
- Health check endpoints for each agent
- Agent metadata configuration

**Agent Registrations**:
```python
agents = [
    {
        "id": "conversation_agent",
        "name": "Conversation Agent",
        "capabilities": ["nlp", "intent_classification", "context_management"],
        "status": "active"
    },
    {
        "id": "quote_agent",
        "name": "Quote Agent",
        "capabilities": ["quote_generation", "price_calculation", "validation"],
        "status": "active"
    },
    # ... more agents
]
```

---

### Task 6: Create Agent Health Monitoring ✅ Priority: MEDIUM
**Owner**: Analytics Agent  
**Estimated Time**: 1 hour

**Deliverables**:
- Health check system
- Agent status dashboard
- Alerting mechanism
- Performance metrics collection

---

### Task 7: Update Shared Context Service ✅ Priority: MEDIUM
**Owner**: Data Sync Agent  
**Estimated Time**: 30 minutes

**Deliverables**:
- Ensure shared context works with orchestrator
- Add agent-specific context isolation
- Add context versioning
- Add context cleanup policies

---

### Task 8: Create Deployment Scripts ✅ Priority: MEDIUM
**Owner**: Orchestrator Agent  
**Estimated Time**: 1 hour

**Deliverables**:
- `scripts/deploy_orchestrator.sh`
- `scripts/start_all_agents.sh`
- `scripts/stop_all_agents.sh`
- `scripts/health_check_all.sh`

---

### Task 9: Documentation ✅ Priority: LOW
**Owner**: All Agents  
**Estimated Time**: 1 hour

**Deliverables**:
- Agent API documentation
- Orchestration flow diagrams
- Troubleshooting guide
- Agent communication protocols

---

### Task 10: Testing & Validation ✅ Priority: HIGH
**Owner**: All Agents  
**Estimated Time**: 2 hours

**Deliverables**:
- Unit tests for orchestrator
- Integration tests for agent communication
- End-to-end workflow tests
- Performance benchmarks

---

## 🚀 Deployment Steps

### Step 1: Pre-Deployment Checklist
- [ ] MongoDB connection verified
- [ ] All environment variables set
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] FastAPI server can start
- [ ] Shared context service accessible

### Step 2: Create Core Orchestration Components
```bash
# Create agent coordinator
python scripts/create_agent_coordinator.py

# Create agent router  
python scripts/create_agent_router.py

# Create orchestrator service
python scripts/create_orchestrator_service.py
```

### Step 3: Register All Agents
```bash
# Register agents with coordinator
python scripts/register_agents.py
```

### Step 4: Update API Server
```bash
# Update api_server.py to use orchestrator
# Test API endpoints
python -m pytest tests/test_orchestrator_integration.py
```

### Step 5: Start Orchestration System
```bash
# Start orchestrator service
python python-scripts/orchestrator_service.py &

# Start background agents
python background_agent_followup.py --continuous &

# Start API server
python api_server.py
```

### Step 6: Verify System Health
```bash
# Check orchestrator status
curl http://localhost:8000/api/orchestrator/status

# Check agent statuses
curl http://localhost:8000/api/orchestrator/agents

# Test message processing
curl -X POST http://localhost:8000/chat/process \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "Hola, quiero cotizar", "telefono": "+59812345678"}'
```

### Step 7: Monitor & Validate
- Monitor logs for errors
- Verify agent coordination
- Test workflow execution
- Validate data persistence

---

## 📊 Success Metrics

### Phase 0 Success Criteria

1. **Orchestration**:
   - ✅ All agents registered and discoverable
   - ✅ Tasks routed correctly to agents
   - ✅ Agent health monitoring functional
   - ✅ Error handling and recovery working

2. **Communication**:
   - ✅ Messages flow through orchestrator
   - ✅ Shared context accessible to all agents
   - ✅ Agent-to-agent communication working
   - ✅ Workflow execution successful

3. **Performance**:
   - ✅ API response time < 2 seconds
   - ✅ Agent task assignment < 100ms
   - ✅ No memory leaks
   - ✅ System handles 10 concurrent requests

4. **Reliability**:
   - ✅ System recovers from agent failures
   - ✅ Tasks retry on failure
   - ✅ No data loss
   - ✅ Graceful degradation

---

## 🔍 Monitoring & Observability

### Logging Strategy

**Log Levels**:
- `ERROR`: Agent failures, system errors
- `WARN`: Retries, fallbacks, degraded performance
- `INFO`: Task assignments, agent status changes
- `DEBUG`: Detailed routing decisions, context updates

**Log Format**:
```json
{
  "timestamp": "2024-11-28T10:00:00Z",
  "level": "INFO",
  "agent": "orchestrator",
  "task_id": "task_123",
  "message": "Task assigned to conversation_agent",
  "metadata": {...}
}
```

### Metrics to Track

1. **Orchestration Metrics**:
   - Tasks submitted per minute
   - Tasks completed per minute
   - Average task processing time
   - Agent utilization rates
   - Task queue depth

2. **Agent Metrics**:
   - Agent response times
   - Agent error rates
   - Agent availability
   - Tasks per agent
   - Agent-specific performance

3. **System Metrics**:
   - API request rate
   - API error rate
   - MongoDB connection pool usage
   - Memory usage
   - CPU usage

---

## 🛠️ Troubleshooting Guide

### Common Issues

**Issue 1: Agent Not Responding**
- Check agent health: `GET /api/orchestrator/agents/{agent_id}/health`
- Verify agent is registered: `GET /api/orchestrator/agents`
- Check agent logs
- Restart agent if needed

**Issue 2: Tasks Not Being Assigned**
- Verify coordinator is running
- Check task queue: `GET /api/orchestrator/tasks/queue`
- Verify agent capabilities match task requirements
- Check router configuration

**Issue 3: Shared Context Not Updating**
- Verify MongoDB connection
- Check context service logs
- Verify session IDs are consistent
- Check context isolation rules

**Issue 4: Workflow Execution Failing**
- Check workflow definition
- Verify all required agents are available
- Check step execution logs
- Verify workflow data format

---

## 📝 Agent Communication Protocol

### Task Submission Format

```json
{
  "task_id": "task_uuid",
  "task_type": "process_message",
  "payload": {
    "message": "Hola, quiero cotizar",
    "phone": "+59812345678",
    "session_id": "sess_123"
  },
  "priority": "normal",
  "required_capabilities": ["nlp", "intent_classification"],
  "metadata": {
    "source": "whatsapp",
    "timestamp": "2024-11-28T10:00:00Z"
  }
}
```

### Agent Response Format

```json
{
  "task_id": "task_uuid",
  "status": "completed",
  "result": {
    "response": "¡Hola! ¿Qué producto te interesa cotizar?",
    "intent": "quote_request",
    "confidence": 0.95,
    "next_action": "collect_quote_data"
  },
  "agent_id": "conversation_agent",
  "processing_time_ms": 250,
  "timestamp": "2024-11-28T10:00:05Z"
}
```

---

## 🎯 Next Steps After Phase 0

### Phase 1: Enhanced Intelligence (Week 1-2)
- Improve NLP accuracy
- Add sentiment analysis
- Implement conversation memory
- Add personalization

### Phase 2: Advanced Features (Week 3-4)
- Multi-language support
- Voice integration
- Advanced analytics
- Predictive follow-ups

### Phase 3: Scale & Optimize (Week 5-6)
- Horizontal scaling
- Caching layer
- Performance optimization
- Advanced monitoring

---

## 📚 References

- [Shared Context Service Documentation](./python-scripts/shared_context_service.py)
- [Workflow Engine Documentation](./agent_workflows.py)
- [API Server Documentation](./api_server.py)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)

---

## ✅ Phase 0 Completion Checklist

- [ ] Agent Coordinator created and tested
- [ ] Agent Router created and tested
- [ ] Orchestrator Service created and tested
- [ ] All agents registered with coordinator
- [ ] API server integrated with orchestrator
- [ ] Health monitoring functional
- [ ] End-to-end tests passing
- [ ] Documentation complete
- [ ] Deployment scripts ready
- [ ] Team trained on orchestration system

---

**Document Version**: 1.0  
**Last Updated**: 2024-11-28  
**Status**: Phase 0 - Ready for Implementation

# Agent Team Quick Start Guide

## 🚀 5-Minute Setup

### Prerequisites Check
```bash
# Check Python
python --version  # Should be 3.8+

# Check MongoDB
mongosh --eval "db.runCommand({ ping: 1 })"

# Check environment variables
echo $OPENAI_API_KEY
echo $MONGODB_URI
```

### Step 1: Initialize System (2 minutes)
```bash
# Start orchestrator
python automated_agent_system.py --mode orchestrator

# In another terminal, verify
curl http://localhost:8000/agent/status
```

### Step 2: Register Agents (1 minute)
```bash
# Run registration script
python scripts/register_agents.py
```

### Step 3: Start Agents (2 minutes)
```bash
# Option A: Docker Compose (Recommended)
docker-compose -f docker-compose.agents.yml up -d

# Option B: Manual (Development)
./scripts/start_all_agents.sh
```

### Step 4: Verify (30 seconds)
```bash
# Check all agents are running
curl http://localhost:8000/agent/list

# Test routing
curl -X POST http://localhost:8000/agent/route \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a quote for Isodec 100mm"}'
```

## ✅ Verification Checklist

- [ ] Orchestrator running
- [ ] All 7 agents registered
- [ ] Task routing working
- [ ] Health checks passing
- [ ] Monitoring dashboard accessible

## 🎯 Agent Roles Summary

| Agent | Role | Port | Status Endpoint |
|-------|------|------|-----------------|
| Orchestrator | System Coordinator | 8000 | `/agent/status` |
| Sales | Sales & Quotes | 8001 | `/agent/sales-001/status` |
| Support | Technical Support | 8002 | `/agent/support-001/status` |
| Router | Intent Routing | 8003 | `/agent/router-001/status` |
| Follow-up | Follow-ups | 8004 | `/agent/followup-001/status` |
| Analytics | Reports | 8005 | `/agent/analytics-001/status` |
| Workflow | Workflows | 8006 | `/agent/workflow-001/status` |

## 📋 Common Commands

### Start Single Agent
```bash
python -m agents.sales_agent --agent-id sales-001
```

### Check Agent Status
```bash
curl http://localhost:8000/agent/sales-001/status
```

### Submit Test Task
```bash
curl -X POST http://localhost:8000/agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "quote_creation",
    "payload": {"product": "isodec", "thickness": "100mm"},
    "priority": "HIGH"
  }'
```

### View Task Queue
```bash
curl http://localhost:8000/agent/queue
```

### Get Metrics
```bash
curl http://localhost:8000/agent/metrics
```

## 🆘 Troubleshooting

### Agent Not Starting
```bash
# Check logs
tail -f logs/orchestrator.log

# Check port availability
netstat -an | grep 8000
```

### Task Not Routing
```bash
# Check router status
curl http://localhost:8000/agent/router-001/status

# Test routing directly
python scripts/test_routing.py
```

### Agent Unavailable
```bash
# Restart agent
docker-compose -f docker-compose.agents.yml restart sales-agent

# Check health
curl http://localhost:8000/agent/sales-001/health
```

## 📚 Next Steps

1. Read `AGENT_TEAM_DEPLOYMENT_PLAN.md` for detailed setup
2. Review `AGENT_TEAM_INSTRUCTIONS.md` for role-specific guidance
3. Check `PHASE_0_ORCHESTRATION_REVIEW.md` for architecture details

## 🔗 Quick Links

- **Dashboard**: http://localhost:3000/agents
- **API Docs**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics
- **Health**: http://localhost:8000/health

---

**Ready to deploy?** Run `./scripts/deploy_agent_team.sh` for automated setup!

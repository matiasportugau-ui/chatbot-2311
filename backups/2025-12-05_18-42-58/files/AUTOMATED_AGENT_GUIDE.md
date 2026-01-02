# Automated Agent System - User Guide

## Overview

The Automated Agent System is a unified orchestration platform that manages multiple AI agents, automates tasks, schedules workflows, and provides comprehensive monitoring for the BMC quotation system.

## Quick Start

### Starting the Agent System

```bash
# Using bmc_system.py
python bmc_system.py --mode agent

# Or directly
python automated_agent_system.py --mode interactive

# With IA integration
python automated_agent_system.py --mode interactive --ia
```

### Interactive Mode Commands

Once started, you can use these commands:

- `status` - Show system status
- `health` - Perform health check
- `agents` - List registered agents
- `schedules` - List scheduled tasks
- `workflows` - List available workflows
- `metrics` - Show metrics
- `alerts` - Show alerts
- `quit` - Exit

## Core Components

### 1. Agent Coordinator

Manages agent registry, task distribution, and health monitoring.

**Key Features:**
- Agent registration and lifecycle management
- Task queue with priorities
- Health checks and recovery
- Load balancing

**Usage:**
```python
from agent_coordinator import get_coordinator

coordinator = get_coordinator()
coordinator.start()

# Register an agent
agent_id = coordinator.register_agent(
    agent_type="sales",
    agent_instance=my_agent,
    capabilities=["quote_creation", "sales"]
)

# Submit a task
task_id = coordinator.submit_task(
    task_type="create_quote",
    payload={"cliente": "John Doe", "producto": "isodec"},
    priority=TaskPriority.HIGH
)
```

### 2. Agent Router

Intelligently routes messages and tasks to appropriate agents based on intent, context, and capabilities.

**Key Features:**
- Intent analysis
- Context-aware routing
- Agent capability matching
- Fallback mechanisms

**Usage:**
```python
from agent_router import get_router, RoutingContext

router = get_router()

context = RoutingContext(
    message="Quiero una cotización",
    user_id="user123",
    urgency="normal"
)

decision = router.route_message("Quiero una cotización", context)
print(f"Routed to: {decision.agent_id}")
```

### 3. Agent Scheduler

Manages task scheduling with cron-based and event-driven triggers.

**Key Features:**
- Recurring task scheduling
- Event-driven triggers
- Task queue management
- Schedule management

**Usage:**
```python
from agent_scheduler import get_scheduler, ScheduleType

scheduler = get_scheduler()
scheduler.start()

# Schedule a recurring task
schedule_id = scheduler.schedule_task(
    task_type="follow_up",
    payload={"message": "Follow-up message"},
    schedule="1 hour",
    schedule_type=ScheduleType.RECURRING
)

# Trigger an event
scheduler.trigger_event("quote_created", {"quote_id": "COT-123"})
```

### 4. Workflow Engine

Executes multi-step automated workflows with conditional branching.

**Key Features:**
- Predefined workflows
- Conditional branching
- Workflow state persistence
- Error handling and retries

**Usage:**
```python
from agent_workflows import get_workflow_engine

engine = get_workflow_engine()

# Execute a workflow
execution_id = engine.execute_workflow(
    workflow_id="followup_workflow",
    initial_data={"phone": "59899123456", "quote_id": "COT-123"}
)

# Check status
status = engine.get_execution_status(execution_id)
```

### 5. Agent Monitoring

Provides real-time metrics, alerts, and performance tracking.

**Key Features:**
- Real-time metrics collection
- Alert generation
- Performance tracking
- Dashboard data

**Usage:**
```python
from agent_monitoring import get_monitoring

monitoring = get_monitoring()
monitoring.start()

# Get metrics
metrics = monitoring.get_metrics(agent_id="agent123", hours=1)

# Get alerts
alerts = monitoring.get_alerts(level=AlertLevel.WARNING, limit=10)

# Get dashboard data
dashboard = monitoring.get_dashboard_data()
```

## API Endpoints

The agent system exposes REST API endpoints through `api_server.py`:

### Task Management

- `POST /agent/tasks` - Submit a task
- `GET /agent/status` - Get agent system status
- `GET /agent/metrics` - Get performance metrics
- `GET /agent/alerts` - Get alerts
- `GET /agent/dashboard` - Get dashboard data

### Scheduling

- `POST /agent/schedule` - Schedule a task
- `GET /agent/schedules` - List scheduled tasks

### Workflows

- `GET /agent/workflows` - List available workflows
- `POST /agent/workflows/execute` - Execute a workflow
- `GET /agent/workflows/{execution_id}` - Get workflow status

## Configuration

Configuration is managed through `agent_config.json` and `agent_config.py`:

```python
from agent_config import get_config

config = get_config()

# Get configuration values
max_tasks = config.get("agents.max_concurrent_tasks", 10)
error_threshold = config.get("monitoring.thresholds.error_rate", 0.1)

# Update configuration
config.set("agents.max_concurrent_tasks", 20)
config.save_config()
```

## Proactive Actions

The system includes several proactive automation features:

### Quote Follow-ups

Automatically sends follow-up messages after 24, 48, and 72 hours:

```python
from proactive_agent_actions import get_proactive_actions

proactive = get_proactive_actions()
proactive.schedule_quote_followups()
```

### Abandoned Cart Recovery

Recovers conversations with incomplete quote requests:

```python
proactive.recover_abandoned_carts()
```

### Product Recommendations

Recommends products based on conversation history:

```python
recommendations = proactive.recommend_products(conversation)
```

## Best Practices

1. **Agent Registration**: Register agents with appropriate capabilities
2. **Task Priorities**: Use appropriate priorities for tasks
3. **Monitoring**: Regularly check metrics and alerts
4. **Configuration**: Adjust thresholds based on your needs
5. **Error Handling**: Implement proper error handling in agent tasks
6. **Resource Management**: Monitor resource usage and adjust limits

## Troubleshooting

### Agent Not Responding

1. Check agent health: `coordinator.health_check(agent_id)`
2. Check agent status: `coordinator.get_agent_status(agent_id)`
3. Review alerts: `monitoring.get_alerts(agent_id=agent_id)`

### Tasks Not Executing

1. Check task queue: `coordinator.task_queue.qsize()`
2. Check agent availability: `coordinator.get_agent_status()`
3. Review task status: `coordinator.get_task_status(task_id)`

### High Error Rates

1. Check monitoring alerts
2. Review agent metrics
3. Adjust error thresholds in configuration
4. Check agent health and recovery

## Examples

See the individual component files for detailed examples:
- `agent_coordinator.py` - Coordinator examples
- `agent_router.py` - Router examples
- `agent_scheduler.py` - Scheduler examples
- `agent_workflows.py` - Workflow examples
- `proactive_agent_actions.py` - Proactive actions examples

## Support

For more information, see:
- `AGENT_ARCHITECTURE.md` - Technical architecture
- `AGENT_WORKFLOWS.md` - Workflow definitions
- `ARCHITECTURE.md` - Overall system architecture


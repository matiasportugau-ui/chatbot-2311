# Agent System Architecture

## Overview

The Automated Agent System is a distributed, scalable architecture for managing multiple AI agents, automating tasks, and orchestrating workflows in the BMC quotation system.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  Automated Agent System                      │
│                  (automated_agent_system.py)                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│ Coordinator  │ │   Router   │ │ Scheduler  │
│              │ │            │ │            │
│ - Registry   │ │ - Intent   │ │ - Cron     │
│ - Tasks      │ │ - Routing  │ │ - Events   │
│ - Health     │ │ - Context  │ │ - Queue    │
└───────┬──────┘ └─────┬──────┘ └─────┬──────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│  Workflows   │ │ Monitoring │ │  Follow-up │
│              │ │            │ │   Agent    │
│ - Execution  │ │ - Metrics  │ │            │
│ - Steps      │ │ - Alerts   │ │ - AI Msgs  │
│ - State      │ │ - Dashboard│ │ - Multi-ch │
└──────────────┘ └────────────┘ └────────────┘
```

## Component Details

### 1. Agent Coordinator

**Purpose**: Central orchestration and task management

**Responsibilities**:
- Agent registry and lifecycle management
- Task distribution
- Health monitoring and recovery
- Task queue management

**Key Classes**:
- `AgentCoordinator`: Main coordinator class
- `AgentInfo`: Agent metadata
- `Task`: Task definition
- `AgentStatus`: Agent status enumeration
- `TaskPriority`: Task priority levels

**Data Flow**:
```
Task Submission → Task Queue → Agent Selection → Task Execution → Result
```

### 2. Agent Router

**Purpose**: Intelligent message and task routing

**Responsibilities**:
- Intent analysis
- Context-aware routing
- Agent capability matching
- Fallback mechanisms

**Key Classes**:
- `AgentRouter`: Main router class
- `RoutingContext`: Routing context information
- `RoutingDecision`: Routing decision result
- `IntentType`: Intent enumeration

**Routing Algorithm**:
1. Analyze message intent
2. Match agent capabilities
3. Check agent availability
4. Select best agent
5. Fallback if no match

### 3. Agent Scheduler

**Purpose**: Task scheduling and event management

**Responsibilities**:
- Cron-based scheduling
- Event-driven triggers
- Recurring task management
- Schedule persistence

**Key Classes**:
- `AgentScheduler`: Main scheduler class
- `ScheduledTask`: Scheduled task definition
- `ScheduleType`: Schedule type enumeration

**Schedule Types**:
- `ONCE`: One-time execution
- `RECURRING`: Recurring interval
- `CRON`: Cron expression
- `EVENT`: Event-driven

### 4. Workflow Engine

**Purpose**: Multi-step workflow execution

**Responsibilities**:
- Workflow definition and execution
- Conditional branching
- State persistence
- Error handling and retries

**Key Classes**:
- `WorkflowEngine`: Main engine class
- `WorkflowDefinition`: Workflow definition
- `WorkflowExecution`: Execution instance
- `WorkflowStep`: Workflow step definition
- `StepType`: Step type enumeration

**Step Types**:
- `TASK`: Execute a task
- `CONDITION`: Conditional branching
- `PARALLEL`: Parallel execution
- `DELAY`: Delay execution
- `CALLBACK`: Custom callback

### 5. Agent Monitoring

**Purpose**: Metrics, alerts, and performance tracking

**Responsibilities**:
- Real-time metrics collection
- Alert generation
- Performance tracking
- Dashboard data aggregation

**Key Classes**:
- `AgentMonitoring`: Main monitoring class
- `AgentMetrics`: Agent metrics data
- `Alert`: Alert definition
- `AlertLevel`: Alert severity levels

**Metrics Collected**:
- Tasks completed/failed
- Average response time
- Success/error rates
- Uptime percentage
- Resource usage

### 6. Follow-up Agent

**Purpose**: Automated follow-up messages

**Responsibilities**:
- Find pending follow-ups
- Generate AI-powered messages
- Multi-channel delivery
- Effectiveness tracking

**Key Features**:
- AI-powered message generation
- Multi-channel support (WhatsApp, Email, n8n)
- Integration with coordinator
- Effectiveness tracking

### 7. Proactive Actions

**Purpose**: Automated proactive behaviors

**Responsibilities**:
- Quote follow-ups
- Abandoned cart recovery
- Product recommendations
- Campaign automation

**Key Features**:
- Automatic quote follow-ups (24/48/72h)
- Abandoned cart recovery
- Product recommendations
- Seasonal campaigns

## Data Flow

### Task Execution Flow

```
1. Task Submission
   ↓
2. Task Queue (Priority Queue)
   ↓
3. Agent Selection (Router/Coordinator)
   ↓
4. Task Distribution
   ↓
5. Agent Execution
   ↓
6. Result Collection
   ↓
7. Metrics Update
   ↓
8. Alert Generation (if needed)
```

### Message Routing Flow

```
1. Message Received
   ↓
2. Intent Analysis (Router)
   ↓
3. Context Building
   ↓
4. Agent Selection
   ↓
5. Capability Matching
   ↓
6. Routing Decision
   ↓
7. Task Submission (if needed)
```

### Workflow Execution Flow

```
1. Workflow Triggered
   ↓
2. Workflow Definition Loaded
   ↓
3. Start Step Execution
   ↓
4. Step Execution
   ↓
5. Result Evaluation
   ↓
6. Next Step Determination
   ↓
7. Conditional Branching (if condition step)
   ↓
8. Continue or Complete
```

## Integration Points

### With IA System

- Uses `IAConversacionalIntegrada` for AI-powered features
- Integrates with function calling for autonomous actions
- Leverages conversation context for routing

### With MongoDB

- Stores conversation history
- Tracks follow-ups
- Persists workflow state
- Stores metrics and alerts

### With API Server

- Exposes REST endpoints for agent management
- Provides dashboard data
- Enables remote task submission
- Supports workflow execution

## Scalability Considerations

### Horizontal Scaling

- Multiple coordinator instances (with shared state)
- Distributed task queue
- Load balancing across agents

### Vertical Scaling

- Configurable task limits
- Adjustable monitoring intervals
- Resource usage tracking

### Performance Optimization

- Task queue prioritization
- Agent health-based routing
- Metrics caching
- Efficient state management

## Security Considerations

- Agent authentication
- Task authorization
- Input validation
- Rate limiting
- Error handling

## Error Handling

- Graceful degradation
- Automatic retries
- Fallback mechanisms
- Alert generation
- Error logging

## Configuration

Configuration is managed through:
- `agent_config.json`: JSON configuration file
- `agent_config.py`: Python configuration manager
- Environment variables: Runtime overrides

## Monitoring and Observability

- Real-time metrics
- Alert system
- Dashboard data
- Health checks
- Performance tracking

## Future Enhancements

- Distributed coordination
- Advanced load balancing
- Machine learning for routing
- Enhanced workflow capabilities
- Real-time collaboration


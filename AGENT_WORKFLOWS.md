# Agent Workflows - Definitions and Usage

## Overview

Workflows are multi-step automated processes that can execute tasks, make decisions, and handle complex automation scenarios in the agent system.

## Predefined Workflows

### 1. Follow-up Workflow

**ID**: `followup_workflow`

**Purpose**: Automated follow-up message workflow

**Steps**:
1. **Check Conversation Status** - Verify conversation needs follow-up
2. **Generate Follow-up Message** - Create personalized message (AI-powered)
3. **Send Follow-up Message** - Deliver via WhatsApp
4. **Log Result** - Record follow-up in database

**Usage**:
```python
from agent_workflows import get_workflow_engine

engine = get_workflow_engine()

execution_id = engine.execute_workflow(
    workflow_id="followup_workflow",
    initial_data={
        "phone": "59899123456",
        "quote_id": "COT-123",
        "interval": "24h"
    }
)
```

### 2. Quote Creation Workflow

**ID**: `quote_workflow`

**Purpose**: Automated quote creation with validation

**Steps**:
1. **Validate Quote Data** - Check data completeness
2. **Check Condition** - Determine if data is complete
3. **Request Missing Data** - If incomplete, request missing information
4. **Create Quote** - If complete, create the quote
5. **Send Confirmation** - Send confirmation message

**Usage**:
```python
execution_id = engine.execute_workflow(
    workflow_id="quote_workflow",
    initial_data={
        "cliente": {
            "nombre": "John Doe",
            "telefono": "59899123456"
        },
        "producto": "isodec",
        "espesor": "100mm",
        "largo": 10,
        "ancho": 5
    }
)
```

## Workflow Definition Structure

### Workflow Definition

```python
@dataclass
class WorkflowDefinition:
    workflow_id: str
    name: str
    description: str
    version: str
    steps: List[WorkflowStep]
    start_step_id: str
    metadata: Dict[str, Any]
```

### Workflow Step

```python
@dataclass
class WorkflowStep:
    step_id: str
    step_type: StepType
    name: str
    config: Dict[str, Any]
    next_steps: List[str]
    condition: Optional[str]
    timeout: Optional[int]
    retry_count: int
    max_retries: int
```

## Step Types

### 1. Task Step

Executes a task through the agent coordinator.

**Configuration**:
```json
{
    "task_type": "create_quote",
    "payload": {
        "cliente": "...",
        "producto": "..."
    },
    "required_capabilities": ["quote_creation"]
}
```

### 2. Condition Step

Evaluates a condition and branches to different steps.

**Configuration**:
```json
{
    "condition": "workflow_data.complete == true",
    "next_steps": ["step_if_true", "step_if_false"]
}
```

**Condition Syntax**:
- Simple comparisons: `workflow_data.value > 10`
- Boolean expressions: `workflow_data.complete == true`
- Access nested data: `workflow_data.cliente.nombre`

### 3. Delay Step

Delays execution for a specified duration.

**Configuration**:
```json
{
    "delay": 60
}
```

### 4. Parallel Step

Executes multiple steps in parallel (future enhancement).

**Configuration**:
```json
{
    "parallel_steps": ["step1", "step2", "step3"]
}
```

### 5. Callback Step

Executes a custom callback function.

**Configuration**:
```json
{
    "callback": "custom_handler_function"
}
```

## Creating Custom Workflows

### Example: Custom Follow-up Workflow

```python
from agent_workflows import WorkflowDefinition, WorkflowStep, StepType

custom_workflow = WorkflowDefinition(
    workflow_id="custom_followup",
    name="Custom Follow-up Workflow",
    description="Custom follow-up with additional steps",
    version="1.0",
    steps=[
        WorkflowStep(
            step_id="check_time",
            step_type=StepType.CONDITION,
            name="Check Time",
            config={},
            condition="workflow_data.hour >= 9 and workflow_data.hour <= 18",
            next_steps=["send_message", "schedule_later"]
        ),
        WorkflowStep(
            step_id="send_message",
            step_type=StepType.TASK,
            name="Send Message",
            config={
                "task_type": "send_message",
                "payload": {"phone": "{{workflow_data.phone}}"}
            },
            next_steps=["log_result"]
        ),
        WorkflowStep(
            step_id="schedule_later",
            step_type=StepType.TASK,
            name="Schedule for Later",
            config={
                "task_type": "schedule_task",
                "payload": {"delay": "2 hours"}
            },
            next_steps=[]
        ),
        WorkflowStep(
            step_id="log_result",
            step_type=StepType.TASK,
            name="Log Result",
            config={
                "task_type": "log_followup"
            },
            next_steps=[]
        )
    ],
    start_step_id="check_time"
)

# Register workflow
engine.register_workflow(custom_workflow)
```

## Workflow Execution

### Execution Lifecycle

1. **Pending** - Workflow is queued
2. **Running** - Workflow is executing
3. **Waiting** - Waiting for condition or delay
4. **Completed** - Successfully completed
5. **Failed** - Execution failed
6. **Cancelled** - Manually cancelled

### Execution Status

```python
status = engine.get_execution_status(execution_id)

# Status includes:
# - execution_id
# - workflow_id
# - status
# - current_step_id
# - step_results
# - workflow_data
# - started_at
# - completed_at
# - error
```

## Error Handling

### Retry Logic

Steps can specify retry behavior:

```python
WorkflowStep(
    step_id="retry_step",
    step_type=StepType.TASK,
    name="Retry Step",
    config={...},
    max_retries=3,  # Retry up to 3 times
    next_steps=[]
)
```

### Error Recovery

- Automatic retries for failed steps
- Error logging and alerting
- Graceful degradation
- Fallback steps

## Best Practices

1. **Step Naming**: Use descriptive step names
2. **Error Handling**: Always include error handling steps
3. **Timeouts**: Set appropriate timeouts for long-running tasks
4. **Conditional Logic**: Use condition steps for branching
5. **State Management**: Keep workflow data minimal and focused
6. **Testing**: Test workflows with sample data before production

## Workflow Examples

### Simple Task Workflow

```python
simple_workflow = WorkflowDefinition(
    workflow_id="simple_task",
    name="Simple Task",
    description="Execute a single task",
    steps=[
        WorkflowStep(
            step_id="execute_task",
            step_type=StepType.TASK,
            name="Execute Task",
            config={"task_type": "my_task", "payload": {}},
            next_steps=[]
        )
    ],
    start_step_id="execute_task"
)
```

### Conditional Workflow

```python
conditional_workflow = WorkflowDefinition(
    workflow_id="conditional",
    name="Conditional Workflow",
    description="Workflow with conditional branching",
    steps=[
        WorkflowStep(
            step_id="check_condition",
            step_type=StepType.CONDITION,
            name="Check Condition",
            condition="workflow_data.value > 10",
            next_steps=["high_value", "low_value"]
        ),
        WorkflowStep(
            step_id="high_value",
            step_type=StepType.TASK,
            name="Handle High Value",
            config={"task_type": "handle_high"},
            next_steps=[]
        ),
        WorkflowStep(
            step_id="low_value",
            step_type=StepType.TASK,
            name="Handle Low Value",
            config={"task_type": "handle_low"},
            next_steps=[]
        )
    ],
    start_step_id="check_condition"
)
```

## API Usage

### Execute Workflow via API

```bash
POST /agent/workflows/execute
{
    "workflow_id": "followup_workflow",
    "initial_data": {
        "phone": "59899123456",
        "quote_id": "COT-123"
    }
}
```

### Get Workflow Status

```bash
GET /agent/workflows/{execution_id}
```

### List Workflows

```bash
GET /agent/workflows
```

## Troubleshooting

### Workflow Stuck

1. Check execution status
2. Review step results
3. Check for errors in logs
4. Verify workflow definition

### Step Failing

1. Check step configuration
2. Verify task type exists
3. Check agent availability
4. Review error messages

### Condition Not Working

1. Verify condition syntax
2. Check workflow data structure
3. Test condition separately
4. Review condition evaluation


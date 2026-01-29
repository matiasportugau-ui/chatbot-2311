# Gravity Agent - Development Automation Orchestrator

## Overview

The **Gravity Agent** is a specialized AI agent designed to interpret and orchestrate automated development for the chatbot-2311 project. It acts as the central coordination point (gravity) for all automated development activities.

## Capabilities

### 🔍 Interpretation
- **Project State Analysis**: Deep analysis of current project state, phases, and progress
- **Blocker Detection**: Identifies blockers and dependencies that prevent progress
- **Opportunity Identification**: Finds optimization opportunities and improvements
- **Context Awareness**: Maintains full context of project history and state

### 🚀 Orchestration
- **Automated Execution**: Orchestrates phase execution using the MainOrchestrator
- **Dependency Management**: Ensures dependencies are met before execution
- **Auto-Approval**: Supports automated approval for seamless execution
- **Phase Coordination**: Manages multi-phase execution workflows

### 👁️ Monitoring
- **Real-time Monitoring**: Tracks execution status and progress
- **Status Reporting**: Provides detailed status reports
- **Health Checks**: Monitors project health and identifies issues

### 🔄 Adaptation
- **Dynamic Planning**: Adapts plans based on changing context
- **Priority Adjustment**: Re-prioritizes tasks based on new information
- **Dependency Updates**: Updates execution plans when dependencies change

## Installation

The Gravity Agent is part of the agents package and uses existing orchestrator infrastructure:

```bash
# Ensure orchestrator dependencies are installed
pip install -r scripts/orchestrator/requirements.txt

# The agent is ready to use
python agents/gravity_agent.py --help
```

## Usage

### Basic Usage

```bash
# Run full cycle (interpret → orchestrate → monitor)
python agents/gravity_agent.py --mode full_cycle

# Interpret project state only
python agents/gravity_agent.py --mode interpret

# Orchestrate development
python agents/gravity_agent.py --mode orchestrate --auto-approve

# Monitor execution
python agents/gravity_agent.py --mode monitor
```

### Advanced Usage

```bash
# Execute specific phase range
python agents/gravity_agent.py --mode full_cycle --start-phase 0 --end-phase 5

# Execute single phase
python agents/gravity_agent.py --mode orchestrate --phase 3

# Use custom config
python agents/gravity_agent.py --mode full_cycle --config custom_config.json

# Save report to specific file
python agents/gravity_agent.py --mode full_cycle --output my_report.json
```

### Programmatic Usage

```python
from agents.gravity_agent import GravityAgent

# Initialize agent
agent = GravityAgent()

# Interpret project state
interpretation = agent.interpret_project_state(deep_analysis=True)

# Orchestrate development
result = agent.orchestrate_development(
    target_phase=0,
    auto_approve=True,
    max_phases=5
)

# Run full cycle
result = agent.run_full_cycle(
    start_phase=0,
    end_phase=15,
    auto_approve=True
)

# Save report
report_path = agent.save_report()
```

## Operation Modes

### 1. Interpret Mode
Analyzes and interprets the current project state without executing anything.

**Use when:**
- You want to understand current project status
- You need recommendations for next steps
- You want to identify blockers or opportunities

### 2. Orchestrate Mode
Executes automated development phases.

**Use when:**
- You want to execute specific phases
- You have a clear execution plan
- You want automated phase execution

### 3. Monitor Mode
Monitors ongoing execution without making changes.

**Use when:**
- Execution is already running
- You want to check status
- You need real-time monitoring

### 4. Adapt Mode
Adapts plans based on new context.

**Use when:**
- Context has changed
- Priorities need adjustment
- Dependencies have changed

### 5. Full Cycle Mode (Default)
Runs complete interpret → orchestrate → monitor cycle.

**Use when:**
- You want complete automation
- You want end-to-end execution
- You want comprehensive monitoring

## Configuration

The agent uses the orchestrator configuration by default:

```json
{
  "orchestrator_config": "scripts/orchestrator/config/orchestrator_config.json"
}
```

You can override this by:
1. Passing `--config` argument
2. Setting config in code: `GravityAgent({"orchestrator_config": "path/to/config.json"})`

## Integration

### With MainOrchestrator

The Gravity Agent integrates seamlessly with the existing MainOrchestrator:

```python
from agents.gravity_agent import GravityAgent
from scripts.orchestrator.main_orchestrator import MainOrchestrator

agent = GravityAgent()
# Agent automatically initializes MainOrchestrator internally
```

### With State Manager

The agent uses the StateManager for state tracking:

```python
agent = GravityAgent()
# Access state manager
state_manager = agent.state_manager
current_phase = state_manager.get_current_phase()
```

### With Context Manager

The agent maintains context through ContextManager:

```python
agent = GravityAgent()
# Context is automatically managed
interpretation = agent.interpret_project_state()
# Context includes full project history
```

## Output and Reports

The agent generates detailed reports in JSON format:

```json
{
  "agent": "GravityAgent",
  "timestamp": "2024-01-01T12:00:00",
  "interpretations": [...],
  "executions": [...],
  "config": {...}
}
```

Reports are automatically saved with timestamps:
- `gravity_agent_report_YYYYMMDD_HHMMSS.json`

## Examples

### Example 1: Quick Status Check

```bash
python agents/gravity_agent.py --mode interpret
```

Output:
```
📊 PROJECT STATE INTERPRETATION
────────────────────────────────────────────────────────────
Current State: ready
Current Phase: 3
Completed Phases: 3
Pending Phases: 13
Confidence: 0.85

✅ Recommendations (3):
   - Proceed with Phase 3
   - Verify dependencies are met
   - Monitor for blockers
```

### Example 2: Execute Next Phase

```bash
python agents/gravity_agent.py --mode orchestrate --phase 4 --auto-approve
```

### Example 3: Full Automation

```bash
python agents/gravity_agent.py --mode full_cycle --start-phase 0 --end-phase 15
```

## Troubleshooting

### Agent Not Initializing

**Problem**: Agent fails to initialize orchestrator

**Solution**:
```bash
# Check orchestrator dependencies
pip install -r scripts/orchestrator/requirements.txt

# Verify config file exists
ls scripts/orchestrator/config/orchestrator_config.json
```

### Blockers Detected

**Problem**: Agent detects blockers and won't proceed

**Solution**:
```bash
# Review blockers
python agents/gravity_agent.py --mode interpret

# Resolve blockers manually
# Then retry orchestration
```

### AI Integration Not Available

**Problem**: AI-powered analysis not working

**Solution**:
- Agent will fall back to basic analysis
- Ensure `model_integrator` is available for AI features
- Basic functionality works without AI

## Best Practices

1. **Always Interpret First**: Run interpret mode before orchestration to understand state
2. **Monitor Progress**: Use monitor mode during long executions
3. **Save Reports**: Keep reports for audit and debugging
4. **Handle Blockers**: Resolve blockers before proceeding
5. **Use Full Cycle**: For complete automation, use full_cycle mode

## Architecture

```
GravityAgent
├── Interpretation Engine
│   ├── Project State Analysis
│   ├── Blocker Detection
│   └── AI-Powered Analysis
├── Orchestration Engine
│   ├── MainOrchestrator Integration
│   ├── Phase Execution
│   └── Dependency Management
├── Monitoring Engine
│   ├── Status Tracking
│   └── Health Checks
└── Adaptation Engine
    ├── Plan Updates
    └── Priority Adjustment
```

## Related Documentation

- [Orchestrator README](../scripts/orchestrator/README.md)
- [Orchestrator Quick Start](../scripts/orchestrator/QUICK_START.md)
- [Agent Handoff Guide](../scripts/orchestrator/AGENT_HANDOFF_GUIDE.md)

## Support

For issues or questions:
1. Check orchestrator logs: `scripts/orchestrator/logs/`
2. Review agent reports: `gravity_agent_report_*.json`
3. Check state manager: `consolidation/state/`

---

**Gravity Agent** - The central point of coordination for automated development 🌌

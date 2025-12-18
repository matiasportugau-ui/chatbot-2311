# Gravity Orchestrator Agent

The **Gravity Orchestrator Agent** is a specialized agent designed to interpret and orchestrate the automated development of the Chatbot project. It sits on top of the existing orchestration scripts to provide high-level management and interpretation.

## Purpose

- **Interpret**: Analyze the current state of the project, including phase completion, errors, and overall health.
- **Orchestrate**: Drive the `MainOrchestrator` to execute development phases (0-15) automatically.

## Usage

### 1. Interpret Current State

To get a quick summary of where the project stands:

```bash
python AI_AGENTS/gravity_orchestrator.py --mode interpret
```

### 2. Orchestrate Development

To start or resume the automated development process:

```bash
python AI_AGENTS/gravity_orchestrator.py --mode orchestrate
```

### 3. Dry Run

To simulate orchestration without making changes:

```bash
python AI_AGENTS/gravity_orchestrator.py --mode dry-run
```

## Integration

This agent integrates with:
- `scripts/orchestrator/main_orchestrator.py`: The core execution engine.
- `scripts/orchestrator/state_manager.py`: For tracking project state.

## Future Enhancements

- **Auto-Fix**: Capability to invoke other specialized agents to fix errors when a phase fails.
- **Deep Analysis**: More detailed interpretation of logs using LLMs.

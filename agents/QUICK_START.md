# Gravity Agent - Quick Start Guide

## 🚀 Quick Start

### 1. Basic Usage

```bash
# Run full cycle (recommended for first use)
python agents/gravity_agent.py --mode full_cycle

# Or use the convenience script
./agents/run_gravity_agent.sh --mode full_cycle
```

### 2. Check Project Status

```bash
# Interpret project state without executing
python agents/gravity_agent.py --mode interpret
```

### 3. Execute Development Phases

```bash
# Execute phases 0-5
python agents/gravity_agent.py --mode orchestrate --start-phase 0 --end-phase 5

# Execute single phase
python agents/gravity_agent.py --mode orchestrate --phase 3
```

### 4. Monitor Execution

```bash
# Monitor current execution
python agents/gravity_agent.py --mode monitor
```

## 📋 Common Workflows

### Workflow 1: First-Time Setup

```bash
# 1. Check current state
python agents/gravity_agent.py --mode interpret

# 2. If no blockers, run full cycle
python agents/gravity_agent.py --mode full_cycle --start-phase 0 --end-phase 15
```

### Workflow 2: Continue from Current Phase

```bash
# 1. Check status
python agents/gravity_agent.py --mode interpret

# 2. Continue execution
python agents/gravity_agent.py --mode orchestrate --auto-approve
```

### Workflow 3: Execute Specific Range

```bash
# Execute phases 5-10
python agents/gravity_agent.py --mode full_cycle --start-phase 5 --end-phase 10
```

## 🎯 What Each Mode Does

| Mode | Purpose | When to Use |
|------|---------|-------------|
| `interpret` | Analyze project state | Before execution, to understand status |
| `orchestrate` | Execute phases | When you want to run specific phases |
| `monitor` | Check status | During or after execution |
| `adapt` | Update plans | When context changes |
| `full_cycle` | Complete automation | For end-to-end execution |

## ⚙️ Configuration

The agent uses the orchestrator config by default:
- Config file: `scripts/orchestrator/config/orchestrator_config.json`
- Auto-approval: Enabled by default
- Execution mode: Automated

## 📊 Output

Reports are automatically saved:
- Location: Project root
- Format: `gravity_agent_report_YYYYMMDD_HHMMSS.json`
- Contains: Interpretations, executions, monitoring data

## 🔧 Troubleshooting

### Agent won't start

```bash
# Check dependencies
pip install -r scripts/orchestrator/requirements.txt

# Verify config exists
ls scripts/orchestrator/config/orchestrator_config.json
```

### Blockers detected

```bash
# Review blockers
python agents/gravity_agent.py --mode interpret

# Resolve blockers manually, then retry
```

### Need help

```bash
# Show help
python agents/gravity_agent.py --help

# See examples
python agents/examples/gravity_agent_example.py
```

## 📚 Next Steps

1. Read [GRAVITY_AGENT_README.md](./GRAVITY_AGENT_README.md) for detailed documentation
2. Check [examples](./examples/gravity_agent_example.py) for code examples
3. Review [Orchestrator README](../scripts/orchestrator/README.md) for underlying system

---

**Ready to orchestrate your development!** 🌌

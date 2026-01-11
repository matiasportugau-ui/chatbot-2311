# 🚀 Quick Start - Gravity Agent

> Get started with the Gravity Agent in under 5 minutes

---

## 📦 Prerequisites

```bash
# Verify GitHub CLI is authenticated
gh auth status

# Verify Python
python --version  # Should be 3.10+
```

---

## ⚡ Quick Commands

### 1. Check Status

```bash
python AI_AGENTS/gravity_agent.py --status
```

Output:
```json
{
  "mode": "full_auto",
  "current_phase": 0,
  "ai_enabled": true,
  "auto_approve": true
}
```

### 2. Analyze a PR

```bash
# Analyze PR #87 (Training System)
python AI_AGENTS/gravity_agent.py --pr 87
```

Output:
```
🔍 Analyzing PR #87...
✅ Analysis complete!
   Title: Implement training/evaluation system
   Tasks: 5
   Phases: [7, 10]
   Agents: ['ValidationAgent', 'PerformanceAgent']
```

### 3. Execute a Phase

```bash
# Execute Phase 7 (Testing Framework)
python AI_AGENTS/gravity_agent.py --phase 7
```

### 4. Run Full Pipeline

```bash
# Run all 24 phases (takes time!)
python AI_AGENTS/gravity_agent.py --full-pipeline
```

---

## 🐍 Python Usage

### Basic Example

```python
from AI_AGENTS.gravity_agent import GravityAgent

# Initialize
agent = GravityAgent()

# Check status
print(agent.get_status())
```

### Analyze PR

```python
from AI_AGENTS.gravity_agent import GravityAgent

agent = GravityAgent()

# Analyze PR
analysis = agent.analyze_pr(87)

# Print results
print(f"PR: {analysis.title}")
print(f"Tasks: {len(analysis.tasks_generated)}")
for task in analysis.tasks_generated:
    print(f"  - [{task.priority.value}] {task.title}")
```

### Execute Tasks

```python
from AI_AGENTS.gravity_agent import GravityAgent

agent = GravityAgent()

# Analyze and execute
analysis = agent.analyze_pr(87)
if analysis:
    results = agent.orchestrate_development(analysis.tasks_generated)
    print(f"Completed: {results['completed']}/{results['total_tasks']}")
```

### Natural Language Input

```python
from AI_AGENTS.gravity_agent import GravityAgent

agent = GravityAgent()

# Interpret and execute
result = agent.interpret_and_execute(
    "Ejecuta el benchmark del sistema de cotizaciones"
)
```

---

## 📊 Modes

| Mode | Command | Description |
|------|---------|-------------|
| `full_auto` | `--mode full_auto` | Fully automated (default) |
| `interpret` | `--mode interpret` | Analyze only, don't execute |
| `orchestrate` | `--mode orchestrate` | Coordinate agents |
| `execute` | `--mode execute` | Execute specific tasks |
| `monitor` | `--mode monitor` | Monitor progress |

---

## 📁 Output Files

After running, check these locations:

| File | Location |
|------|----------|
| PR Analysis | `consolidation/pr_analysis/pr_87_analysis.json` |
| Execution Report | `consolidation/execution_reports/` |
| State | `consolidation/gravity_state.json` |

---

## 🎯 Common Workflows

### Workflow 1: PR to Production

```bash
# 1. Analyze PR
python AI_AGENTS/gravity_agent.py --pr 87

# 2. Execute generated tasks (auto-executed in full_auto mode)

# 3. Check results
cat consolidation/pr_analysis/pr_87_analysis.json
```

### Workflow 2: Phase-by-Phase Execution

```bash
# Execute phases sequentially
for phase in 0 1 2 3 4 5 6 7; do
    python AI_AGENTS/gravity_agent.py --phase $phase
done
```

### Workflow 3: Training + Benchmarks

```python
from AI_AGENTS.gravity_agent import GravityAgent

agent = GravityAgent()

# Run training
agent.run_training_session("session_001")

# Run benchmarks
results = agent.run_benchmark("quotation")
print(f"Score: {results.get('score')}")
```

---

## ❓ Troubleshooting

### GitHub CLI Not Authenticated

```bash
gh auth login
```

### AI Features Not Available

```bash
# Set API key
export OPENAI_API_KEY=your_key_here

# Or use Groq
export GROQ_API_KEY=your_key_here
```

### PR Not Found

```bash
# Check PR exists
gh pr view 87
```

---

## 📚 Next Steps

1. Read [GRAVITY_AGENT_README.md](GRAVITY_AGENT_README.md) for full documentation
2. Review [GRAVITY_AGENT_PROMPT.md](GRAVITY_AGENT_PROMPT.md) for system prompt
3. Explore the consolidation plan phases
4. Try analyzing different PRs

---

**Ready to orchestrate? Run:**

```bash
python AI_AGENTS/gravity_agent.py --pr 87
```

🌍 **Gravity Agent** - *Making automated development effortless*

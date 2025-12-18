# 🌍 Gravity Agent

> **Master Orchestrator for Automated Development in Cursor Agent Mode**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Agent Mode](https://img.shields.io/badge/mode-agent--mode-green.svg)](https://cursor.sh)
[![Auto-Approve](https://img.shields.io/badge/auto--approve-enabled-success.svg)](https://cursor.sh)

---

## 📋 Overview

The **Gravity Agent** is a specialized AI agent designed for Cursor's Agent Mode that interprets and orchestrates automated development for the BMC Chatbot project. It serves as the master orchestrator, coordinating between multiple specialized agents to execute the 16-phase consolidation plan.

### Key Capabilities

| Capability | Description |
|------------|-------------|
| 🔍 **PR Interpretation** | Analyze GitHub PRs and extract actionable tasks |
| 🎭 **Orchestration** | Coordinate multi-phase development pipelines |
| 🤖 **Agent Coordination** | Delegate tasks to 14 specialized agents |
| 📚 **Training Management** | Run bot training with emoji-triggered corrections |
| 📊 **Benchmarking** | Execute performance benchmarks |
| ✅ **Quality Assurance** | Automated testing and validation |

---

## 🚀 Quick Start

### 1. Basic Usage

```bash
# Show status
python AI_AGENTS/gravity_agent.py --status

# Analyze a PR
python AI_AGENTS/gravity_agent.py --pr 87

# Run full pipeline
python AI_AGENTS/gravity_agent.py --full-pipeline
```

### 2. Python API

```python
from AI_AGENTS.gravity_agent import GravityAgent, GravityMode

# Initialize
agent = GravityAgent(mode=GravityMode.FULL_AUTO)

# Analyze PR
analysis = agent.analyze_pr(87)
print(f"Tasks: {len(analysis.tasks_generated)}")

# Execute tasks
results = agent.orchestrate_development(analysis.tasks_generated)
print(f"Completed: {results['completed']}/{results['total_tasks']}")
```

### 3. Natural Language

```python
agent = GravityAgent()
result = agent.interpret_and_execute(
    "Analiza el PR #87 y ejecuta las tareas de entrenamiento"
)
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GRAVITY AGENT                            │
│              Master Orchestrator (Agent Mode)                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│   │  INTERPRET  │ → │ ORCHESTRATE │ → │   EXECUTE   │    │
│   └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│   │ PR Analysis │    │Task Manager │    │Phase Runner │    │
│   │ Task Gen    │    │Agent Coord  │    │Test Runner  │    │
│   │ Risk Assess │    │Dependencies │    │Benchmarks   │    │
│   └─────────────┘    └─────────────┘    └─────────────┘    │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                    SPECIALIZED AGENTS                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Level 1: Core          Level 2: Consolidation               │
│  ├─ OrchestratorAgent   ├─ MergeAgent                       │
│  ├─ RepositoryAgent     └─ IntegrationAgent                 │
│  └─ DiscoveryAgent                                          │
│                                                              │
│  Level 3: Production    Level 4: Deployment                  │
│  ├─ SecurityAgent       ├─ CICDAgent                        │
│  ├─ InfrastructureAgent ├─ DisasterRecoveryAgent            │
│  ├─ ObservabilityAgent  └─ ValidationAgent                  │
│  └─ PerformanceAgent                                        │
│                                                              │
│  Level 5: Domain (Optional)                                  │
│  ├─ NLUAgent                                                │
│  └─ QuotationAgent                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Consolidation Phases

The Gravity Agent executes a 24-phase plan (8 preliminary + 16 main):

### Preliminary Phases (-8 to -1)

| Phase | Name | Description |
|-------|------|-------------|
| -8 | Preliminary Analysis | Initial system assessment |
| -7 | Environment Setup | Configure development environment |
| -6 | Dependencies Check | Verify all dependencies |
| -5 | Configuration Validation | Validate configuration files |
| -4 | Database Setup | Initialize MongoDB, Qdrant |
| -3 | Integration Check | Verify external integrations |
| -2 | Security Scan | Run security analysis |
| -1 | Final Preparation | Last checks before main phases |

### Main Phases (0 to 15)

| Phase | Name | Description |
|-------|------|-------------|
| 0 | Discovery & Analysis | Deep codebase analysis |
| 1 | Repository Consolidation | Merge and organize repos |
| 2 | Integration Layer | Setup integration points |
| 3 | API Consolidation | Unify API endpoints |
| 4 | Frontend Consolidation | Merge frontend components |
| 5 | Workflow Integration | Configure n8n workflows |
| 6 | Knowledge Base | Setup Qdrant vector DB |
| 7 | Testing Framework | Implement test suite |
| 8 | Documentation | Generate documentation |
| 9 | Security Hardening | Apply security measures |
| 10 | Performance Optimization | Optimize system performance |
| 11 | Observability | Setup monitoring & logging |
| 12 | CI/CD Pipeline | Configure GitHub Actions |
| 13 | Disaster Recovery | Implement backup strategies |
| 14 | Staging Deployment | Deploy to staging |
| 15 | Production Readiness | Final validation for production |

---

## 🔧 Configuration

### Environment Variables

```bash
# Model Integration
OPENAI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here

# GitHub
GITHUB_TOKEN=your_token_here

# Workspace
WORKSPACE_PATH=/workspace
```

### Agent Configuration

Edit `agent_config.json`:

```json
{
  "gravity_agent": {
    "enabled": true,
    "mode": "full_auto",
    "auto_approve": true,
    "execution": {
      "max_retries": 3,
      "retry_delay_seconds": 60
    }
  }
}
```

---

## 📊 PR Analysis

When analyzing a PR, the Gravity Agent:

1. **Fetches PR metadata** using `gh pr view`
2. **Categorizes files** by component and type
3. **Identifies affected phases** based on changes
4. **Assigns specialized agents** for each area
5. **Generates development tasks** with priorities
6. **Analyzes risks** and provides mitigations
7. **Saves analysis** to `consolidation/pr_analysis/`

### Example PR Analysis Output

```json
{
  "pr_number": 87,
  "title": "Implement training/evaluation system",
  "affected_phases": [7, 10],
  "affected_agents": ["ValidationAgent", "PerformanceAgent"],
  "affected_components": ["training_system", "benchmark_system"],
  "tasks_generated": [
    {
      "id": "PR87_P7_T1",
      "title": "[Phase 7] Training System Implementation",
      "priority": "P1",
      "agent": "ValidationAgent"
    }
  ],
  "risks": [
    {
      "risk": "Large change size",
      "probability": "medium",
      "impact": "high",
      "mitigation": "Break into smaller changes"
    }
  ]
}
```

---

## 🎮 CLI Reference

```bash
# General
python AI_AGENTS/gravity_agent.py --help
python AI_AGENTS/gravity_agent.py --status

# PR Analysis
python AI_AGENTS/gravity_agent.py --pr 87
python AI_AGENTS/gravity_agent.py --pr 87 --mode interpret

# Phase Execution
python AI_AGENTS/gravity_agent.py --phase 0
python AI_AGENTS/gravity_agent.py --phase 7 --mode execute

# Full Pipeline
python AI_AGENTS/gravity_agent.py --full-pipeline

# With Custom Input
python AI_AGENTS/gravity_agent.py --input "Run benchmarks for quotation system"
```

---

## 📈 Outputs

| Output | Location |
|--------|----------|
| PR Analysis | `consolidation/pr_analysis/pr_<N>_analysis.json` |
| Task Lists | `consolidation/pr_analysis/pr_<N>_tasks.md` |
| Execution Reports | `consolidation/execution_reports/` |
| Agent State | `consolidation/gravity_state.json` |
| Logs | `consolidation/logs/gravity_agent.log` |

---

## 🔗 Integration with PR #87

PR #87 introduces the Training/Evaluation System. The Gravity Agent integrates with:

### Training System

```python
agent = GravityAgent()

# Run training session
result = agent.run_training_session(
    session_id="training_20251218",
    corrections=[
        {
            "original": "El precio es $X",
            "correction": "Incluir precios específicos por espesor",
            "context": {"product": "Isodec"}
        }
    ]
)
```

### Benchmark System

```python
agent = GravityAgent()

# Run benchmarks
result = agent.run_benchmark(suite_name="quotation")
print(f"Score: {result.get('score')}")
```

---

## 🧪 Testing

```bash
# Run Gravity Agent tests
python -m pytest tests/test_gravity_agent.py -v

# Test PR analysis
python -c "from AI_AGENTS.gravity_agent import GravityAgent; GravityAgent().analyze_pr(87)"
```

---

## 📚 Related Documentation

- [GRAVITY_AGENT_PROMPT.md](GRAVITY_AGENT_PROMPT.md) - System prompt and configuration
- [QUICK_START_GRAVITY.md](QUICK_START_GRAVITY.md) - Quick start guide
- [EXECUTOR/execution_ai_agent.py](EXECUTOR/execution_ai_agent.py) - Execution agent
- [watcher_agent.py](watcher_agent.py) - Watcher agent

---

## ✅ Requirements

- Python 3.10+
- GitHub CLI (`gh`) authenticated
- OpenAI or Groq API key (optional, for AI features)
- Access to workspace repository

---

## 🔐 Security

- Uses `gh` CLI for authenticated GitHub access
- No secrets hardcoded in code
- Respects `.env` configuration
- Auto-approve mode is configurable

---

## 📝 License

Part of the BMC Chatbot System. See main repository for license.

---

**Created by Gravity Agent System** | Version 1.0.0 | December 2025

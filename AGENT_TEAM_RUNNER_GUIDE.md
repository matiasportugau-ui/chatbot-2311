# 🤖 Agent Team Runner Guide

**Version:** 1.0  
**Date:** 2025-01-12  
**Purpose:** Procedure for running the team of 12 agents for BMC Chatbot Platform consolidation

---

## 📋 Overview

This guide provides procedures for:
1. **Checking project status** before running agents
2. **Running the agent team** according to the unified 16-phase plan
3. **Monitoring execution** and handling issues

---

## 🎯 Quick Start

### 1. Check Project Status

```bash
# Check current project status
python scripts/check_project_status.py
```

This will show:
- Current phase progress
- Component status
- Integration status
- Security status
- Recommendations

### 2. Run Agent Team

```bash
# Full automated execution
python scripts/run_agent_team.py

# With options
python scripts/run_agent_team.py --mode automated --resume
```

### 3. View Agent Team Info

```bash
# Show agent team configuration
python scripts/run_agent_team.py --info

# Show current status
python scripts/run_agent_team.py --status
```

---

## 🤖 Agent Team Architecture

### 12-Agent Team Structure

#### **Nivel 1: Core Agents (3)**
1. **OrchestratorAgent** - Master coordinator (all phases)
2. **RepositoryAgent** - Git & workspace management (phases 1-8)
3. **DiscoveryAgent** - BMC + Technical discovery (phase 0)

#### **Nivel 2: Consolidation Agents (2)**
4. **MergeAgent** - Merge strategy & conflict resolution (phases 3-6)
5. **IntegrationAgent** - Integration specialist (phases 7-8)

#### **Nivel 3: Production Agents (4)**
6. **SecurityAgent** - Security hardening (phase 9)
7. **InfrastructureAgent** - Infrastructure as Code (phase 10)
8. **ObservabilityAgent** - Monitoring & logging (phase 11)
9. **PerformanceAgent** - Performance & load testing (phase 12)

#### **Nivel 4: Deployment Agents (3)**
10. **CICDAgent** - CI/CD Pipeline (phase 13)
11. **DisasterRecoveryAgent** - DR & Backup (phase 14)
12. **ValidationAgent** - Final validation & QA (phase 15)

---

## 📊 Phase-Agent Mapping

| Phase | Name | Assigned Agent |
|-------|------|----------------|
| 0 | BMC Discovery & Assessment | DiscoveryAgent |
| 1 | Repository Analysis | RepositoryAgent |
| 2 | Component Mapping | RepositoryAgent |
| 3 | Merge Strategy | MergeAgent |
| 4 | Conflict Resolution | MergeAgent |
| 5 | Testing & Validation | MergeAgent |
| 6 | Documentation | MergeAgent |
| 7 | Integration Testing | IntegrationAgent |
| 8 | Final Configuration | IntegrationAgent |
| 9 | Security Hardening | SecurityAgent |
| 10 | Infrastructure as Code | InfrastructureAgent |
| 11 | Observability & Monitoring | ObservabilityAgent |
| 12 | Performance & Load Testing | PerformanceAgent |
| 13 | CI/CD Pipeline | CICDAgent |
| 14 | Disaster Recovery & Backup | DisasterRecoveryAgent |
| 15 | Final Production Validation | ValidationAgent |

---

## 🚀 Execution Modes

### Automated Mode (Default)

```bash
python scripts/run_agent_team.py --mode automated
```

- **Full automated execution** of all 16 phases
- **Auto-approval** when success criteria are met
- **Automatic retry** on failures
- **State persistence** for recovery

### Manual Mode

```bash
python scripts/run_agent_team.py --mode manual
```

- **Pauses for approval** after each phase
- **Manual review** of outputs
- **Interactive confirmation** before proceeding

### Dry-Run Mode

```bash
python scripts/run_agent_team.py --mode dry-run
```

- **Validates setup** without execution
- **Checks dependencies** and configuration
- **No actual changes** made

---

## 📝 Common Procedures

### Procedure 1: Initial Setup

```bash
# 1. Check project status
python scripts/check_project_status.py

# 2. Install dependencies (if needed)
pip install -r scripts/orchestrator/requirements.txt

# 3. Configure environment (optional)
cp scripts/orchestrator/.env.example scripts/orchestrator/.env
# Edit .env with your settings

# 4. Start execution
python scripts/run_agent_team.py
```

### Procedure 2: Resume Interrupted Execution

```bash
# Check current status
python scripts/run_agent_team.py --status

# Resume from saved state
python scripts/run_agent_team.py --resume
```

### Procedure 3: Run Single Phase

```bash
# Run specific phase (e.g., Phase 0)
python scripts/run_agent_team.py --phase 0

# Run with specific mode
python scripts/run_agent_team.py --phase 0 --mode manual
```

### Procedure 4: Monitor Execution

```bash
# Check status periodically
python scripts/run_agent_team.py --status

# View execution state
cat consolidation/execution_state.json | jq

# View latest report
ls -lt consolidation/reports/ | head -5
```

---

## 🔍 Status Checking

### Check Project Status

```bash
python scripts/check_project_status.py
```

**Output includes:**
- Overall project status
- Phase progress (completed/in_progress/pending)
- Component status (files present/missing)
- Integration status
- Security status
- Recommendations

**Status Levels:**
- `phase_0_not_started` - Need to start Phase 0
- `setup_required` - Missing directories or setup
- `components_missing` - Core components missing
- `in_progress_early` - <50% complete
- `in_progress` - 50-99% complete
- `completed` - 100% complete

### Check Agent Team Status

```bash
python scripts/run_agent_team.py --status
```

**Shows:**
- Current phase
- Overall execution status
- Status of each phase (0-15)
- Assigned agent for each phase

---

## 📁 File Locations

### Status Files
- `consolidation/execution_state.json` - Execution state
- `consolidation/reports/status_check_*.json` - Status check reports
- `consolidation/reports/status_report_*.json` - Execution reports

### Configuration Files
- `scripts/agent_team_config.json` - Agent team configuration
- `scripts/orchestrator/config/orchestrator_config.json` - Orchestrator config
- `scripts/orchestrator/config/phase_config.json` - Phase definitions
- `scripts/orchestrator/config/success_criteria.json` - Success criteria

### Logs
- `consolidation/logs/` - Execution logs
- `consolidation/logs/auto_start.log` - Auto-start logs

---

## 🛠️ Troubleshooting

### Issue: Orchestrator Not Available

**Error:** `Orchestrator modules not importable`

**Solution:**
```bash
pip install -r scripts/orchestrator/requirements.txt
```

### Issue: Phase 0 Not Started

**Status:** `phase_0_not_started`

**Solution:**
```bash
# Start Phase 0 manually
python scripts/discovery/run_phase_0.py

# Or run via agent team
python scripts/run_agent_team.py --phase 0
```

### Issue: Execution Stuck

**Check:**
```bash
# View current state
cat consolidation/execution_state.json | jq

# Check for errors
grep -i error consolidation/logs/*.log

# Resume execution
python scripts/run_agent_team.py --resume
```

### Issue: Missing Components

**Status:** `components_missing`

**Solution:**
1. Check which components are missing:
   ```bash
   python scripts/check_project_status.py
   ```
2. Review `ARCHITECTURE_STATUS_REPORT.md` for component locations
3. Restore missing files from backups or repositories

---

## 📊 Expected Timeline

Based on the unified plan:

| Phase Group | Phases | Duration | Agent |
|-------------|--------|----------|-------|
| Discovery | 0 | 2-3 days | DiscoveryAgent |
| Consolidation | 1-8 | 3-5 weeks | RepositoryAgent, MergeAgent, IntegrationAgent |
| Production | 9-15 | 5-6 weeks | SecurityAgent, InfrastructureAgent, ObservabilityAgent, PerformanceAgent, CICDAgent, DisasterRecoveryAgent, ValidationAgent |
| **Total** | **0-15** | **8-10 weeks** | **All 12 Agents** |

---

## ✅ Success Criteria

### Phase Completion
- All required output files generated
- Success criteria validated
- Auto-approval passed
- Next phase triggered

### Overall Completion
- All 16 phases completed
- All success criteria met
- Production readiness: 100%
- Final validation passed

---

## 📚 Reference Documents

- **Consolidation Plan:** `consolidation/PLAN_COMPLETO_REPOSITORIO_WORKSPACE.md`
- **Architecture Report:** `ARCHITECTURE_STATUS_REPORT.md`
- **Agent Architecture:** `AGENT_ARCHITECTURE.md`
- **Orchestrator README:** `scripts/orchestrator/README.md`

---

## 🎯 Next Steps

1. **Check Status:** Run `python scripts/check_project_status.py`
2. **Review Status:** Understand current state and recommendations
3. **Start Execution:** Run `python scripts/run_agent_team.py`
4. **Monitor Progress:** Check status periodically
5. **Handle Issues:** Follow troubleshooting guide if needed

---

**Last Updated:** 2025-01-12  
**Version:** 1.0


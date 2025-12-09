# Phase 0: BMC Discovery & Assessment Scripts

This directory contains all scripts for Phase 0 of the consolidation plan: **BMC Discovery & Assessment**.

## Overview

Phase 0 combines technical discovery with BMC domain discovery to:
- Analyze repositories and workspace structure
- Inventory BMC-specific components
- Validate integrations (WhatsApp, n8n, Qdrant, Chatwoot)
- Assess quotation engine completeness
- Identify production readiness gaps
- Create production baseline

## Scripts

### T0.1: `analyze_repositories.py`
Analyzes GitHub repositories structure, technologies, dependencies, and duplicates.

**Usage:**
```bash
python analyze_repositories.py --output consolidation/discovery/repository_analysis.json
```

**Output:** `repository_analysis.json`

### T0.2: `analyze_workspace.py`
Analyzes the chatbot-2311 workspace structure, components, and completeness.

**Usage:**
```bash
python analyze_workspace.py --workspace /path/to/workspace --output consolidation/discovery/workspace_analysis.json
```

**Output:** `workspace_analysis.json`

### T0.3: `inventory_bmc_components.py`
Inventories BMC-specific components: quotation engine, products, zones, integrations, n8n workflows.

**Usage:**
```bash
python inventory_bmc_components.py --workspace /path/to/workspace --output consolidation/discovery/bmc_inventory.json
```

**Output:** `bmc_inventory.json`

### T0.4: `validate_integrations.py`
Validates WhatsApp, n8n, Qdrant, and Chatwoot integrations configuration.

**Usage:**
```bash
python validate_integrations.py --workspace /path/to/workspace --output consolidation/discovery/integrations_status.json
```

**Output:** `integrations_status.json`

### T0.5: `assess_quotation_engine.py`
Assesses quotation engine completeness: products, zones, dimensions, services.

**Usage:**
```bash
python assess_quotation_engine.py --workspace /path/to/workspace --output consolidation/discovery/quotation_assessment.json
```

**Output:** `quotation_assessment.json`

### T0.6: `identify_production_gaps.py`
Identifies production readiness gaps by comparing current state vs production requirements.

**Usage:**
```bash
python identify_production_gaps.py --discovery-dir consolidation/discovery --output consolidation/discovery/production_gaps.json
```

**Output:** `production_gaps.json`

### T0.7: `create_production_baseline.py`
Creates production baseline documenting current state, metrics, and acceptance criteria.

**Usage:**
```bash
python create_production_baseline.py --discovery-dir consolidation/discovery --output consolidation/discovery/production_baseline.json
```

**Output:** `production_baseline.json`

## DiscoveryAgent

The `DiscoveryAgent` class orchestrates all Phase 0 tasks:

```python
from discovery.discovery_agent import DiscoveryAgent

agent = DiscoveryAgent(
    workspace_path="/path/to/workspace",
    output_dir="consolidation/discovery"
)

results = agent.execute_phase_0()
```

## Running Phase 0

### Option 1: Using DiscoveryAgent directly
```bash
python scripts/discovery/discovery_agent.py --workspace /path/to/workspace --output-dir consolidation/discovery
```

### Option 2: Using the main entry point
```bash
python scripts/discovery/run_phase_0.py --workspace /path/to/workspace --output-dir consolidation/discovery
```

### Option 3: Using Phase0Executor (from orchestrator)
The Phase0Executor automatically uses these scripts when delegation fails.

## Output Structure

All outputs are saved to `consolidation/discovery/`:

```
consolidation/discovery/
├── repository_analysis.json      # T0.1 output
├── workspace_analysis.json      # T0.2 output
├── bmc_inventory.json            # T0.3 output
├── integrations_status.json      # T0.4 output
├── quotation_assessment.json    # T0.5 output
├── production_gaps.json          # T0.6 output
├── production_baseline.json      # T0.7 output
└── phase_0_execution_summary.json # Execution summary
```

## Dependencies

- Python 3.8+
- `requests` (optional, for GitHub API access)
- Standard library: `json`, `pathlib`, `subprocess`, `datetime`

## Notes

- All scripts are executable and can be run independently
- Scripts automatically create output directories if they don't exist
- GitHub API token can be provided via `--github-token` or `GITHUB_TOKEN` environment variable
- Scripts handle missing files gracefully and provide error messages

## Integration with Orchestrator

The Phase0Executor in `scripts/orchestrator/phase_executors/phase_0_executor.py` automatically uses these scripts when agent delegation is not available.


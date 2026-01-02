# Automated Execution Orchestrator

Automated orchestration system for executing the unified consolidation and production plan with triggers, automated approvals, and GitHub integration.

## Overview

This orchestrator automatically executes all 16 phases of the unified plan:
- Phase 0: BMC Discovery & Assessment
- Phases 1-8: Consolidation
- Phases 9-15: Production

## Features

- **Automated Execution**: Non-stop execution until completion
- **Success Criteria-Based Approvals**: Auto-approve phases when criteria are met
- **GitHub Integration**: Track execution via GitHub issues
- **Error Handling**: Automatic retry with exponential backoff
- **State Management**: Resume from saved state
- **Dependency Resolution**: Automatic dependency checking

## Setup

### 1. Install Dependencies

```bash
pip install -r scripts/orchestrator/requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp scripts/orchestrator/.env.example scripts/orchestrator/.env
```

Edit `.env` with your GitHub token and repository details.

### 3. Configure Phase Settings

Edit configuration files in `scripts/orchestrator/config/`:
- `orchestrator_config.json` - Main configuration
- `phase_config.json` - Phase definitions and dependencies
- `success_criteria.json` - Success criteria for each phase
- `github_config.json` - GitHub integration settings

## Usage

### Run Automated Execution

```bash
python scripts/orchestrator/run_automated_execution.py
```

### Run with Options

```bash
# Resume from saved state
python scripts/orchestrator/run_automated_execution.py --resume

# Manual mode (pause for approvals)
python scripts/orchestrator/run_automated_execution.py --mode manual

# Dry-run (validate without execution)
python scripts/orchestrator/run_automated_execution.py --mode dry-run
```

## Execution Flow

1. **Startup**: Initialize state manager, create GitHub issue
2. **Phase Loop**: For each phase (0-15):
   - Check dependencies
   - Execute phase tasks
   - Collect outputs
   - Validate success criteria
   - Auto-approve if criteria met
   - Trigger next phase
3. **Completion**: Generate final report, close GitHub issue

## State Management

Execution state is saved to `consolidation/execution_state.json`. This enables:
- Recovery from failures
- Resuming interrupted executions
- Progress tracking

## Success Criteria

Each phase has defined success criteria in `config/success_criteria.json`:
- Required output files
- Validation checks (file existence, JSON validity, metric thresholds)
- Auto-approval when all criteria are met

## Error Handling

- **Transient Errors**: Automatically retried with exponential backoff
- **Permanent Errors**: Logged and require manual intervention
- **Dependency Errors**: Wait for dependencies to complete
- **Configuration Errors**: Stop execution, fix configuration

## GitHub Integration

When configured, the orchestrator:
- Creates a GitHub issue for execution tracking
- Updates issue with phase status
- Posts approval notifications
- Closes issue on completion

## Monitoring

Status reports are saved to `consolidation/reports/status_report_*.json`:
- Execution progress
- Phase status
- Error summaries
- Final report

## Architecture

- **StateManager**: Manages execution state
- **DependencyResolver**: Resolves phase dependencies
- **TriggerManager**: Manages phase triggers
- **ApprovalEngine**: Evaluates and approves phases
- **ErrorHandler**: Classifies and handles errors
- **RetryManager**: Manages retry logic
- **GitHubIntegration**: GitHub API integration
- **StatusReporter**: Generates status reports
- **PhaseExecutors**: Execute phase-specific tasks

## File Structure

```
scripts/orchestrator/
├── main_orchestrator.py          # Main orchestrator
├── state_manager.py               # State management
├── dependency_resolver.py         # Dependency resolution
├── triggers.py                    # Trigger management
├── approval_engine.py             # Approval logic
├── success_criteria.py            # Success criteria
├── error_handler.py               # Error handling
├── retry_manager.py               # Retry logic
├── github_integration.py          # GitHub integration
├── status_reporter.py             # Status reporting
├── run_automated_execution.py     # Main entry point
├── phase_executors/               # Phase executors
│   ├── base_executor.py
│   ├── phase_0_executor.py
│   └── ...
├── config/                        # Configuration files
│   ├── orchestrator_config.json
│   ├── phase_config.json
│   ├── success_criteria.json
│   └── github_config.json
├── utils/                         # Utility modules
│   ├── file_validator.py
│   ├── json_validator.py
│   └── metric_validator.py
├── requirements.txt               # Dependencies
├── .env.example                   # Environment template
└── README.md                      # This file
```

## Troubleshooting

### Execution Stuck

Check `consolidation/execution_state.json` for current phase and status.

### Phase Failing

Check phase errors in state file. Review logs for details.

### GitHub Integration Not Working

Verify `GITHUB_TOKEN` is set in `.env` and has appropriate permissions.

### Resume Not Working

Ensure `consolidation/execution_state.json` exists and is valid.

## License

Part of the Ultimate-CHATBOT project.


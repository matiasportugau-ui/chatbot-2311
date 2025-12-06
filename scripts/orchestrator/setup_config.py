#!/usr/bin/env python3
"""
Setup Configuration Files
Creates default configuration files if they don't exist
"""

import json
from pathlib import Path


def create_config_files():
    """Create default configuration files"""
    config_dir = Path(__file__).parent / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Orchestrator config
    orchestrator_config = {
        "max_retries": 3,
        "retry_delay": 60,
        "backoff_multiplier": 2,
        "phase_timeout": 3600,
        "github": {
            "token": None,
            "repo": "chatbot-2311",
            "owner": None
        },
        "execution_mode": "automated",
        "log_level": "INFO"
    }
    
    # Phase config
    phase_config = {
        "phases": {
            str(i): {
                "name": f"Phase {i}",
                "dependencies": [i - 1] if i > 0 else [],
                "timeout": 3600,
                "agent": "OrchestratorAgent"
            }
            for i in range(16)
        }
    }
    
    # Update phase names
    phase_names = {
        "0": "BMC Discovery & Assessment",
        "1": "Repository Analysis",
        "2": "Component Mapping",
        "3": "Merge Strategy",
        "4": "Conflict Resolution",
        "5": "Testing & Validation",
        "6": "Documentation",
        "7": "Integration Testing",
        "8": "Final Configuration",
        "9": "Production Security Hardening",
        "10": "Infrastructure as Code",
        "11": "Observability & Monitoring",
        "12": "Performance & Load Testing",
        "13": "CI/CD Pipeline",
        "14": "Disaster Recovery & Backup",
        "15": "Final Production Validation"
    }
    
    for phase_num, name in phase_names.items():
        phase_config["phases"][phase_num]["name"] = name
    
    # Success criteria
    success_criteria = {
        "0": {
            "required_outputs": [
                "consolidation/discovery/repository_analysis.json",
                "consolidation/discovery/workspace_analysis.json",
                "consolidation/discovery/bmc_inventory.json",
                "consolidation/discovery/integrations_status.json",
                "consolidation/discovery/quotation_assessment.json",
                "consolidation/discovery/production_gaps.json",
                "consolidation/discovery/production_baseline.json"
            ],
            "validation_checks": [
                {
                    "type": "file_exists",
                    "path": "consolidation/discovery/repository_analysis.json"
                },
                {
                    "type": "json_valid",
                    "path": "consolidation/discovery/bmc_inventory.json"
                },
                {
                    "type": "metric_threshold",
                    "file": "consolidation/discovery/bmc_inventory.json",
                    "metric": "components_found",
                    "min": 5
                }
            ]
        },
        "9": {
            "required_outputs": [
                "consolidation/security/webhook_validation.json",
                "consolidation/security/n8n_validation.json",
                "consolidation/security/secrets_migration.json",
                "consolidation/security/rate_limiting.json",
                "consolidation/security/cors_config.json",
                "consolidation/security/auth_implementation.json",
                "consolidation/security/security_audit_report.json"
            ],
            "validation_checks": [
                {
                    "type": "file_exists",
                    "path": "consolidation/security/webhook_validation.json"
                },
                {
                    "type": "json_valid",
                    "path": "consolidation/security/security_audit_report.json"
                },
                {
                    "type": "metric_threshold",
                    "file": "consolidation/security/security_audit_report.json",
                    "metric": "p0_issues",
                    "max": 0
                }
            ]
        },
        "15": {
            "required_outputs": [
                "consolidation/validation/production_readiness_audit.json",
                "consolidation/validation/stakeholder_signoff.json",
                "consolidation/validation/deployment_log.json",
                "consolidation/validation/post_deployment_report.json"
            ],
            "validation_checks": [
                {
                    "type": "file_exists",
                    "path": "consolidation/validation/production_readiness_audit.json"
                },
                {
                    "type": "json_valid",
                    "path": "consolidation/validation/production_readiness_audit.json"
                },
                {
                    "type": "metric_threshold",
                    "file": "consolidation/validation/production_readiness_audit.json",
                    "metric": "all_checks_passed",
                    "exact": True
                }
            ]
        }
    }
    
    # GitHub config
    github_config = {
        "enabled": True,
        "create_issues": True,
        "update_on_phase_start": True,
        "update_on_phase_complete": True,
        "update_on_approval": True,
        "update_on_error": True,
        "labels": [
            "automation",
            "consolidation",
            "production"
        ]
    }
    
    # Write config files
    configs = {
        "orchestrator_config.json": orchestrator_config,
        "phase_config.json": phase_config,
        "success_criteria.json": success_criteria,
        "github_config.json": github_config
    }
    
    for filename, config in configs.items():
        config_file = config_dir / filename
        if not config_file.exists():
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Created {config_file}")
        else:
            print(f"{config_file} already exists, skipping")


if __name__ == "__main__":
    create_config_files()


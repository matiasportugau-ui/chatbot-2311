"""
Success Criteria Definitions
Defines success criteria for each phase and validates outputs
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from .utils.file_validator import FileValidator
from .utils.json_validator import JSONValidator
from .utils.metric_validator import MetricValidator


class SuccessCriteria:
    """Defines and validates success criteria for phases"""
    
    def __init__(self, config_file: str = "scripts/orchestrator/config/success_criteria.json"):
        self.config_file = Path(config_file)
        self.criteria = self._load_criteria()
    
    def _load_criteria(self) -> Dict[str, Any]:
        """Load success criteria from config file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading success criteria: {e}. Using default criteria.")
                return self._default_criteria()
        else:
            return self._default_criteria()
    
    def _default_criteria(self) -> Dict[str, Any]:
        """Default success criteria for each phase"""
        return {
            "0": {
                "required_outputs": [
                    "consolidation/discovery/repository_analysis.json",
                    "consolidation/discovery/bmc_inventory.json",
                    "consolidation/discovery/integrations_status.json"
                ],
                "validation_checks": [
                    {"type": "file_exists", "path": "consolidation/discovery/repository_analysis.json"},
                    {"type": "json_valid", "path": "consolidation/discovery/bmc_inventory.json"},
                    {"type": "metric_threshold", "file": "consolidation/discovery/bmc_inventory.json", 
                     "metric": "components_found", "min": 5}
                ]
            },
            "9": {
                "required_outputs": [
                    "consolidation/security/webhook_validation.json",
                    "consolidation/security/security_audit_report.json"
                ],
                "validation_checks": [
                    {"type": "file_exists", "path": "consolidation/security/webhook_validation.json"},
                    {"type": "json_valid", "path": "consolidation/security/security_audit_report.json"},
                    {"type": "metric_threshold", "file": "consolidation/security/security_audit_report.json",
                     "metric": "p0_issues", "max": 0}
                ]
            },
            "15": {
                "required_outputs": [
                    "consolidation/validation/production_readiness_audit.json",
                    "consolidation/validation/post_deployment_report.json"
                ],
                "validation_checks": [
                    {"type": "file_exists", "path": "consolidation/validation/production_readiness_audit.json"},
                    {"type": "json_valid", "path": "consolidation/validation/production_readiness_audit.json"},
                    {"type": "metric_threshold", "file": "consolidation/validation/production_readiness_audit.json",
                     "metric": "all_checks_passed", "exact": True}
                ]
            }
        }
    
    def get_criteria(self, phase: int) -> Dict[str, Any]:
        """Get success criteria for a phase"""
        return self.criteria.get(str(phase), {
            "required_outputs": [],
            "validation_checks": []
        })
    
    def validate_phase(self, phase: int, outputs: List[str]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate phase outputs against success criteria
        Returns: (all_met, passed_checks, failed_checks)
        """
        criteria = self.get_criteria(phase)
        passed = []
        failed = []
        
        # Check required outputs
        required_outputs = criteria.get("required_outputs", [])
        for output in required_outputs:
            exists, error = FileValidator.file_exists(output)
            if exists:
                passed.append(f"Required output exists: {output}")
            else:
                failed.append(f"Required output missing: {output} - {error}")
        
        # Run validation checks
        validation_checks = criteria.get("validation_checks", [])
        for check in validation_checks:
            check_type = check.get("type")
            result = self._run_validation_check(check_type, check)
            
            if result[0]:
                passed.append(f"Validation passed: {check_type} - {check.get('path', check.get('metric', ''))}")
            else:
                failed.append(f"Validation failed: {check_type} - {result[1]}")
        
        all_met = len(failed) == 0
        return all_met, passed, failed
    
    def _run_validation_check(self, check_type: str, check_config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Run a single validation check"""
        if check_type == "file_exists":
            return FileValidator.file_exists(check_config.get("path", ""))
        
        elif check_type == "json_valid":
            return FileValidator.json_valid(check_config.get("path", ""))
        
        elif check_type == "json_schema":
            return FileValidator.json_schema_valid(
                check_config.get("path", ""),
                check_config.get("schema", {})
            )
        
        elif check_type == "file_not_empty":
            return FileValidator.file_not_empty(check_config.get("path", ""))
        
        elif check_type == "metric_threshold":
            return MetricValidator.validate_metric_threshold(
                check_config.get("file", ""),
                check_config.get("metric", ""),
                min_value=check_config.get("min"),
                max_value=check_config.get("max"),
                exact_value=check_config.get("exact")
            )
        
        elif check_type == "metric_exists":
            return MetricValidator.validate_metric_exists(
                check_config.get("file", ""),
                check_config.get("metric", "")
            )
        
        else:
            return False, f"Unknown validation check type: {check_type}"
    
    def get_required_outputs(self, phase: int) -> List[str]:
        """Get list of required outputs for a phase"""
        criteria = self.get_criteria(phase)
        return criteria.get("required_outputs", [])
    
    def has_criteria(self, phase: int) -> bool:
        """Check if phase has success criteria defined"""
        return str(phase) in self.criteria


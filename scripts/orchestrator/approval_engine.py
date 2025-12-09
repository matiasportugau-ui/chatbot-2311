"""
Approval Engine
Evaluates success criteria and auto-approves phases
"""

from typing import Dict, Any, List, Tuple
from .state_manager import StateManager
from .success_criteria import SuccessCriteria


class ApprovalEngine:
    """Handles automated approval based on success criteria"""
    
    def __init__(self, state_manager: StateManager, success_criteria: SuccessCriteria):
        self.state_manager = state_manager
        self.success_criteria = success_criteria
    
    def evaluate_criteria(self, phase: int) -> Tuple[bool, List[str], List[str]]:
        """
        Evaluate success criteria for a phase
        Returns: (all_met, passed_checks, failed_checks)
        """
        outputs = self.state_manager.get_phase_outputs(phase)
        return self.success_criteria.validate_phase(phase, outputs)
    
    def auto_approve(self, phase: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Auto-approve a phase if criteria are met
        Returns: (approved, approval_report)
        """
        all_met, passed, failed = self.evaluate_criteria(phase)
        
        approval_report = {
            "phase": phase,
            "approved": all_met,
            "criteria_met": all_met,
            "passed_checks": passed,
            "failed_checks": failed,
            "timestamp": self._get_timestamp()
        }
        
        if all_met:
            self.state_manager.set_phase_approved(phase, True, True)
            approval_report["status"] = "auto_approved"
        else:
            self.state_manager.set_phase_approved(phase, False, False)
            approval_report["status"] = "approval_failed"
        
        return all_met, approval_report
    
    def generate_approval_report(self, phase: int) -> Dict[str, Any]:
        """Generate detailed approval report for a phase"""
        all_met, passed, failed = self.evaluate_criteria(phase)
        phase_data = self.state_manager.state.get("phases", {}).get(str(phase), {})
        
        report = {
            "phase": phase,
            "status": phase_data.get("status", "unknown"),
            "approved": phase_data.get("approved", False),
            "criteria_met": all_met,
            "required_outputs": self.success_criteria.get_required_outputs(phase),
            "actual_outputs": self.state_manager.get_phase_outputs(phase),
            "passed_checks": passed,
            "failed_checks": failed,
            "retry_count": phase_data.get("retry_count", 0),
            "errors": phase_data.get("errors", []),
            "timestamp": self._get_timestamp()
        }
        
        return report
    
    def can_auto_approve(self, phase: int) -> bool:
        """Check if phase can be auto-approved"""
        # Check if phase is completed
        status = self.state_manager.get_phase_status(phase)
        if status != "completed":
            return False
        
        # Check if criteria are met
        all_met, _, _ = self.evaluate_criteria(phase)
        return all_met
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


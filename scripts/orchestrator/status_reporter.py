"""
Status Reporter
Generates status reports and updates GitHub issue
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from .state_manager import StateManager
from .github_integration import GitHubIntegration


class StatusReporter:
    """Generates and reports execution status"""
    
    def __init__(self, state_manager: StateManager, github_integration: Optional[GitHubIntegration] = None):
        self.state_manager = state_manager
        self.github_integration = github_integration
        self.reports_dir = Path("consolidation/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        execution_id = self.state_manager.get_execution_id()
        current_phase = self.state_manager.get_current_phase()
        overall_status = self.state_manager.get_overall_status()
        progress = self.state_manager.get_progress_percentage()
        completed_phases = self.state_manager.get_completed_phases()
        
        phases_status = {}
        for phase_num in range(16):
            phase_data = self.state_manager.state.get("phases", {}).get(str(phase_num), {})
            phases_status[str(phase_num)] = {
                "status": phase_data.get("status", "pending"),
                "approved": phase_data.get("approved", False),
                "retry_count": phase_data.get("retry_count", 0),
                "has_errors": len(phase_data.get("errors", [])) > 0,
                "output_count": len(phase_data.get("outputs", []))
            }
        
        report = {
            "execution_id": execution_id,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": overall_status,
            "current_phase": current_phase,
            "progress_percentage": progress,
            "completed_phases": completed_phases,
            "phases_status": phases_status,
            "summary": {
                "total_phases": 16,
                "completed": len(completed_phases),
                "in_progress": sum(1 for p in phases_status.values() if p["status"] == "in_progress"),
                "failed": sum(1 for p in phases_status.values() if p["status"] == "failed"),
                "approved": sum(1 for p in phases_status.values() if p["approved"])
            }
        }
        
        return report
    
    def save_status_report(self, report: Optional[Dict[str, Any]] = None) -> str:
        """Save status report to file"""
        if report is None:
            report = self.generate_status_report()
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"status_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(report_file)
    
    def print_status(self) -> None:
        """Print status to console"""
        report = self.generate_status_report()
        
        print("\n" + "="*60)
        print("EXECUTION STATUS REPORT")
        print("="*60)
        print(f"Execution ID: {report['execution_id']}")
        print(f"Overall Status: {report['overall_status']}")
        print(f"Current Phase: {report['current_phase']}")
        print(f"Progress: {report['progress_percentage']:.1f}%")
        print(f"Completed Phases: {len(report['completed_phases'])}/16")
        print("\nPhase Status:")
        
        for phase_num in range(16):
            phase_status = report['phases_status'][str(phase_num)]
            status_icon = {
                "pending": "⏳",
                "in_progress": "🔄",
                "completed": "✅",
                "approved": "✅",
                "failed": "❌"
            }.get(phase_status['status'], "❓")
            
            approved_icon = "✓" if phase_status['approved'] else "✗"
            print(f"  Phase {phase_num:2d}: {status_icon} {phase_status['status']:12s} Approved: {approved_icon}")
        
        print("="*60 + "\n")
    
    def update_github_issue(self, issue_number: int) -> bool:
        """Update GitHub issue with current status"""
        if not self.github_integration or not self.github_integration.is_available():
            return False
        
        report = self.generate_status_report()
        execution_id = report['execution_id']
        current_phase = report['current_phase']
        progress = report['progress_percentage']
        
        return self.github_integration.update_issue_body(
            issue_number, execution_id, current_phase, progress
        )
    
    def generate_phase_summary(self, phase: int) -> Dict[str, Any]:
        """Generate summary for a specific phase"""
        phase_data = self.state_manager.state.get("phases", {}).get(str(phase), {})
        
        return {
            "phase": phase,
            "status": phase_data.get("status", "pending"),
            "started_at": phase_data.get("started_at"),
            "completed_at": phase_data.get("completed_at"),
            "approved": phase_data.get("approved", False),
            "outputs": phase_data.get("outputs", []),
            "errors": phase_data.get("errors", []),
            "retry_count": phase_data.get("retry_count", 0),
            "metadata": phase_data.get("metadata", {})
        }
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Generate final execution report"""
        report = self.generate_status_report()
        
        # Add final summary
        report["final_summary"] = {
            "all_phases_completed": len(report["completed_phases"]) == 16,
            "all_phases_approved": report["summary"]["approved"] == 16,
            "total_errors": sum(
                len(self.state_manager.state.get("phases", {}).get(str(p), {}).get("errors", []))
                for p in range(16)
            ),
            "total_retries": sum(
                self.state_manager.state.get("phases", {}).get(str(p), {}).get("retry_count", 0)
                for p in range(16)
            )
        }
        
        return report


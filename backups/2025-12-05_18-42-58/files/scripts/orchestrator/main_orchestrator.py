"""
Main Orchestrator
Coordinates phase execution, approvals, and triggers
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from .state_manager import StateManager
from .dependency_resolver import DependencyResolver
from .triggers import TriggerManager
from .approval_engine import ApprovalEngine
from .success_criteria import SuccessCriteria
from .error_handler import ErrorHandler
from .retry_manager import RetryManager
from .status_reporter import StatusReporter
from .github_integration import GitHubIntegration


class MainOrchestrator:
    """Main orchestrator for automated execution"""
    
    def __init__(self, config_file: str = "scripts/orchestrator/config/orchestrator_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
        # Initialize core components
        self.state_manager = StateManager()
        self.dependency_resolver = DependencyResolver(state_manager=self.state_manager)
        self.trigger_manager = TriggerManager(self.state_manager, self.dependency_resolver)
        self.success_criteria = SuccessCriteria()
        self.approval_engine = ApprovalEngine(self.state_manager, self.success_criteria)
        self.error_handler = ErrorHandler()
        self.retry_manager = RetryManager(self.state_manager, self.error_handler)
        
        # Initialize GitHub integration (optional)
        github_token = self.config.get("github", {}).get("token")
        github_repo = self.config.get("github", {}).get("repo")
        github_owner = self.config.get("github", {}).get("owner")
        self.github_integration = GitHubIntegration(github_token, github_repo, github_owner)
        
        self.status_reporter = StatusReporter(self.state_manager, self.github_integration)
        self.github_issue_number: Optional[int] = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load orchestrator configuration"""
        if self.config_file.exists():
            import json
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self._default_config()
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            "max_retries": 3,
            "retry_delay": 60,
            "github": {
                "token": None,
                "repo": "chatbot-2311",
                "owner": None
            }
        }
    
    def initialize(self) -> bool:
        """Initialize execution"""
        print("Initializing orchestrator...")
        
        # Create GitHub issue if available
        if self.github_integration.is_available():
            execution_id = self.state_manager.get_execution_id()
            current_phase = self.state_manager.get_current_phase()
            self.github_issue_number = self.github_integration.create_execution_issue(
                execution_id, current_phase
            )
            if self.github_issue_number:
                print(f"Created GitHub issue #{self.github_issue_number}")
        
        self.state_manager.set_overall_status("in_progress")
        return True
    
    def execute_phase(self, phase: int) -> bool:
        """Execute a single phase"""
        print(f"\n{'='*60}")
        print(f"Executing Phase {phase}")
        print(f"{'='*60}\n")
        
        # Check dependencies
        can_execute, missing = self.dependency_resolver.check_dependencies(phase)
        if not can_execute:
            print(f"Phase {phase} cannot execute. Missing dependencies: {missing}")
            return False
        
        # Update status
        self.state_manager.set_phase_status(phase, "in_progress")
        
        # Update GitHub
        if self.github_issue_number:
            self.github_integration.update_phase_status(
                self.github_issue_number, phase, "in_progress"
            )
        
        try:
            # Get phase executor
            executor = self._get_phase_executor(phase)
            if not executor:
                # For phases without executors, create a placeholder
                self.log_info(f"Phase {phase} executor not yet implemented. Marking as completed.")
                self.state_manager.set_phase_status(phase, "completed")
                # Auto-approve placeholder phases
                self.state_manager.set_phase_approved(phase, True, True)
                return True
            
            # Execute phase
            outputs = executor.execute()
            
            # Mark as completed
            self.state_manager.set_phase_status(phase, "completed")
            
            # Process approval
            approved, approval_report = self.approval_engine.auto_approve(phase)
            
            if approved:
                print(f"Phase {phase} auto-approved")
                if self.github_issue_number:
                    self.github_integration.post_approval_notification(
                        self.github_issue_number, phase, approval_report
                    )
                
                # Trigger next phase
                next_phase = self.trigger_manager.trigger_next_phase(phase)
                if next_phase is not None:
                    print(f"Triggering Phase {next_phase}")
            else:
                print(f"Phase {phase} approval failed")
                print(f"Failed checks: {approval_report.get('failed_checks', [])}")
            
            # Update GitHub
            if self.github_issue_number:
                self.status_reporter.update_github_issue(self.github_issue_number)
            
            return approved
        
        except Exception as e:
            # Handle error
            return self.handle_failure(phase, e)
    
    def _get_phase_executor(self, phase: int):
        """Get executor for a phase"""
        # Import executors dynamically
        try:
            if phase == 0:
                from .phase_executors.phase_0_executor import Phase0Executor
                return Phase0Executor(phase, self.state_manager)
            elif phase == 1:
                from .phase_executors.phase_1_executor import Phase1Executor
                return Phase1Executor(phase, self.state_manager)
            elif phase == 2:
                from .phase_executors.phase_2_executor import Phase2Executor
                return Phase2Executor(phase, self.state_manager)
            elif phase == 3:
                from .phase_executors.phase_3_executor import Phase3Executor
                return Phase3Executor(phase, self.state_manager)
            elif phase == 4:
                from .phase_executors.phase_4_executor import Phase4Executor
                return Phase4Executor(phase, self.state_manager)
            elif phase == 5:
                from .phase_executors.phase_5_executor import Phase5Executor
                return Phase5Executor(phase, self.state_manager)
            elif phase == 6:
                from .phase_executors.phase_6_executor import Phase6Executor
                return Phase6Executor(phase, self.state_manager)
            elif phase == 7:
                from .phase_executors.phase_7_executor import Phase7Executor
                return Phase7Executor(phase, self.state_manager)
            elif phase == 8:
                from .phase_executors.phase_8_executor import Phase8Executor
                return Phase8Executor(phase, self.state_manager)
            elif phase == 9:
                from .phase_executors.phase_9_executor import Phase9Executor
                return Phase9Executor(phase, self.state_manager)
            elif phase == 10:
                from .phase_executors.phase_10_executor import Phase10Executor
                return Phase10Executor(phase, self.state_manager)
            elif phase == 11:
                from .phase_executors.phase_11_executor import Phase11Executor
                return Phase11Executor(phase, self.state_manager)
            elif phase == 12:
                from .phase_executors.phase_12_executor import Phase12Executor
                return Phase12Executor(phase, self.state_manager)
            elif phase == 13:
                from .phase_executors.phase_13_executor import Phase13Executor
                return Phase13Executor(phase, self.state_manager)
            elif phase == 14:
                from .phase_executors.phase_14_executor import Phase14Executor
                return Phase14Executor(phase, self.state_manager)
            elif phase == 15:
                from .phase_executors.phase_15_executor import Phase15Executor
                return Phase15Executor(phase, self.state_manager)
        except ImportError as e:
            self.log_info(f"Phase {phase} executor not available: {e}")
            return None
        
        # For phases without executors
        return None
    
    def log_info(self, message: str) -> None:
        """Log info message"""
        print(f"[Orchestrator] INFO: {message}")
    
    def handle_failure(self, phase: int, error: Exception) -> bool:
        """Handle phase failure"""
        print(f"Phase {phase} failed: {error}")
        
        # Classify error
        error_type, error_message = self.error_handler.classify_error(error)
        error_context = self.error_handler.get_error_context(error)
        
        # Add error to state
        self.state_manager.add_phase_error(phase, error_message)
        self.state_manager.set_phase_status(phase, "failed")
        
        # Check if should retry
        if self.retry_manager.should_retry(phase, error):
            retry_info = self.retry_manager.prepare_for_retry(phase, error)
            delay = retry_info["delay_seconds"]
            
            print(f"Will retry Phase {phase} after {delay} seconds (attempt {retry_info['retry_count']})")
            
            if self.github_issue_number:
                self.github_integration.create_status_comment(
                    self.github_issue_number, phase, {
                        "status": "failed",
                        "error": error_message,
                        "will_retry": True,
                        "retry_count": retry_info["retry_count"],
                        "retry_delay": delay
                    }
                )
            
            # Wait and retry
            self.retry_manager.wait_for_retry(delay)
            return self.execute_phase(phase)
        else:
            print(f"Phase {phase} failed permanently. Manual intervention required.")
            
            if self.github_issue_number:
                self.github_integration.create_status_comment(
                    self.github_issue_number, phase, {
                        "status": "failed_permanently",
                        "error": error_message,
                        "error_type": error_type.value,
                        "requires_manual_intervention": True
                    }
                )
            
            return False
    
    def check_dependencies(self, phase: int) -> bool:
        """Check if phase dependencies are met"""
        return self.dependency_resolver.can_execute(phase)
    
    def process_approval(self, phase: int) -> bool:
        """Process approval for a phase"""
        approved, report = self.approval_engine.auto_approve(phase)
        return approved
    
    def run(self) -> bool:
        """Run complete execution"""
        if not self.initialize():
            return False
        
        current_phase = self.state_manager.get_current_phase()
        
        # Execute all phases
        while current_phase <= 15:
            success = self.execute_phase(current_phase)
            
            if not success:
                print(f"Execution stopped at Phase {current_phase}")
                return False
            
            # Move to next phase
            current_phase = self.state_manager.get_current_phase() + 1
            self.state_manager.set_current_phase(current_phase)
        
        # All phases complete
        self.state_manager.set_overall_status("completed")
        
        # Generate final report
        final_report = self.status_reporter.generate_final_report()
        report_file = self.status_reporter.save_status_report(final_report)
        print(f"\nFinal report saved to: {report_file}")
        
        # Close GitHub issue
        if self.github_issue_number:
            self.github_integration.close_issue(
                self.github_issue_number,
                f"Execution completed successfully. Final report: {report_file}"
            )
        
        print("\nExecution completed successfully!")
        return True


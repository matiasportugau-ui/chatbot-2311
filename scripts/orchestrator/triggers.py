"""
Trigger System for Phase Execution
Manages phase completion triggers and automatic progression
"""

from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime
from .state_manager import StateManager
from .dependency_resolver import DependencyResolver


class TriggerManager:
    """Manages triggers for phase execution"""
    
    def __init__(self, state_manager: StateManager, dependency_resolver: DependencyResolver):
        self.state_manager = state_manager
        self.dependency_resolver = dependency_resolver
    
    def check_phase_complete(self, phase: int) -> bool:
        """Check if a phase is completed"""
        status = self.state_manager.get_phase_status(phase)
        return status in ["completed", "approved"]
    
    def check_phase_approved(self, phase: int) -> bool:
        """Check if a phase is approved"""
        phase_data = self.state_manager.state.get("phases", {}).get(str(phase), {})
        return phase_data.get("approved", False)
    
    def validate_trigger(self, trigger_type: str, phase: int) -> Tuple[bool, Optional[str]]:
        """
        Validate if a trigger can be executed
        Returns: (is_valid, error_message)
        """
        if trigger_type == "phase_completion":
            if not self.check_phase_complete(phase):
                return False, f"Phase {phase} is not completed"
            return True, None
        
        elif trigger_type == "approval":
            if not self.check_phase_approved(phase):
                return False, f"Phase {phase} is not approved"
            return True, None
        
        elif trigger_type == "dependency":
            can_execute = self.dependency_resolver.can_execute(phase)
            if not can_execute:
                missing = self.dependency_resolver.check_dependencies(phase)[1]
                return False, f"Phase {phase} dependencies not met: {missing}"
            return True, None
        
        elif trigger_type == "manual":
            return True, None  # Manual triggers always valid
        
        else:
            return False, f"Unknown trigger type: {trigger_type}"
    
    def trigger_next_phase(self, current_phase: int) -> Optional[int]:
        """
        Trigger the next phase after current phase completion
        Returns: next phase number or None if no next phase
        """
        next_phase = current_phase + 1
        
        if next_phase > 15:
            return None  # All phases complete
        
        # Check if dependencies are met
        can_execute, missing = self.dependency_resolver.check_dependencies(next_phase)
        
        if not can_execute:
            print(f"Phase {next_phase} cannot be triggered yet. Missing dependencies: {missing}")
            return None
        
        # Check if phase is already completed
        status = self.state_manager.get_phase_status(next_phase)
        if status in ["completed", "approved"]:
            return self.trigger_next_phase(next_phase)  # Skip to next
        
        return next_phase
    
    def resolve_dependencies(self, phase: int) -> tuple[bool, List[int]]:
        """Resolve dependencies for a phase"""
        return self.dependency_resolver.check_dependencies(phase)
    
    def should_trigger_next(self, phase: int) -> bool:
        """Check if next phase should be triggered"""
        if not self.check_phase_approved(phase):
            return False
        
        next_phase = phase + 1
        if next_phase > 15:
            return False  # All phases complete
        
        return self.dependency_resolver.can_execute(next_phase)
    
    def get_trigger_info(self, phase: int) -> Dict[str, Any]:
        """Get trigger information for a phase"""
        is_complete = self.check_phase_complete(phase)
        is_approved = self.check_phase_approved(phase)
        can_execute_next, missing = self.dependency_resolver.check_dependencies(phase + 1)
        
        return {
            "phase": phase,
            "is_complete": is_complete,
            "is_approved": is_approved,
            "next_phase": phase + 1 if phase < 15 else None,
            "next_phase_ready": can_execute_next if phase < 15 else False,
            "next_phase_missing_deps": missing if phase < 15 else []
        }


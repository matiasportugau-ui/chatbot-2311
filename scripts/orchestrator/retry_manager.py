"""
Retry Manager
Handles retry logic for failed phases
"""

import time
from typing import Optional, Dict, Any
from .state_manager import StateManager
from .error_handler import ErrorHandler, ErrorType


class RetryManager:
    """Manages retry logic for failed phases"""
    
    def __init__(self, state_manager: StateManager, error_handler: ErrorHandler,
                 max_retries: int = 3, initial_delay: int = 60, backoff_multiplier: int = 2):
        self.state_manager = state_manager
        self.error_handler = error_handler
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_multiplier = backoff_multiplier
    
    def should_retry(self, phase: int, error: Exception) -> bool:
        """Determine if phase should be retried"""
        retry_count = self.state_manager.get_retry_count(phase)
        
        if retry_count >= self.max_retries:
            return False
        
        return self.error_handler.should_retry(error, retry_count, self.max_retries)
    
    def get_retry_delay(self, phase: int, error: Exception) -> int:
        """Get delay before retry"""
        retry_count = self.state_manager.get_retry_count(phase)
        return self.error_handler.get_retry_delay(
            error, retry_count, self.initial_delay, self.backoff_multiplier
        )
    
    def prepare_for_retry(self, phase: int, error: Exception) -> Dict[str, Any]:
        """
        Prepare phase for retry
        Returns retry information
        """
        retry_count = self.state_manager.increment_retry_count(phase)
        delay = self.get_retry_delay(phase, error)
        
        # Reset phase status to pending
        self.state_manager.set_phase_status(phase, "pending")
        
        # Clear errors (will be re-added if retry fails)
        phase_key = str(phase)
        if phase_key in self.state_manager.state.get("phases", {}):
            self.state_manager.state["phases"][phase_key]["errors"] = []
        
        retry_info = {
            "phase": phase,
            "retry_count": retry_count,
            "max_retries": self.max_retries,
            "delay_seconds": delay,
            "error_type": self.error_handler.classify_error(error)[0].value,
            "will_retry": retry_count < self.max_retries
        }
        
        return retry_info
    
    def wait_for_retry(self, delay: int) -> None:
        """Wait for retry delay"""
        if delay > 0:
            print(f"Waiting {delay} seconds before retry...")
            time.sleep(delay)
    
    def can_retry_after_dependency(self, phase: int) -> bool:
        """Check if phase can be retried after dependency resolution"""
        retry_count = self.state_manager.get_retry_count(phase)
        return retry_count < self.max_retries
    
    def get_retry_summary(self, phase: int) -> Dict[str, Any]:
        """Get retry summary for a phase"""
        retry_count = self.state_manager.get_retry_count(phase)
        phase_data = self.state_manager.state.get("phases", {}).get(str(phase), {})
        
        return {
            "phase": phase,
            "retry_count": retry_count,
            "max_retries": self.max_retries,
            "can_retry": retry_count < self.max_retries,
            "errors": phase_data.get("errors", [])
        }


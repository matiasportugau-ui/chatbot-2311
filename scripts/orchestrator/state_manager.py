"""
State Management System for Automated Execution
Tracks phase status, outputs, and enables state recovery
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid


class StateManager:
    """Manages execution state persistence and recovery"""
    
    def __init__(self, state_file: str = "consolidation/execution_state.json"):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state: Dict[str, Any] = {}
        self.load_state()
    
    def load_state(self) -> None:
        """Load state from file or initialize new state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading state: {e}. Initializing new state.")
                self._initialize_state()
        else:
            self._initialize_state()
    
    def _initialize_state(self) -> None:
        """Initialize new execution state"""
        self.state = {
            "execution_id": str(uuid.uuid4()),
            "started_at": datetime.utcnow().isoformat(),
            "current_phase": 0,
            "phases": {},
            "overall_status": "pending",
            "last_updated": datetime.utcnow().isoformat()
        }
        # Initialize all phases (0-15)
        for phase_num in range(16):
            self.state["phases"][str(phase_num)] = {
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "approved": False,
                "approval_criteria_met": False,
                "outputs": [],
                "errors": [],
                "retry_count": 0,
                "metadata": {}
            }
        self.save_state()
    
    def save_state(self) -> None:
        """Save state to file"""
        self.state["last_updated"] = datetime.utcnow().isoformat()
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except IOError as e:
            print(f"Error saving state: {e}")
    
    def get_execution_id(self) -> str:
        """Get current execution ID"""
        return self.state.get("execution_id", str(uuid.uuid4()))
    
    def get_current_phase(self) -> int:
        """Get current phase number"""
        return self.state.get("current_phase", 0)
    
    def set_current_phase(self, phase: int) -> None:
        """Set current phase"""
        self.state["current_phase"] = phase
        self.save_state()
    
    def get_phase_status(self, phase: int) -> str:
        """Get status of a specific phase"""
        return self.state["phases"].get(str(phase), {}).get("status", "pending")
    
    def set_phase_status(self, phase: int, status: str) -> None:
        """Set status of a specific phase"""
        phase_key = str(phase)
        if phase_key not in self.state["phases"]:
            self.state["phases"][phase_key] = {}
        
        self.state["phases"][phase_key]["status"] = status
        
        if status == "in_progress" and not self.state["phases"][phase_key].get("started_at"):
            self.state["phases"][phase_key]["started_at"] = datetime.utcnow().isoformat()
        
        if status in ["completed", "failed", "approved"]:
            self.state["phases"][phase_key]["completed_at"] = datetime.utcnow().isoformat()
        
        self.save_state()
    
    def add_phase_output(self, phase: int, output_path: str) -> None:
        """Add output file path to phase"""
        phase_key = str(phase)
        if phase_key not in self.state["phases"]:
            self.state["phases"][phase_key] = {}
        if "outputs" not in self.state["phases"][phase_key]:
            self.state["phases"][phase_key]["outputs"] = []
        
        if output_path not in self.state["phases"][phase_key]["outputs"]:
            self.state["phases"][phase_key]["outputs"].append(output_path)
        self.save_state()
    
    def get_phase_outputs(self, phase: int) -> List[str]:
        """Get all outputs for a phase"""
        return self.state["phases"].get(str(phase), {}).get("outputs", [])
    
    def add_phase_error(self, phase: int, error: str) -> None:
        """Add error to phase"""
        phase_key = str(phase)
        if phase_key not in self.state["phases"]:
            self.state["phases"][phase_key] = {}
        if "errors" not in self.state["phases"][phase_key]:
            self.state["phases"][phase_key]["errors"] = []
        
        error_entry = {
            "message": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.state["phases"][phase_key]["errors"].append(error_entry)
        self.save_state()
    
    def set_phase_approved(self, phase: int, approved: bool, criteria_met: bool = True) -> None:
        """Set approval status for a phase"""
        phase_key = str(phase)
        if phase_key not in self.state["phases"]:
            self.state["phases"][phase_key] = {}
        
        self.state["phases"][phase_key]["approved"] = approved
        self.state["phases"][phase_key]["approval_criteria_met"] = criteria_met
        if approved:
            self.state["phases"][phase_key]["status"] = "approved"
        self.save_state()
    
    def increment_retry_count(self, phase: int) -> int:
        """Increment retry count for a phase"""
        phase_key = str(phase)
        if phase_key not in self.state["phases"]:
            self.state["phases"][phase_key] = {}
        
        current_count = self.state["phases"][phase_key].get("retry_count", 0)
        self.state["phases"][phase_key]["retry_count"] = current_count + 1
        self.save_state()
        return self.state["phases"][phase_key]["retry_count"]
    
    def get_retry_count(self, phase: int) -> int:
        """Get retry count for a phase"""
        return self.state["phases"].get(str(phase), {}).get("retry_count", 0)
    
    def set_phase_metadata(self, phase: int, key: str, value: Any) -> None:
        """Set metadata for a phase"""
        phase_key = str(phase)
        if phase_key not in self.state["phases"]:
            self.state["phases"][phase_key] = {}
        if "metadata" not in self.state["phases"][phase_key]:
            self.state["phases"][phase_key]["metadata"] = {}
        
        self.state["phases"][phase_key]["metadata"][key] = value
        self.save_state()
    
    def get_phase_metadata(self, phase: int, key: str, default: Any = None) -> Any:
        """Get metadata for a phase"""
        return self.state["phases"].get(str(phase), {}).get("metadata", {}).get(key, default)
    
    def set_overall_status(self, status: str) -> None:
        """Set overall execution status"""
        self.state["overall_status"] = status
        self.save_state()
    
    def get_overall_status(self) -> str:
        """Get overall execution status"""
        return self.state.get("overall_status", "pending")
    
    def get_completed_phases(self) -> List[int]:
        """Get list of completed phase numbers"""
        completed = []
        for phase_num, phase_data in self.state["phases"].items():
            if phase_data.get("status") in ["completed", "approved"]:
                completed.append(int(phase_num))
        return sorted(completed)
    
    def get_progress_percentage(self) -> float:
        """Calculate overall progress percentage"""
        total_phases = 16
        completed = len(self.get_completed_phases())
        return (completed / total_phases) * 100
    
    def can_resume(self) -> bool:
        """Check if execution can be resumed"""
        return self.state_file.exists() and self.get_overall_status() in ["in_progress", "pending"]
    
    def reset_phase(self, phase: int) -> None:
        """Reset a phase to pending state"""
        phase_key = str(phase)
        self.state["phases"][phase_key] = {
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "approved": False,
            "approval_criteria_met": False,
            "outputs": [],
            "errors": [],
            "retry_count": 0,
            "metadata": {}
        }
        self.save_state()


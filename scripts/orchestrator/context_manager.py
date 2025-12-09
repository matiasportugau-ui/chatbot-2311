"""
Context Manager
Manages execution context and enables handoff between agents/phases
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
try:
    from .state_manager import StateManager
except ImportError:
    # For standalone execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from scripts.orchestrator.state_manager import StateManager


class ContextManager:
    """Manages execution context for phase handoffs"""
    
    def __init__(self, state_manager: StateManager, context_file: str = "consolidation/execution_context.json"):
        self.state_manager = state_manager
        self.context_file = Path(context_file)
        self.context_file.parent.mkdir(parents=True, exist_ok=True)
        self.context: Dict[str, Any] = {}
        self.load_context()
    
    def load_context(self) -> None:
        """Load context from file"""
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r') as f:
                    self.context = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading context: {e}. Initializing new context.")
                self._initialize_context()
        else:
            self._initialize_context()
    
    def _initialize_context(self) -> None:
        """Initialize new context"""
        self.context = {
            "execution_id": self.state_manager.get_execution_id(),
            "created_at": datetime.utcnow().isoformat(),
            "phases": {},
            "global_context": {},
            "shared_artifacts": {},
            "agent_handoffs": []
        }
        self.save_context()
    
    def save_context(self) -> None:
        """Save context to file"""
        self.context["last_updated"] = datetime.utcnow().isoformat()
        try:
            with open(self.context_file, 'w') as f:
                json.dump(self.context, f, indent=2)
        except IOError as e:
            print(f"Error saving context: {e}")
    
    def add_phase_context(self, phase: int, context_data: Dict[str, Any]) -> None:
        """Add context data for a specific phase"""
        phase_key = str(phase)
        if phase_key not in self.context["phases"]:
            self.context["phases"][phase_key] = {
                "phase": phase,
                "context": {},
                "outputs": [],
                "artifacts": {},
                "dependencies_met": [],
                "created_at": datetime.utcnow().isoformat()
            }
        
        self.context["phases"][phase_key]["context"].update(context_data)
        self.context["phases"][phase_key]["last_updated"] = datetime.utcnow().isoformat()
        self.save_context()
    
    def get_phase_context(self, phase: int) -> Dict[str, Any]:
        """Get context for a specific phase"""
        return self.context["phases"].get(str(phase), {}).get("context", {})
    
    def add_phase_output(self, phase: int, output_path: str, output_type: str = "file") -> None:
        """Add output artifact to phase context"""
        phase_key = str(phase)
        if phase_key not in self.context["phases"]:
            self.context["phases"][phase_key] = {
                "phase": phase,
                "context": {},
                "outputs": [],
                "artifacts": {},
                "dependencies_met": [],
                "created_at": datetime.utcnow().isoformat()
            }
        
        output_entry = {
            "path": output_path,
            "type": output_type,
            "added_at": datetime.utcnow().isoformat()
        }
        
        if output_entry not in self.context["phases"][phase_key]["outputs"]:
            self.context["phases"][phase_key]["outputs"].append(output_entry)
        
        self.save_context()
    
    def get_phase_outputs(self, phase: int) -> List[Dict[str, Any]]:
        """Get all outputs for a phase"""
        return self.context["phases"].get(str(phase), {}).get("outputs", [])
    
    def add_shared_artifact(self, key: str, artifact: Any, description: str = "") -> None:
        """Add artifact to shared context (accessible by all phases)"""
        self.context["shared_artifacts"][key] = {
            "value": artifact,
            "description": description,
            "created_at": datetime.utcnow().isoformat()
        }
        self.save_context()
    
    def get_shared_artifact(self, key: str) -> Optional[Any]:
        """Get shared artifact"""
        artifact = self.context["shared_artifacts"].get(key)
        return artifact.get("value") if artifact else None
    
    def set_global_context(self, key: str, value: Any) -> None:
        """Set global context variable"""
        self.context["global_context"][key] = {
            "value": value,
            "updated_at": datetime.utcnow().isoformat()
        }
        self.save_context()
    
    def get_global_context(self, key: str, default: Any = None) -> Any:
        """Get global context variable"""
        ctx = self.context["global_context"].get(key)
        return ctx.get("value") if ctx else default
    
    def create_handoff_package(self, from_phase: int, to_phase: int) -> Dict[str, Any]:
        """
        Create a handoff package for passing context between phases/agents
        Returns a complete context package for the next phase
        """
        # Get all completed phases' contexts
        completed_phases = self.state_manager.get_completed_phases()
        
        # Build dependency chain
        dependency_context = {}
        for phase_num in completed_phases:
            if phase_num < to_phase:
                phase_key = str(phase_num)
                if phase_key in self.context["phases"]:
                    dependency_context[phase_key] = {
                        "context": self.context["phases"][phase_key].get("context", {}),
                        "outputs": self.context["phases"][phase_key].get("outputs", []),
                        "artifacts": self.context["phases"][phase_key].get("artifacts", {})
                    }
        
        # Get immediate previous phase context
        previous_phase_context = {}
        if from_phase >= 0:
            previous_phase_context = self.get_phase_context(from_phase)
        
        handoff_package = {
            "execution_id": self.context["execution_id"],
            "from_phase": from_phase,
            "to_phase": to_phase,
            "previous_phase_context": previous_phase_context,
            "dependency_contexts": dependency_context,
            "shared_artifacts": self.context["shared_artifacts"],
            "global_context": self.context["global_context"],
            "state_summary": {
                "completed_phases": completed_phases,
                "current_phase": to_phase,
                "overall_status": self.state_manager.get_overall_status(),
                "progress": self.state_manager.get_progress_percentage()
            },
            "handoff_timestamp": datetime.utcnow().isoformat()
        }
        
        return handoff_package
    
    def save_handoff_package(self, handoff_package: Dict[str, Any], handoff_file: Optional[str] = None) -> str:
        """Save handoff package to file"""
        if handoff_file is None:
            to_phase = handoff_package["to_phase"]
            handoff_file = f"consolidation/handoffs/handoff_phase_{to_phase}.json"
        
        handoff_path = Path(handoff_file)
        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(handoff_path, 'w') as f:
            json.dump(handoff_package, f, indent=2)
        
        # Record handoff
        self.context["agent_handoffs"].append({
            "from_phase": handoff_package["from_phase"],
            "to_phase": handoff_package["to_phase"],
            "handoff_file": handoff_file,
            "timestamp": handoff_package["handoff_timestamp"]
        })
        self.save_context()
        
        return handoff_file
    
    def load_handoff_package(self, handoff_file: str) -> Dict[str, Any]:
        """Load handoff package from file"""
        with open(handoff_file, 'r') as f:
            return json.load(f)
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context"""
        return {
            "execution_id": self.context["execution_id"],
            "total_phases_with_context": len(self.context["phases"]),
            "shared_artifacts_count": len(self.context["shared_artifacts"]),
            "global_context_keys": list(self.context["global_context"].keys()),
            "handoff_count": len(self.context["agent_handoffs"]),
            "last_updated": self.context.get("last_updated")
        }
    
    def export_context_for_agent(self, phase: int) -> Dict[str, Any]:
        """
        Export complete context package for an agent to execute a phase
        This includes everything the agent needs to know
        """
        handoff = self.create_handoff_package(phase - 1, phase)
        
        # Add phase-specific requirements
        phase_data = self.state_manager.state.get("phases", {}).get(str(phase), {})
        handoff["phase_requirements"] = {
            "status": phase_data.get("status", "pending"),
            "dependencies": phase_data.get("dependencies", []),
            "expected_outputs": phase_data.get("expected_outputs", []),
            "success_criteria": phase_data.get("success_criteria", {})
        }
        
        return handoff


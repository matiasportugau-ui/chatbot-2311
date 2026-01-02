"""
Phase 4 Executor: Conflict Resolution
Multi-agent pattern with MergeAgent delegation
"""

from .base_executor import BaseExecutor
from typing import List, Dict, Any
import json
import sys
from pathlib import Path

ORCHESTRATOR_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ORCHESTRATOR_DIR.parent.parent))

try:
    from scripts.orchestrator.agent_interface import AgentCoordinator
except ImportError:
    AgentCoordinator = None


class Phase4Executor(BaseExecutor):
    """Executes Phase 4: Conflict Resolution with Multi-Agent Delegation"""
    
    def __init__(self, phase: int, state_manager):
        super().__init__(phase, state_manager)
        self.coordinator = AgentCoordinator() if AgentCoordinator else None
    
    def execute(self) -> List[str]:
        """Execute Phase 4: Conflict Resolution"""
        self.log_info("Starting Phase 4: Conflict Resolution")
        
        output_dir = self.ensure_output_dir("consolidation/repository_consolidation")
        
        # T4.1: Resolve conflicts
        self.log_info("T4.1: Resolving conflicts...")
        
        conflict_resolution = self._delegate_or_execute()
        
        # Save output
        output_file = output_dir / "conflict_resolution.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(conflict_resolution, f, indent=2, ensure_ascii=False)
        
        self.add_output(str(output_file))
        self.log_success("Phase 4 completed: Conflict resolution generated")
        
        return self.collect_outputs()
    
    def _delegate_or_execute(self) -> Dict[str, Any]:
        """Delegate to MergeAgent or execute directly"""
        if self.coordinator:
            try:
                result = self.coordinator.delegate_task(
                    "MergeAgent",
                    "T4.1",
                    {"type": "resolve_conflicts"}
                )
                return result.get("result", {})
            except Exception as e:
                self.log_error(f"Delegation failed: {e}, using fallback")
        
        # Fallback: direct execution
        return {
            "phase": 4,
            "timestamp": self._get_timestamp(),
            "conflicts_identified": [],
            "resolution_plan": [],
            "status": "pending_manual_review"
        }
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()


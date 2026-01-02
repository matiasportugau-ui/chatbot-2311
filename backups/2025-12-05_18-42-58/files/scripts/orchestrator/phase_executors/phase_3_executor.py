"""
Phase 3 Executor: Merge Strategy
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


class Phase3Executor(BaseExecutor):
    """Executes Phase 3: Merge Strategy with Multi-Agent Delegation"""
    
    def __init__(self, phase: int, state_manager):
        super().__init__(phase, state_manager)
        self.coordinator = AgentCoordinator() if AgentCoordinator else None
    
    def execute(self) -> List[str]:
        """Execute Phase 3: Merge Strategy"""
        self.log_info("Starting Phase 3: Merge Strategy")
        
        output_dir = self.ensure_output_dir("consolidation/repository_consolidation")
        
        # T3.1: Create merge strategy
        self.log_info("T3.1: Creating merge strategy...")
        
        merge_strategy = self._delegate_or_execute()
        
        # Save output
        output_file = output_dir / "merge_strategy.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merge_strategy, f, indent=2, ensure_ascii=False)
        
        self.add_output(str(output_file))
        self.log_success("Phase 3 completed: Merge strategy generated")
        
        return self.collect_outputs()
    
    def _delegate_or_execute(self) -> Dict[str, Any]:
        """Delegate to MergeAgent or execute directly"""
        if self.coordinator:
            try:
                result = self.coordinator.delegate_task(
                    "MergeAgent",
                    "T3.1",
                    {"type": "create_merge_strategy"}
                )
                return result.get("result", {})
            except Exception as e:
                self.log_error(f"Delegation failed: {e}, using fallback")
        
        # Fallback: direct execution
        return {
            "phase": 3,
            "timestamp": self._get_timestamp(),
            "strategy": "sequential_merge",
            "order": [],
            "conflict_resolution": "manual_review",
            "validation_steps": []
        }
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()


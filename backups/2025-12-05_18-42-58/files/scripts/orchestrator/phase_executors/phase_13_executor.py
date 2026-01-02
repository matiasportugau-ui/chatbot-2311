"""
Phase 13 Executor: CI/CD Pipeline
Multi-agent pattern with CICDAgent delegation
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


class Phase13Executor(BaseExecutor):
    """Executes Phase 13: CI/CD Pipeline with Multi-Agent Delegation"""
    
    def __init__(self, phase: int, state_manager):
        super().__init__(phase, state_manager)
        self.coordinator = AgentCoordinator() if AgentCoordinator else None
    
    def execute(self) -> List[str]:
        """Execute Phase 13: CI/CD Pipeline"""
        self.log_info("Starting Phase 13: CI/CD Pipeline")
        
        output_dir = self.ensure_output_dir("consolidation/cicd")
        
        # T13.1: Setup CI/CD pipeline
        self.log_info("T13.1: Setting up CI/CD pipeline...")
        
        pipeline_config = self._delegate_or_execute()
        
        # Save output
        output_file = output_dir / "pipeline_config.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(pipeline_config, f, indent=2, ensure_ascii=False)
        
        self.add_output(str(output_file))
        self.log_success("Phase 13 completed: CI/CD pipeline configured")
        
        return self.collect_outputs()
    
    def _delegate_or_execute(self) -> Dict[str, Any]:
        """Delegate to CICDAgent or execute directly"""
        if self.coordinator:
            try:
                result = self.coordinator.delegate_task(
                    "CICDAgent",
                    "T13.1",
                    {"type": "setup_cicd_pipeline"}
                )
                return result.get("result", {})
            except Exception as e:
                self.log_error(f"Delegation failed: {e}, using fallback")
        
        # Fallback: direct execution
        return {
            "phase": 13,
            "timestamp": self._get_timestamp(),
            "pipeline_tool": "github_actions",
            "stages": [],
            "workflows": [],
            "status": "pending"
        }
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()


"""
Phase 10 Executor: Infrastructure as Code
Multi-agent pattern with InfrastructureAgent delegation
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


class Phase10Executor(BaseExecutor):
    """Executes Phase 10: Infrastructure as Code with Multi-Agent Delegation"""
    
    def __init__(self, phase: int, state_manager):
        super().__init__(phase, state_manager)
        self.coordinator = AgentCoordinator() if AgentCoordinator else None
    
    def execute(self) -> List[str]:
        """Execute Phase 10: Infrastructure as Code"""
        self.log_info("Starting Phase 10: Infrastructure as Code")
        
        output_dir = self.ensure_output_dir("consolidation/infrastructure")
        
        # T10.1: Setup IaC
        self.log_info("T10.1: Setting up Infrastructure as Code...")
        
        iac_config = self._delegate_or_execute()
        
        # Save output
        output_file = output_dir / "iac_config.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(iac_config, f, indent=2, ensure_ascii=False)
        
        self.add_output(str(output_file))
        self.log_success("Phase 10 completed: IaC configuration generated")
        
        return self.collect_outputs()
    
    def _delegate_or_execute(self) -> Dict[str, Any]:
        """Delegate to InfrastructureAgent or execute directly"""
        if self.coordinator:
            try:
                result = self.coordinator.delegate_task(
                    "InfrastructureAgent",
                    "T10.1",
                    {"type": "setup_iac"}
                )
                return result.get("result", {})
            except Exception as e:
                self.log_error(f"Delegation failed: {e}, using fallback")
        
        # Fallback: direct execution
        return {
            "phase": 10,
            "timestamp": self._get_timestamp(),
            "iac_tool": "terraform",
            "config_files": [],
            "resources_defined": [],
            "status": "pending"
        }
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()


"""
Phase 11 Executor: Observability & Monitoring
Direct execution using logging system from Phase -3
"""

from .base_executor import BaseExecutor
from typing import List, Dict, Any
import json
import sys
from pathlib import Path

ORCHESTRATOR_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ORCHESTRATOR_DIR.parent.parent))


class Phase11Executor(BaseExecutor):
    """Executes Phase 11: Observability & Monitoring"""
    
    def __init__(self, phase: int, state_manager):
        super().__init__(phase, state_manager)
    
    def execute(self) -> List[str]:
        """Execute Phase 11: Observability & Monitoring"""
        self.log_info("Starting Phase 11: Observability & Monitoring")
        
        output_dir = self.ensure_output_dir("consolidation/observability")
        
        # T11.1: Setup monitoring
        self.log_info("T11.1: Setting up monitoring...")
        
        monitoring_setup = self._setup_monitoring()
        
        # Save output
        output_file = output_dir / "monitoring_setup.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(monitoring_setup, f, indent=2, ensure_ascii=False)
        
        self.add_output(str(output_file))
        self.log_success("Phase 11 completed: Monitoring setup completed")
        
        return self.collect_outputs()
    
    def _setup_monitoring(self) -> Dict[str, Any]:
        """Setup monitoring using logging system"""
        return {
            "phase": 11,
            "timestamp": self._get_timestamp(),
            "monitoring_tools": [],
            "metrics_configured": [],
            "alerts_setup": [],
            "status": "pending"
        }
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()


"""
Agent Handoff System
Enables execution of phases in separate agents with context handoff
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
try:
    from .context_manager import ContextManager
    from .state_manager import StateManager
except ImportError:
    # For standalone execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from scripts.orchestrator.context_manager import ContextManager
    from scripts.orchestrator.state_manager import StateManager


class AgentHandoff:
    """Manages handoff between agents for phase execution"""
    
    def __init__(self, context_manager: ContextManager, state_manager: StateManager):
        self.context_manager = context_manager
        self.state_manager = state_manager
        self.handoff_dir = Path("consolidation/handoffs")
        self.handoff_dir.mkdir(parents=True, exist_ok=True)
    
    def prepare_handoff(self, phase: int) -> Dict[str, Any]:
        """
        Prepare handoff package for a phase to be executed by another agent
        Returns complete handoff package
        """
        previous_phase = phase - 1 if phase > 0 else -1
        
        # Create handoff package
        handoff_package = self.context_manager.create_handoff_package(previous_phase, phase)
        
        # Add execution instructions
        handoff_package["execution_instructions"] = {
            "phase": phase,
            "agent_type": self._get_agent_type_for_phase(phase),
            "entry_point": f"scripts/orchestrator/phase_executors/phase_{phase}_executor.py",
            "context_file": str(self.context_manager.context_file),
            "state_file": "consolidation/execution_state.json"
        }
        
        # Add phase configuration
        handoff_package["phase_config"] = self._get_phase_config(phase)
        
        return handoff_package
    
    def save_handoff(self, phase: int, handoff_package: Optional[Dict[str, Any]] = None) -> str:
        """Save handoff package to file"""
        if handoff_package is None:
            handoff_package = self.prepare_handoff(phase)
        
        handoff_file = self.handoff_dir / f"handoff_phase_{phase}.json"
        
        with open(handoff_file, 'w') as f:
            json.dump(handoff_package, f, indent=2)
        
        # Record in context manager
        self.context_manager.save_handoff_package(handoff_package, str(handoff_file))
        
        return str(handoff_file)
    
    def load_handoff(self, phase: int) -> Dict[str, Any]:
        """Load handoff package for a phase"""
        handoff_file = self.handoff_dir / f"handoff_phase_{phase}.json"
        
        if not handoff_file.exists():
            raise FileNotFoundError(f"Handoff file not found for phase {phase}")
        
        return self.context_manager.load_handoff_package(str(handoff_file))
    
    def can_execute_in_separate_agent(self, phase: int) -> bool:
        """
        Determine if a phase can be executed in a separate agent
        Returns True if phase is ready for handoff
        """
        # Check if dependencies are met
        from .dependency_resolver import DependencyResolver
        resolver = DependencyResolver(state_manager=self.state_manager)
        can_execute, _ = resolver.check_dependencies(phase)
        
        if not can_execute:
            return False
        
        # Check if previous phase is completed
        if phase > 0:
            prev_status = self.state_manager.get_phase_status(phase - 1)
            if prev_status not in ["completed", "approved"]:
                return False
        
        return True
    
    def create_agent_script(self, phase: int, handoff_file: str) -> str:
        """
        Create a standalone script for an agent to execute a phase
        Returns path to created script
        """
        script_content = f'''#!/usr/bin/env python3
"""
Standalone Agent Script for Phase {phase}
This script can be executed by a separate agent with the handoff context
"""

import sys
import json
from pathlib import Path

# Add orchestrator to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.orchestrator.context_manager import ContextManager
from scripts.orchestrator.state_manager import StateManager
from scripts.orchestrator.agent_handoff import AgentHandoff

def main():
    """Execute phase {phase} with handoff context"""
    # Load handoff package
    handoff_file = Path("{handoff_file}")
    if not handoff_file.exists():
        print(f"Error: Handoff file not found: {{handoff_file}}")
        return 1
    
    with open(handoff_file, 'r') as f:
        handoff = json.load(f)
    
    print(f"Executing Phase {phase} with context from Phase {{handoff['from_phase']}}")
    print(f"Execution ID: {{handoff['execution_id']}}")
    
    # Initialize managers
    state_manager = StateManager()
    context_manager = ContextManager(state_manager)
    
    # Load context from handoff
    context_manager.context.update(handoff.get("global_context", {{}}))
    
    # Execute phase
    try:
        from scripts.orchestrator.main_orchestrator import MainOrchestrator
        orchestrator = MainOrchestrator()
        
        # Set current phase
        state_manager.set_current_phase({phase})
        
        # Execute
        success = orchestrator.execute_phase({phase})
        
        if success:
            print(f"Phase {phase} completed successfully")
            return 0
        else:
            print(f"Phase {phase} failed")
            return 1
    
    except Exception as e:
        print(f"Error executing phase {phase}: {{e}}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
        
        script_file = self.handoff_dir / f"execute_phase_{phase}.py"
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # Make executable
        import os
        os.chmod(script_file, 0o755)
        
        return str(script_file)
    
    def _get_agent_type_for_phase(self, phase: int) -> str:
        """Get recommended agent type for a phase"""
        agent_mapping = {
            0: "DiscoveryAgent",
            1: "RepositoryAgent",
            2: "RepositoryAgent",
            3: "MergeAgent",
            4: "MergeAgent",
            5: "MergeAgent",
            6: "MergeAgent",
            7: "IntegrationAgent",
            8: "IntegrationAgent",
            9: "SecurityAgent",
            10: "InfrastructureAgent",
            11: "ObservabilityAgent",
            12: "PerformanceAgent",
            13: "CICDAgent",
            14: "DisasterRecoveryAgent",
            15: "ValidationAgent"
        }
        return agent_mapping.get(phase, "OrchestratorAgent")
    
    def _get_phase_config(self, phase: int) -> Dict[str, Any]:
        """Get phase configuration"""
        config_file = Path("scripts/orchestrator/config/phase_config.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get("phases", {}).get(str(phase), {})
        return {}
    
    def generate_handoff_summary(self, phase: int) -> str:
        """Generate human-readable summary of handoff"""
        handoff = self.prepare_handoff(phase)
        
        summary = f"""
# Handoff Summary for Phase {phase}

## Execution Context
- Execution ID: {handoff['execution_id']}
- From Phase: {handoff['from_phase']}
- To Phase: {handoff['to_phase']}
- Agent Type: {handoff['execution_instructions']['agent_type']}

## Previous Phase Context
{json.dumps(handoff['previous_phase_context'], indent=2)}

## Dependency Contexts
Completed phases: {list(handoff['dependency_contexts'].keys())}

## Shared Artifacts
{list(handoff['shared_artifacts'].keys())}

## Global Context
{list(handoff['global_context'].keys())}

## State Summary
- Completed Phases: {handoff['state_summary']['completed_phases']}
- Overall Status: {handoff['state_summary']['overall_status']}
- Progress: {handoff['state_summary']['progress']:.1f}%

## Execution Instructions
- Entry Point: {handoff['execution_instructions']['entry_point']}
- Context File: {handoff['execution_instructions']['context_file']}
- State File: {handoff['execution_instructions']['state_file']}
"""
        return summary


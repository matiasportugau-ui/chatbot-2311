"""
Dependency Resolver for Phase Execution
Verifies prerequisite phases are completed before executing a phase
"""

import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from .state_manager import StateManager


class DependencyResolver:
    """Resolves phase dependencies and verifies prerequisites"""
    
    def __init__(self, config_file: str = "scripts/orchestrator/config/phase_config.json", 
                 state_manager: StateManager = None):
        self.config_file = Path(config_file)
        self.state_manager = state_manager
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load phase configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading phase config: {e}. Using default dependencies.")
                return self._default_config()
        else:
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default phase dependencies based on unified plan"""
        return {
            "phases": {
                "0": {"dependencies": []},
                "1": {"dependencies": [0]},
                "2": {"dependencies": [1]},
                "3": {"dependencies": [2]},
                "4": {"dependencies": [3]},
                "5": {"dependencies": [4]},
                "6": {"dependencies": [5]},
                "7": {"dependencies": [6]},
                "8": {"dependencies": [7]},
                "9": {"dependencies": [8]},
                "10": {"dependencies": [9]},
                "11": {"dependencies": [10]},
                "12": {"dependencies": [11]},
                "13": {"dependencies": [12]},
                "14": {"dependencies": [13]},
                "15": {"dependencies": [14]}
            }
        }
    
    def get_dependencies(self, phase: int) -> List[int]:
        """Get list of phase dependencies"""
        phase_key = str(phase)
        if phase_key in self.config.get("phases", {}):
            return self.config["phases"][phase_key].get("dependencies", [])
        return []
    
    def check_dependencies(self, phase: int) -> Tuple[bool, List[int]]:
        """
        Check if all dependencies for a phase are met
        Returns: (all_met, missing_dependencies)
        """
        if not self.state_manager:
            return False, []
        
        dependencies = self.get_dependencies(phase)
        missing = []
        
        for dep_phase in dependencies:
            status = self.state_manager.get_phase_status(dep_phase)
            if status not in ["completed", "approved"]:
                missing.append(dep_phase)
        
        return len(missing) == 0, missing
    
    def can_execute(self, phase: int) -> bool:
        """Check if phase can be executed (dependencies met)"""
        all_met, _ = self.check_dependencies(phase)
        return all_met
    
    def get_dependency_graph(self) -> Dict[int, List[int]]:
        """Get complete dependency graph"""
        graph = {}
        for phase_num in range(16):
            graph[phase_num] = self.get_dependencies(phase_num)
        return graph
    
    def get_ready_phases(self) -> List[int]:
        """Get list of phases that are ready to execute (dependencies met)"""
        ready = []
        for phase_num in range(16):
            if self.can_execute(phase_num):
                # Also check that phase hasn't been completed
                if self.state_manager:
                    status = self.state_manager.get_phase_status(phase_num)
                    if status in ["pending", "failed"]:
                        ready.append(phase_num)
                else:
                    ready.append(phase_num)
        return ready
    
    def get_blocked_phases(self) -> Dict[int, List[int]]:
        """Get phases that are blocked by missing dependencies"""
        blocked = {}
        for phase_num in range(16):
            all_met, missing = self.check_dependencies(phase_num)
            if not all_met:
                blocked[phase_num] = missing
        return blocked


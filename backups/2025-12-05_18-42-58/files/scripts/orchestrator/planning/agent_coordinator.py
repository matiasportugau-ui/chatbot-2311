"""
Planning Agent Coordinator
Coordinates task delegation to all 12 specialized agents
"""

from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add parent directory to path for imports
ORCHESTRATOR_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ORCHESTRATOR_DIR.parent.parent))

try:
    from scripts.orchestrator.agent_interface import AgentCoordinator, RepositoryAgent, IntegrationAgent, QuotationAgent
except ImportError:
    AgentCoordinator = None
    RepositoryAgent = None
    IntegrationAgent = None
    QuotationAgent = None


class PlanningAgentCoordinator:
    """Coordinates PlanningAgent tasks with all specialized agents"""

    def __init__(self):
        self.base_coordinator = AgentCoordinator() if AgentCoordinator else None
        self.agent_mapping = {
            # Phase 1: PR Analysis
            "T1.1": "RepositoryAgent",  # Extract PR metadata
            "T1.2": "RepositoryAgent",  # Analyze changed files
            "T1.3": "DiscoveryAgent",   # Understand PR purpose
            "T1.4": "DiscoveryAgent",   # Dependency analysis

            # Phase 2: Impact Assessment
            "T2.1": "RepositoryAgent",  # Architecture impact (also IntegrationAgent)
            "T2.2": "OrchestratorAgent",  # Consolidation plan alignment
            "T2.3": "QuotationAgent",   # BMC domain impact
            "T2.4": "SecurityAgent",    # Security & production readiness

            # Phase 3: Integration Strategy
            "T3.1": "MergeAgent",       # Merge strategy
            "T3.2": "ValidationAgent", # Testing strategy
            "T3.3": "DiscoveryAgent",  # Documentation updates

            # Phase 4: Plan Generation
            "T4.1": "OrchestratorAgent",  # Task breakdown
            "T4.2": "OrchestratorAgent",  # Phase integration
            "T4.3": "OrchestratorAgent",  # Timeline estimation
            "T4.4": "OrchestratorAgent",  # Risk assessment
        }

    def delegate_task(self, task_id: str, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate a task to the appropriate agent"""
        agent_type = self.agent_mapping.get(task_id)

        if not agent_type:
            return {"error": f"No agent mapping for task {task_id}"}

        if not self.base_coordinator:
            # Fallback: return task config for direct execution
            return {
                "task_id": task_id,
                "agent_type": agent_type,
                "task_config": task_config,
                "delegated": False,
                "fallback": True
            }

        try:
            # Delegate to base coordinator
            request_file = self.base_coordinator.delegate_task(agent_type, task_id, task_config)
            result = self.base_coordinator.execute_delegated_task(task_id, agent_type)
            return result
        except Exception as e:
            return {
                "error": f"Failed to delegate task {task_id} to {agent_type}: {str(e)}",
                "task_id": task_id,
                "agent_type": agent_type,
                "task_config": task_config
            }

    def delegate_to_multiple_agents(self, task_id: str, task_config: Dict[str, Any],
                                    agent_types: list) -> Dict[str, Any]:
        """Delegate a task to multiple agents and aggregate results"""
        results = {}
        for agent_type in agent_types:
            try:
                if self.base_coordinator:
                    request_file = self.base_coordinator.delegate_task(agent_type, f"{task_id}_{agent_type}", task_config)
                    result = self.base_coordinator.execute_delegated_task(f"{task_id}_{agent_type}", agent_type)
                    results[agent_type] = result
                else:
                    results[agent_type] = {
                        "task_id": f"{task_id}_{agent_type}",
                        "agent_type": agent_type,
                        "task_config": task_config,
                        "fallback": True
                    }
            except Exception as e:
                results[agent_type] = {"error": str(e)}

        return {
            "task_id": task_id,
            "results": results,
            "aggregated": True
        }


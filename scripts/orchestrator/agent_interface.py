"""
Agent Interface System
Provides communication interfaces between agents for task delegation
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod


class AgentInterface(ABC):
    """Base interface for all agents"""

    def __init__(self, agent_name: str, agent_type: str):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.task_dir = Path("consolidation/tasks")
        self.task_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def execute_task(self, task_id: str, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return results"""
        pass

    def create_task_request(self, task_id: str, task_config: Dict[str, Any]) -> str:
        """Create a task request file for delegation"""
        request = {
            "task_id": task_id,
            "agent_type": self.agent_type,
            "agent_name": self.agent_name,
            "task_config": task_config,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }

        request_file = self.task_dir / f"{task_id}_request.json"
        with open(request_file, 'w') as f:
            json.dump(request, f, indent=2)

        return str(request_file)

    def save_task_result(self, task_id: str, result: Dict[str, Any]) -> str:
        """Save task execution result"""
        result_file = self.task_dir / f"{task_id}_result.json"

        result_data = {
            "task_id": task_id,
            "agent_type": self.agent_type,
            "agent_name": self.agent_name,
            "result": result,
            "completed_at": datetime.now().isoformat(),
            "status": "completed"
        }

        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)

        return str(result_file)

    def load_task_request(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load a task request"""
        request_file = self.task_dir / f"{task_id}_request.json"
        if request_file.exists():
            with open(request_file, 'r') as f:
                return json.load(f)
        return None


class RepositoryAgent(AgentInterface):
    """Repository Agent - Handles repository and workspace analysis"""

    def __init__(self):
        super().__init__("RepositoryAgent", "RepositoryAgent")

    def execute_task(self, task_id: str, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute repository/workspace analysis tasks"""
        task_type = task_config.get("type")

        if task_type == "analyze_repositories":
            return self._analyze_repositories(task_config)
        elif task_type == "analyze_workspace":
            return self._analyze_workspace(task_config)
        else:
            return {"error": f"Unknown task type: {task_type}"}

    def _analyze_repositories(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze repository structure"""
        repositories = config.get("repositories", [])

        # Placeholder - would call actual analysis script
        return {
            "repositories": repositories,
            "analysis_date": datetime.now().isoformat(),
            "technologies": ["Python", "TypeScript", "Docker"],
            "dependencies": {},
            "duplicates": [],
            "status": "completed"
        }

    def _analyze_workspace(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workspace structure"""
        workspace_path = config.get("workspace_path", ".")

        # Placeholder - would call actual analysis script
        return {
            "workspace_path": workspace_path,
            "components_found": 10,
            "files_analyzed": 247,
            "status": "completed"
        }


class IntegrationAgent(AgentInterface):
    """Integration Agent - Handles integration validation"""

    def __init__(self):
        super().__init__("IntegrationAgent", "IntegrationAgent")

    def execute_task(self, task_id: str, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration validation tasks"""
        task_type = task_config.get("type")

        if task_type == "validate_integrations":
            return self._validate_integrations(task_config)
        else:
            return {"error": f"Unknown task type: {task_type}"}

    def _validate_integrations(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate integrations"""
        integrations = config.get("integrations", [])

        # Placeholder - would call actual validation script
        results = {}
        for integration in integrations:
            results[integration] = {
                "status": "pending_credentials" if integration == "whatsapp" else "configured",
                "configured": integration != "whatsapp"
            }

        return {
            "integrations": results,
            "status": "completed"
        }


class QuotationAgent(AgentInterface):
    """Quotation Agent - Handles BMC quotation engine tasks"""

    def __init__(self):
        super().__init__("QuotationAgent", "QuotationAgent")

    def execute_task(self, task_id: str, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute quotation engine tasks"""
        task_type = task_config.get("type")

        if task_type == "inventory_bmc_components":
            return self._inventory_bmc_components(task_config)
        elif task_type == "assess_quotation_engine":
            return self._assess_quotation_engine(task_config)
        else:
            return {"error": f"Unknown task type: {task_type}"}

    def _inventory_bmc_components(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Inventory BMC components"""
        # Placeholder - would call actual inventory script
        return {
            "components_found": 7,
            "components": [
                "quotation_engine",
                "whatsapp_integration",
                "n8n_workflows",
                "knowledge_base",
                "background_agents",
                "dashboard",
                "api_server"
            ],
            "status": "completed"
        }

    def _assess_quotation_engine(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quotation engine"""
        # Placeholder - would call actual assessment script
        return {
            "status": "functional",
            "products_supported": 3,
            "zones_supported": 4,
            "completeness": 0.85,
            "status": "completed"
        }


class PlanningAgent(AgentInterface):
    """Planning Agent - Analyzes PRs and generates implementation plans"""

    def __init__(self):
        super().__init__("PlanningAgent", "PlanningAgent")
        self._impl = None

    def _get_impl(self):
        """Lazy load implementation to avoid circular dependencies"""
        if self._impl is None:
            from scripts.orchestrator.planning_agent import PlanningAgent as PlanningAgentImpl
            self._impl = PlanningAgentImpl()
        return self._impl

    def execute_task(self, task_id: str, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a planning task"""
        agent = self._get_impl()

        task_type = task_config.get("type")
        if task_type == "analyze_pr":
            pr_number = task_config.get("pr_number")
            return agent.analyze_pr(pr_number)
        elif task_type == "analyze_local_changes":
            return agent.analyze_local_changes()
        else:
            return {"error": f"Unknown task type: {task_type}"}


class AgentCoordinator:
    """Coordinates communication between agents"""

    def __init__(self):
        self.agents = {
            "RepositoryAgent": RepositoryAgent(),
            "IntegrationAgent": IntegrationAgent(),
            "QuotationAgent": QuotationAgent(),
            "PlanningAgent": PlanningAgent()
        }
        self.task_dir = Path("consolidation/tasks")
        self.task_dir.mkdir(parents=True, exist_ok=True)

    def delegate_task(self, agent_type: str, task_id: str, task_config: Dict[str, Any]) -> str:
        """Delegate a task to a specific agent"""
        if agent_type not in self.agents:
            raise ValueError(f"Unknown agent type: {agent_type}")

        agent = self.agents[agent_type]
        request_file = agent.create_task_request(task_id, task_config)

        return request_file

    def execute_delegated_task(self, task_id: str, agent_type: str) -> Dict[str, Any]:
        """Execute a delegated task"""
        if agent_type not in self.agents:
            raise ValueError(f"Unknown agent type: {agent_type}")

        agent = self.agents[agent_type]
        request_file = self.task_dir / f"{task_id}_request.json"

        if not request_file.exists():
            return {"error": f"Task request not found: {task_id}"}

        with open(request_file, 'r') as f:
            request = json.load(f)

        task_config = request.get("task_config", {})
        result = agent.execute_task(task_id, task_config)
        result_file = agent.save_task_result(task_id, result)

        return {
            "task_id": task_id,
            "agent_type": agent_type,
            "result": result,
            "result_file": result_file
        }

    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get result of a completed task"""
        result_file = self.task_dir / f"{task_id}_result.json"

        if result_file.exists():
            with open(result_file, 'r') as f:
                return json.load(f)
        return None

    def wait_for_task(self, task_id: str, timeout: int = 300) -> Optional[Dict[str, Any]]:
        """Wait for a task to complete"""
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = self.get_task_result(task_id)
            if result:
                return result
            time.sleep(1)

        return None


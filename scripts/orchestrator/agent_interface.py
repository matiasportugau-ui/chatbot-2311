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


class OrchestratorAgent(AgentInterface):
    """
    Orchestrator Agent (Gravity-mode)
    Master coordinator for interpreting changes and orchestrating automated development.

    Focused on:
    - Mapping PR intent to the unified consolidation plan (Task 2.2)
    - Generating actionable task breakdowns (Task 4.1)
    - Integrating tasks to phases (Task 4.2)
    - Timeline estimation (Task 4.3)
    - Risk assessment (Task 4.4)
    """

    def __init__(self):
        super().__init__("OrchestratorAgent", "OrchestratorAgent")

    def execute_task(self, task_id: str, task_config: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task_config.get("type")

        if task_type == "assess_plan_alignment":
            return self._assess_plan_alignment(task_config)
        if task_type == "create_task_breakdown":
            return self._create_task_breakdown(task_config)
        if task_type == "integrate_phases":
            return self._integrate_phases(task_config)
        if task_type == "estimate_timeline":
            return self._estimate_timeline(task_config)
        if task_type == "assess_risks":
            return self._assess_risks(task_config)

        return {"error": f"Unknown task type: {task_type}"}

    def _assess_plan_alignment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        related_phases = config.get("related_phases") or []
        consolidation_plan = config.get("consolidation_plan") or {}

        phases = consolidation_plan.get("phases") or {}
        existing_phase_nums = set()
        for k in phases.keys():
            try:
                existing_phase_nums.add(int(k))
            except Exception:
                pass

        affected = []
        for p in related_phases:
            try:
                p_int = int(p)
            except Exception:
                continue
            if not existing_phase_nums or p_int in existing_phase_nums:
                affected.append(p_int)

        affected = sorted(set(affected))

        return {
            "primary_phase": affected[0] if affected else None,
            "affected_phases": affected,
            "phase_updates_required": [
                {"phase": phase, "update_type": "documentation", "tasks_to_add": []}
                for phase in affected
            ],
            "new_phase_required": False,
            "conflicts": [],
            "dependencies": []
        }

    def _create_task_breakdown(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        analysis = config.get("analysis") or {}
        impact = config.get("impact") or {}
        strategy = config.get("strategy") or {}

        files_analysis = (analysis.get("task_1.2") or {})
        categories = files_analysis.get("categories") or {}

        tasks: List[Dict[str, Any]] = []

        # Docs-centric tasks
        doc_files = categories.get("documentation") or []
        if doc_files:
            tasks.append({
                "task_id": "T0.8",
                "task_name": "Revisar e integrar documentación del cambio",
                "script": "scripts/orchestrator/planning_agent.py",
                "action": "Revisar documentación agregada/modificada y vincularla a la fase correspondiente del plan.",
                "files": [f.get("path") for f in doc_files if isinstance(f, dict)],
                "dependencies": [],
                "output": "consolidation/pr_analysis/",
                "priority": "P1",
                "agent": "DiscoveryAgent",
                "estimated_duration": "2 hours",
                "bmc_context": "Asegurar consistencia con el Plan Unificado y con el modo automático/auto-aprobación."
            })

        # Code-centric tasks
        src_files = categories.get("source_code") or []
        if src_files:
            tasks.append({
                "task_id": "T15.1",
                "task_name": "Validación rápida de regresión (tests/lint)",
                "script": "scripts/orchestrator/run_automated_execution.py",
                "action": "Ejecutar suite de pruebas relevante y validar que no se introduzcan regresiones.",
                "files": [f.get("path") for f in src_files if isinstance(f, dict)],
                "dependencies": [],
                "output": "consolidation/reports/",
                "priority": "P0",
                "agent": "ValidationAgent",
                "estimated_duration": "1.5 hours",
                "bmc_context": "Priorizar flujos críticos: cotizaciones, integraciones, training/benchmark si aplica."
            })

        # Config/deps tasks
        dep_files = categories.get("dependencies") or []
        cfg_files = categories.get("configuration") or []
        if dep_files or cfg_files:
            tasks.append({
                "task_id": "T1.9",
                "task_name": "Verificar dependencias/config y compatibilidad de entorno",
                "script": "scripts/orchestrator/verify_implementation.py",
                "action": "Validar cambios en dependencias/configuración y compatibilidad con el stack actual.",
                "files": [f.get("path") for f in (dep_files + cfg_files) if isinstance(f, dict)],
                "dependencies": [],
                "output": "consolidation/reports/",
                "priority": "P1",
                "agent": "RepositoryAgent",
                "estimated_duration": "1 hour",
                "bmc_context": "Mantener coherencia con secrets/env y configuración del orchestrator."
            })

        # If strategy suggests docs, include them
        doc_updates = (strategy.get("task_3.3") or {}).get("new_documentation") or []
        for idx, doc in enumerate(doc_updates, start=1):
            file_path = doc.get("file") if isinstance(doc, dict) else None
            if not file_path:
                continue
            tasks.append({
                "task_id": f"T0.8.{idx}",
                "task_name": f"Validar documento: {Path(file_path).name}",
                "script": None,
                "action": "Revisar consistencia, links, comandos y alineación al plan.",
                "files": [file_path],
                "dependencies": ["T0.8"] if doc_files else [],
                "output": None,
                "priority": "P2",
                "agent": "DiscoveryAgent",
                "estimated_duration": "0.5 hours",
                "bmc_context": "Mantener estilo y convenciones del repo."
            })

        return tasks

    def _integrate_phases(self, config: Dict[str, Any]) -> Dict[str, Any]:
        tasks = config.get("tasks") or []
        impact = config.get("impact") or {}
        plan_alignment = impact.get("task_2.2") or {}
        affected_phases = plan_alignment.get("affected_phases") or [0]

        tasks_by_phase: Dict[str, List[Dict[str, Any]]] = {str(p): [] for p in affected_phases}

        for task in tasks:
            task_id = (task or {}).get("task_id", "")
            phase_key = None
            if isinstance(task_id, str) and task_id.startswith("T"):
                try:
                    phase_key = task_id.split(".")[0][1:]
                except Exception:
                    phase_key = None
            if phase_key and phase_key.isdigit():
                tasks_by_phase.setdefault(phase_key, []).append(task)
            else:
                tasks_by_phase.setdefault(str(affected_phases[0]), []).append(task)

        return {
            "tasks_by_phase": tasks_by_phase,
            "phase_executor_updates": [],
            "new_phase_required": False,
            "orchestrator_config_updates": []
        }

    def _estimate_timeline(self, config: Dict[str, Any]) -> Dict[str, Any]:
        tasks = config.get("tasks") or []

        def _parse_hours(duration: str) -> float:
            if not duration:
                return 0.0
            parts = duration.strip().split()
            if not parts:
                return 0.0
            try:
                value = float(parts[0])
            except Exception:
                return 0.0
            unit = parts[1].lower() if len(parts) > 1 else "hours"
            if unit.startswith("day"):
                return value * 8.0
            return value

        total_hours = 0.0
        for t in tasks:
            total_hours += _parse_hours((t or {}).get("estimated_duration", ""))

        total_estimated_duration = f"{round(total_hours, 1)} hours"

        return {
            "total_estimated_duration": total_estimated_duration,
            "critical_path": [(t or {}).get("task_id") for t in tasks if (t or {}).get("task_id")],
            "parallel_opportunities": [],
            "milestones": [
                {
                    "milestone": "Plan ejecutable validado",
                    "tasks": [(t or {}).get("task_id") for t in tasks if (t or {}).get("task_id")],
                    "estimated_completion": total_estimated_duration
                }
            ],
            "dependencies_resolved": True,
            "buffer_time": "30 minutes"
        }

    def _assess_risks(self, config: Dict[str, Any]) -> Dict[str, Any]:
        analysis = config.get("analysis") or {}
        files_analysis = (analysis.get("task_1.2") or {})
        categories = files_analysis.get("categories") or {}

        risks = []
        if categories.get("dependencies"):
            risks.append({
                "risk": "Cambios en dependencias pueden romper compatibilidad o builds",
                "probability": "medium",
                "impact": "high",
                "mitigation": "Validar instalación y ejecutar tests mínimos de smoke",
                "owner": "RepositoryAgent"
            })
        if categories.get("source_code"):
            risks.append({
                "risk": "Cambios de código pueden introducir regresiones en flujos críticos",
                "probability": "medium",
                "impact": "high",
                "mitigation": "Ejecutar tests y revisar paths críticos (cotizaciones, integraciones, training/benchmark)",
                "owner": "ValidationAgent"
            })
        if categories.get("configuration"):
            risks.append({
                "risk": "Cambios de configuración/secrets pueden romper despliegues",
                "probability": "low",
                "impact": "high",
                "mitigation": "Validar env template y secretos requeridos; no hardcodear credenciales",
                "owner": "SecurityAgent"
            })

        return {
            "risks": risks,
            "blockers": [],
            "assumptions": [
                "El orchestrator y el plan unificado son la fuente de verdad para fases (0-15).",
                "Auto-aprobación y modo automated se mantienen como default."
            ],
            "constraints": [
                "No introducir credenciales en el repo",
                "Mantener compatibilidad con el orchestrator existente"
            ],
            "rollback_procedures": [
                "Revertir cambios puntuales y re-ejecutar validaciones"
            ]
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
            "OrchestratorAgent": OrchestratorAgent(),
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


"""
Plan Generator Module
Implements Phase 4: Implementation Plan Generation (Tasks 4.1-4.4)
"""

from typing import Dict, Any, List
from datetime import datetime
from scripts.orchestrator.planning.agent_coordinator import PlanningAgentCoordinator


class PlanGenerator:
    """Generates detailed implementation plans"""

    def __init__(self):
        self.coordinator = PlanningAgentCoordinator()

    def generate_plan(self, analysis: Dict[str, Any], impact: Dict[str, Any],
                     strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for plan generation - Phase 4"""
        # Task 4.1: Create Detailed Task Breakdown
        tasks = self.create_task_breakdown(analysis, impact, strategy)

        # Task 4.2: Phase Integration
        phase_integration = self.integrate_phases(tasks, impact)

        # Task 4.3: Timeline Estimation
        timeline = self.estimate_timeline(tasks)

        # Task 4.4: Risk Assessment
        risks = self.assess_risks(analysis, impact, strategy)

        return {
            "phase": 4,
            "task_4.1": tasks,
            "task_4.2": phase_integration,
            "task_4.3": timeline,
            "task_4.4": risks,
            "plan_complete": True
        }

    def create_task_breakdown(self, analysis: Dict[str, Any], impact: Dict[str, Any],
                            strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Task 4.1: Create Detailed Task Breakdown"""
        # Delegate to OrchestratorAgent
        task_config = {
            "type": "create_task_breakdown",
            "analysis": analysis,
            "impact": impact,
            "strategy": strategy
        }

        result = self.coordinator.delegate_task("T4.1", task_config)

        if result.get("error") or result.get("fallback"):
            # Fallback: generate basic tasks
            tasks = []

            # Generate task for documentation review if needed
            doc_updates = strategy.get("task_3.3", {}).get("new_documentation", [])
            if doc_updates:
                tasks.append({
                    "task_id": "T0.8",
                    "task_name": "Review and integrate documentation",
                    "script": "scripts/orchestrator/documentation/review_deployment_docs.py",
                    "action": "Review new documentation files and integrate into Phase 0",
                    "files": [doc.get("file") for doc in doc_updates],
                    "dependencies": [],
                    "output": "consolidation/discovery/deployment_docs_integration.json",
                    "priority": "P1",
                    "agent": "DiscoveryAgent",
                    "estimated_duration": "2 hours",
                    "bmc_context": "Ensure deployment plan aligns with BMC production requirements"
                })

            return tasks

        return result.get("result", [])

    def integrate_phases(self, tasks: List[Dict[str, Any]], impact: Dict[str, Any]) -> Dict[str, Any]:
        """Task 4.2: Phase Integration"""
        # Delegate to OrchestratorAgent
        task_config = {
            "type": "integrate_phases",
            "tasks": tasks,
            "impact": impact
        }

        result = self.coordinator.delegate_task("T4.2", task_config)

        if result.get("error") or result.get("fallback"):
            # Fallback: map tasks to phases
            plan_alignment = impact.get("task_2.2", {})
            affected_phases = plan_alignment.get("affected_phases", [0])

            tasks_by_phase = {}
            for phase in affected_phases:
                tasks_by_phase[str(phase)] = [
                    task for task in tasks if task.get("task_id", "").startswith(f"T{phase}.")
                ]

            return {
                "tasks_by_phase": tasks_by_phase,
                "phase_executor_updates": [],
                "new_phase_required": False,
                "orchestrator_config_updates": []
            }

        return result.get("result", {})

    def estimate_timeline(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Task 4.3: Timeline Estimation"""
        # Delegate to OrchestratorAgent
        task_config = {
            "type": "estimate_timeline",
            "tasks": tasks
        }

        result = self.coordinator.delegate_task("T4.3", task_config)

        if result.get("error") or result.get("fallback"):
            # Fallback: estimate from task durations
            total_duration = "0 hours"
            if tasks:
                # Simple estimation: sum up durations
                durations = []
                for task in tasks:
                    duration_str = task.get("estimated_duration", "0 hours")
                    # Parse duration (simple: assume "X hours" format)
                    try:
                        hours = float(duration_str.split()[0])
                        durations.append(hours)
                    except:
                        pass

                total_hours = sum(durations)
                total_duration = f"{total_hours} hours"

            return {
                "total_estimated_duration": total_duration,
                "critical_path": [task.get("task_id") for task in tasks],
                "parallel_opportunities": [],
                "milestones": [
                    {
                        "milestone": "Documentation Review Complete",
                        "tasks": [task.get("task_id") for task in tasks],
                        "estimated_completion": total_duration
                    }
                ],
                "dependencies_resolved": True,
                "buffer_time": "30 minutes"
            }

        return result.get("result", {})

    def assess_risks(self, analysis: Dict[str, Any], impact: Dict[str, Any],
                    strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Task 4.4: Risk Assessment"""
        # Delegate to OrchestratorAgent
        task_config = {
            "type": "assess_risks",
            "analysis": analysis,
            "impact": impact,
            "strategy": strategy
        }

        result = self.coordinator.delegate_task("T4.4", task_config)

        if result.get("error") or result.get("fallback"):
            # Fallback: basic risk assessment
            files_analysis = analysis.get("task_1.2", {})
            doc_files = files_analysis.get("categories", {}).get("documentation", [])

            risks = []
            if doc_files:
                risks.append({
                    "risk": "Documentation may conflict with existing plans",
                    "probability": "low",
                    "impact": "medium",
                    "mitigation": "Review existing plans before integration",
                    "owner": "DiscoveryAgent"
                })

            return {
                "risks": risks,
                "blockers": [],
                "assumptions": [
                    "PR changes are documentation-only",
                    "No code changes required"
                ],
                "constraints": [
                    "Must maintain compatibility with existing orchestrator system"
                ],
                "rollback_procedures": [
                    "Revert documentation changes if conflicts arise"
                ]
            }

        return result.get("result", {})


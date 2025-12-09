"""
Integration Strategist Module
Implements Phase 3: Integration Strategy (Tasks 3.1-3.3)
"""

from typing import Dict, Any, List
from scripts.orchestrator.planning.agent_coordinator import PlanningAgentCoordinator


class IntegrationStrategist:
    """Develops integration strategy for PR changes"""

    def __init__(self):
        self.coordinator = PlanningAgentCoordinator()

    def develop_strategy(self, analysis: Dict[str, Any], impact: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for integration strategy - Phase 3"""
        # Task 3.1: Merge Strategy Development
        merge_strategy = self.develop_merge_strategy(analysis, impact)

        # Task 3.2: Testing Strategy
        testing_strategy = self.develop_testing_strategy(analysis, impact)

        # Task 3.3: Documentation Updates
        documentation_updates = self.plan_documentation_updates(analysis, impact)

        return {
            "phase": 3,
            "task_3.1": merge_strategy,
            "task_3.2": testing_strategy,
            "task_3.3": documentation_updates,
            "strategy_complete": True
        }

    def develop_merge_strategy(self, analysis: Dict[str, Any], impact: Dict[str, Any]) -> Dict[str, Any]:
        """Task 3.1: Merge Strategy Development"""
        metadata = analysis.get("task_1.1", {})
        plan_alignment = impact.get("task_2.2", {})

        # Delegate to MergeAgent
        task_config = {
            "type": "develop_merge_strategy",
            "metadata": metadata,
            "plan_alignment": plan_alignment
        }

        result = self.coordinator.delegate_task("T3.1", task_config)

        if result.get("error") or result.get("fallback"):
            # Fallback: determine merge strategy
            base_branch = metadata.get("base_branch", "main")
            state = metadata.get("state", "open")

            merge_strategy = "direct_merge"
            if state == "merged":
                merge_strategy = "already_merged"

            return {
                "merge_strategy": merge_strategy,
                "target_branch": base_branch,
                "conflicts_expected": False,
                "conflict_resolution": "not_required",
                "pre_merge_testing": ["documentation_review"],
                "rollback_plan": "git_revert"
            }

        return result.get("result", {})

    def develop_testing_strategy(self, analysis: Dict[str, Any], impact: Dict[str, Any]) -> Dict[str, Any]:
        """Task 3.2: Testing Strategy"""
        files_analysis = analysis.get("task_1.2", {})
        bmc_impact = impact.get("task_2.3", {})

        # Delegate to ValidationAgent
        task_config = {
            "type": "develop_testing_strategy",
            "files": files_analysis.get("files", []),
            "bmc_impact": bmc_impact
        }

        result = self.coordinator.delegate_task("T3.2", task_config)

        if result.get("error") or result.get("fallback"):
            # Fallback: basic testing strategy
            has_code_changes = len(files_analysis.get("categories", {}).get("source_code", [])) > 0
            bmc_testing_required = bmc_impact.get("bmc_testing_required", False)

            return {
                "test_updates_required": has_code_changes,
                "integration_testing": {
                    "required": has_code_changes,
                    "scenarios": []
                },
                "bmc_testing": {
                    "required": bmc_testing_required,
                    "scenarios": []
                },
                "regression_testing": {
                    "required": has_code_changes,
                    "scope": []
                },
                "performance_testing": {
                    "required": False
                },
                "uat_required": False
            }

        return result.get("result", {})

    def plan_documentation_updates(self, analysis: Dict[str, Any], impact: Dict[str, Any]) -> Dict[str, Any]:
        """Task 3.3: Documentation Updates"""
        files_analysis = analysis.get("task_1.2", {})
        plan_alignment = impact.get("task_2.2", {})

        # Delegate to DiscoveryAgent
        task_config = {
            "type": "plan_documentation_updates",
            "files": files_analysis.get("files", []),
            "plan_alignment": plan_alignment
        }

        result = self.coordinator.delegate_task("T3.3", task_config)

        if result.get("error") or result.get("fallback"):
            # Fallback: identify documentation needs
            doc_files = files_analysis.get("categories", {}).get("documentation", [])
            affected_phases = plan_alignment.get("affected_phases", [])

            documentation_updates = []
            if affected_phases:
                documentation_updates.append({
                    "file": ".cursor/plans/UNIFIED_CONSOLIDATION_PRODUCTION_PLAN.md",
                    "update_type": "reference",
                    "priority": "low"
                })

            new_documentation = [
                {
                    "file": doc.get("path"),
                    "status": "added" if doc.get("status") == "added" else "modified",
                    "location": "root" if "/" not in doc.get("path", "") else "subdirectory"
                }
                for doc in doc_files
            ]

            return {
                "documentation_updates": documentation_updates,
                "new_documentation": new_documentation,
                "diagram_updates": False
            }

        return result.get("result", {})


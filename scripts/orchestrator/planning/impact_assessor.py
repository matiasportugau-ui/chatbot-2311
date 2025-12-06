"""
Impact Assessor Module
Implements Phase 2: Impact Assessment (Tasks 2.1-2.4)
"""

from typing import Dict, Any, Optional
from pathlib import Path
import sys

ORCHESTRATOR_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ORCHESTRATOR_DIR.parent.parent))

from scripts.orchestrator.planning.utils import load_consolidation_plan, map_to_bmc_components
from scripts.orchestrator.planning.agent_coordinator import PlanningAgentCoordinator


class ImpactAssessor:
    """Assesses impact of PR changes on system architecture and consolidation plan"""

    def __init__(self):
        self.coordinator = PlanningAgentCoordinator()
        self.consolidation_plan = None

    def assess_impact(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for impact assessment - Phase 2"""
        # Load consolidation plan
        self.consolidation_plan = load_consolidation_plan()

        # Task 2.1: Architecture Impact Analysis
        architecture_impact = self.analyze_architecture_impact(analysis)

        # Task 2.2: Consolidation Plan Alignment
        plan_alignment = self.assess_plan_alignment(analysis)

        # Task 2.3: BMC Domain Impact
        bmc_impact = self.assess_bmc_domain_impact(analysis)

        # Task 2.4: Security & Production Readiness
        security_impact = self.assess_security_impact(analysis)

        return {
            "phase": 2,
            "task_2.1": architecture_impact,
            "task_2.2": plan_alignment,
            "task_2.3": bmc_impact,
            "task_2.4": security_impact,
            "assessment_complete": True
        }

    def analyze_architecture_impact(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Task 2.1: Architecture Impact Analysis"""
        files_analysis = analysis.get("task_1.2", {})
        files = files_analysis.get("files", [])
        bmc_components = files_analysis.get("bmc_components", [])

        # Delegate to RepositoryAgent and IntegrationAgent
        task_config = {
            "type": "analyze_architecture_impact",
            "files": files,
            "bmc_components": bmc_components
        }

        result = self.coordinator.delegate_to_multiple_agents(
            "T2.1",
            task_config,
            ["RepositoryAgent", "IntegrationAgent"]
        )

        if result.get("aggregated"):
            # Aggregate results
            repo_result = result["results"].get("RepositoryAgent", {})
            int_result = result["results"].get("IntegrationAgent", {})

            affected_components = list(set(
                repo_result.get("affected_components", []) +
                int_result.get("affected_components", [])
            ))
        else:
            # Fallback: analyze locally
            affected_components = bmc_components
            for file in files:
                path = file.get("path", "")
                components = map_to_bmc_components(path)
                affected_components.extend(components)
            affected_components = list(set(affected_components))

        return {
            "affected_components": affected_components,
            "service_boundaries": "no_change" if not files else "potential_change",
            "api_contracts": "no_change",
            "data_models": "no_change",
            "integration_points": {
                "whatsapp": "no_impact" if "whatsapp_integration" not in affected_components else "potential_impact",
                "n8n": "no_impact" if "n8n_workflows" not in affected_components else "potential_impact",
                "qdrant": "no_impact" if "qdrant" not in affected_components else "potential_impact",
                "chatwoot": "no_impact" if "chatwoot" not in affected_components else "potential_impact"
            },
            "consolidation_alignment": "high",
            "architectural_changes_required": len(affected_components) > 0
        }

    def assess_plan_alignment(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Task 2.2: Consolidation Plan Alignment"""
        purpose = analysis.get("task_1.3", {})
        related_phases = purpose.get("related_phases", [])

        # Delegate to OrchestratorAgent
        task_config = {
            "type": "assess_plan_alignment",
            "related_phases": related_phases,
            "consolidation_plan": self.consolidation_plan
        }

        result = self.coordinator.delegate_task("T2.2", task_config)

        if result.get("error") or result.get("fallback"):
            # Fallback: map to phases
            affected_phases = related_phases if related_phases else []

            # Determine if new phase needed
            new_phase_required = False
            if not affected_phases:
                # Check if this is a major new feature
                business_domain = purpose.get("business_domain", "")
                if business_domain in ["deployment_orchestration", "security"]:
                    new_phase_required = False  # Likely fits existing phases

            return {
                "primary_phase": affected_phases[0] if affected_phases else None,
                "affected_phases": affected_phases,
                "phase_updates_required": [
                    {
                        "phase": phase,
                        "update_type": "documentation",
                        "tasks_to_add": []
                    }
                    for phase in affected_phases
                ],
                "new_phase_required": new_phase_required,
                "conflicts": [],
                "dependencies": []
            }

        return result.get("result", {})

    def assess_bmc_domain_impact(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Task 2.3: BMC Domain Impact Assessment"""
        files_analysis = analysis.get("task_1.2", {})
        bmc_components = files_analysis.get("bmc_components", [])

        # Delegate to QuotationAgent
        task_config = {
            "type": "assess_bmc_domain_impact",
            "bmc_components": bmc_components,
            "files": files_analysis.get("files", [])
        }

        result = self.coordinator.delegate_task("T2.3", task_config)

        if result.get("error") or result.get("fallback"):
            # Fallback: assess locally
            quotation_impact = "none"
            if "quotation_engine" in bmc_components:
                quotation_impact = "potential_impact"

            integration_impact = {}
            for component in ["whatsapp", "n8n", "qdrant", "chatwoot"]:
                integration_impact[component] = "none"
                if f"{component}_integration" in bmc_components or component in bmc_components:
                    integration_impact[component] = "potential_impact"

            return {
                "quotation_engine_impact": quotation_impact,
                "integration_impact": integration_impact,
                "business_logic_preserved": True,
                "bmc_testing_required": any(comp in bmc_components for comp in ["quotation_engine", "whatsapp_integration", "n8n_workflows"])
            }

        return result.get("result", {})

    def assess_security_impact(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Task 2.4: Security & Production Readiness Impact"""
        files_analysis = analysis.get("task_1.2", {})
        files = files_analysis.get("files", [])
        categories = files_analysis.get("categories", {})

        # Delegate to SecurityAgent
        task_config = {
            "type": "assess_security_impact",
            "files": files,
            "categories": categories
        }

        result = self.coordinator.delegate_task("T2.4", task_config)

        if result.get("error") or result.get("fallback"):
            # Fallback: basic security assessment
            security_files = categories.get("configuration", []) + categories.get("source_code", [])
            has_security_changes = any(
                "security" in f.get("path", "").lower() or
                "auth" in f.get("path", "").lower() or
                "secret" in f.get("path", "").lower()
                for f in security_files
            )

            return {
                "security_impact": "low" if not has_security_changes else "medium",
                "production_readiness_impact": "documentation_only" if not security_files else "code_changes",
                "security_hardening_required": has_security_changes,
                "phase_9_updates": [] if not has_security_changes else [
                    {
                        "task": "Review security implications",
                        "priority": "P1"
                    }
                ]
            }

        return result.get("result", {})


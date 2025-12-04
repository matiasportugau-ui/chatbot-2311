"""
Planning Agent
Main agent class that analyzes PRs and generates implementation plans
"""

from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add parent directory to path
ORCHESTRATOR_DIR = Path(__file__).parent
sys.path.insert(0, str(ORCHESTRATOR_DIR.parent.parent))

try:
    from scripts.orchestrator.agent_interface import AgentInterface
    from scripts.orchestrator.state_manager import StateManager
    from scripts.orchestrator.context_manager import ContextManager
    from scripts.orchestrator.github_integration import GitHubIntegration
except ImportError:
    AgentInterface = None
    StateManager = None
    ContextManager = None
    GitHubIntegration = None

from scripts.orchestrator.planning.pr_analyzer import PRAnalyzer
from scripts.orchestrator.planning.impact_assessor import ImpactAssessor
from scripts.orchestrator.planning.integration_strategist import IntegrationStrategist
from scripts.orchestrator.planning.plan_generator import PlanGenerator
from scripts.orchestrator.planning.output_generators import OutputGenerators


class PlanningAgent(AgentInterface if AgentInterface else object):
    """Planning Agent - Analyzes PRs and generates implementation plans"""

    def __init__(self, state_manager: Optional[StateManager] = None,
                 context_manager: Optional[ContextManager] = None,
                 github_integration: Optional[GitHubIntegration] = None):
        if AgentInterface:
            super().__init__("PlanningAgent", "PlanningAgent")
        else:
            self.agent_name = "PlanningAgent"
            self.agent_type = "PlanningAgent"
            self.task_dir = Path("consolidation/tasks")
            self.task_dir.mkdir(parents=True, exist_ok=True)

        self.state_manager = state_manager
        self.context_manager = context_manager
        self.github_integration = github_integration

        # Initialize sub-modules
        self.pr_analyzer = PRAnalyzer(github_integration)
        self.impact_assessor = ImpactAssessor()
        self.integration_strategist = IntegrationStrategist()
        self.plan_generator = PlanGenerator()
        self.output_generators = OutputGenerators()

    def execute_task(self, task_id: str, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a planning task (required by AgentInterface)"""
        task_type = task_config.get("type")

        if task_type == "analyze_pr":
            pr_number = task_config.get("pr_number")
            return self.analyze_pr(pr_number)
        elif task_type == "analyze_local_changes":
            return self.analyze_local_changes()
        else:
            return {"error": f"Unknown task type: {task_type}"}

    def analyze_pr(self, pr_number: Optional[int] = None, pr_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main entry point: Analyze PR and generate implementation plan"""
        print(f"PlanningAgent: Starting analysis for PR #{pr_number}")

        # Phase 1: PR/Change Analysis
        print("Phase 1: PR/Change Analysis...")
        analysis = self.pr_analyzer.analyze_pr(pr_number, pr_data)

        if "error" in analysis:
            return analysis

        # Phase 2: Impact Assessment
        print("Phase 2: Impact Assessment...")
        impact = self.impact_assessor.assess_impact(analysis)

        # Phase 3: Integration Strategy
        print("Phase 3: Integration Strategy...")
        strategy = self.integration_strategist.develop_strategy(analysis, impact)

        # Phase 4: Implementation Plan Generation
        print("Phase 4: Implementation Plan Generation...")
        plan = self.plan_generator.generate_plan(analysis, impact, strategy)

        # Generate outputs
        print("Generating outputs...")
        outputs = {}

        if pr_number:
            outputs["analysis_report"] = self.output_generators.generate_analysis_report(
                pr_number, analysis, impact, strategy
            )
            outputs["task_list"] = self.output_generators.generate_task_list(pr_number, plan)
            outputs["integration_checklist"] = self.output_generators.generate_integration_checklist(
                pr_number, strategy
            )

            plan_updates = self.output_generators.generate_plan_updates(pr_number, plan)
            if plan_updates:
                outputs["plan_updates"] = plan_updates

        # Store in context if available
        if self.context_manager:
            self.context_manager.add_phase_context(0, {
                "planning_agent_analysis": {
                    "pr_number": pr_number,
                    "analysis": analysis,
                    "impact": impact,
                    "strategy": strategy,
                    "plan": plan,
                    "outputs": outputs
                }
            })

        return {
            "pr_number": pr_number,
            "analysis": analysis,
            "impact": impact,
            "strategy": strategy,
            "plan": plan,
            "outputs": outputs,
            "status": "completed"
        }

    def analyze_local_changes(self) -> Dict[str, Any]:
        """Analyze local uncommitted changes"""
        # This would analyze git diff or workspace changes
        # For now, return a placeholder
        return {
            "error": "Local changes analysis not yet implemented",
            "suggestion": "Use analyze_pr() with a PR number"
        }


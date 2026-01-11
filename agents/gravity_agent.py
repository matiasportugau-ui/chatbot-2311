#!/usr/bin/env python3
"""
Gravity Agent
=============

Specialized agent for interpreting and orchestrating automated development.
Operates in "Agent Mode" to autonomously manage the development lifecycle.

Capabilities:
- Interprets PRs and code changes (Context Awareness)
- Orchestrates execution of development phases (Orchestration)
- Manages the automated development pipeline (Management)

"""

import sys
import os
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add workspace root to path
WORKSPACE_ROOT = Path("/workspace")
sys.path.insert(0, str(WORKSPACE_ROOT))

# Import orchestrator components
try:
    from scripts.orchestrator.main_orchestrator import MainOrchestrator
    from scripts.orchestrator.planning_agent import PlanningAgent
    from scripts.orchestrator.context_manager import ContextManager
    from scripts.orchestrator.state_manager import StateManager
    from scripts.orchestrator.github_integration import GitHubIntegration
except ImportError as e:
    print(f"Error importing orchestrator components: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gravity_agent.log')
    ]
)
logger = logging.getLogger("GravityAgent")

class GravityAgent:
    """
    Gravity Agent - The central force that holds the development process together.
    Interprets context and orchestrates execution.
    """
    
    def __init__(self, mode: str = "agent_mode"):
        self.mode = mode
        self.logger = logger
        self.state_manager = StateManager()
        self.context_manager = ContextManager(state_manager=self.state_manager)
        self.github_integration = GitHubIntegration()
        self.planning_agent = PlanningAgent(
            context_manager=self.context_manager,
            github_integration=self.github_integration
        )
        self.orchestrator = MainOrchestrator()
        
        self.logger.info(f"Gravity Agent initialized in {self.mode}")

    def interpret_context(self, pr_number: Optional[int] = None) -> Dict[str, Any]:
        """
        Interprets the current development context, optionally focusing on a PR.
        """
        self.logger.info(f"Interpreting context..." + (f" (PR #{pr_number})" if pr_number else ""))
        
        context = {
            "mode": self.mode,
            "pr_context": None,
            "system_state": "unknown"
        }

        if pr_number:
            # Use PlanningAgent to analyze PR
            self.logger.info(f"analyzing PR #{pr_number}...")
            analysis_result = self.planning_agent.analyze_pr(pr_number)
            context["pr_context"] = analysis_result
            
            if "error" in analysis_result:
                self.logger.error(f"Error analyzing PR: {analysis_result['error']}")
            else:
                self.logger.info("PR analysis completed successfully")
                
        return context

    def orchestrate_development(self, context: Dict[str, Any]) -> bool:
        """
        Orchestrates the development process based on the interpreted context.
        """
        self.logger.info("Orchestrating development based on context...")
        
        # Determine strategy based on context
        pr_context = context.get("pr_context")
        
        if pr_context and not pr_context.get("error"):
            # We have a plan from the PR analysis
            plan = pr_context.get("plan", {})
            self.logger.info(f"Found implementation plan with {len(plan.get('tasks', []))} tasks")
            
            # Here we would typically map the plan to orchestrator phases
            # For now, we will trigger the standard orchestration but informed by the context
            pass
            
        # Initialize orchestrator
        if not self.orchestrator.initialize():
            self.logger.error("Failed to initialize orchestrator")
            return False
            
        # Run orchestration
        # In "agent_mode", we run autonomously
        self.logger.info("Starting autonomous execution...")
        
        # Depending on the PR content, we might want to target specific phases
        # For general purpose, we run the full cycle
        success = self.orchestrator.run()
        
        if success:
            self.logger.info("Orchestration completed successfully")
        else:
            self.logger.warning("Orchestration completed with warnings or errors")
            
        return success

    def run(self, pr_number: Optional[int] = None):
        """
        Main entry point for the agent's operation.
        """
        self.logger.info("Gravity Agent starting run cycle")
        
        # 1. Interpret
        context = self.interpret_context(pr_number)
        
        # 2. Orchestrate
        success = self.orchestrate_development(context)
        
        return 0 if success else 1

def main():
    parser = argparse.ArgumentParser(description="Gravity Agent")
    parser.add_argument("--mode", default="agent_mode", help="Operating mode")
    parser.add_argument("--pr", type=int, help="PR number to focus on")
    
    args = parser.parse_args()
    
    agent = GravityAgent(mode=args.mode)
    sys.exit(agent.run(pr_number=args.pr))

if __name__ == "__main__":
    main()

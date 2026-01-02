#!/usr/bin/env python3
"""
CLI Interface for Planning Agent
Run planning agent analysis for PRs or local changes
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
ORCHESTRATOR_DIR = Path(__file__).parent
sys.path.insert(0, str(ORCHESTRATOR_DIR.parent.parent))

from scripts.orchestrator.planning_agent import PlanningAgent
from scripts.orchestrator.state_manager import StateManager
from scripts.orchestrator.context_manager import ContextManager
from scripts.orchestrator.github_integration import GitHubIntegration


def main():
    parser = argparse.ArgumentParser(description="Planning Agent - Analyze PRs and generate implementation plans")
    parser.add_argument("--pr", type=int, help="PR number to analyze")
    parser.add_argument("--local-changes", action="store_true", help="Analyze local uncommitted changes")
    parser.add_argument("--config", type=str, default="scripts/orchestrator/config/orchestrator_config.json",
                       help="Path to orchestrator config file")

    args = parser.parse_args()

    if not args.pr and not args.local_changes:
        parser.print_help()
        sys.exit(1)

    # Initialize components
    state_manager = StateManager()
    context_manager = ContextManager(state_manager)

    # Load config for GitHub integration
    import json
    config = {}
    config_file = Path(args.config)
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)

    github_token = config.get("github", {}).get("token")
    github_repo = config.get("github", {}).get("repo", "chatbot-2311")
    github_owner = config.get("github", {}).get("owner")
    github_integration = GitHubIntegration(github_token, github_repo, github_owner)

    # Initialize Planning Agent
    planning_agent = PlanningAgent(state_manager, context_manager, github_integration)

    # Run analysis
    if args.pr:
        print(f"Analyzing PR #{args.pr}...")
        result = planning_agent.analyze_pr(args.pr)
    elif args.local_changes:
        print("Analyzing local changes...")
        result = planning_agent.analyze_local_changes()

    # Print results
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)

    print("\n✅ Analysis complete!")
    if "outputs" in result:
        print("\nGenerated outputs:")
        for output_type, output_path in result["outputs"].items():
            print(f"  - {output_type}: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())


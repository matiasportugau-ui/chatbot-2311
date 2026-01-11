#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import sys
from pathlib import Path

# Ensure project root is on sys.path when executed as a script
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from AI_AGENTS.GRAVITY.gravity_orchestrator_agent import GravityOrchestratorAgent  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gravity Orchestrator Agent - interpreta PRs y genera runbooks de ejecución automatizada"
    )
    parser.add_argument("--pr", type=int, required=True, help="PR number (GitHub)")
    parser.add_argument(
        "--repo",
        type=str,
        default="matiasportugau-ui/chatbot-2311",
        help="GitHub repo (owner/name)",
    )
    parser.add_argument(
        "--print",
        dest="print_json",
        action="store_true",
        help="Imprime el runbook por stdout (JSON)",
    )

    args = parser.parse_args()

    agent = GravityOrchestratorAgent(repo=args.repo)
    analysis = agent.analyze_pr(args.pr)
    runbook = agent.build_runbook(args.pr, analysis)
    analysis_path, runbook_path = agent.export(args.pr, analysis, runbook)

    if args.print_json:
        print(json.dumps(runbook.to_dict(), indent=2, ensure_ascii=False))

    print("✅ Gravity agent generado")
    print(f"- Analysis: {analysis_path}")
    print(f"- Runbook:  {runbook_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

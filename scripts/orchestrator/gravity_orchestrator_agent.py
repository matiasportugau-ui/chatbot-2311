"""
Gravity Orchestrator Agent (Agent Mode)

Purpose
-------
Specialist agent to *interpret* high-level product/development intents and *orchestrate*
automated development for this repository using the existing orchestrator framework.

Notes
-----
- "Gravity" here is implemented as a Grok/xAI-first agent (provider="grok") when available,
  but it degrades gracefully to deterministic orchestration when API keys are not present.
- This agent is designed for *development orchestration* (plans, phase routing, handoffs),
  not for runtime chatbot message handling.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, List


@dataclass(frozen=True)
class GravityAgentInputs:
    """Normalized input payload for the Gravity orchestrator."""
    goal: str
    pr_number: Optional[int] = None
    repo: Optional[str] = None  # e.g. "owner/name"
    constraints: Optional[Dict[str, Any]] = None


class GravityOrchestratorAgentImpl:
    """
    Implementation class (kept separate to allow lazy-loading wrappers elsewhere).
    """

    DEFAULT_SYSTEM_PROMPT = """You are Gravity, the lead orchestrator for automated development in the repository 'chatbot-2311'.

Your job is to interpret the user's intent and produce an execution-ready plan that fits this repo's automation tools:
- scripts/orchestrator/* (phases 0-15, approvals, handoffs)
- scripts/run_agent_team.py (agent team execution)
- scripts/orchestrator/run_planning_agent.py (PR analysis & plan generation)

Output must be STRICT JSON with keys:
  summary: string
  assumptions: string[]
  plan: {steps: [{title: string, details: string, commands: string[]}], risks: string[]}
  delegation: {agents: [{agent: string, tasks: string[]}]}
  artifacts: {files: string[], outputs: string[]}

Keep it repo-specific, actionable, and avoid speculative files. If you can't access credentials, propose fallbacks.
"""

    def __init__(
        self,
        prefer_provider: str = "grok",
        model_id: Optional[str] = None,
        strategy: str = "balanced",
    ) -> None:
        self.prefer_provider = prefer_provider
        self.model_id = model_id
        self.strategy = strategy

    # -----------------------------
    # Public entrypoints
    # -----------------------------
    def orchestrate(self, inputs: GravityAgentInputs) -> Dict[str, Any]:
        """
        Orchestrate a development objective.

        If inputs.pr_number is provided, the agent will fetch PR metadata (optionally from inputs.repo)
        and generate an integration plan using the existing PlanningAgent.
        """
        pr_data: Optional[Dict[str, Any]] = None
        planning_outputs: Optional[Dict[str, Any]] = None

        if inputs.pr_number is not None:
            pr_data = self._fetch_pr(inputs.pr_number, repo=inputs.repo)
            planning_outputs = self._run_planning_agent(pr_number=inputs.pr_number, pr_data=pr_data)

        deterministic_plan = self._build_deterministic_plan(inputs, planning_outputs=planning_outputs)

        # If LLM is available, ask it to refine the plan into a strict JSON schema
        llm_plan = self._maybe_llm_refine(inputs, deterministic_plan, planning_outputs)
        return llm_plan or deterministic_plan

    # -----------------------------
    # Planning agent integration
    # -----------------------------
    def _run_planning_agent(self, pr_number: int, pr_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            from scripts.orchestrator.planning_agent import PlanningAgent
        except Exception as e:
            return {"error": f"PlanningAgent import failed: {e}"}

        agent = PlanningAgent()
        # Provide pr_data to avoid dependency on gh defaults.
        return agent.analyze_pr(pr_number=pr_number, pr_data=pr_data)

    # -----------------------------
    # PR fetching
    # -----------------------------
    def _fetch_pr(self, pr_number: int, repo: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Fetch PR data via GitHub CLI.

        Uses --repo when provided to avoid relying on current git remote config.
        """
        cmd = [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--json",
            "number,title,body,author,state,baseRefName,headRefName,createdAt,updatedAt,mergedAt,labels,files,commits",
        ]
        if repo:
            cmd.extend(["--repo", repo])

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if proc.returncode != 0:
                return None
            return json.loads(proc.stdout)
        except Exception:
            return None

    # -----------------------------
    # Deterministic orchestration plan
    # -----------------------------
    def _build_deterministic_plan(
        self,
        inputs: GravityAgentInputs,
        planning_outputs: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        constraints = inputs.constraints or {}

        files: List[str] = []
        if planning_outputs and isinstance(planning_outputs, dict):
            # Try to extract changed files from planning analysis
            analysis = planning_outputs.get("analysis") or {}
            files_analysis = analysis.get("task_1.2") if isinstance(analysis, dict) else None
            if isinstance(files_analysis, dict):
                files = [f.get("path") for f in files_analysis.get("files", []) if isinstance(f, dict) and f.get("path")]

        commands: List[str] = []
        if inputs.pr_number is not None:
            repo_flag = f" --repo {inputs.repo}" if inputs.repo else ""
            commands.append(f"gh pr view {inputs.pr_number}{repo_flag} --json title,body,files,commits")
            commands.append(f"python3 scripts/orchestrator/run_planning_agent.py --pr {inputs.pr_number}")

        # Repo-native automated execution entrypoints (safe defaults)
        commands.extend(
            [
                "python3 scripts/run_agent_team.py --mode dry-run --info",
                "python3 scripts/run_agent_team.py --mode dry-run --status",
                # NOTE: full automated run can be long; keep as an optional command in plan.
            ]
        )

        # Build plan skeleton
        plan_steps = [
            {
                "title": "Interpret goal & scope",
                "details": inputs.goal,
                "commands": [],
            },
            {
                "title": "Analyze PR / change impact (if applicable)",
                "details": "Generate an integration plan using the built-in PlanningAgent and identify touched components.",
                "commands": commands[:2] if inputs.pr_number is not None else [],
            },
            {
                "title": "Map work to orchestrator phases & delegate",
                "details": "Select phases 0-15 to run/verify, prepare handoffs if needed, and coordinate specialized agents.",
                "commands": [
                    "python3 scripts/run_agent_team.py --info",
                    "python3 scripts/run_agent_team.py --status",
                ],
            },
            {
                "title": "Execute automation (optional)",
                "details": "Run automated phases only after validation/dry-run is clean.",
                "commands": [
                    "python3 scripts/run_agent_team.py --mode dry-run",
                    "python3 scripts/run_agent_team.py --mode automated --resume",
                ],
            },
        ]

        risks = [
            "Missing credentials (GitHub token, API keys) can limit automation; use gh-authenticated CLI fallbacks.",
            "Long-running automated execution may require resume; rely on state in consolidation/execution_state.json.",
        ]
        if constraints.get("no_long_runs") is True:
            risks.append("Constraint no_long_runs=true: avoid full automated runs; use dry-run and targeted scripts.")

        delegation = {
            "agents": [
                {"agent": "GravityOrchestratorAgent", "tasks": ["Interpret request", "Sequence phases", "Track risks"]},
                {"agent": "PlanningAgent", "tasks": ["Analyze PR", "Generate integration checklist/task list"]},
                {"agent": "RepositoryAgent", "tasks": ["Identify impacted modules", "Confirm file structure changes"]},
                {"agent": "IntegrationAgent", "tasks": ["Validate integrations touched by changes (n8n/WhatsApp/etc.)"]},
            ]
        }

        outputs = []
        if planning_outputs and isinstance(planning_outputs, dict):
            out_paths = (planning_outputs.get("outputs") or {}).values() if isinstance(planning_outputs.get("outputs"), dict) else []
            outputs = [str(p) for p in out_paths]

        return {
            "summary": "Gravity orchestrated an execution-ready development plan.",
            "assumptions": [
                "This repo uses scripts/orchestrator as the primary automation backbone.",
                "The environment may not have all API keys; the plan must remain executable with fallbacks.",
            ],
            "plan": {
                "steps": plan_steps,
                "risks": risks,
            },
            "delegation": delegation,
            "artifacts": {
                "files": files,
                "outputs": outputs,
            },
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "pr_number": inputs.pr_number,
                "repo": inputs.repo,
                "constraints": constraints,
            },
        }

    # -----------------------------
    # Optional LLM refinement
    # -----------------------------
    def _maybe_llm_refine(
        self,
        inputs: GravityAgentInputs,
        deterministic_plan: Dict[str, Any],
        planning_outputs: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        If the multi-provider integrator is configured, ask the preferred provider (default: grok)
        to reformat/refine the deterministic plan into the strict JSON schema required.
        """
        try:
            from cursor_agent_wrapper import get_cursor_agent
        except Exception:
            return None

        # Basic availability check: if no keys are set, don't attempt.
        # model_integrator treats GROK_API_KEY or XAI_API_KEY as required for provider="grok".
        has_grok_key = bool(os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY"))
        has_any_key = has_grok_key or bool(os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY"))
        if not has_any_key:
            return None

        agent = get_cursor_agent(strategy=self.strategy, provider=self.prefer_provider)

        context_blob = {
            "goal": inputs.goal,
            "pr_number": inputs.pr_number,
            "repo": inputs.repo,
            "planning_outputs": planning_outputs,
            "deterministic_plan": deterministic_plan,
        }

        messages = [
            {"role": "system", "content": self.DEFAULT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Refine the plan for this request. Return ONLY the strict JSON object.\n\n"
                    + json.dumps(context_blob, ensure_ascii=False)
                ),
            },
        ]

        try:
            resp = agent.chat(messages, model=self.model_id, temperature=0.2, max_tokens=2000)
            content = resp.get("content") or ""
            # Must be JSON
            refined = json.loads(content)
            if isinstance(refined, dict):
                return refined
        except Exception:
            return None

        return None


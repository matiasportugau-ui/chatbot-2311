"""
OrchestratorAgent
Specialist agent that interprets requirements and orchestrates automated development
for this repository's unified execution/orchestrator system.

This agent is intentionally deterministic (no external LLM dependency required) so it
can run inside CI and local environments without API keys.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime

from .agent_interface import AgentInterface


@dataclass(frozen=True)
class _Duration:
    hours: float

    @staticmethod
    def parse(value: str) -> "_Duration":
        """
        Parse a simple duration string. Supported examples:
        - "2 hours", "1.5 hours"
        - "30 minutes"
        - "45 min"
        """
        s = (value or "").strip().lower()
        if not s:
            return _Duration(0.0)

        def _as_float(token: str) -> Optional[float]:
            try:
                return float(token)
            except Exception:
                return None

        parts = s.split()
        if not parts:
            return _Duration(0.0)

        qty = _as_float(parts[0])
        if qty is None:
            return _Duration(0.0)

        unit = parts[1] if len(parts) > 1 else "hours"
        if unit.startswith("hour"):
            return _Duration(qty)
        if unit.startswith("min"):
            return _Duration(qty / 60.0)
        return _Duration(0.0)

    def format_hours(self) -> str:
        if self.hours == int(self.hours):
            return f"{int(self.hours)} hours"
        return f"{self.hours:.1f} hours"


class OrchestratorAgent(AgentInterface):
    """
    OrchestratorAgent - interprets change context and produces orchestration artifacts.

    Primary consumers:
    - PlanningAgent modules (T2.2, T4.1-4.4) via PlanningAgentCoordinator
    - Higher-level "agent mode" workflows that need structured plans.
    """

    def __init__(self):
        super().__init__("OrchestratorAgent", "OrchestratorAgent")

    def execute_task(self, task_id: str, task_config: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task_config.get("type")

        # Task 2.2 naming (ImpactAssessor) vs older/internal naming.
        if task_type in {"assess_plan_alignment", "align_consolidation_plan"}:
            return self._assess_plan_alignment(task_config)

        if task_type == "create_task_breakdown":
            return self._create_task_breakdown(task_config)

        if task_type == "integrate_phases":
            return self._integrate_phases(task_config)

        if task_type == "estimate_timeline":
            return self._estimate_timeline(task_config)

        if task_type == "assess_risks":
            return self._assess_risks(task_config)

        if task_type == "interpret_and_orchestrate":
            return self._interpret_and_orchestrate(task_config)

        return {"error": f"Unknown task type: {task_type}"}

    # --- Planning: Task 2.2 -------------------------------------------------

    def _assess_plan_alignment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task 2.2: Consolidation Plan Alignment

        Input (from ImpactAssessor):
        - related_phases: list[int]
        - consolidation_plan: optional dict (not required for deterministic alignment)

        Output shape matches ImpactAssessor fallback:
        - primary_phase, affected_phases, phase_updates_required, new_phase_required, conflicts, dependencies
        """
        related_phases = config.get("related_phases", []) or []
        affected_phases = sorted(set(int(p) for p in related_phases)) if related_phases else [0]
        primary_phase = affected_phases[0] if affected_phases else None

        return {
            "primary_phase": primary_phase,
            "affected_phases": affected_phases,
            "phase_updates_required": [
                {
                    "phase": phase,
                    "update_type": "documentation",
                    "tasks_to_add": [],
                }
                for phase in affected_phases
            ],
            "new_phase_required": False,
            "conflicts": [],
            "dependencies": [],
            "timestamp": datetime.now().isoformat(),
        }

    # --- Planning: Task 4.1 -------------------------------------------------

    def _create_task_breakdown(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        analysis = config.get("analysis", {}) or {}
        strategy = config.get("strategy", {}) or {}

        files_analysis = analysis.get("task_1.2", {}) or {}
        categories = (files_analysis.get("categories") or {}) if isinstance(files_analysis, dict) else {}

        tasks: List[Dict[str, Any]] = []

        # Documentation integration tasks (common case for PRs like #87).
        doc_updates = (strategy.get("task_3.3", {}) or {}).get("new_documentation", [])
        doc_files = categories.get("documentation", []) if isinstance(categories, dict) else []

        doc_file_paths: List[str] = []
        for item in doc_updates:
            if isinstance(item, dict) and item.get("file"):
                doc_file_paths.append(item["file"])
        for f in doc_files:
            # doc_files may be list[str] or list[dict]
            if isinstance(f, str):
                doc_file_paths.append(f)
            elif isinstance(f, dict) and f.get("path"):
                doc_file_paths.append(f["path"])

        doc_file_paths = sorted(set(doc_file_paths))
        if doc_file_paths:
            tasks.append(
                {
                    "task_id": "T0.8",
                    "task_name": "Integrate new documentation into unified plan",
                    "script": "scripts/orchestrator/planning/output_generators.py",
                    "action": "Review new/updated docs and align with orchestrator phases and runbooks",
                    "files": doc_file_paths,
                    "dependencies": [],
                    "output": "consolidation/planning/documentation_integration.json",
                    "priority": "P1",
                    "agent": "OrchestratorAgent",
                    "estimated_duration": "1.5 hours",
                    "bmc_context": "Keep operational docs consistent with BMC quotation + WhatsApp + n8n flows",
                }
            )

        # Training / evaluation system integration (PR #87 context).
        if self._looks_like_training_system_change(analysis):
            tasks.extend(
                [
                    {
                        "task_id": "T5.7",
                        "task_name": "Run training system unit tests",
                        "script": "python3 -m pytest -q test_training_system.py",
                        "action": "Validate training/evaluation workflow and benchmark scoring",
                        "files": ["test_training_system.py"],
                        "dependencies": ["T0.8"] if doc_file_paths else [],
                        "output": "consolidation/tests/training_system_test_results.json",
                        "priority": "P1",
                        "agent": "ValidationAgent",
                        "estimated_duration": "0.5 hours",
                        "bmc_context": "Ensure training mode doesn't regress production response quality",
                    },
                    {
                        "task_id": "T6.4",
                        "task_name": "Add operator quick-start commands to runbooks",
                        "script": "QUICK_REFERENCE_TRAINING.md",
                        "action": "Confirm operator commands match CLI behavior and update if needed",
                        "files": [
                            "QUICK_REFERENCE_TRAINING.md",
                            "TRAINING_SYSTEM_GUIDE.md",
                        ],
                        "dependencies": ["T0.8"] if doc_file_paths else [],
                        "output": "consolidation/docs/training_quickstart_review.json",
                        "priority": "P2",
                        "agent": "OrchestratorAgent",
                        "estimated_duration": "0.5 hours",
                        "bmc_context": "Make training commands safe for agents and supervisors",
                    },
                ]
            )

        return tasks

    # --- Planning: Task 4.2 -------------------------------------------------

    def _integrate_phases(self, config: Dict[str, Any]) -> Dict[str, Any]:
        tasks = config.get("tasks", []) or []
        impact = config.get("impact", {}) or {}
        plan_alignment = impact.get("task_2.2", {}) or {}
        affected_phases = plan_alignment.get("affected_phases", []) if isinstance(plan_alignment, dict) else []
        if not affected_phases:
            affected_phases = [0]

        tasks_by_phase: Dict[str, List[Dict[str, Any]]] = {str(p): [] for p in sorted(set(affected_phases))}

        for task in tasks:
            task_id = (task or {}).get("task_id", "")
            phase = self._infer_phase_from_task_id(task_id)
            if phase is None:
                # Put "unclassified" tasks into the first affected phase
                tasks_by_phase[str(affected_phases[0])].append(task)
            else:
                tasks_by_phase.setdefault(str(phase), []).append(task)

        return {
            "tasks_by_phase": tasks_by_phase,
            "phase_executor_updates": [],
            "new_phase_required": False,
            "orchestrator_config_updates": [],
        }

    # --- Planning: Task 4.3 -------------------------------------------------

    def _estimate_timeline(self, config: Dict[str, Any]) -> Dict[str, Any]:
        tasks = config.get("tasks", []) or []
        durations = [_Duration.parse((t or {}).get("estimated_duration", "")) for t in tasks]
        total = _Duration(sum(d.hours for d in durations))

        critical_path = [t.get("task_id") for t in tasks if isinstance(t, dict) and t.get("task_id")]

        return {
            "total_estimated_duration": total.format_hours(),
            "critical_path": critical_path,
            "parallel_opportunities": [],
            "milestones": [
                {
                    "milestone": "Planning artifacts generated",
                    "tasks": critical_path,
                    "estimated_completion": total.format_hours(),
                }
            ],
            "dependencies_resolved": True,
            "buffer_time": "30 minutes",
        }

    # --- Planning: Task 4.4 -------------------------------------------------

    def _assess_risks(self, config: Dict[str, Any]) -> Dict[str, Any]:
        analysis = config.get("analysis", {}) or {}
        files_analysis = analysis.get("task_1.2", {}) or {}
        categories = (files_analysis.get("categories") or {}) if isinstance(files_analysis, dict) else {}

        risks: List[Dict[str, Any]] = []

        if isinstance(categories, dict) and categories.get("documentation"):
            risks.append(
                {
                    "risk": "Documentation may diverge from actual runtime behavior",
                    "probability": "medium",
                    "impact": "medium",
                    "mitigation": "Validate docs against current entrypoints and CLI scripts; update quick-start commands.",
                    "owner": "OrchestratorAgent",
                }
            )

        if self._looks_like_training_system_change(analysis):
            risks.append(
                {
                    "risk": "Training-mode features could leak into production responses or persistence",
                    "probability": "low",
                    "impact": "high",
                    "mitigation": "Ensure mode gating; run unit tests; verify persistence paths under data/training/.",
                    "owner": "ValidationAgent",
                }
            )

        return {
            "risks": risks,
            "blockers": [],
            "assumptions": [
                "Orchestrator phases and success criteria remain the source of truth for automation.",
                "Agent mode should be able to operate without external API keys.",
            ],
            "constraints": [
                "Must remain compatible with scripts/orchestrator execution model.",
            ],
            "rollback_procedures": [
                "Revert plan/doc updates if they conflict with current orchestrator behavior.",
            ],
        }

    # --- “Gravity agent mode” helper ---------------------------------------

    def _interpret_and_orchestrate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        High-level helper intended for agent-mode usage.
        Produces an actionable plan for the repo's automation entrypoints.

        Input:
        - goal: str (user goal)
        - pr_number: int | None
        - recommended_entrypoint: optional override
        """
        goal = (config.get("goal") or "").strip()
        pr_number = config.get("pr_number")

        entrypoints = [
            {
                "name": "planning_agent",
                "command": "python3 scripts/orchestrator/run_planning_agent.py --pr <N>",
                "when": "When you need a structured plan for a PR",
            },
            {
                "name": "automated_execution",
                "command": "python3 scripts/orchestrator/run_automated_execution.py",
                "when": "When you want to execute phases end-to-end",
            },
            {
                "name": "agent_team_runner",
                "command": "python3 scripts/run_agent_team.py --mode automated",
                "when": "When you want the 12-agent phase mapping output + orchestrator run",
            },
        ]

        plan: List[Dict[str, Any]] = []
        if pr_number is not None:
            plan.append(
                {
                    "step": "analyze_pr",
                    "command": f"python3 scripts/orchestrator/run_planning_agent.py --pr {int(pr_number)}",
                    "output": "consolidation/planning/",
                }
            )
        if goal:
            plan.append(
                {
                    "step": "map_goal_to_phases",
                    "goal": goal,
                    "hint": "Use PlanningAgent outputs + affected phases to decide what to run next.",
                }
            )
        plan.append(
            {
                "step": "execute_if_ready",
                "command": "python3 scripts/orchestrator/run_automated_execution.py",
                "note": "Runs phases with auto-approval; check consolidation/ for artifacts.",
            }
        )

        return {
            "goal": goal,
            "pr_number": pr_number,
            "recommended_entrypoints": entrypoints,
            "recommended_plan": plan,
            "timestamp": datetime.now().isoformat(),
        }

    # --- Helpers -------------------------------------------------------------

    def _infer_phase_from_task_id(self, task_id: str) -> Optional[int]:
        if not task_id or not task_id.startswith("T"):
            return None
        # Expected formats: "T4.1", "T0.8", etc.
        try:
            head = task_id[1:].split(".", 1)[0]
            return int(head)
        except Exception:
            return None

    def _looks_like_training_system_change(self, analysis: Dict[str, Any]) -> bool:
        files_analysis = analysis.get("task_1.2", {}) or {}
        files = files_analysis.get("files", []) if isinstance(files_analysis, dict) else []
        file_paths: List[str] = []
        for f in files:
            if isinstance(f, dict) and f.get("path"):
                file_paths.append(f["path"])
            elif isinstance(f, str):
                file_paths.append(f)
        joined = " ".join(file_paths).lower()
        return any(
            token in joined
            for token in [
                "training_",
                "benchmark_",
                "test_training_system.py",
                "quick_reference_training",
            ]
        )


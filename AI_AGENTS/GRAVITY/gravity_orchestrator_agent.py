#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gravity Orchestrator Agent

Agente especialista en:
- Interpretar cambios (PRs) y extraer intención/impacto
- Orquestar ejecución automatizada del proyecto (orchestrator, agent team runner)
- Generar runbooks reproducibles (comandos + artefactos esperados)

Diseñado para funcionar en modo automatizado (auto-aprobación) y sin requerir
configuración adicional: usa `gh` CLI si el GitHubIntegration no está disponible.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


@dataclass
class GravityRunbook:
    """Runbook ejecutable y auditable."""

    pr_number: int
    created_at: str
    summary: str
    recommended_commands: list[str]
    artifacts: list[str]
    notes: list[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pr_number": self.pr_number,
            "created_at": self.created_at,
            "summary": self.summary,
            "recommended_commands": self.recommended_commands,
            "artifacts": self.artifacts,
            "notes": self.notes,
        }


class GravityOrchestratorAgent:
    """Agente Gravity para orquestación automatizada del repo."""

    def __init__(self, repo: str = "matiasportugau-ui/chatbot-2311"):
        self.repo = repo
        self.output_dir = Path("consolidation/gravity")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def fetch_pr(self, pr_number: int) -> Dict[str, Any]:
        """Obtiene JSON de PR vía gh CLI (ya autenticado en el entorno)."""
        cmd = [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--repo",
            self.repo,
            "--json",
            "number,title,body,author,state,baseRefName,headRefName,createdAt,updatedAt,mergedAt,labels,files,commits,url",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Failed to fetch PR via gh")
        return json.loads(result.stdout)

    def analyze_pr(self, pr_number: int) -> Dict[str, Any]:
        """Ejecuta PlanningAgent si está disponible; sino retorna un fallback básico."""
        pr_data = self.fetch_pr(pr_number)

        try:
            from scripts.orchestrator.planning_agent import PlanningAgent

            agent = PlanningAgent()
            return agent.analyze_pr(pr_number=pr_number, pr_data=pr_data)
        except Exception as e:
            # Fallback mínimo (no rompe el flujo)
            return {
                "pr_number": pr_number,
                "status": "fallback",
                "error": str(e),
                "metadata": {
                    "title": pr_data.get("title"),
                    "state": pr_data.get("state"),
                    "base": pr_data.get("baseRefName"),
                    "head": pr_data.get("headRefName"),
                    "url": pr_data.get("url"),
                },
                "files": pr_data.get("files", []),
            }

    def build_runbook(self, pr_number: int, analysis: Dict[str, Any]) -> GravityRunbook:
        """Construye un runbook de ejecución automática para implementar/validar cambios."""

        # Heurística: si hay tests nuevos o cambios de código, recomendar correr tests.
        files = []
        try:
            files = (analysis.get("analysis", {}) or {}).get("task_1.2", {}).get("files", [])  # type: ignore[assignment]
        except Exception:
            files = []

        has_py = any((f.get("path", "").endswith(".py") for f in files if isinstance(f, dict)))
        has_tests = any(("test" in f.get("path", "").lower() for f in files if isinstance(f, dict)))

        commands: list[str] = []
        artifacts: list[str] = []
        notes: list[str] = []

        commands.append("python3 scripts/orchestrator/verify_implementation.py")
        artifacts.append("consolidation/reports/")

        if has_py or has_tests:
            commands.append("python3 -m pytest -q")
            notes.append("Si el entorno no tiene deps, instalar según requirements del módulo correspondiente.")

        # Siempre sugerir planning (sirve para orquestar trabajo automatizado)
        commands.append(f"python3 scripts/orchestrator/run_planning_agent.py --pr {pr_number}")
        artifacts.append("consolidation/pr_analysis/")

        # Si el cambio es grande, sugerir run del orchestrator (en automated)
        commands.append("python3 scripts/orchestrator/run_automated_execution.py --mode automated")
        artifacts.append("consolidation/execution_state.json")

        summary = "Orquestación automatizada basada en análisis de PR y plan unificado."

        return GravityRunbook(
            pr_number=pr_number,
            created_at=datetime.utcnow().isoformat() + "Z",
            summary=summary,
            recommended_commands=commands,
            artifacts=sorted(set(artifacts)),
            notes=notes,
        )

    def export(self, pr_number: int, analysis: Dict[str, Any], runbook: GravityRunbook) -> Tuple[str, str]:
        """Guarda análisis y runbook en consolidation/gravity."""
        analysis_path = self.output_dir / f"pr_{pr_number}_analysis.json"
        runbook_path = self.output_dir / f"pr_{pr_number}_runbook.json"

        with open(analysis_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)

        with open(runbook_path, "w", encoding="utf-8") as f:
            json.dump(runbook.to_dict(), f, indent=2, ensure_ascii=False)

        return str(analysis_path), str(runbook_path)

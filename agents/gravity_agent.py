#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gravity Agent - Development Orchestration Specialist
===================================================

Un agente especializado en interpretar y orquestar el desarrollo automatizado
del proyecto. Actúa como el "centro de gravedad" que coordina todos los
componentes del sistema de desarrollo automatizado.

Capacidades:
- Interpretación de PRs, cambios locales y requerimientos
- Orquestación automática del desarrollo
- Coordinación de múltiples agentes especializados
- Gestión del flujo completo de ejecución
- Análisis de contexto y toma de decisiones inteligentes
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

# Add project paths
_current_dir = Path(__file__).parent
_project_root = _current_dir.parent
sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_project_root / "scripts"))

# Import agent interfaces
try:
    from scripts.orchestrator.agent_interface import (
        AgentInterface,
        AgentCoordinator,
        PlanningAgent,
        RepositoryAgent,
        IntegrationAgent,
        QuotationAgent
    )
    AGENT_INTERFACE_AVAILABLE = True
except ImportError:
    AGENT_INTERFACE_AVAILABLE = False
    AgentInterface = object
    AgentCoordinator = None

# Import orchestrator components
try:
    from scripts.orchestrator.main_orchestrator import MainOrchestrator
    from scripts.orchestrator.state_manager import StateManager
    from scripts.orchestrator.context_manager import ContextManager
    from scripts.orchestrator.github_integration import GitHubIntegration
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    MainOrchestrator = None
    StateManager = None
    ContextManager = None
    GitHubIntegration = None

# Import planning components
try:
    from scripts.orchestrator.planning_agent import PlanningAgent as PlanningAgentImpl
    from scripts.orchestrator.planning.pr_analyzer import PRAnalyzer
    from scripts.orchestrator.planning.impact_assessor import ImpactAssessor
    from scripts.orchestrator.planning.integration_strategist import IntegrationStrategist
    from scripts.orchestrator.planning.plan_generator import PlanGenerator
    PLANNING_AVAILABLE = True
except ImportError:
    PLANNING_AVAILABLE = False
    PlanningAgentImpl = None


class ExecutionMode(Enum):
    """Modos de ejecución del agente"""
    AUTOMATED = "automated"
    INTERACTIVE = "interactive"
    DRY_RUN = "dry_run"
    ANALYSIS_ONLY = "analysis_only"


class TaskPriority(Enum):
    """Prioridades de tareas"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class InterpretationResult:
    """Resultado de la interpretación de un requerimiento"""
    intent: str
    context: Dict[str, Any]
    affected_components: List[str]
    required_agents: List[str]
    estimated_complexity: str
    confidence: float
    recommendations: List[str]


@dataclass
class OrchestrationPlan:
    """Plan de orquestación generado"""
    plan_id: str
    phases: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]]
    estimated_duration: int
    risk_assessment: Dict[str, Any]
    execution_strategy: str


class GravityAgent(AgentInterface if AGENT_INTERFACE_AVAILABLE else object):
    """
    Gravity Agent - Especialista en interpretación y orquestación
    
    Este agente actúa como el centro de coordinación para:
    1. Interpretar PRs, cambios y requerimientos
    2. Generar planes de ejecución automatizada
    3. Orquestar la ejecución coordinando múltiples agentes
    4. Monitorear y ajustar el flujo de desarrollo
    """

    def __init__(
        self,
        state_manager: Optional[StateManager] = None,
        context_manager: Optional[ContextManager] = None,
        github_integration: Optional[GitHubIntegration] = None,
        execution_mode: ExecutionMode = ExecutionMode.AUTOMATED
    ):
        if AGENT_INTERFACE_AVAILABLE:
            super().__init__("GravityAgent", "GravityAgent")
        else:
            self.agent_name = "GravityAgent"
            self.agent_type = "GravityAgent"
            self.task_dir = Path("consolidation/tasks")
            self.task_dir.mkdir(parents=True, exist_ok=True)

        # Core components
        self.state_manager = state_manager or (StateManager() if ORCHESTRATOR_AVAILABLE else None)
        self.context_manager = context_manager or (ContextManager() if ORCHESTRATOR_AVAILABLE else None)
        self.github_integration = github_integration
        self.execution_mode = execution_mode

        # Agent coordinator
        self.agent_coordinator = AgentCoordinator() if AgentCoordinator else None

        # Planning components
        if PLANNING_AVAILABLE:
            self.pr_analyzer = PRAnalyzer(github_integration)
            self.impact_assessor = ImpactAssessor()
            self.integration_strategist = IntegrationStrategist()
            self.plan_generator = PlanGenerator()
        else:
            self.pr_analyzer = None
            self.impact_assessor = None
            self.integration_strategist = None
            self.plan_generator = None

        # Orchestrator
        self.orchestrator = MainOrchestrator() if MainOrchestrator else None

        # Output directory
        self.output_dir = Path("consolidation/gravity_agent")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def execute_task(self, task_id: str, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task (required by AgentInterface)"""
        task_type = task_config.get("type")

        if task_type == "interpret_and_orchestrate":
            return self.interpret_and_orchestrate(
                task_config.get("pr_number"),
                task_config.get("pr_data"),
                task_config.get("local_changes", False)
            )
        elif task_type == "interpret_pr":
            return self.interpret_pr(
                task_config.get("pr_number"),
                task_config.get("pr_data")
            )
        elif task_type == "orchestrate_execution":
            return self.orchestrate_execution(
                task_config.get("plan"),
                task_config.get("start_phase"),
                task_config.get("end_phase")
            )
        elif task_type == "analyze_context":
            return self.analyze_context(task_config.get("context"))
        else:
            return {"error": f"Unknown task type: {task_type}"}

    def interpret_and_orchestrate(
        self,
        pr_number: Optional[int] = None,
        pr_data: Optional[Dict[str, Any]] = None,
        local_changes: bool = False
    ) -> Dict[str, Any]:
        """
        Método principal: Interpreta un requerimiento y orquesta su ejecución
        
        Args:
            pr_number: Número del PR a analizar
            pr_data: Datos del PR (opcional, si no se proporciona se obtiene de GitHub)
            local_changes: Si es True, analiza cambios locales en lugar de PR
        
        Returns:
            Dict con el resultado completo de interpretación y orquestación
        """
        print("=" * 80)
        print("🌌 GRAVITY AGENT - INTERPRETACIÓN Y ORQUESTACIÓN")
        print("=" * 80)
        print(f"\n📋 Modo: {self.execution_mode.value}")
        print(f"🔍 Analizando: {'Cambios locales' if local_changes else f'PR #{pr_number}'}\n")

        # Paso 1: Interpretación
        interpretation = self.interpret_pr(pr_number, pr_data) if not local_changes else self.interpret_local_changes()
        
        if "error" in interpretation:
            return interpretation

        # Paso 2: Generación de plan de orquestación
        orchestration_plan = self.generate_orchestration_plan(interpretation)
        
        # Paso 3: Ejecución orquestada (si está habilitada)
        execution_result = None
        if self.execution_mode in [ExecutionMode.AUTOMATED, ExecutionMode.INTERACTIVE]:
            execution_result = self.orchestrate_execution(
                orchestration_plan,
                start_phase=orchestration_plan.get("start_phase", -8),
                end_phase=orchestration_plan.get("end_phase", 15)
            )
        elif self.execution_mode == ExecutionMode.DRY_RUN:
            execution_result = {
                "status": "dry_run",
                "message": "Plan generado pero no ejecutado (modo dry-run)",
                "plan": orchestration_plan
            }

        # Guardar resultados
        result = {
            "interpretation": interpretation,
            "orchestration_plan": orchestration_plan,
            "execution_result": execution_result,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }

        self._save_result(result, pr_number or "local_changes")

        return result

    def interpret_pr(
        self,
        pr_number: Optional[int] = None,
        pr_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Interpreta un PR para entender su propósito y requerimientos
        
        Returns:
            InterpretationResult como dict
        """
        print("\n🔍 Fase 1: Interpretación del PR...")

        if not self.pr_analyzer:
            return {"error": "Planning components not available"}

        # Análisis del PR
        analysis = self.pr_analyzer.analyze_pr(pr_number, pr_data)
        
        if "error" in analysis:
            return analysis

        # Evaluación de impacto
        impact = self.impact_assessor.assess_impact(analysis)
        
        # Estrategia de integración
        strategy = self.integration_strategist.develop_strategy(analysis, impact)

        # Generar interpretación estructurada
        interpretation = InterpretationResult(
            intent=self._extract_intent(analysis),
            context={
                "pr_number": pr_number,
                "analysis": analysis,
                "impact": impact,
                "strategy": strategy
            },
            affected_components=self._extract_affected_components(analysis, impact),
            required_agents=self._determine_required_agents(analysis, impact, strategy),
            estimated_complexity=self._estimate_complexity(analysis, impact),
            confidence=self._calculate_confidence(analysis, impact),
            recommendations=self._generate_recommendations(analysis, impact, strategy)
        )

        print(f"✅ Interpretación completada")
        print(f"   - Intención: {interpretation.intent}")
        print(f"   - Componentes afectados: {len(interpretation.affected_components)}")
        print(f"   - Agentes requeridos: {len(interpretation.required_agents)}")
        print(f"   - Complejidad: {interpretation.estimated_complexity}")
        print(f"   - Confianza: {interpretation.confidence:.2%}")

        return asdict(interpretation)

    def interpret_local_changes(self) -> Dict[str, Any]:
        """Interpreta cambios locales no commiteados"""
        print("\n🔍 Fase 1: Interpretación de cambios locales...")
        
        # Analizar cambios locales usando git
        try:
            import subprocess
            result = subprocess.run(
                ["git", "diff", "--name-status"],
                capture_output=True,
                text=True,
                cwd=self._project_root
            )
            
            changed_files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        changed_files.append({
                            "status": parts[0],
                            "file": parts[1]
                        })

            # Generar interpretación básica
            interpretation = InterpretationResult(
                intent="Local changes detected",
                context={
                    "changed_files": changed_files,
                    "change_count": len(changed_files)
                },
                affected_components=self._extract_components_from_files(changed_files),
                required_agents=["RepositoryAgent", "PlanningAgent"],
                estimated_complexity="medium",
                confidence=0.7,
                recommendations=[
                    "Review changed files",
                    "Run tests before committing",
                    "Consider creating PR for review"
                ]
            )

            return asdict(interpretation)

        except Exception as e:
            return {"error": f"Failed to analyze local changes: {str(e)}"}

    def generate_orchestration_plan(
        self,
        interpretation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera un plan de orquestación basado en la interpretación
        
        Returns:
            OrchestrationPlan como dict
        """
        print("\n📋 Fase 2: Generación de plan de orquestación...")

        if not self.plan_generator:
            # Plan básico si no hay plan_generator
            return self._generate_basic_plan(interpretation)

        # Usar el plan generator existente
        analysis = interpretation.get("context", {}).get("analysis", {})
        impact = interpretation.get("context", {}).get("impact", {})
        strategy = interpretation.get("context", {}).get("strategy", {})

        plan = self.plan_generator.generate_plan(analysis, impact, strategy)

        # Convertir a OrchestrationPlan
        orchestration_plan = OrchestrationPlan(
            plan_id=f"gravity_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            phases=self._extract_phases_from_plan(plan),
            dependencies=self._extract_dependencies(plan),
            estimated_duration=self._estimate_duration(plan),
            risk_assessment=plan.get("task_4.4", {}),
            execution_strategy=self._determine_execution_strategy(interpretation)
        )

        print(f"✅ Plan de orquestación generado")
        print(f"   - ID: {orchestration_plan.plan_id}")
        print(f"   - Fases: {len(orchestration_plan.phases)}")
        print(f"   - Duración estimada: {orchestration_plan.estimated_duration} minutos")

        return asdict(orchestration_plan)

    def orchestrate_execution(
        self,
        plan: Dict[str, Any],
        start_phase: int = -8,
        end_phase: int = 15
    ) -> Dict[str, Any]:
        """
        Orquesta la ejecución del plan usando el MainOrchestrator
        
        Args:
            plan: Plan de orquestación generado
            start_phase: Fase inicial
            end_phase: Fase final
        
        Returns:
            Resultado de la ejecución
        """
        print("\n🚀 Fase 3: Orquestación de ejecución...")

        if not self.orchestrator:
            return {
                "error": "Orchestrator not available",
                "plan": plan
            }

        try:
            # Inicializar orchestrator
            if not self.orchestrator.initialize():
                return {"error": "Failed to initialize orchestrator"}

            # Ejecutar fases
            print(f"📊 Ejecutando fases {start_phase} a {end_phase}...")
            success = self.orchestrator.run(start_phase=start_phase, end_phase=end_phase)

            return {
                "status": "completed" if success else "completed_with_warnings",
                "success": success,
                "start_phase": start_phase,
                "end_phase": end_phase,
                "execution_id": self.state_manager.get_execution_id() if self.state_manager else None
            }

        except Exception as e:
            return {
                "error": f"Execution failed: {str(e)}",
                "plan": plan
            }

    def analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el contexto del proyecto para tomar decisiones"""
        print("\n🔍 Analizando contexto del proyecto...")

        analysis = {
            "project_structure": self._analyze_project_structure(),
            "current_state": self._get_current_state(),
            "dependencies": self._analyze_dependencies(),
            "recommendations": []
        }

        return analysis

    # Métodos auxiliares privados

    def _extract_intent(self, analysis: Dict[str, Any]) -> str:
        """Extrae la intención principal del análisis"""
        title = analysis.get("pr_data", {}).get("title", "")
        description = analysis.get("pr_data", {}).get("body", "")
        
        # Análisis simple de intención
        if "fix" in title.lower() or "bug" in title.lower():
            return "Bug fix"
        elif "feature" in title.lower() or "add" in title.lower():
            return "New feature"
        elif "refactor" in title.lower():
            return "Refactoring"
        elif "test" in title.lower():
            return "Testing"
        else:
            return "General improvement"

    def _extract_affected_components(
        self,
        analysis: Dict[str, Any],
        impact: Dict[str, Any]
    ) -> List[str]:
        """Extrae los componentes afectados"""
        components = set()
        
        # De los archivos cambiados
        changed_files = analysis.get("changed_files", [])
        for file_info in changed_files:
            file_path = file_info.get("file", "")
            if "scripts/" in file_path:
                components.add("scripts")
            elif "src/" in file_path:
                components.add("frontend")
            elif "system/" in file_path:
                components.add("system")
            elif "python-scripts/" in file_path:
                components.add("python_scripts")
            elif "agents/" in file_path:
                components.add("agents")
        
        # De la evaluación de impacto
        impact_areas = impact.get("impact_areas", [])
        components.update(impact_areas)
        
        return list(components)

    def _determine_required_agents(
        self,
        analysis: Dict[str, Any],
        impact: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> List[str]:
        """Determina qué agentes se requieren para la ejecución"""
        agents = ["PlanningAgent"]
        
        affected_components = self._extract_affected_components(analysis, impact)
        
        if "scripts" in affected_components or "python_scripts" in affected_components:
            agents.append("RepositoryAgent")
        
        if impact.get("integration_impact", {}).get("has_integration_changes", False):
            agents.append("IntegrationAgent")
        
        if "quotation" in str(analysis).lower() or "bmc" in str(analysis).lower():
            agents.append("QuotationAgent")
        
        return list(set(agents))

    def _estimate_complexity(
        self,
        analysis: Dict[str, Any],
        impact: Dict[str, Any]
    ) -> str:
        """Estima la complejidad del cambio"""
        changed_files_count = len(analysis.get("changed_files", []))
        impact_score = impact.get("overall_impact_score", 0)
        
        if changed_files_count > 20 or impact_score > 0.8:
            return "high"
        elif changed_files_count > 10 or impact_score > 0.5:
            return "medium"
        else:
            return "low"

    def _calculate_confidence(
        self,
        analysis: Dict[str, Any],
        impact: Dict[str, Any]
    ) -> float:
        """Calcula el nivel de confianza en la interpretación"""
        confidence = 0.5  # Base
        
        # Más archivos analizados = más confianza
        if len(analysis.get("changed_files", [])) > 0:
            confidence += 0.2
        
        # Si hay descripción del PR = más confianza
        if analysis.get("pr_data", {}).get("body"):
            confidence += 0.2
        
        # Si el impacto está bien evaluado = más confianza
        if impact.get("overall_impact_score") is not None:
            confidence += 0.1
        
        return min(confidence, 1.0)

    def _generate_recommendations(
        self,
        analysis: Dict[str, Any],
        impact: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        recommendations = []
        
        # Recomendaciones basadas en impacto
        if impact.get("overall_impact_score", 0) > 0.7:
            recommendations.append("High impact change - consider staged rollout")
        
        # Recomendaciones basadas en estrategia
        merge_strategy = strategy.get("merge_strategy", {})
        if merge_strategy.get("complexity") == "high":
            recommendations.append("Consider feature branch approach")
        
        # Recomendaciones generales
        recommendations.append("Run full test suite before merging")
        recommendations.append("Update documentation if needed")
        
        return recommendations

    def _extract_phases_from_plan(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrae las fases del plan generado"""
        phases = []
        
        tasks = plan.get("task_4.1", {}).get("tasks", [])
        for task in tasks:
            phase = task.get("phase", 0)
            if not any(p.get("phase") == phase for p in phases):
                phases.append({
                    "phase": phase,
                    "tasks": [t for t in tasks if t.get("phase") == phase]
                })
        
        return sorted(phases, key=lambda x: x["phase"])

    def _extract_dependencies(self, plan: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extrae las dependencias del plan"""
        dependencies = {}
        
        tasks = plan.get("task_4.1", {}).get("tasks", [])
        for task in tasks:
            task_id = task.get("id")
            deps = task.get("dependencies", [])
            if deps:
                dependencies[task_id] = deps
        
        return dependencies

    def _estimate_duration(self, plan: Dict[str, Any]) -> int:
        """Estima la duración total en minutos"""
        timeline = plan.get("task_4.3", {})
        return timeline.get("total_estimated_minutes", 60)

    def _determine_execution_strategy(self, interpretation: Dict[str, Any]) -> str:
        """Determina la estrategia de ejecución"""
        complexity = interpretation.get("estimated_complexity", "medium")
        
        if complexity == "high":
            return "staged_rollout"
        elif complexity == "medium":
            return "standard_execution"
        else:
            return "fast_track"

    def _generate_basic_plan(self, interpretation: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un plan básico cuando no hay plan_generator"""
        return {
            "plan_id": f"gravity_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "phases": [
                {
                    "phase": 0,
                    "tasks": [
                        {
                            "id": "T0.1",
                            "description": "Initial setup",
                            "agent": "PlanningAgent"
                        }
                    ]
                }
            ],
            "dependencies": {},
            "estimated_duration": 30,
            "risk_assessment": {},
            "execution_strategy": "standard_execution",
            "start_phase": -8,
            "end_phase": 15
        }

    def _extract_components_from_files(self, changed_files: List[Dict[str, Any]]) -> List[str]:
        """Extrae componentes de la lista de archivos cambiados"""
        components = set()
        for file_info in changed_files:
            file_path = file_info.get("file", "")
            if "/" in file_path:
                component = file_path.split("/")[0]
                components.add(component)
        return list(components)

    def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analiza la estructura del proyecto"""
        structure = {
            "directories": [],
            "file_count": 0
        }
        
        try:
            for item in Path(self._project_root).iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    structure["directories"].append(item.name)
                elif item.is_file():
                    structure["file_count"] += 1
        except Exception:
            pass
        
        return structure

    def _get_current_state(self) -> Dict[str, Any]:
        """Obtiene el estado actual del proyecto"""
        if self.state_manager:
            return {
                "current_phase": self.state_manager.get_current_phase(),
                "execution_id": self.state_manager.get_execution_id(),
                "overall_status": self.state_manager.get_overall_status()
            }
        return {}

    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analiza las dependencias del proyecto"""
        # Placeholder - implementar análisis real de dependencias
        return {
            "python_packages": [],
            "node_modules": [],
            "external_services": []
        }

    def _save_result(self, result: Dict[str, Any], identifier: str):
        """Guarda el resultado en un archivo"""
        output_file = self.output_dir / f"gravity_result_{identifier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n💾 Resultado guardado en: {output_file}")


def main():
    """Función principal para ejecutar el Gravity Agent"""
    import argparse

    parser = argparse.ArgumentParser(description="Gravity Agent - Development Orchestration Specialist")
    parser.add_argument("--pr", type=int, help="PR number to analyze")
    parser.add_argument("--local", action="store_true", help="Analyze local changes")
    parser.add_argument("--mode", choices=["automated", "interactive", "dry_run", "analysis_only"],
                       default="automated", help="Execution mode")
    parser.add_argument("--start-phase", type=int, default=-8, help="Start phase")
    parser.add_argument("--end-phase", type=int, default=15, help="End phase")

    args = parser.parse_args()

    # Crear agente
    execution_mode = ExecutionMode(args.mode)
    agent = GravityAgent(execution_mode=execution_mode)

    # Ejecutar
    if args.local:
        result = agent.interpret_and_orchestrate(local_changes=True)
    elif args.pr:
        result = agent.interpret_and_orchestrate(pr_number=args.pr)
    else:
        print("Error: Debe especificar --pr o --local")
        return 1

    # Mostrar resultado
    print("\n" + "=" * 80)
    print("✅ GRAVITY AGENT - COMPLETADO")
    print("=" * 80)
    print(f"\nEstado: {result.get('status', 'unknown')}")

    return 0 if result.get("status") == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())

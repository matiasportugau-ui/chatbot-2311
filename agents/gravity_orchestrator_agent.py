#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gravity Orchestrator Agent
==========================

Agente especialista en interpretar y orquestar el desarrollo automatizado del proyecto.
Diseñado para funcionar en "agent mode" de Gravity.

Este agente:
- Interpreta el estado actual del proyecto y las fases de ejecución
- Orquesta el desarrollo automatizado usando el sistema de orquestación existente
- Gestiona la ejecución de fases desde -8 hasta 15
- Proporciona análisis inteligente y toma de decisiones automatizada
- Integra con el sistema de estado y reportes existente

Basado en patrones:
- ReAct (Reasoning + Acting)
- Context-Aware Planning
- Automated Orchestration
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import orchestrator components
try:
    from scripts.orchestrator.main_orchestrator import MainOrchestrator
    from scripts.orchestrator.state_manager import StateManager
    from scripts.orchestrator.dependency_resolver import DependencyResolver
    from scripts.orchestrator.status_reporter import StatusReporter
    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    ORCHESTRATOR_AVAILABLE = False
    print(f"⚠️  Warning: Orchestrator components not available: {e}")

# Import AI agent components if available
try:
    from AI_AGENTS.EXECUTOR.execution_ai_agent import ExecutionAIAgent
    AI_AGENT_AVAILABLE = True
except ImportError:
    AI_AGENT_AVAILABLE = False


class AgentMode(Enum):
    """Modos de operación del agente"""
    INTERPRET = "interpret"  # Solo interpreta y analiza
    ORCHESTRATE = "orchestrate"  # Orquesta ejecución
    HYBRID = "hybrid"  # Interpreta y orquesta


class PhaseStatus(Enum):
    """Estado de las fases"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


@dataclass
class ProjectState:
    """Estado actual del proyecto"""
    current_phase: int
    overall_status: str
    phases_status: Dict[int, str]
    execution_id: str
    last_update: str
    blockers: List[str]
    next_actions: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class OrchestrationPlan:
    """Plan de orquestación"""
    goal: str
    phases_to_execute: List[int]
    dependencies: Dict[int, List[int]]
    estimated_time: Optional[str]
    priority_order: List[int]
    risk_assessment: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class GravityOrchestratorAgent:
    """
    Agente especialista en interpretar y orquestar el desarrollo automatizado.
    
    Funcionalidades principales:
    1. Interpretación: Analiza el estado del proyecto y determina qué hacer
    2. Orquestación: Ejecuta las fases de desarrollo de forma automatizada
    3. Monitoreo: Supervisa el progreso y detecta problemas
    4. Toma de decisiones: Decide automáticamente el siguiente paso
    """
    
    def __init__(
        self,
        config_file: str = "scripts/orchestrator/config/orchestrator_config.json",
        mode: AgentMode = AgentMode.HYBRID,
        auto_approve: bool = True
    ):
        """
        Inicializa el agente Gravity Orchestrator
        
        Args:
            config_file: Ruta al archivo de configuración del orchestrator
            mode: Modo de operación (interpret, orchestrate, hybrid)
            auto_approve: Si True, auto-aprueba las fases automáticamente
        """
        self.config_file = Path(config_file)
        self.mode = mode
        self.auto_approve = auto_approve
        
        # Initialize orchestrator components
        self.orchestrator: Optional[MainOrchestrator] = None
        self.state_manager: Optional[StateManager] = None
        self.dependency_resolver: Optional[DependencyResolver] = None
        self.status_reporter: Optional[StatusReporter] = None
        
        # Initialize AI agent if available
        self.ai_agent: Optional[ExecutionAIAgent] = None
        
        # Agent state
        self.project_state: Optional[ProjectState] = None
        self.orchestration_plan: Optional[OrchestrationPlan] = None
        self.execution_history: List[Dict] = []
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Inicializa los componentes necesarios"""
        if not ORCHESTRATOR_AVAILABLE:
            print("⚠️  Warning: Orchestrator not available. Limited functionality.")
            return
        
        try:
            # Initialize main orchestrator
            self.orchestrator = MainOrchestrator(str(self.config_file))
            self.state_manager = self.orchestrator.state_manager
            self.dependency_resolver = self.orchestrator.dependency_resolver
            self.status_reporter = self.orchestrator.status_reporter
            
            # Initialize orchestrator
            if not self.orchestrator.initialize():
                print("❌ Failed to initialize orchestrator")
                return
            
            print("✅ Orchestrator components initialized")
            
            # Initialize AI agent if available
            if AI_AGENT_AVAILABLE:
                try:
                    self.ai_agent = ExecutionAIAgent()
                    if self.ai_agent.is_available():
                        print("✅ AI Agent initialized")
                    else:
                        print("⚠️  AI Agent not available (no model integrator)")
                except Exception as e:
                    print(f"⚠️  Could not initialize AI Agent: {e}")
            
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            import traceback
            traceback.print_exc()
    
    def interpret_project_state(self) -> ProjectState:
        """
        Interpreta el estado actual del proyecto.
        
        Analiza:
        - Fase actual de ejecución
        - Estado de todas las fases
        - Bloqueadores y dependencias
        - Próximas acciones recomendadas
        
        Returns:
            ProjectState con el análisis completo
        """
        print("\n" + "="*80)
        print("🔍 INTERPRETANDO ESTADO DEL PROYECTO")
        print("="*80 + "\n")
        
        if not self.state_manager:
            raise RuntimeError("StateManager not initialized")
        
        # Get current state
        current_phase = self.state_manager.get_current_phase()
        overall_status = self.state_manager.get_overall_status()
        execution_id = self.state_manager.get_execution_id()
        
        # Get phase statuses
        phases_status = {}
        for phase in range(-8, 16):  # Fases desde -8 hasta 15
            phase_status = self.state_manager.get_phase_status(phase)
            phases_status[phase] = phase_status
        
        # Analyze blockers
        blockers = self._identify_blockers(current_phase, phases_status)
        
        # Determine next actions
        next_actions = self._determine_next_actions(current_phase, phases_status, blockers)
        
        # Create project state
        self.project_state = ProjectState(
            current_phase=current_phase,
            overall_status=overall_status,
            phases_status=phases_status,
            execution_id=execution_id,
            last_update=datetime.now().isoformat(),
            blockers=blockers,
            next_actions=next_actions
        )
        
        # Print interpretation
        self._print_interpretation(self.project_state)
        
        return self.project_state
    
    def _identify_blockers(self, current_phase: int, phases_status: Dict[int, str]) -> List[str]:
        """Identifica bloqueadores en la ejecución"""
        blockers = []
        
        if not self.dependency_resolver:
            return blockers
        
        # Check if current phase is blocked
        can_execute, missing = self.dependency_resolver.check_dependencies(current_phase)
        if not can_execute:
            blockers.append(f"Phase {current_phase} blocked by missing dependencies: {missing}")
        
        # Check for failed phases
        for phase, status in phases_status.items():
            if status == "failed":
                blockers.append(f"Phase {phase} has failed and may block subsequent phases")
        
        # Check for in-progress phases that might be stuck
        for phase, status in phases_status.items():
            if status == "in_progress" and phase < current_phase:
                blockers.append(f"Phase {phase} is still in progress (may be stuck)")
        
        return blockers
    
    def _determine_next_actions(self, current_phase: int, phases_status: Dict[int, str], blockers: List[str]) -> List[str]:
        """Determina las próximas acciones recomendadas"""
        actions = []
        
        if blockers:
            actions.append(f"Resolve blockers: {', '.join(blockers[:3])}")
        
        # Find next pending phase
        for phase in range(current_phase, 16):
            if phases_status.get(phase) == "pending":
                actions.append(f"Execute Phase {phase}")
                break
        
        # Check if we should retry failed phases
        failed_phases = [p for p, s in phases_status.items() if s == "failed"]
        if failed_phases:
            actions.append(f"Consider retrying failed phases: {failed_phases[:3]}")
        
        # Check completion status
        completed = sum(1 for s in phases_status.values() if s == "completed")
        total = len(phases_status)
        if completed < total:
            actions.append(f"Continue execution: {completed}/{total} phases completed")
        
        if not actions:
            actions.append("All phases completed or execution finished")
        
        return actions
    
    def _print_interpretation(self, state: ProjectState):
        """Imprime la interpretación del estado"""
        print(f"📊 Estado General: {state.overall_status}")
        print(f"📍 Fase Actual: {state.current_phase}")
        print(f"🆔 Execution ID: {state.execution_id}")
        print(f"⏰ Última Actualización: {state.last_update}\n")
        
        # Phase summary
        completed = sum(1 for s in state.phases_status.values() if s == "completed")
        in_progress = sum(1 for s in state.phases_status.values() if s == "in_progress")
        failed = sum(1 for s in state.phases_status.values() if s == "failed")
        pending = sum(1 for s in state.phases_status.values() if s == "pending")
        
        print("📈 Resumen de Fases:")
        print(f"   ✅ Completadas: {completed}")
        print(f"   🔄 En Progreso: {in_progress}")
        print(f"   ❌ Fallidas: {failed}")
        print(f"   ⏳ Pendientes: {pending}\n")
        
        if state.blockers:
            print("🚫 Bloqueadores:")
            for blocker in state.blockers:
                print(f"   • {blocker}")
            print()
        
        if state.next_actions:
            print("🎯 Próximas Acciones Recomendadas:")
            for i, action in enumerate(state.next_actions, 1):
                print(f"   {i}. {action}")
            print()
    
    def create_orchestration_plan(
        self,
        goal: str = "Complete all phases from current state",
        start_phase: Optional[int] = None,
        end_phase: int = 15
    ) -> OrchestrationPlan:
        """
        Crea un plan de orquestación basado en el estado actual.
        
        Args:
            goal: Objetivo del plan
            start_phase: Fase inicial (None = usar fase actual)
            end_phase: Fase final
            
        Returns:
            OrchestrationPlan con el plan detallado
        """
        print("\n" + "="*80)
        print("📋 CREANDO PLAN DE ORQUESTACIÓN")
        print("="*80 + "\n")
        
        if not self.project_state:
            self.interpret_project_state()
        
        # Determine start phase
        if start_phase is None:
            start_phase = self.project_state.current_phase
        
        # Determine phases to execute
        phases_to_execute = []
        for phase in range(start_phase, end_phase + 1):
            status = self.project_state.phases_status.get(phase, "pending")
            if status in ["pending", "failed"]:
                phases_to_execute.append(phase)
        
        # Get dependencies
        dependencies = {}
        if self.dependency_resolver:
            for phase in phases_to_execute:
                can_execute, missing = self.dependency_resolver.check_dependencies(phase)
                dependencies[phase] = missing if not can_execute else []
        
        # Determine priority order (respect dependencies)
        priority_order = self._determine_priority_order(phases_to_execute, dependencies)
        
        # Risk assessment
        risk_assessment = self._assess_risks(phases_to_execute, dependencies)
        
        # Estimate time (rough estimate: 30 min per phase)
        estimated_time = f"~{len(phases_to_execute) * 30} minutes"
        
        # Create plan
        self.orchestration_plan = OrchestrationPlan(
            goal=goal,
            phases_to_execute=phases_to_execute,
            dependencies=dependencies,
            estimated_time=estimated_time,
            priority_order=priority_order,
            risk_assessment=risk_assessment
        )
        
        # Print plan
        self._print_orchestration_plan(self.orchestration_plan)
        
        return self.orchestration_plan
    
    def _determine_priority_order(self, phases: List[int], dependencies: Dict[int, List[int]]) -> List[int]:
        """Determina el orden de prioridad respetando dependencias"""
        # Simple topological sort
        ordered = []
        remaining = set(phases)
        
        while remaining:
            # Find phases with no unmet dependencies
            ready = [
                p for p in remaining
                if not dependencies.get(p, []) or
                all(dep not in remaining for dep in dependencies.get(p, []))
            ]
            
            if not ready:
                # Circular dependency or missing dependency
                # Add remaining phases in order
                ordered.extend(sorted(remaining))
                break
            
            # Add ready phases in order
            ordered.extend(sorted(ready))
            remaining -= set(ready)
        
        return ordered
    
    def _assess_risks(self, phases: List[int], dependencies: Dict[int, List[int]]) -> Dict[str, Any]:
        """Evalúa los riesgos del plan"""
        risks = {
            "high_risk_phases": [],
            "dependency_risks": [],
            "blocked_phases": [],
            "overall_risk": "low"
        }
        
        # Check for phases with many dependencies
        for phase in phases:
            deps = dependencies.get(phase, [])
            if len(deps) > 3:
                risks["dependency_risks"].append({
                    "phase": phase,
                    "dependencies": len(deps),
                    "risk": "high"
                })
        
        # Check for blocked phases
        for phase in phases:
            deps = dependencies.get(phase, [])
            if deps:
                risks["blocked_phases"].append({
                    "phase": phase,
                    "blocked_by": deps
                })
        
        # Determine overall risk
        if risks["blocked_phases"] or risks["dependency_risks"]:
            risks["overall_risk"] = "medium"
        if len(risks["blocked_phases"]) > 5:
            risks["overall_risk"] = "high"
        
        return risks
    
    def _print_orchestration_plan(self, plan: OrchestrationPlan):
        """Imprime el plan de orquestación"""
        print(f"🎯 Objetivo: {plan.goal}")
        print(f"⏱️  Tiempo Estimado: {plan.estimated_time}")
        print(f"📊 Riesgo General: {plan.risk_assessment['overall_risk']}\n")
        
        print(f"📋 Fases a Ejecutar ({len(plan.phases_to_execute)}):")
        for phase in plan.phases_to_execute:
            deps = plan.dependencies.get(phase, [])
            deps_str = f" (deps: {deps})" if deps else ""
            print(f"   • Phase {phase}{deps_str}")
        print()
        
        print(f"🔄 Orden de Prioridad:")
        for i, phase in enumerate(plan.priority_order, 1):
            print(f"   {i}. Phase {phase}")
        print()
        
        if plan.risk_assessment.get("blocked_phases"):
            print("⚠️  Fases Bloqueadas:")
            for blocked in plan.risk_assessment["blocked_phases"][:5]:
                print(f"   • Phase {blocked['phase']} bloqueada por: {blocked['blocked_by']}")
            print()
    
    def orchestrate_execution(
        self,
        start_phase: Optional[int] = None,
        end_phase: int = 15,
        auto_approve: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Orquesta la ejecución automatizada de las fases.
        
        Args:
            start_phase: Fase inicial (None = usar fase actual)
            end_phase: Fase final
            auto_approve: Si True, auto-aprueba fases (None = usar self.auto_approve)
            
        Returns:
            Dict con el resultado de la ejecución
        """
        print("\n" + "="*80)
        print("🚀 ORQUESTANDO EJECUCIÓN AUTOMATIZADA")
        print("="*80 + "\n")
        
        if not self.orchestrator:
            raise RuntimeError("Orchestrator not initialized")
        
        # Use provided auto_approve or instance default
        if auto_approve is None:
            auto_approve = self.auto_approve
        
        # Interpret current state if not done
        if not self.project_state:
            self.interpret_project_state()
        
        # Create plan if not exists
        if not self.orchestration_plan:
            self.create_orchestration_plan(start_phase=start_phase, end_phase=end_phase)
        
        # Determine start phase
        if start_phase is None:
            start_phase = self.project_state.current_phase
        
        print(f"🎯 Ejecutando fases desde {start_phase} hasta {end_phase}")
        print(f"✅ Auto-aprobación: {'HABILITADA' if auto_approve else 'DESHABILITADA'}\n")
        
        # Execute using orchestrator
        try:
            success = self.orchestrator.run(start_phase=start_phase, end_phase=end_phase)
            
            # Record execution
            execution_record = {
                "timestamp": datetime.now().isoformat(),
                "start_phase": start_phase,
                "end_phase": end_phase,
                "success": success,
                "auto_approve": auto_approve
            }
            self.execution_history.append(execution_record)
            
            # Update project state
            self.interpret_project_state()
            
            return {
                "success": success,
                "execution_record": execution_record,
                "final_state": self.project_state.to_dict() if self.project_state else None
            }
            
        except Exception as e:
            print(f"❌ Error durante la ejecución: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "execution_record": {
                    "timestamp": datetime.now().isoformat(),
                    "start_phase": start_phase,
                    "end_phase": end_phase,
                    "success": False,
                    "error": str(e)
                }
            }
    
    def execute_phase(self, phase: int) -> Dict[str, Any]:
        """
        Ejecuta una fase específica.
        
        Args:
            phase: Número de fase a ejecutar
            
        Returns:
            Dict con el resultado de la ejecución
        """
        print(f"\n🎯 Ejecutando Phase {phase}...\n")
        
        if not self.orchestrator:
            raise RuntimeError("Orchestrator not initialized")
        
        try:
            success = self.orchestrator.execute_phase(phase)
            
            # Update project state
            self.interpret_project_state()
            
            return {
                "success": success,
                "phase": phase,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "phase": phase,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_status_report(self) -> Dict[str, Any]:
        """Obtiene un reporte completo del estado"""
        if not self.project_state:
            self.interpret_project_state()
        
        if not self.orchestration_plan:
            self.create_orchestration_plan()
        
        return {
            "project_state": self.project_state.to_dict() if self.project_state else None,
            "orchestration_plan": self.orchestration_plan.to_dict() if self.orchestration_plan else None,
            "execution_history": self.execution_history,
            "mode": self.mode.value,
            "auto_approve": self.auto_approve,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_report(self, output_file: Optional[str] = None) -> Path:
        """Guarda un reporte en archivo"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"consolidation/gravity_agent_report_{timestamp}.json"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = self.get_status_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Reporte guardado en: {output_path}")
        return output_path


def main():
    """CLI interface para Gravity Orchestrator Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gravity Orchestrator Agent - Especialista en interpretar y orquestar desarrollo automatizado"
    )
    
    parser.add_argument(
        "--mode",
        choices=["interpret", "orchestrate", "hybrid"],
        default="hybrid",
        help="Modo de operación del agente"
    )
    
    parser.add_argument(
        "--action",
        choices=["interpret", "plan", "execute", "phase", "status"],
        default="interpret",
        help="Acción a realizar"
    )
    
    parser.add_argument(
        "--phase",
        type=int,
        help="Número de fase (para acción 'phase')"
    )
    
    parser.add_argument(
        "--start-phase",
        type=int,
        help="Fase inicial para ejecución"
    )
    
    parser.add_argument(
        "--end-phase",
        type=int,
        default=15,
        help="Fase final para ejecución"
    )
    
    parser.add_argument(
        "--no-auto-approve",
        action="store_true",
        help="Deshabilitar auto-aprobación"
    )
    
    parser.add_argument(
        "--output",
        help="Archivo de salida para reportes"
    )
    
    args = parser.parse_args()
    
    # Initialize agent
    mode = AgentMode(args.mode)
    auto_approve = not args.no_auto_approve
    
    agent = GravityOrchestratorAgent(mode=mode, auto_approve=auto_approve)
    
    print("\n" + "="*80)
    print("🤖 GRAVITY ORCHESTRATOR AGENT")
    print("="*80)
    print(f"Modo: {mode.value}")
    print(f"Auto-aprobación: {'HABILITADA' if auto_approve else 'DESHABILITADA'}")
    print("="*80 + "\n")
    
    # Execute action
    if args.action == "interpret":
        agent.interpret_project_state()
        
    elif args.action == "plan":
        agent.interpret_project_state()
        agent.create_orchestration_plan(
            start_phase=args.start_phase,
            end_phase=args.end_phase
        )
        
    elif args.action == "execute":
        agent.interpret_project_state()
        agent.create_orchestration_plan(
            start_phase=args.start_phase,
            end_phase=args.end_phase
        )
        result = agent.orchestrate_execution(
            start_phase=args.start_phase,
            end_phase=args.end_phase
        )
        
        if result.get("success"):
            print("\n✅ Ejecución completada exitosamente")
        else:
            print("\n❌ Ejecución falló o fue interrumpida")
            
    elif args.action == "phase":
        if args.phase is None:
            print("❌ Error: --phase requerido para acción 'phase'")
            return 1
        
        result = agent.execute_phase(args.phase)
        
        if result.get("success"):
            print(f"\n✅ Phase {args.phase} ejecutada exitosamente")
        else:
            print(f"\n❌ Phase {args.phase} falló: {result.get('error', 'Unknown error')}")
            
    elif args.action == "status":
        report = agent.get_status_report()
        print("\n📊 Estado del Proyecto:")
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    
    # Save report if requested or if execution was performed
    if args.output or args.action in ["execute", "phase"]:
        agent.save_report(args.output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

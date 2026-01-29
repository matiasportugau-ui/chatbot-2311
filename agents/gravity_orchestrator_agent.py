#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌌 GRAVITY ORCHESTRATOR AGENT
====================================

Agente especialista para Cursor Agent Mode que interpreta y orquesta
el desarrollo automatizado del proyecto BMC Chatbot.

Este agente es el "cerebro" central que:
- Interpreta el estado del proyecto y PRs
- Orquesta la ejecución de fases automatizadas
- Coordina entre diferentes agentes especializados
- Gestiona el ciclo de vida del desarrollo

Basado en patrones de Prompt Engineering:
- ReAct (Reasoning + Acting)
- Chain-of-Thought
- Context-Aware Planning
- Tool-Using Agent
- Multi-Agent Coordination

Autor: AI Development Team
Versión: 1.0.0
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict, field

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))


# ============================================================================
# ENUMS Y CONFIGURACIÓN
# ============================================================================

class AgentMode(Enum):
    """Modos de operación del agente"""
    PLANNING = "planning"           # Análisis y planificación
    EXECUTION = "execution"         # Ejecución de tareas
    MONITORING = "monitoring"       # Monitoreo continuo
    TRAINING = "training"           # Modo entrenamiento (PR #87)
    EVALUATION = "evaluation"       # Evaluación y benchmarking
    ORCHESTRATION = "orchestration" # Orquestación multi-agente


class TaskPriority(Enum):
    """Prioridades de tareas"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(Enum):
    """Estados de tareas"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class PhaseCategory(Enum):
    """Categorías de fases del proyecto"""
    PRELIMINARY = "preliminary"     # Fases -8 a -1
    FOUNDATION = "foundation"       # Fases 0-3
    INTEGRATION = "integration"     # Fases 4-7
    ENHANCEMENT = "enhancement"     # Fases 8-11
    PRODUCTION = "production"       # Fases 12-15


# ============================================================================
# MODELOS DE DATOS
# ============================================================================

@dataclass
class ProjectState:
    """Estado actual del proyecto"""
    current_phase: int = 0
    overall_status: str = "unknown"
    pending_prs: List[int] = field(default_factory=list)
    active_branches: List[str] = field(default_factory=list)
    last_execution: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DevelopmentTask:
    """Representa una tarea de desarrollo"""
    id: str
    title: str
    description: str
    category: str
    priority: TaskPriority
    status: TaskStatus
    phase: Optional[int] = None
    dependencies: List[str] = field(default_factory=list)
    assigned_agent: Optional[str] = None
    estimated_time: Optional[str] = None
    actual_time: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["priority"] = self.priority.value
        data["status"] = self.status.value
        return data


@dataclass
class PRAnalysis:
    """Análisis de un Pull Request"""
    pr_number: int
    title: str
    description: str
    files_changed: List[str] = field(default_factory=list)
    impact_level: str = "medium"
    integration_complexity: str = "medium"
    affected_systems: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    training_relevance: bool = False  # Si es relevante para el sistema de training

    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# GRAVITY ORCHESTRATOR AGENT - CLASE PRINCIPAL
# ============================================================================

class GravityOrchestratorAgent:
    """
    🌌 GRAVITY ORCHESTRATOR AGENT
    
    Agente central de orquestación que interpreta el estado del proyecto
    y coordina el desarrollo automatizado utilizando el patrón ReAct.
    
    Capacidades principales:
    1. Análisis de PRs y cambios del proyecto
    2. Generación de planes de implementación
    3. Orquestación de ejecución por fases
    4. Coordinación de agentes especializados
    5. Monitoreo y evaluación continua
    6. Integración con sistema de training (PR #87)
    
    Uso con Cursor Agent Mode:
    - Este agente puede ser invocado desde Cursor para planificar tareas
    - Coordina con otros agentes (Executor, Planner, Trainer)
    - Mantiene el contexto entre sesiones
    """

    VERSION = "1.0.0"
    AGENT_NAME = "GravityOrchestratorAgent"

    def __init__(self, 
                 mode: AgentMode = AgentMode.ORCHESTRATION,
                 auto_approve: bool = True,
                 verbose: bool = True):
        """
        Inicializa el Gravity Orchestrator Agent.
        
        Args:
            mode: Modo de operación del agente
            auto_approve: Si True, auto-aprueba fases (según .cursorrules)
            verbose: Si True, imprime información detallada
        """
        self.mode = mode
        self.auto_approve = auto_approve
        self.verbose = verbose
        
        # Estado del proyecto
        self.project_state = ProjectState()
        self.tasks: List[DevelopmentTask] = []
        self.execution_history: List[Dict] = []
        
        # Configuración de paths
        self.project_root = PROJECT_ROOT
        self.consolidation_dir = PROJECT_ROOT / "consolidation"
        self.logs_dir = PROJECT_ROOT / "system" / "logs"
        
        # Inicializar componentes
        self._init_components()
        
        # Cargar estado previo si existe
        self._load_state()

        if self.verbose:
            self._print_banner()

    def _print_banner(self):
        """Imprime el banner del agente"""
        print("\n" + "=" * 70)
        print("🌌 GRAVITY ORCHESTRATOR AGENT v" + self.VERSION)
        print("=" * 70)
        print(f"   Modo: {self.mode.value}")
        print(f"   Auto-approve: {self.auto_approve}")
        print(f"   Project Root: {self.project_root}")
        print("=" * 70 + "\n")

    def _init_components(self):
        """Inicializa los componentes del agente"""
        # Importar componentes del orchestrator si están disponibles
        self.state_manager = None
        self.context_manager = None
        self.github_integration = None
        self.planning_agent = None
        self.components_available = False
        
        try:
            from scripts.orchestrator.state_manager import StateManager
            self.state_manager = StateManager()
        except Exception as e:
            if self.verbose:
                print(f"⚠️  StateManager no disponible: {e}")
        
        try:
            from scripts.orchestrator.context_manager import ContextManager
            if self.state_manager:
                self.context_manager = ContextManager(self.state_manager)
            else:
                self.context_manager = None
        except Exception as e:
            if self.verbose:
                print(f"⚠️  ContextManager no disponible: {e}")
        
        try:
            from scripts.orchestrator.github_integration import GitHubIntegration
            self.github_integration = GitHubIntegration(None, "chatbot-2311", None)
        except Exception as e:
            if self.verbose:
                print(f"⚠️  GitHubIntegration no disponible: {e}")
        
        try:
            from scripts.orchestrator.planning_agent import PlanningAgent
            self.planning_agent = PlanningAgent(
                self.state_manager,
                self.context_manager,
                self.github_integration
            )
            self.components_available = True
        except Exception as e:
            if self.verbose:
                print(f"⚠️  PlanningAgent no disponible: {e}")
        
        # Si al menos el state_manager está disponible, consideramos componentes parcialmente disponibles
        if self.state_manager:
            self.components_available = True

    def _load_state(self):
        """Carga el estado previo del agente"""
        state_file = self.consolidation_dir / "gravity_agent_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    self.project_state = ProjectState(**data.get("project_state", {}))
                    if self.verbose:
                        print(f"✅ Estado cargado desde {state_file}")
            except Exception as e:
                if self.verbose:
                    print(f"⚠️  Error cargando estado: {e}")

    def _save_state(self):
        """Guarda el estado del agente"""
        self.consolidation_dir.mkdir(parents=True, exist_ok=True)
        state_file = self.consolidation_dir / "gravity_agent_state.json"
        
        data = {
            "agent_version": self.VERSION,
            "timestamp": datetime.now().isoformat(),
            "mode": self.mode.value,
            "project_state": self.project_state.to_dict(),
            "tasks": [t.to_dict() for t in self.tasks],
            "execution_history_count": len(self.execution_history)
        }
        
        with open(state_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        if self.verbose:
            print(f"💾 Estado guardado en {state_file}")

    # ========================================================================
    # MÉTODOS ReAct: THINK - ACT - OBSERVE
    # ========================================================================

    def think(self, situation: str, context: Optional[Dict] = None) -> Dict:
        """
        🧠 FASE THINK: Analiza la situación y planifica el enfoque.
        
        Args:
            situation: Descripción de la situación actual
            context: Contexto adicional
            
        Returns:
            Dict con análisis, plan, y próximos pasos
        """
        if self.verbose:
            print("\n🧠 THINK: Analizando situación...")
        
        context = context or {}
        
        # Analizar la situación
        analysis = self._analyze_situation(situation, context)
        
        # Generar plan de acción
        plan = self._generate_plan(analysis)
        
        # Identificar próximos pasos inmediatos
        next_steps = self._prioritize_next_steps(plan)
        
        result = {
            "analysis": analysis,
            "plan": plan,
            "next_steps": next_steps,
            "confidence": self._calculate_confidence(analysis),
            "potential_issues": self._identify_potential_issues(analysis),
            "recommendations": self._generate_recommendations(analysis)
        }
        
        if self.verbose:
            print(f"   📊 Análisis: {analysis.get('summary', 'N/A')[:80]}...")
            print(f"   📋 Plan: {len(plan)} tareas identificadas")
            print(f"   ➡️  Próximos pasos: {len(next_steps)}")
        
        return result

    def act(self, action: str, parameters: Optional[Dict] = None) -> Dict:
        """
        ⚡ FASE ACT: Ejecuta acciones utilizando las herramientas disponibles.
        
        Args:
            action: Acción a ejecutar
            parameters: Parámetros de la acción
            
        Returns:
            Dict con resultado de la acción
        """
        if self.verbose:
            print(f"\n⚡ ACT: Ejecutando '{action}'...")
        
        parameters = parameters or {}
        result = {
            "action": action,
            "parameters": parameters,
            "success": False,
            "output": None,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Mapear acciones a métodos
            action_map = {
                "analyze_pr": self._act_analyze_pr,
                "review_project_state": self._act_review_project_state,
                "generate_implementation_plan": self._act_generate_implementation_plan,
                "execute_phase": self._act_execute_phase,
                "run_training_mode": self._act_run_training_mode,
                "run_benchmark": self._act_run_benchmark,
                "coordinate_agents": self._act_coordinate_agents,
                "check_github_prs": self._act_check_github_prs,
                "generate_report": self._act_generate_report,
                "sync_state": self._act_sync_state,
                # Acciones adicionales
                "initial_setup": self._act_initial_setup,
                "execute_pending_tasks": self._act_execute_pending_tasks,
                "review_pending_prs": self._act_review_pending_prs,
                "prepare_training_integration": self._act_prepare_training_integration,
            }
            
            if action in action_map:
                result.update(action_map[action](parameters))
            else:
                result["error"] = f"Acción desconocida: {action}"
                
        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
        
        # Registrar en historial
        self.execution_history.append(result)
        
        if self.verbose:
            status = "✅ OK" if result.get("success") else "❌ FALLO"
            print(f"   {status}")
        
        return result

    def observe(self, action_result: Dict) -> Dict:
        """
        👁️ FASE OBSERVE: Evalúa resultados y ajusta estrategia.
        
        Args:
            action_result: Resultado de la fase ACT
            
        Returns:
            Dict con observaciones y recomendaciones
        """
        if self.verbose:
            print("\n👁️ OBSERVE: Evaluando resultados...")
        
        observation = {
            "success": action_result.get("success", False),
            "observation": "",
            "issues": [],
            "next_steps": [],
            "recommendations": [],
            "should_retry": False,
            "retry_strategy": None
        }
        
        if action_result.get("success"):
            observation["observation"] = "Acción completada exitosamente"
            observation["next_steps"] = self._determine_next_steps(action_result)
        else:
            error = action_result.get("error", "Error desconocido")
            observation["observation"] = f"Acción falló: {error}"
            observation["issues"] = [error]
            observation["should_retry"] = self._should_retry(action_result)
            observation["retry_strategy"] = self._get_retry_strategy(action_result)
            observation["recommendations"] = self._get_recovery_recommendations(action_result)
        
        if self.verbose:
            print(f"   📝 Observación: {observation['observation'][:80]}...")
        
        return observation

    def react_cycle(self, situation: str, max_iterations: int = 5) -> Dict:
        """
        🔄 CICLO REACT COMPLETO: Think → Act → Observe → Repeat
        
        Args:
            situation: Situación inicial
            max_iterations: Máximo de iteraciones
            
        Returns:
            Resumen completo de la ejecución
        """
        print("\n" + "=" * 70)
        print("🔄 INICIANDO CICLO REACT: THINK → ACT → OBSERVE")
        print("=" * 70)
        
        iteration = 0
        current_situation = situation
        all_results = []
        final_success = False
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n{'─' * 50}")
            print(f"📍 Iteración {iteration}/{max_iterations}")
            print(f"{'─' * 50}")
            
            # THINK
            think_result = self.think(current_situation)
            
            if not think_result.get("next_steps"):
                print("✅ No hay más acciones pendientes")
                final_success = True
                break
            
            # ACT
            next_action = think_result["next_steps"][0]
            if isinstance(next_action, dict):
                action_name = next_action.get("action", "unknown")
                action_params = next_action.get("parameters", {})
            else:
                action_name = str(next_action)
                action_params = {}
            
            act_result = self.act(action_name, action_params)
            all_results.append(act_result)
            
            # OBSERVE
            observe_result = self.observe(act_result)
            
            if observe_result.get("success") and not observe_result.get("should_retry"):
                if not observe_result.get("next_steps"):
                    final_success = True
                    break
                current_situation = f"Última acción: {action_name}. Resultado: exitoso"
            elif observe_result.get("should_retry"):
                current_situation = f"Reintentando: {action_name}. Error previo: {act_result.get('error')}"
            else:
                print(f"⚠️ Deteniendo ciclo por fallo en: {action_name}")
                break
        
        # Guardar estado
        self._save_state()
        
        summary = {
            "iterations": iteration,
            "final_situation": current_situation,
            "results": all_results,
            "success": final_success,
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n" + "=" * 70)
        print(f"{'✅ CICLO COMPLETADO' if final_success else '⚠️ CICLO DETENIDO'}")
        print(f"   Iteraciones: {iteration}")
        print(f"   Resultados: {len(all_results)}")
        print("=" * 70)
        
        return summary

    # ========================================================================
    # MÉTODOS DE ANÁLISIS Y PLANIFICACIÓN
    # ========================================================================

    def analyze_pr(self, pr_number: int) -> PRAnalysis:
        """
        Analiza un Pull Request y determina su impacto en el proyecto.
        
        Args:
            pr_number: Número del PR a analizar
            
        Returns:
            PRAnalysis con el análisis completo
        """
        print(f"\n📋 Analizando PR #{pr_number}...")
        
        # Obtener información del PR via GitHub CLI
        try:
            result = subprocess.run(
                ["gh", "pr", "view", str(pr_number), "--json", 
                 "title,body,files,state,labels,headRefName"],
                capture_output=True, text=True, cwd=self.project_root
            )
            
            if result.returncode == 0:
                pr_data = json.loads(result.stdout)
            else:
                print(f"⚠️ Error obteniendo PR: {result.stderr}")
                pr_data = {}
        except Exception as e:
            print(f"⚠️ Error: {e}")
            pr_data = {}
        
        # Analizar contenido
        files = [f.get("path", "") for f in pr_data.get("files", [])]
        title = pr_data.get("title", f"PR #{pr_number}")
        body = pr_data.get("body", "")
        
        # Determinar sistemas afectados
        affected_systems = self._determine_affected_systems(files, body)
        
        # Determinar si es relevante para training (PR #87 pattern)
        training_relevance = any(
            keyword in (title + body).lower() 
            for keyword in ["training", "entrenamiento", "benchmark", "evaluación"]
        )
        
        # Calcular complejidad
        complexity = self._calculate_complexity(files, body)
        
        analysis = PRAnalysis(
            pr_number=pr_number,
            title=title,
            description=body[:500] if body else "",
            files_changed=files,
            impact_level=self._calculate_impact(files),
            integration_complexity=complexity,
            affected_systems=affected_systems,
            recommended_actions=self._recommend_pr_actions(files, body),
            training_relevance=training_relevance
        )
        
        if self.verbose:
            print(f"   ✅ Análisis completado:")
            print(f"      - Archivos: {len(files)}")
            print(f"      - Impacto: {analysis.impact_level}")
            print(f"      - Complejidad: {complexity}")
            print(f"      - Training relevante: {training_relevance}")
        
        return analysis

    def generate_implementation_plan(self, 
                                     pr_analysis: Optional[PRAnalysis] = None,
                                     goal: Optional[str] = None) -> List[DevelopmentTask]:
        """
        Genera un plan de implementación basado en análisis de PR o meta específica.
        
        Args:
            pr_analysis: Análisis de PR (opcional)
            goal: Meta a lograr (opcional)
            
        Returns:
            Lista de DevelopmentTask ordenadas
        """
        print("\n📝 Generando plan de implementación...")
        
        tasks = []
        
        if pr_analysis:
            # Plan basado en PR
            tasks.extend(self._generate_pr_tasks(pr_analysis))
        
        if goal:
            # Plan basado en meta
            tasks.extend(self._generate_goal_tasks(goal))
        
        # Resolver dependencias y ordenar
        tasks = self._resolve_dependencies(tasks)
        
        # Guardar en el estado
        self.tasks = tasks
        
        if self.verbose:
            print(f"   ✅ Plan generado: {len(tasks)} tareas")
            for i, task in enumerate(tasks[:5], 1):
                print(f"      {i}. [{task.priority.value}] {task.title}")
            if len(tasks) > 5:
                print(f"      ... y {len(tasks) - 5} tareas más")
        
        return tasks

    def execute_orchestrated_development(self, 
                                         start_phase: int = 0,
                                         end_phase: int = 15,
                                         interactive: bool = False) -> Dict:
        """
        Ejecuta el desarrollo orquestado por fases.
        
        Args:
            start_phase: Fase inicial
            end_phase: Fase final
            interactive: Si True, pide confirmación en cada fase
            
        Returns:
            Resumen de ejecución
        """
        print("\n" + "=" * 70)
        print("🚀 INICIANDO DESARROLLO ORQUESTADO")
        print(f"   Fases: {start_phase} → {end_phase}")
        print(f"   Auto-approve: {self.auto_approve}")
        print("=" * 70)
        
        results = {
            "phases_executed": [],
            "phases_completed": 0,
            "phases_failed": 0,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "success": False
        }
        
        current_phase = start_phase
        
        while current_phase <= end_phase:
            print(f"\n{'─' * 50}")
            print(f"📍 Fase {current_phase}")
            print(f"{'─' * 50}")
            
            if interactive and not self.auto_approve:
                response = input(f"¿Ejecutar fase {current_phase}? [S/n]: ").strip().lower()
                if response == 'n':
                    print("   ⏭️ Fase saltada por usuario")
                    current_phase += 1
                    continue
            
            # Ejecutar fase
            phase_result = self._execute_phase(current_phase)
            results["phases_executed"].append({
                "phase": current_phase,
                "result": phase_result
            })
            
            if phase_result.get("success"):
                results["phases_completed"] += 1
                print(f"   ✅ Fase {current_phase} completada")
            else:
                results["phases_failed"] += 1
                print(f"   ❌ Fase {current_phase} falló: {phase_result.get('error')}")
                
                if not self.auto_approve:
                    print("   ⚠️ Deteniendo ejecución por fallo")
                    break
            
            current_phase += 1
        
        results["end_time"] = datetime.now().isoformat()
        results["success"] = results["phases_failed"] == 0
        
        # Guardar estado
        self.project_state.current_phase = current_phase
        self.project_state.last_execution = results["end_time"]
        self._save_state()
        
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE EJECUCIÓN")
        print(f"   Fases ejecutadas: {len(results['phases_executed'])}")
        print(f"   Completadas: {results['phases_completed']}")
        print(f"   Fallidas: {results['phases_failed']}")
        print("=" * 70)
        
        return results

    # ========================================================================
    # INTEGRACIÓN CON SISTEMA DE TRAINING (PR #87)
    # ========================================================================

    def activate_training_mode(self, session_id: str = None) -> Dict:
        """
        Activa el modo de entrenamiento para el chatbot.
        
        Integra con el sistema de training_evaluation_system.py del PR #87.
        
        Args:
            session_id: ID de sesión de entrenamiento
            
        Returns:
            Estado del modo training
        """
        print("\n🎓 ACTIVANDO MODO ENTRENAMIENTO")
        
        session_id = session_id or f"gravity_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = {
            "session_id": session_id,
            "mode": "training",
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "capabilities": [
                "correction_detection",
                "response_reformulation",
                "approval_workflow",
                "knowledge_persistence"
            ]
        }
        
        # Intentar cargar el sistema de training
        try:
            training_module = self.project_root / "training_evaluation_system.py"
            if training_module.exists():
                result["training_system"] = "available"
                print("   ✅ Sistema de training disponible")
            else:
                result["training_system"] = "not_installed"
                result["suggestion"] = "Merge PR #87 para activar sistema completo"
                print("   ⚠️ Sistema de training no instalado (ver PR #87)")
        except Exception as e:
            result["training_system"] = "error"
            result["error"] = str(e)
        
        self.mode = AgentMode.TRAINING
        return result

    def run_benchmark(self, test_suite: str = "default") -> Dict:
        """
        Ejecuta benchmark del chatbot.
        
        Integra con benchmark_system.py del PR #87.
        
        Args:
            test_suite: Suite de tests a ejecutar
            
        Returns:
            Resultados del benchmark
        """
        print(f"\n📊 EJECUTANDO BENCHMARK: {test_suite}")
        
        result = {
            "suite": test_suite,
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "score": 0,
            "recommendations": []
        }
        
        # Intentar cargar el sistema de benchmark
        try:
            benchmark_module = self.project_root / "benchmark_system.py"
            if benchmark_module.exists():
                result["benchmark_system"] = "available"
                # TODO: Integrar con BenchmarkSystem class
                print("   ✅ Sistema de benchmark disponible")
            else:
                result["benchmark_system"] = "not_installed"
                result["suggestion"] = "Merge PR #87 para activar benchmarking"
                print("   ⚠️ Sistema de benchmark no instalado (ver PR #87)")
        except Exception as e:
            result["error"] = str(e)
        
        return result

    # ========================================================================
    # MÉTODOS DE ACCIÓN ESPECÍFICOS (_act_*)
    # ========================================================================

    def _act_analyze_pr(self, params: Dict) -> Dict:
        """Acción: Analizar PR"""
        pr_number = params.get("pr_number")
        if not pr_number:
            return {"success": False, "error": "pr_number requerido"}
        
        analysis = self.analyze_pr(pr_number)
        return {"success": True, "output": analysis.to_dict()}

    def _act_review_project_state(self, params: Dict) -> Dict:
        """Acción: Revisar estado del proyecto"""
        # Actualizar estado
        self._refresh_project_state()
        return {"success": True, "output": self.project_state.to_dict()}

    def _act_generate_implementation_plan(self, params: Dict) -> Dict:
        """Acción: Generar plan de implementación"""
        goal = params.get("goal")
        pr_number = params.get("pr_number")
        
        pr_analysis = None
        if pr_number:
            pr_analysis = self.analyze_pr(pr_number)
        
        tasks = self.generate_implementation_plan(pr_analysis, goal)
        return {
            "success": True, 
            "output": {
                "task_count": len(tasks),
                "tasks": [t.to_dict() for t in tasks[:10]]
            }
        }

    def _act_execute_phase(self, params: Dict) -> Dict:
        """Acción: Ejecutar una fase específica"""
        phase = params.get("phase", 0)
        result = self._execute_phase(phase)
        return result

    def _act_run_training_mode(self, params: Dict) -> Dict:
        """Acción: Activar modo training"""
        session_id = params.get("session_id")
        result = self.activate_training_mode(session_id)
        return {"success": True, "output": result}

    def _act_run_benchmark(self, params: Dict) -> Dict:
        """Acción: Ejecutar benchmark"""
        suite = params.get("suite", "default")
        result = self.run_benchmark(suite)
        return {"success": True, "output": result}

    def _act_coordinate_agents(self, params: Dict) -> Dict:
        """Acción: Coordinar con otros agentes"""
        target_agent = params.get("agent")
        task = params.get("task")
        
        return {
            "success": True,
            "output": {
                "coordinated": True,
                "agent": target_agent,
                "task": task,
                "status": "delegated"
            }
        }

    def _act_check_github_prs(self, params: Dict) -> Dict:
        """Acción: Verificar PRs en GitHub"""
        try:
            result = subprocess.run(
                ["gh", "pr", "list", "--json", "number,title,state"],
                capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                prs = json.loads(result.stdout)
                self.project_state.pending_prs = [p["number"] for p in prs if p["state"] == "OPEN"]
                return {"success": True, "output": {"prs": prs}}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _act_generate_report(self, params: Dict) -> Dict:
        """Acción: Generar reporte"""
        report_type = params.get("type", "summary")
        report = self._generate_report(report_type)
        return {"success": True, "output": report}

    def _act_sync_state(self, params: Dict) -> Dict:
        """Acción: Sincronizar estado"""
        self._refresh_project_state()
        self._save_state()
        return {"success": True, "output": {"synced": True}}

    def _act_initial_setup(self, params: Dict) -> Dict:
        """Acción: Configuración inicial del proyecto"""
        setup_steps = []
        
        # Verificar directorios
        self.consolidation_dir.mkdir(parents=True, exist_ok=True)
        setup_steps.append("consolidation_dir created")
        
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        setup_steps.append("logs_dir created")
        
        # Refrescar estado
        self._refresh_project_state()
        setup_steps.append("state refreshed")
        
        # Guardar estado
        self._save_state()
        setup_steps.append("state saved")
        
        return {
            "success": True,
            "output": {
                "setup_completed": True,
                "steps": setup_steps
            }
        }

    def _act_execute_pending_tasks(self, params: Dict) -> Dict:
        """Acción: Ejecutar tareas pendientes"""
        pending = [t for t in self.tasks if t.status == TaskStatus.PENDING]
        
        if not pending:
            return {"success": True, "output": {"message": "No hay tareas pendientes"}}
        
        executed = 0
        for task in pending[:5]:  # Máximo 5 a la vez
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.now().isoformat()
            # Simular ejecución
            task.status = TaskStatus.COMPLETED
            executed += 1
        
        return {
            "success": True,
            "output": {
                "tasks_executed": executed,
                "remaining": len(pending) - executed
            }
        }

    def _act_review_pending_prs(self, params: Dict) -> Dict:
        """Acción: Revisar PRs pendientes"""
        # Primero verificar PRs
        check_result = self._act_check_github_prs({})
        
        if not check_result.get("success"):
            return check_result
        
        prs = check_result.get("output", {}).get("prs", [])
        open_prs = [p for p in prs if p.get("state") == "OPEN"]
        
        analyses = []
        for pr in open_prs[:3]:  # Máximo 3 análisis
            analysis = self.analyze_pr(pr["number"])
            analyses.append(analysis.to_dict())
        
        return {
            "success": True,
            "output": {
                "total_open_prs": len(open_prs),
                "analyzed": len(analyses),
                "analyses": analyses
            }
        }

    def _act_prepare_training_integration(self, params: Dict) -> Dict:
        """Acción: Preparar integración del sistema de training (PR #87)"""
        preparation_steps = []
        issues = []
        
        # Verificar si los archivos del PR #87 existen
        training_files = [
            "training_evaluation_system.py",
            "benchmark_system.py",
            "training_integrated_bot.py"
        ]
        
        for file in training_files:
            file_path = self.project_root / file
            if file_path.exists():
                preparation_steps.append(f"✅ {file} existe")
            else:
                issues.append(f"❌ {file} no encontrado - requiere merge de PR #87")
        
        # Verificar directorios de datos
        data_dirs = [
            "data/training",
            "data/benchmarks"
        ]
        
        for dir_path in data_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                preparation_steps.append(f"✅ {dir_path} existe")
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                preparation_steps.append(f"📁 {dir_path} creado")
        
        return {
            "success": len(issues) == 0,
            "output": {
                "preparation_steps": preparation_steps,
                "issues": issues,
                "ready_for_training": len(issues) == 0,
                "suggestion": "Merge PR #87 para completar la integración" if issues else "Listo para training"
            }
        }

    # ========================================================================
    # MÉTODOS AUXILIARES
    # ========================================================================

    def _analyze_situation(self, situation: str, context: Dict) -> Dict:
        """Analiza la situación actual"""
        return {
            "summary": situation,
            "context": context,
            "project_state": self.project_state.to_dict(),
            "pending_tasks": len([t for t in self.tasks if t.status == TaskStatus.PENDING]),
            "active_mode": self.mode.value
        }

    def _generate_plan(self, analysis: Dict) -> List[Dict]:
        """Genera plan basado en análisis"""
        plan = []
        
        # Determinar acciones basadas en el estado
        if analysis.get("pending_tasks", 0) > 0:
            plan.append({"action": "execute_pending_tasks", "priority": "high"})
        
        if self.project_state.pending_prs:
            plan.append({"action": "review_pending_prs", "priority": "medium"})
        
        if not self.project_state.last_execution:
            plan.append({"action": "initial_setup", "priority": "critical"})
        
        return plan

    def _prioritize_next_steps(self, plan: List[Dict]) -> List[Dict]:
        """Prioriza los próximos pasos"""
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        return sorted(plan, key=lambda x: priority_order.get(x.get("priority", "low"), 3))

    def _calculate_confidence(self, analysis: Dict) -> float:
        """Calcula nivel de confianza del análisis"""
        confidence = 0.5
        if self.components_available:
            confidence += 0.2
        if self.project_state.last_execution:
            confidence += 0.1
        if not self.project_state.errors:
            confidence += 0.2
        return min(confidence, 1.0)

    def _identify_potential_issues(self, analysis: Dict) -> List[str]:
        """Identifica problemas potenciales"""
        issues = []
        if self.project_state.errors:
            issues.extend(self.project_state.errors)
        if not self.components_available:
            issues.append("Algunos componentes del orchestrator no están disponibles")
        return issues

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Genera recomendaciones"""
        recommendations = []
        
        if self.project_state.pending_prs:
            recommendations.append(f"Revisar {len(self.project_state.pending_prs)} PRs pendientes")
        
        if not self.auto_approve:
            recommendations.append("Considerar habilitar auto-approve para ejecución continua")
        
        if self.mode != AgentMode.ORCHESTRATION:
            recommendations.append(f"Modo actual: {self.mode.value}. Considerar cambiar según necesidad")
        
        return recommendations

    def _determine_next_steps(self, action_result: Dict) -> List[str]:
        """Determina próximos pasos basado en resultado"""
        steps = []
        output = action_result.get("output", {})
        
        if isinstance(output, dict):
            if output.get("prs"):
                steps.append("Analizar PRs pendientes")
            if output.get("task_count", 0) > 0:
                steps.append("Ejecutar tareas pendientes")
        
        return steps

    def _should_retry(self, action_result: Dict) -> bool:
        """Determina si debe reintentar"""
        error = action_result.get("error", "")
        # Reintentar en errores de red o temporales
        retry_keywords = ["timeout", "connection", "temporary", "network"]
        return any(k in error.lower() for k in retry_keywords)

    def _get_retry_strategy(self, action_result: Dict) -> Optional[str]:
        """Obtiene estrategia de reintento"""
        if self._should_retry(action_result):
            return "exponential_backoff"
        return None

    def _get_recovery_recommendations(self, action_result: Dict) -> List[str]:
        """Obtiene recomendaciones de recuperación"""
        error = action_result.get("error", "")
        recommendations = []
        
        if "permission" in error.lower():
            recommendations.append("Verificar permisos de acceso")
        if "not found" in error.lower():
            recommendations.append("Verificar que el recurso existe")
        if "connection" in error.lower():
            recommendations.append("Verificar conectividad de red")
        
        return recommendations or ["Revisar logs para más detalles"]

    def _execute_phase(self, phase: int) -> Dict:
        """Ejecuta una fase específica"""
        try:
            if self.state_manager:
                # Usar el orchestrator real
                from scripts.orchestrator.main_orchestrator import MainOrchestrator
                orchestrator = MainOrchestrator()
                success = orchestrator.execute_phase(phase)
                return {"success": success, "phase": phase}
            else:
                # Modo simulado
                print(f"   [Simulado] Ejecutando fase {phase}...")
                return {"success": True, "phase": phase, "simulated": True}
        except Exception as e:
            return {"success": False, "phase": phase, "error": str(e)}

    def _determine_affected_systems(self, files: List[str], description: str) -> List[str]:
        """Determina sistemas afectados por cambios"""
        systems = set()
        
        for f in files:
            if "api" in f.lower() or "server" in f.lower():
                systems.add("API")
            if "training" in f.lower() or "benchmark" in f.lower():
                systems.add("Training")
            if "whatsapp" in f.lower():
                systems.add("WhatsApp")
            if "n8n" in f.lower() or "workflow" in f.lower():
                systems.add("n8n")
            if "nextjs" in f.lower() or "tsx" in f.lower():
                systems.add("Frontend")
            if "mongo" in f.lower() or "db" in f.lower():
                systems.add("Database")
        
        return list(systems)

    def _calculate_complexity(self, files: List[str], description: str) -> str:
        """Calcula complejidad de integración"""
        file_count = len(files)
        
        if file_count > 20:
            return "high"
        elif file_count > 10:
            return "medium"
        else:
            return "low"

    def _calculate_impact(self, files: List[str]) -> str:
        """Calcula nivel de impacto"""
        critical_patterns = ["api_server", "main_orchestrator", "integracion"]
        
        for f in files:
            if any(p in f.lower() for p in critical_patterns):
                return "high"
        
        return "medium" if len(files) > 5 else "low"

    def _recommend_pr_actions(self, files: List[str], description: str) -> List[str]:
        """Recomienda acciones para el PR"""
        actions = ["review_code", "run_tests"]
        
        if any("test" in f.lower() for f in files):
            actions.append("validate_test_coverage")
        
        if any("doc" in f.lower() or ".md" in f.lower() for f in files):
            actions.append("review_documentation")
        
        if "training" in description.lower():
            actions.append("validate_training_integration")
        
        return actions

    def _generate_pr_tasks(self, pr_analysis: PRAnalysis) -> List[DevelopmentTask]:
        """Genera tareas basadas en análisis de PR"""
        tasks = []
        
        # Tarea de revisión
        tasks.append(DevelopmentTask(
            id=f"pr_{pr_analysis.pr_number}_review",
            title=f"Revisar PR #{pr_analysis.pr_number}",
            description=f"Revisar: {pr_analysis.title}",
            category="review",
            priority=TaskPriority.HIGH if pr_analysis.impact_level == "high" else TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            dependencies=[]
        ))
        
        # Tareas por sistema afectado
        for system in pr_analysis.affected_systems:
            tasks.append(DevelopmentTask(
                id=f"pr_{pr_analysis.pr_number}_{system.lower()}_validate",
                title=f"Validar integración {system}",
                description=f"Validar cambios en sistema {system}",
                category="validation",
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.PENDING,
                dependencies=[f"pr_{pr_analysis.pr_number}_review"]
            ))
        
        return tasks

    def _generate_goal_tasks(self, goal: str) -> List[DevelopmentTask]:
        """Genera tareas basadas en meta"""
        tasks = []
        
        # Tarea principal
        tasks.append(DevelopmentTask(
            id="goal_main",
            title=f"Objetivo: {goal[:50]}",
            description=goal,
            category="execution",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            dependencies=[]
        ))
        
        return tasks

    def _resolve_dependencies(self, tasks: List[DevelopmentTask]) -> List[DevelopmentTask]:
        """Resuelve y ordena tareas por dependencias"""
        # Ordenar por prioridad y dependencias
        priority_order = {TaskPriority.CRITICAL: 0, TaskPriority.HIGH: 1, 
                         TaskPriority.MEDIUM: 2, TaskPriority.LOW: 3}
        
        return sorted(tasks, key=lambda t: (
            len(t.dependencies),
            priority_order.get(t.priority, 3)
        ))

    def _refresh_project_state(self):
        """Actualiza el estado del proyecto"""
        # Verificar estado de Git
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                current_branch = result.stdout.strip()
                if current_branch not in self.project_state.active_branches:
                    self.project_state.active_branches.append(current_branch)
        except Exception:
            pass

    def _generate_report(self, report_type: str) -> Dict:
        """Genera un reporte del estado"""
        return {
            "type": report_type,
            "timestamp": datetime.now().isoformat(),
            "project_state": self.project_state.to_dict(),
            "task_summary": {
                "total": len(self.tasks),
                "pending": len([t for t in self.tasks if t.status == TaskStatus.PENDING]),
                "completed": len([t for t in self.tasks if t.status == TaskStatus.COMPLETED]),
                "failed": len([t for t in self.tasks if t.status == TaskStatus.FAILED])
            },
            "execution_history_count": len(self.execution_history),
            "agent_mode": self.mode.value
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Interfaz de línea de comandos para el Gravity Orchestrator Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🌌 Gravity Orchestrator Agent - Orquesta el desarrollo automatizado"
    )
    
    parser.add_argument(
        "--mode",
        choices=["orchestration", "planning", "execution", "training", "evaluation", "monitoring"],
        default="orchestration",
        help="Modo de operación del agente"
    )
    
    parser.add_argument(
        "--analyze-pr",
        type=int,
        metavar="PR_NUMBER",
        help="Analizar un Pull Request específico"
    )
    
    parser.add_argument(
        "--execute-phases",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="Ejecutar fases desde START hasta END"
    )
    
    parser.add_argument(
        "--react",
        metavar="SITUATION",
        help="Ejecutar ciclo ReAct con la situación especificada"
    )
    
    parser.add_argument(
        "--training",
        action="store_true",
        help="Activar modo de entrenamiento"
    )
    
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Ejecutar benchmark del sistema"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Modo interactivo (pedir confirmaciones)"
    )
    
    parser.add_argument(
        "--no-auto-approve",
        action="store_true",
        help="Desactivar auto-aprobación"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Modo silencioso (menos output)"
    )
    
    args = parser.parse_args()
    
    # Inicializar agente
    mode = AgentMode(args.mode)
    agent = GravityOrchestratorAgent(
        mode=mode,
        auto_approve=not args.no_auto_approve,
        verbose=not args.quiet
    )
    
    # Ejecutar acción solicitada
    if args.analyze_pr:
        analysis = agent.analyze_pr(args.analyze_pr)
        print("\n📋 Análisis del PR:")
        print(json.dumps(analysis.to_dict(), indent=2, ensure_ascii=False))
        
    elif args.execute_phases:
        start, end = args.execute_phases
        result = agent.execute_orchestrated_development(
            start_phase=start,
            end_phase=end,
            interactive=args.interactive
        )
        print("\n📊 Resultado:")
        print(json.dumps(result, indent=2, default=str))
        
    elif args.react:
        result = agent.react_cycle(args.react)
        print("\n📊 Resultado del ciclo ReAct:")
        print(json.dumps(result, indent=2, default=str))
        
    elif args.training:
        result = agent.activate_training_mode()
        print("\n🎓 Modo Training:")
        print(json.dumps(result, indent=2))
        
    elif args.benchmark:
        result = agent.run_benchmark()
        print("\n📊 Benchmark:")
        print(json.dumps(result, indent=2))
        
    else:
        # Modo interactivo por defecto
        print("\n🌌 Gravity Orchestrator Agent listo.")
        print("   Use --help para ver opciones disponibles")
        print("\n   Ejemplo de uso:")
        print("   python gravity_orchestrator_agent.py --analyze-pr 87")
        print("   python gravity_orchestrator_agent.py --react 'Revisar estado del proyecto'")
        print("   python gravity_orchestrator_agent.py --execute-phases 0 5")


if __name__ == "__main__":
    main()

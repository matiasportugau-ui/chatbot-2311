#!/usr/bin/env python3
"""
Gravity Agent - Especialista en Interpretación y Orquestación del Desarrollo Automatizado

El Gravity Agent actúa como el punto central de gravedad del proyecto, interpretando
el estado del sistema y orquestando el desarrollo automatizado de manera inteligente.

Características principales:
- Interpretación profunda del estado del proyecto
- Orquestación automática de fases y tareas
- Coordinación de múltiples agentes especializados
- Análisis de dependencias y optimización de flujos
- Toma de decisiones inteligente basada en contexto
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import subprocess

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    from scripts.orchestrator.agent_interface import AgentInterface, AgentCoordinator
except (ImportError, NameError) as e:
    print(f"Warning: Could not import agent_interface: {e}")
    AgentInterface = None
    AgentCoordinator = None

try:
    from scripts.orchestrator.main_orchestrator import MainOrchestrator
except (ImportError, NameError) as e:
    print(f"Warning: Could not import main_orchestrator: {e}")
    MainOrchestrator = None

try:
    from scripts.orchestrator.state_manager import StateManager
except (ImportError, NameError) as e:
    print(f"Warning: Could not import state_manager: {e}")
    StateManager = None

try:
    from scripts.orchestrator.dependency_resolver import DependencyResolver
except (ImportError, NameError) as e:
    print(f"Warning: Could not import dependency_resolver: {e}")
    DependencyResolver = None

try:
    from scripts.orchestrator.planning_agent import PlanningAgent
except (ImportError, NameError) as e:
    print(f"Warning: Could not import planning_agent: {e}")
    PlanningAgent = None

try:
    from scripts.orchestrator.github_integration import GitHubIntegration
except (ImportError, NameError) as e:
    print(f"Warning: Could not import github_integration: {e}")
    GitHubIntegration = None


@dataclass
class ProjectState:
    """Estado actual del proyecto"""
    current_phase: int
    overall_status: str
    phases_status: Dict[int, str]
    active_tasks: List[str]
    blockers: List[str]
    dependencies_met: bool
    last_update: str


@dataclass
class AgentTask:
    """Tarea para delegar a un agente"""
    task_id: str
    agent_type: str
    task_config: Dict[str, Any]
    priority: int
    dependencies: List[str]


class GravityAgent:
    """
    Gravity Agent - Orquestador Central del Desarrollo Automatizado
    
    Este agente actúa como el núcleo gravitacional del proyecto, interpretando
    el estado del sistema y coordinando todos los aspectos del desarrollo automatizado.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """Inicializar el Gravity Agent"""
        self.agent_name = "GravityAgent"
        self.agent_type = "GravityAgent"
        self.workspace_root = Path(__file__).parent.parent
        
        # Cargar configuración
        if config_file:
            self.config = self._load_config(config_file)
        else:
            self.config = self._default_config()
        
        # Inicializar componentes del sistema
        self.state_manager = StateManager() if StateManager else None
        self.orchestrator = None
        self.agent_coordinator = AgentCoordinator() if AgentCoordinator else None
        self.planning_agent = None
        
        # Estado interno
        self.project_state: Optional[ProjectState] = None
        self.task_queue: List[AgentTask] = []
        self.execution_history: List[Dict[str, Any]] = []
        
        # Directorios de trabajo
        self.output_dir = self.workspace_root / "consolidation" / "gravity_agent"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar componentes
        self._initialize_components()
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Cargar configuración desde archivo"""
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self._default_config()
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            "auto_approve": True,
            "execution_mode": "automated",
            "max_retries": 3,
            "retry_delay": 60,
            "parallel_execution": True,
            "monitor_interval": 30,
            "github": {
                "enabled": True,
                "repo": "chatbot-2311",
                "owner": "matiasportugau-ui"
            },
            "agents": {
                "planning": True,
                "repository": True,
                "integration": True,
                "quotation": True
            }
        }
    
    def _initialize_components(self):
        """Inicializar componentes del sistema"""
        print(f"[{self.agent_name}] Inicializando componentes...")
        
        # Inicializar orchestrator
        if MainOrchestrator:
            try:
                config_file = self.workspace_root / "scripts" / "orchestrator" / "config" / "orchestrator_config.json"
                self.orchestrator = MainOrchestrator(str(config_file))
                print(f"[{self.agent_name}] Orchestrator inicializado")
            except Exception as e:
                print(f"[{self.agent_name}] Warning: No se pudo inicializar orchestrator: {e}")
        
        # Inicializar planning agent
        if PlanningAgent:
            try:
                self.planning_agent = PlanningAgent(
                    state_manager=self.state_manager
                )
                print(f"[{self.agent_name}] Planning Agent inicializado")
            except Exception as e:
                print(f"[{self.agent_name}] Warning: No se pudo inicializar planning agent: {e}")
        
        print(f"[{self.agent_name}] Componentes inicializados")
    
    def interpret_project_state(self) -> ProjectState:
        """
        Interpretar el estado actual del proyecto
        
        Analiza el estado del proyecto desde múltiples fuentes:
        - Estado del orchestrator
        - Estado de las fases
        - Tareas pendientes
        - Bloqueadores
        - Dependencias
        """
        print(f"[{self.agent_name}] Interpretando estado del proyecto...")
        
        # Obtener estado del orchestrator
        current_phase = 0
        overall_status = "unknown"
        phases_status = {}
        
        if self.state_manager:
            current_phase = self.state_manager.get_current_phase()
            overall_status = self.state_manager.get_overall_status()
            
            # Obtener estado de todas las fases
            for phase_num in range(16):
                phases_status[phase_num] = self.state_manager.get_phase_status(phase_num)
        
        # Analizar tareas activas
        active_tasks = self._get_active_tasks()
        
        # Identificar bloqueadores
        blockers = self._identify_blockers()
        
        # Verificar dependencias
        dependencies_met = self._check_dependencies()
        
        # Crear estado del proyecto
        self.project_state = ProjectState(
            current_phase=current_phase,
            overall_status=overall_status,
            phases_status=phases_status,
            active_tasks=active_tasks,
            blockers=blockers,
            dependencies_met=dependencies_met,
            last_update=datetime.utcnow().isoformat()
        )
        
        # Guardar estado interpretado
        self._save_project_state()
        
        print(f"[{self.agent_name}] Estado interpretado:")
        print(f"  - Fase actual: {current_phase}")
        print(f"  - Estado general: {overall_status}")
        print(f"  - Tareas activas: {len(active_tasks)}")
        print(f"  - Bloqueadores: {len(blockers)}")
        print(f"  - Dependencias cumplidas: {dependencies_met}")
        
        return self.project_state
    
    def _get_active_tasks(self) -> List[str]:
        """Obtener lista de tareas activas"""
        active_tasks = []
        
        # Buscar tareas en el directorio de tareas
        tasks_dir = self.workspace_root / "consolidation" / "tasks"
        if tasks_dir.exists():
            for task_file in tasks_dir.glob("*_request.json"):
                try:
                    with open(task_file, 'r') as f:
                        task_data = json.load(f)
                        if task_data.get("status") == "pending":
                            active_tasks.append(task_data.get("task_id", "unknown"))
                except Exception:
                    pass
        
        return active_tasks
    
    def _identify_blockers(self) -> List[str]:
        """Identificar bloqueadores del proyecto"""
        blockers = []
        
        # Verificar si hay fases fallidas
        if self.state_manager:
            for phase_num in range(16):
                status = self.state_manager.get_phase_status(phase_num)
                if status == "failed":
                    blockers.append(f"Phase {phase_num} failed")
        
        # Verificar dependencias no cumplidas
        if self.orchestrator:
            for phase_num in range(16):
                can_execute, missing = self.orchestrator.dependency_resolver.check_dependencies(phase_num)
                if not can_execute and missing:
                    blockers.append(f"Phase {phase_num} missing dependencies: {missing}")
        
        return blockers
    
    def _check_dependencies(self) -> bool:
        """Verificar si las dependencias están cumplidas"""
        if not self.orchestrator:
            return True
        
        current_phase = self.state_manager.get_current_phase() if self.state_manager else 0
        can_execute, _ = self.orchestrator.dependency_resolver.check_dependencies(current_phase)
        return can_execute
    
    def _save_project_state(self):
        """Guardar estado del proyecto"""
        if not self.project_state:
            return
        
        state_file = self.output_dir / "project_state.json"
        with open(state_file, 'w') as f:
            json.dump(asdict(self.project_state), f, indent=2)
    
    def orchestrate_development(self, target_phase: Optional[int] = None) -> Dict[str, Any]:
        """
        Orquestar el desarrollo automatizado del proyecto
        
        Coordina la ejecución de fases, delegación de tareas a agentes,
        y gestión del flujo de desarrollo.
        """
        print(f"\n{'='*80}")
        print(f"[{self.agent_name}] Iniciando Orquestación del Desarrollo Automatizado")
        print(f"{'='*80}\n")
        
        # Interpretar estado actual
        project_state = self.interpret_project_state()
        
        # Determinar fase objetivo
        if target_phase is None:
            target_phase = project_state.current_phase
        
        # Planificar ejecución
        execution_plan = self._create_execution_plan(target_phase)
        
        # Ejecutar plan
        results = self._execute_plan(execution_plan)
        
        # Generar reporte
        report = self._generate_execution_report(results)
        
        print(f"\n{'='*80}")
        print(f"[{self.agent_name}] Orquestación Completada")
        print(f"{'='*80}\n")
        
        return report
    
    def _create_execution_plan(self, target_phase: int) -> Dict[str, Any]:
        """Crear plan de ejecución"""
        print(f"[{self.agent_name}] Creando plan de ejecución hasta fase {target_phase}...")
        
        plan = {
            "target_phase": target_phase,
            "current_phase": self.project_state.current_phase if self.project_state else 0,
            "phases_to_execute": [],
            "tasks_to_delegate": [],
            "estimated_time": 0
        }
        
        # Determinar fases a ejecutar
        current = self.project_state.current_phase if self.project_state else 0
        for phase in range(current, target_phase + 1):
            status = self.project_state.phases_status.get(phase, "pending") if self.project_state else "pending"
            if status in ["pending", "failed"]:
                plan["phases_to_execute"].append(phase)
        
        # Identificar tareas a delegar
        if self.agent_coordinator:
            # Analizar qué agentes necesitan ser activados
            for phase in plan["phases_to_execute"]:
                tasks = self._get_tasks_for_phase(phase)
                plan["tasks_to_delegate"].extend(tasks)
        
        print(f"[{self.agent_name}] Plan creado:")
        print(f"  - Fases a ejecutar: {plan['phases_to_execute']}")
        print(f"  - Tareas a delegar: {len(plan['tasks_to_delegate'])}")
        
        return plan
    
    def _get_tasks_for_phase(self, phase: int) -> List[AgentTask]:
        """Obtener tareas para una fase específica"""
        tasks = []
        
        # Mapeo de fases a tipos de agentes
        phase_agent_mapping = {
            0: ["PlanningAgent"],
            1: ["RepositoryAgent", "IntegrationAgent"],
            2: ["PlanningAgent", "IntegrationAgent"],
            3: ["QuotationAgent", "IntegrationAgent"],
            # Agregar más mapeos según sea necesario
        }
        
        agent_types = phase_agent_mapping.get(phase, [])
        
        for agent_type in agent_types:
            task = AgentTask(
                task_id=f"phase_{phase}_{agent_type.lower()}",
                agent_type=agent_type,
                task_config={"phase": phase, "type": "phase_execution"},
                priority=phase,
                dependencies=[]
            )
            tasks.append(task)
        
        return tasks
    
    def _execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar el plan de desarrollo"""
        print(f"[{self.agent_name}] Ejecutando plan...")
        
        results = {
            "phases_executed": [],
            "phases_failed": [],
            "tasks_delegated": [],
            "tasks_completed": [],
            "start_time": datetime.utcnow().isoformat()
        }
        
        # Ejecutar fases
        if self.orchestrator:
            for phase in plan["phases_to_execute"]:
                print(f"\n[{self.agent_name}] Ejecutando fase {phase}...")
                try:
                    success = self.orchestrator.execute_phase(phase)
                    if success:
                        results["phases_executed"].append(phase)
                        print(f"[{self.agent_name}] Fase {phase} completada exitosamente")
                    else:
                        results["phases_failed"].append(phase)
                        print(f"[{self.agent_name}] Fase {phase} falló")
                except Exception as e:
                    results["phases_failed"].append(phase)
                    print(f"[{self.agent_name}] Error ejecutando fase {phase}: {e}")
        
        # Delegar tareas a agentes
        if self.agent_coordinator:
            for task in plan["tasks_to_delegate"]:
                print(f"[{self.agent_name}] Delegando tarea {task.task_id} a {task.agent_type}...")
                try:
                    request_file = self.agent_coordinator.delegate_task(
                        task.agent_type,
                        task.task_id,
                        task.task_config
                    )
                    results["tasks_delegated"].append({
                        "task_id": task.task_id,
                        "agent_type": task.agent_type,
                        "request_file": request_file
                    })
                except Exception as e:
                    print(f"[{self.agent_name}] Error delegando tarea {task.task_id}: {e}")
        
        results["end_time"] = datetime.utcnow().isoformat()
        results["duration_seconds"] = (
            datetime.fromisoformat(results["end_time"]) - 
            datetime.fromisoformat(results["start_time"])
        ).total_seconds()
        
        return results
    
    def _generate_execution_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generar reporte de ejecución"""
        report = {
            "agent": self.agent_name,
            "execution_id": self.state_manager.get_execution_id() if self.state_manager else "unknown",
            "timestamp": datetime.utcnow().isoformat(),
            "results": results,
            "project_state": asdict(self.project_state) if self.project_state else None,
            "summary": {
                "phases_executed": len(results.get("phases_executed", [])),
                "phases_failed": len(results.get("phases_failed", [])),
                "tasks_delegated": len(results.get("tasks_delegated", [])),
                "success_rate": (
                    len(results.get("phases_executed", [])) / 
                    max(len(results.get("phases_executed", [])) + len(results.get("phases_failed", [])), 1)
                ) * 100
            }
        }
        
        # Guardar reporte
        report_file = self.output_dir / f"execution_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"[{self.agent_name}] Reporte guardado en: {report_file}")
        
        return report
    
    def analyze_pr(self, pr_number: Optional[int] = None, pr_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Analizar un Pull Request y generar plan de implementación
        
        Utiliza el Planning Agent para analizar PRs y generar planes de implementación.
        """
        print(f"[{self.agent_name}] Analizando PR #{pr_number if pr_number else 'local'}...")
        
        if not self.planning_agent:
            return {"error": "Planning Agent no disponible"}
        
        try:
            # Si se proporciona URL, extraer número de PR
            if pr_url and not pr_number:
                # Extraer número de PR de la URL
                # Ejemplo: https://github.com/owner/repo/pull/87
                parts = pr_url.rstrip('/').split('/')
                if 'pull' in parts:
                    idx = parts.index('pull')
                    if idx + 1 < len(parts):
                        pr_number = int(parts[idx + 1])
            
            # Analizar PR
            result = self.planning_agent.analyze_pr(pr_number)
            
            # Si hay un plan generado, integrarlo con la orquestación
            if "plan" in result:
                self._integrate_pr_plan(result["plan"])
            
            return result
            
        except Exception as e:
            return {"error": f"Error analizando PR: {e}"}
    
    def _integrate_pr_plan(self, plan: Dict[str, Any]):
        """Integrar plan de PR con el sistema de orquestación"""
        print(f"[{self.agent_name}] Integrando plan de PR con orquestación...")
        
        # Aquí se podría integrar el plan del PR con las fases del orchestrator
        # Por ahora, solo guardamos el plan
        plan_file = self.output_dir / "pr_plan.json"
        with open(plan_file, 'w') as f:
            json.dump(plan, f, indent=2)
        
        print(f"[{self.agent_name}] Plan de PR guardado en: {plan_file}")
    
    def monitor_project(self, interval: int = 30) -> Dict[str, Any]:
        """
        Monitorear el estado del proyecto continuamente
        
        Ejecuta un ciclo de monitoreo que interpreta el estado y toma acciones
        cuando es necesario.
        """
        print(f"[{self.agent_name}] Iniciando monitoreo del proyecto (intervalo: {interval}s)...")
        
        monitoring_results = {
            "start_time": datetime.utcnow().isoformat(),
            "checks": [],
            "actions_taken": []
        }
        
        try:
            # Interpretar estado
            state = self.interpret_project_state()
            
            # Verificar si hay bloqueadores
            if state.blockers:
                print(f"[{self.agent_name}] Bloqueadores detectados: {state.blockers}")
                # Intentar resolver bloqueadores
                for blocker in state.blockers:
                    action = self._resolve_blocker(blocker)
                    if action:
                        monitoring_results["actions_taken"].append(action)
            
            # Verificar si hay tareas pendientes
            if state.active_tasks:
                print(f"[{self.agent_name}] Tareas activas detectadas: {len(state.active_tasks)}")
            
            # Verificar si se puede avanzar a la siguiente fase
            if state.dependencies_met and state.current_phase < 15:
                print(f"[{self.agent_name}] Dependencias cumplidas, listo para avanzar")
            
            monitoring_results["checks"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "state": asdict(state)
            })
            
        except Exception as e:
            print(f"[{self.agent_name}] Error en monitoreo: {e}")
            monitoring_results["error"] = str(e)
        
        monitoring_results["end_time"] = datetime.utcnow().isoformat()
        
        return monitoring_results
    
    def _resolve_blocker(self, blocker: str) -> Optional[Dict[str, Any]]:
        """Intentar resolver un bloqueador"""
        print(f"[{self.agent_name}] Intentando resolver bloqueador: {blocker}")
        
        # Lógica para resolver diferentes tipos de bloqueadores
        # Por ahora, solo registramos el intento
        return {
            "blocker": blocker,
            "action": "logged",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_status_report(self) -> Dict[str, Any]:
        """Obtener reporte de estado completo"""
        state = self.interpret_project_state()
        
        report = {
            "agent": self.agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "project_state": asdict(state) if state else None,
            "config": self.config,
            "components": {
                "orchestrator": self.orchestrator is not None,
                "planning_agent": self.planning_agent is not None,
                "agent_coordinator": self.agent_coordinator is not None,
                "state_manager": self.state_manager is not None
            }
        }
        
        return report


def main():
    """Función principal para ejecutar el Gravity Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gravity Agent - Orquestador Central del Desarrollo Automatizado")
    parser.add_argument("--mode", choices=["orchestrate", "analyze-pr", "monitor", "status"], 
                       default="orchestrate", help="Modo de operación")
    parser.add_argument("--phase", type=int, help="Fase objetivo para orquestación")
    parser.add_argument("--pr-number", type=int, help="Número de PR a analizar")
    parser.add_argument("--pr-url", type=str, help="URL del PR a analizar")
    parser.add_argument("--config", type=str, help="Archivo de configuración")
    parser.add_argument("--interval", type=int, default=30, help="Intervalo de monitoreo en segundos")
    
    args = parser.parse_args()
    
    # Crear agente
    agent = GravityAgent(config_file=args.config)
    
    # Ejecutar según modo
    if args.mode == "orchestrate":
        result = agent.orchestrate_development(target_phase=args.phase)
        print("\n" + json.dumps(result, indent=2))
    
    elif args.mode == "analyze-pr":
        result = agent.analyze_pr(pr_number=args.pr_number, pr_url=args.pr_url)
        print("\n" + json.dumps(result, indent=2))
    
    elif args.mode == "monitor":
        result = agent.monitor_project(interval=args.interval)
        print("\n" + json.dumps(result, indent=2))
    
    elif args.mode == "status":
        result = agent.get_status_report()
        print("\n" + json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

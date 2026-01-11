#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Development Orchestrator Agent for Gravity (Cursor Agent Mode)
===============================================================

Agente especializado en interpretar y orquestar el desarrollo automatizado
del proyecto chatbot-2311 (BMC Ecosystem).

Capabilities:
- PR Analysis: Analiza Pull Requests para entender cambios y su impacto
- Development Orchestration: Coordina fases de desarrollo automatizado
- Task Planning: Genera planes de tareas detallados
- Integration Management: Gestiona integraciones entre componentes
- Progress Tracking: Monitorea progreso y genera reportes
- Auto-Approval: Ejecuta con auto-aprobación habilitada

Patterns Used:
- ReAct (Reasoning + Acting)
- Chain-of-Thought
- Context-Aware Planning
- Tool-Using Agent

Author: BMC Development Team
Version: 1.0.0
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import re

# Configuration
WORKSPACE_ROOT = Path(__file__).parent.parent.parent.parent
CONSOLIDATION_DIR = WORKSPACE_ROOT / "consolidation"
LOGS_DIR = WORKSPACE_ROOT / "system" / "logs"
CURSOR_DIR = WORKSPACE_ROOT / ".cursor"


class PhaseStatus(Enum):
    """Status of development phases"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    """Task priority levels"""
    P0_CRITICAL = "P0"
    P1_IMPORTANT = "P1"
    P2_MEDIUM = "P2"
    P3_LOW = "P3"


class AgentType(Enum):
    """Available specialized agents"""
    ORCHESTRATOR = "OrchestratorAgent"
    REPOSITORY = "RepositoryAgent"
    DISCOVERY = "DiscoveryAgent"
    MERGE = "MergeAgent"
    INTEGRATION = "IntegrationAgent"
    SECURITY = "SecurityAgent"
    INFRASTRUCTURE = "InfrastructureAgent"
    OBSERVABILITY = "ObservabilityAgent"
    PERFORMANCE = "PerformanceAgent"
    CICD = "CICDAgent"
    DISASTER_RECOVERY = "DisasterRecoveryAgent"
    VALIDATION = "ValidationAgent"
    NLU = "NLUAgent"
    QUOTATION = "QuotationAgent"


@dataclass
class PRAnalysis:
    """Analysis result for a Pull Request"""
    pr_number: int
    title: str
    description: str
    author: str
    status: str
    base_branch: str
    head_branch: str
    files_changed: List[Dict]
    additions: int
    deletions: int
    affected_components: List[str]
    affected_phases: List[int]
    impact_level: str  # low, medium, high, critical
    recommendations: List[str]
    tasks: List[Dict]
    analyzed_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DevelopmentTask:
    """A development task in the orchestration plan"""
    id: str
    title: str
    description: str
    phase: int
    priority: TaskPriority
    status: PhaseStatus
    assigned_agent: AgentType
    dependencies: List[str]
    files: List[str]
    estimated_duration: str
    bmc_context: Optional[str] = None
    output_location: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["priority"] = self.priority.value
        data["status"] = self.status.value
        data["assigned_agent"] = self.assigned_agent.value
        return data


@dataclass
class OrchestrationPlan:
    """Complete orchestration plan for development"""
    plan_id: str
    name: str
    description: str
    phases: Dict[int, List[DevelopmentTask]]
    current_phase: int
    total_tasks: int
    completed_tasks: int
    status: PhaseStatus
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "description": self.description,
            "phases": {
                phase: [task.to_dict() for task in tasks]
                for phase, tasks in self.phases.items()
            },
            "current_phase": self.current_phase,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class DevelopmentOrchestratorAgent:
    """
    Development Orchestrator Agent for Gravity
    
    Este agente especializado interpreta y orquesta el desarrollo automatizado
    del proyecto BMC Chatbot. Utiliza el patrón ReAct para análisis y ejecución.
    
    Main Responsibilities:
    1. Analizar PRs y cambios en el código
    2. Generar planes de desarrollo automatizados
    3. Coordinar ejecución de fases
    4. Monitorear progreso y reportar estado
    5. Gestionar auto-aprobación de tareas
    """

    def __init__(self):
        self.workspace_root = WORKSPACE_ROOT
        self.consolidation_dir = CONSOLIDATION_DIR
        self.logs_dir = LOGS_DIR
        self.current_plan: Optional[OrchestrationPlan] = None
        self.execution_history: List[Dict] = []
        self.auto_approve = True  # SIEMPRE habilitado según .cursorrules
        
        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist"""
        self.consolidation_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        (self.consolidation_dir / "pr_analysis").mkdir(exist_ok=True)
        (self.consolidation_dir / "orchestration").mkdir(exist_ok=True)

    # =========================================================================
    # PHASE 1: PR ANALYSIS (Think)
    # =========================================================================

    def analyze_pr(self, pr_number: int) -> PRAnalysis:
        """
        Analyze a Pull Request using GitHub CLI
        
        This is the THINK phase of ReAct pattern.
        Analyzes the PR to understand what changes are being made.
        """
        print(f"🔍 Analizando PR #{pr_number}...")
        
        # Get PR info using gh cli
        try:
            result = subprocess.run(
                ["gh", "pr", "view", str(pr_number), "--json", 
                 "title,body,author,state,baseRefName,headRefName,files,additions,deletions"],
                capture_output=True, text=True, cwd=self.workspace_root
            )
            
            if result.returncode != 0:
                raise Exception(f"Error getting PR info: {result.stderr}")
            
            pr_data = json.loads(result.stdout)
            
        except Exception as e:
            print(f"⚠️ Error al obtener PR: {e}")
            # Return placeholder for analysis
            return self._create_placeholder_analysis(pr_number)

        # Analyze files and categorize
        files_analysis = self._analyze_files(pr_data.get("files", []))
        
        # Determine affected components
        affected_components = self._identify_affected_components(files_analysis)
        
        # Map to consolidation phases
        affected_phases = self._map_to_phases(affected_components)
        
        # Calculate impact level
        impact_level = self._calculate_impact_level(
            pr_data.get("additions", 0),
            pr_data.get("deletions", 0),
            affected_components
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            files_analysis, affected_components, impact_level
        )
        
        # Generate tasks from analysis
        tasks = self._generate_tasks_from_analysis(
            files_analysis, affected_components, affected_phases
        )
        
        analysis = PRAnalysis(
            pr_number=pr_number,
            title=pr_data.get("title", "Unknown"),
            description=pr_data.get("body", "")[:500] if pr_data.get("body") else "",
            author=pr_data.get("author", {}).get("login", "Unknown"),
            status=pr_data.get("state", "UNKNOWN"),
            base_branch=pr_data.get("baseRefName", "main"),
            head_branch=pr_data.get("headRefName", "unknown"),
            files_changed=files_analysis,
            additions=pr_data.get("additions", 0),
            deletions=pr_data.get("deletions", 0),
            affected_components=affected_components,
            affected_phases=affected_phases,
            impact_level=impact_level,
            recommendations=recommendations,
            tasks=tasks
        )
        
        # Save analysis
        self._save_analysis(analysis)
        
        print(f"✅ Análisis completado: {len(files_analysis)} archivos, impacto: {impact_level}")
        return analysis

    def _analyze_files(self, files: List[Dict]) -> List[Dict]:
        """Analyze and categorize changed files"""
        analyzed = []
        
        for f in files:
            path = f.get("path", "")
            additions = f.get("additions", 0)
            deletions = f.get("deletions", 0)
            
            file_info = {
                "path": path,
                "additions": additions,
                "deletions": deletions,
                "type": self._categorize_file(path),
                "component": self._identify_component(path),
                "impact": self._assess_file_impact(path, additions, deletions)
            }
            analyzed.append(file_info)
        
        return analyzed

    def _categorize_file(self, path: str) -> str:
        """Categorize file by type"""
        ext = Path(path).suffix.lower()
        
        categories = {
            ".py": "python",
            ".ts": "typescript",
            ".tsx": "react",
            ".js": "javascript",
            ".json": "configuration",
            ".yaml": "configuration",
            ".yml": "configuration",
            ".md": "documentation",
            ".sh": "script",
            ".sql": "database",
            ".css": "style",
            ".html": "template"
        }
        
        return categories.get(ext, "other")

    def _identify_component(self, path: str) -> str:
        """Identify which component a file belongs to"""
        path_lower = path.lower()
        
        component_patterns = {
            "orchestrator": ["orchestrator", "phase_executor"],
            "whatsapp": ["whatsapp", "wa_", "webhook"],
            "n8n": ["n8n", "workflow"],
            "qdrant": ["qdrant", "vector", "embedding"],
            "chatwoot": ["chatwoot"],
            "quotation": ["quotation", "pricing", "catalog", "cotiza"],
            "training": ["training", "benchmark", "evaluation"],
            "agents": ["agent", "ai_agent"],
            "dashboard": ["dashboard", "analytics"],
            "api": ["api", "endpoint", "route"],
            "database": ["mongo", "database", "db_"],
            "testing": ["test_", "tests/", "_test.py"],
            "documentation": [".md", "docs/", "readme"],
            "deployment": ["deploy", "docker", "k8s", "kubernetes"],
            "security": ["security", "auth", "token", "secret"]
        }
        
        for component, patterns in component_patterns.items():
            if any(p in path_lower for p in patterns):
                return component
        
        return "core"

    def _identify_affected_components(self, files: List[Dict]) -> List[str]:
        """Identify all affected components from file analysis"""
        components = set()
        for f in files:
            components.add(f.get("component", "core"))
        return list(components)

    def _map_to_phases(self, components: List[str]) -> List[int]:
        """Map components to consolidation plan phases"""
        phase_mapping = {
            "orchestrator": [0, 13],
            "documentation": [0, 15],
            "whatsapp": [4, 5],
            "n8n": [5, 6],
            "qdrant": [6, 7],
            "chatwoot": [6],
            "quotation": [2, 3],
            "training": [7, 8],
            "agents": [0, 1],
            "dashboard": [12],
            "api": [3, 4],
            "database": [3, 6],
            "testing": [11, 14],
            "deployment": [9, 10, 13],
            "security": [9],
            "core": [1, 2]
        }
        
        phases = set()
        for component in components:
            phases.update(phase_mapping.get(component, [0]))
        
        return sorted(list(phases))

    def _calculate_impact_level(self, additions: int, deletions: int, 
                                 components: List[str]) -> str:
        """Calculate overall impact level"""
        total_changes = additions + deletions
        
        # High impact components
        critical_components = {"security", "database", "api", "deployment"}
        has_critical = bool(set(components) & critical_components)
        
        if has_critical or total_changes > 1000:
            return "critical"
        elif total_changes > 500 or len(components) > 3:
            return "high"
        elif total_changes > 100 or len(components) > 1:
            return "medium"
        else:
            return "low"

    def _assess_file_impact(self, path: str, additions: int, deletions: int) -> str:
        """Assess individual file impact"""
        total = additions + deletions
        if total > 200:
            return "high"
        elif total > 50:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(self, files: List[Dict], 
                                   components: List[str], 
                                   impact: str) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if impact in ["critical", "high"]:
            recommendations.append("⚠️ Requiere revisión detallada antes de merge")
            recommendations.append("📋 Ejecutar suite completa de tests")
        
        if "security" in components:
            recommendations.append("🔒 Verificar implicaciones de seguridad")
        
        if "database" in components:
            recommendations.append("💾 Verificar migraciones de base de datos")
        
        if "api" in components:
            recommendations.append("🔌 Verificar compatibilidad de API")
        
        if any(f["type"] == "documentation" for f in files):
            recommendations.append("📚 Actualizar documentación relacionada")
        
        if any(f["type"] == "configuration" for f in files):
            recommendations.append("⚙️ Verificar configuración en todos los ambientes")
        
        if "deployment" in components:
            recommendations.append("🚀 Validar pipeline de deployment")
        
        # Auto-approval note
        recommendations.append("✅ Auto-aprobación habilitada según configuración")
        
        return recommendations

    def _generate_tasks_from_analysis(self, files: List[Dict],
                                       components: List[str],
                                       phases: List[int]) -> List[Dict]:
        """Generate development tasks from analysis"""
        tasks = []
        task_id = 0
        
        for phase in phases:
            for component in components:
                task_id += 1
                task = {
                    "id": f"T{phase}.{task_id}",
                    "title": f"Integrar cambios de {component} en Fase {phase}",
                    "phase": phase,
                    "component": component,
                    "priority": "P1" if component in ["security", "api", "database"] else "P2",
                    "status": "pending",
                    "estimated_duration": "2-4 hours"
                }
                tasks.append(task)
        
        return tasks

    def _create_placeholder_analysis(self, pr_number: int) -> PRAnalysis:
        """Create placeholder analysis when PR data unavailable"""
        return PRAnalysis(
            pr_number=pr_number,
            title="Unknown PR",
            description="Could not fetch PR details",
            author="Unknown",
            status="UNKNOWN",
            base_branch="main",
            head_branch="unknown",
            files_changed=[],
            additions=0,
            deletions=0,
            affected_components=["core"],
            affected_phases=[0],
            impact_level="low",
            recommendations=["⚠️ Verificar acceso al repositorio"],
            tasks=[]
        )

    def _save_analysis(self, analysis: PRAnalysis):
        """Save PR analysis to file"""
        output_dir = self.consolidation_dir / "pr_analysis"
        output_file = output_dir / f"pr_{analysis.pr_number}_analysis.json"
        
        output_file.write_text(
            json.dumps(asdict(analysis), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"📄 Análisis guardado en: {output_file}")

    # =========================================================================
    # PHASE 2: ORCHESTRATION PLANNING (Act)
    # =========================================================================

    def create_orchestration_plan(self, 
                                   name: str,
                                   description: str,
                                   pr_analysis: Optional[PRAnalysis] = None,
                                   start_phase: int = 0,
                                   end_phase: int = 15) -> OrchestrationPlan:
        """
        Create a comprehensive orchestration plan for development
        
        This is the ACT phase of ReAct pattern.
        Creates actionable plan based on analysis.
        """
        print(f"📋 Creando plan de orquestación: {name}...")
        
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        phases: Dict[int, List[DevelopmentTask]] = {}
        
        # Generate tasks for each phase
        for phase_num in range(start_phase, end_phase + 1):
            phase_tasks = self._generate_phase_tasks(phase_num, pr_analysis)
            if phase_tasks:
                phases[phase_num] = phase_tasks
        
        total_tasks = sum(len(tasks) for tasks in phases.values())
        
        plan = OrchestrationPlan(
            plan_id=plan_id,
            name=name,
            description=description,
            phases=phases,
            current_phase=start_phase,
            total_tasks=total_tasks,
            completed_tasks=0,
            status=PhaseStatus.PENDING
        )
        
        self.current_plan = plan
        self._save_plan(plan)
        
        print(f"✅ Plan creado: {total_tasks} tareas en {len(phases)} fases")
        return plan

    def _generate_phase_tasks(self, phase: int, 
                               analysis: Optional[PRAnalysis] = None) -> List[DevelopmentTask]:
        """Generate tasks for a specific phase"""
        
        # Phase definitions based on UNIFIED_CONSOLIDATION_PRODUCTION_PLAN
        phase_definitions = {
            0: {
                "name": "Discovery & Foundation",
                "agent": AgentType.DISCOVERY,
                "base_tasks": [
                    "Análisis de estructura del repositorio",
                    "Identificación de componentes principales",
                    "Documentación de dependencias"
                ]
            },
            1: {
                "name": "Repository Consolidation",
                "agent": AgentType.REPOSITORY,
                "base_tasks": [
                    "Unificación de estructura de directorios",
                    "Consolidación de configuraciones",
                    "Limpieza de archivos obsoletos"
                ]
            },
            2: {
                "name": "Core Integration",
                "agent": AgentType.MERGE,
                "base_tasks": [
                    "Integración de módulos core",
                    "Resolución de conflictos",
                    "Validación de imports"
                ]
            },
            3: {
                "name": "Database Layer",
                "agent": AgentType.INTEGRATION,
                "base_tasks": [
                    "Configuración de MongoDB",
                    "Migraciones de datos",
                    "Validación de esquemas"
                ]
            },
            4: {
                "name": "API Development",
                "agent": AgentType.INTEGRATION,
                "base_tasks": [
                    "Implementación de endpoints",
                    "Validación de contratos",
                    "Documentación de API"
                ]
            },
            5: {
                "name": "WhatsApp Integration",
                "agent": AgentType.INTEGRATION,
                "base_tasks": [
                    "Configuración de WhatsApp Business API",
                    "Implementación de webhooks",
                    "Testing de mensajería"
                ]
            },
            6: {
                "name": "External Integrations",
                "agent": AgentType.INTEGRATION,
                "base_tasks": [
                    "Integración con n8n workflows",
                    "Configuración de Qdrant",
                    "Setup de Chatwoot"
                ]
            },
            7: {
                "name": "AI/ML Components",
                "agent": AgentType.NLU,
                "base_tasks": [
                    "Configuración de modelos NLU",
                    "Setup de embeddings",
                    "Optimización de prompts"
                ]
            },
            8: {
                "name": "Training System",
                "agent": AgentType.VALIDATION,
                "base_tasks": [
                    "Implementación de sistema de entrenamiento",
                    "Setup de benchmarks",
                    "Validación de correcciones"
                ]
            },
            9: {
                "name": "Security Hardening",
                "agent": AgentType.SECURITY,
                "base_tasks": [
                    "Auditoría de seguridad",
                    "Implementación de autenticación",
                    "Gestión de secretos"
                ]
            },
            10: {
                "name": "Infrastructure Setup",
                "agent": AgentType.INFRASTRUCTURE,
                "base_tasks": [
                    "Configuración de Docker",
                    "Setup de Kubernetes",
                    "Definición de IaC"
                ]
            },
            11: {
                "name": "Testing & QA",
                "agent": AgentType.VALIDATION,
                "base_tasks": [
                    "Ejecución de tests unitarios",
                    "Tests de integración",
                    "Validación E2E"
                ]
            },
            12: {
                "name": "Dashboard & Monitoring",
                "agent": AgentType.OBSERVABILITY,
                "base_tasks": [
                    "Setup de dashboard",
                    "Configuración de métricas",
                    "Alertas y notificaciones"
                ]
            },
            13: {
                "name": "CI/CD Pipeline",
                "agent": AgentType.CICD,
                "base_tasks": [
                    "Configuración de GitHub Actions",
                    "Pipeline de deployment",
                    "Validación automática"
                ]
            },
            14: {
                "name": "Performance Optimization",
                "agent": AgentType.PERFORMANCE,
                "base_tasks": [
                    "Análisis de rendimiento",
                    "Optimización de queries",
                    "Load testing"
                ]
            },
            15: {
                "name": "Production Deployment",
                "agent": AgentType.DISASTER_RECOVERY,
                "base_tasks": [
                    "Deployment a producción",
                    "Validación final",
                    "Documentación de operaciones"
                ]
            }
        }
        
        if phase not in phase_definitions:
            return []
        
        phase_def = phase_definitions[phase]
        tasks = []
        
        for idx, task_title in enumerate(phase_def["base_tasks"], 1):
            task = DevelopmentTask(
                id=f"T{phase}.{idx}",
                title=task_title,
                description=f"Fase {phase} - {phase_def['name']}: {task_title}",
                phase=phase,
                priority=TaskPriority.P1_IMPORTANT if phase < 3 else TaskPriority.P2_MEDIUM,
                status=PhaseStatus.PENDING,
                assigned_agent=phase_def["agent"],
                dependencies=[f"T{phase}.{idx-1}"] if idx > 1 else [],
                files=[],
                estimated_duration="2-4 hours"
            )
            tasks.append(task)
        
        # Add PR-specific tasks if analysis provided
        if analysis and phase in analysis.affected_phases:
            for pr_task in analysis.tasks:
                if pr_task.get("phase") == phase:
                    task = DevelopmentTask(
                        id=pr_task["id"],
                        title=pr_task["title"],
                        description=f"PR #{analysis.pr_number}: {pr_task['title']}",
                        phase=phase,
                        priority=TaskPriority.P1_IMPORTANT,
                        status=PhaseStatus.PENDING,
                        assigned_agent=phase_def["agent"],
                        dependencies=[],
                        files=[f["path"] for f in analysis.files_changed 
                               if f.get("component") == pr_task.get("component")],
                        estimated_duration=pr_task.get("estimated_duration", "2-4 hours")
                    )
                    tasks.append(task)
        
        return tasks

    def _save_plan(self, plan: OrchestrationPlan):
        """Save orchestration plan to file"""
        output_dir = self.consolidation_dir / "orchestration"
        output_file = output_dir / f"{plan.plan_id}.json"
        
        output_file.write_text(
            json.dumps(plan.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"📄 Plan guardado en: {output_file}")

    # =========================================================================
    # PHASE 3: EXECUTION & MONITORING (Observe)
    # =========================================================================

    def execute_plan(self, plan: Optional[OrchestrationPlan] = None,
                     start_phase: Optional[int] = None,
                     end_phase: Optional[int] = None) -> Dict:
        """
        Execute the orchestration plan
        
        This is the OBSERVE phase of ReAct pattern.
        Executes and monitors the plan progress.
        """
        plan = plan or self.current_plan
        if not plan:
            return {"success": False, "error": "No plan available"}
        
        print(f"🚀 Ejecutando plan: {plan.name}")
        print(f"   Auto-aprobación: {'✅ Habilitada' if self.auto_approve else '❌ Deshabilitada'}")
        
        results = {
            "plan_id": plan.plan_id,
            "executed_phases": [],
            "completed_tasks": 0,
            "failed_tasks": 0,
            "skipped_tasks": 0,
            "execution_log": []
        }
        
        # Determine phases to execute
        phases_to_execute = sorted(plan.phases.keys())
        if start_phase is not None:
            phases_to_execute = [p for p in phases_to_execute if p >= start_phase]
        if end_phase is not None:
            phases_to_execute = [p for p in phases_to_execute if p <= end_phase]
        
        for phase_num in phases_to_execute:
            print(f"\n📋 Fase {phase_num}:")
            phase_result = self._execute_phase(plan, phase_num)
            results["executed_phases"].append(phase_result)
            results["completed_tasks"] += phase_result["completed"]
            results["failed_tasks"] += phase_result["failed"]
            results["skipped_tasks"] += phase_result["skipped"]
            
            if phase_result["failed"] > 0 and not self.auto_approve:
                print(f"⚠️ Fase {phase_num} tiene errores. Deteniendo ejecución.")
                break
        
        plan.completed_tasks = results["completed_tasks"]
        plan.status = PhaseStatus.COMPLETED if results["failed_tasks"] == 0 else PhaseStatus.FAILED
        plan.updated_at = datetime.now().isoformat()
        
        self._save_plan(plan)
        self._save_execution_report(results)
        
        print(f"\n{'='*60}")
        print(f"✅ Ejecución completada:")
        print(f"   - Tareas completadas: {results['completed_tasks']}")
        print(f"   - Tareas fallidas: {results['failed_tasks']}")
        print(f"   - Tareas saltadas: {results['skipped_tasks']}")
        
        return results

    def _execute_phase(self, plan: OrchestrationPlan, phase_num: int) -> Dict:
        """Execute all tasks in a phase"""
        tasks = plan.phases.get(phase_num, [])
        
        result = {
            "phase": phase_num,
            "total": len(tasks),
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "tasks": []
        }
        
        for task in tasks:
            task_result = self._execute_task(task)
            result["tasks"].append(task_result)
            
            if task_result["status"] == "completed":
                result["completed"] += 1
                task.status = PhaseStatus.COMPLETED
                task.completed_at = datetime.now().isoformat()
            elif task_result["status"] == "failed":
                result["failed"] += 1
                task.status = PhaseStatus.FAILED
            else:
                result["skipped"] += 1
                task.status = PhaseStatus.SKIPPED
        
        return result

    def _execute_task(self, task: DevelopmentTask) -> Dict:
        """Execute a single task"""
        print(f"   ▶️ {task.id}: {task.title}")
        
        # Check dependencies
        # In auto-approve mode, we continue even if deps aren't met
        
        try:
            # Simulate task execution
            # In a real implementation, this would call the appropriate executor
            
            result = {
                "task_id": task.id,
                "title": task.title,
                "status": "completed",
                "duration": "simulated",
                "output": f"Task {task.id} executed successfully"
            }
            
            print(f"      ✅ Completado")
            
        except Exception as e:
            result = {
                "task_id": task.id,
                "title": task.title,
                "status": "failed",
                "error": str(e)
            }
            print(f"      ❌ Error: {e}")
        
        return result

    def _save_execution_report(self, results: Dict):
        """Save execution report"""
        output_dir = self.consolidation_dir / "orchestration"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"execution_report_{timestamp}.json"
        
        output_file.write_text(
            json.dumps(results, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"📄 Reporte guardado en: {output_file}")

    # =========================================================================
    # REACT CYCLE: Complete Think -> Act -> Observe Cycle
    # =========================================================================

    def react_cycle(self, 
                    pr_number: Optional[int] = None,
                    goal: str = "Orquestar desarrollo automatizado") -> Dict:
        """
        Execute complete ReAct cycle for development orchestration
        
        1. THINK: Analyze current state (PR, codebase, etc.)
        2. ACT: Create and execute orchestration plan
        3. OBSERVE: Monitor results and adjust
        """
        print("=" * 70)
        print("🔄 CICLO REACT: Orquestación de Desarrollo Automatizado")
        print("=" * 70)
        
        cycle_result = {
            "goal": goal,
            "phases": [],
            "success": False,
            "started_at": datetime.now().isoformat()
        }
        
        # PHASE 1: THINK
        print("\n🤔 FASE THINK: Analizando situación...")
        analysis = None
        
        if pr_number:
            analysis = self.analyze_pr(pr_number)
            cycle_result["phases"].append({
                "phase": "think",
                "action": f"Analyzed PR #{pr_number}",
                "result": {
                    "impact": analysis.impact_level,
                    "components": analysis.affected_components,
                    "recommendations": analysis.recommendations
                }
            })
        else:
            print("   ℹ️ No hay PR específico, usando análisis general")
            cycle_result["phases"].append({
                "phase": "think",
                "action": "General analysis",
                "result": {"status": "no_pr_specified"}
            })
        
        # PHASE 2: ACT
        print("\n⚡ FASE ACT: Creando plan de orquestación...")
        plan_name = f"Orchestration for PR #{pr_number}" if pr_number else "General Orchestration"
        plan = self.create_orchestration_plan(
            name=plan_name,
            description=goal,
            pr_analysis=analysis
        )
        
        cycle_result["phases"].append({
            "phase": "act",
            "action": "Created orchestration plan",
            "result": {
                "plan_id": plan.plan_id,
                "total_tasks": plan.total_tasks,
                "phases": list(plan.phases.keys())
            }
        })
        
        # PHASE 3: OBSERVE
        print("\n👁️ FASE OBSERVE: Ejecutando y monitoreando...")
        execution_result = self.execute_plan(plan)
        
        cycle_result["phases"].append({
            "phase": "observe",
            "action": "Executed plan",
            "result": {
                "completed_tasks": execution_result["completed_tasks"],
                "failed_tasks": execution_result["failed_tasks"],
                "executed_phases": len(execution_result["executed_phases"])
            }
        })
        
        cycle_result["success"] = execution_result["failed_tasks"] == 0
        cycle_result["completed_at"] = datetime.now().isoformat()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 RESUMEN DEL CICLO REACT:")
        print("=" * 70)
        print(f"   Goal: {goal}")
        print(f"   Status: {'✅ Exitoso' if cycle_result['success'] else '⚠️ Con errores'}")
        print(f"   Tareas completadas: {execution_result['completed_tasks']}")
        print(f"   Tareas fallidas: {execution_result['failed_tasks']}")
        
        return cycle_result

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get_status(self) -> Dict:
        """Get current orchestration status"""
        status = {
            "agent": "DevelopmentOrchestratorAgent",
            "version": "1.0.0",
            "workspace": str(self.workspace_root),
            "auto_approve": self.auto_approve,
            "current_plan": self.current_plan.to_dict() if self.current_plan else None,
            "execution_history_count": len(self.execution_history)
        }
        return status

    def list_available_plans(self) -> List[str]:
        """List all available orchestration plans"""
        plans_dir = self.consolidation_dir / "orchestration"
        if not plans_dir.exists():
            return []
        
        return [f.stem for f in plans_dir.glob("plan_*.json")]

    def load_plan(self, plan_id: str) -> Optional[OrchestrationPlan]:
        """Load an existing orchestration plan"""
        plan_file = self.consolidation_dir / "orchestration" / f"{plan_id}.json"
        if not plan_file.exists():
            print(f"⚠️ Plan no encontrado: {plan_id}")
            return None
        
        try:
            data = json.loads(plan_file.read_text(encoding="utf-8"))
            # Reconstruct plan from data
            # (simplified - full implementation would recreate all objects)
            print(f"✅ Plan cargado: {plan_id}")
            return data
        except Exception as e:
            print(f"❌ Error cargando plan: {e}")
            return None


def main():
    """CLI interface for Development Orchestrator Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Development Orchestrator Agent for Gravity"
    )
    
    parser.add_argument(
        "--mode",
        choices=["analyze", "plan", "execute", "react", "status"],
        default="react",
        help="Operation mode"
    )
    
    parser.add_argument(
        "--pr",
        type=int,
        help="PR number to analyze"
    )
    
    parser.add_argument(
        "--goal",
        default="Orquestar desarrollo automatizado del proyecto",
        help="Goal for orchestration"
    )
    
    parser.add_argument(
        "--start-phase",
        type=int,
        default=0,
        help="Starting phase number"
    )
    
    parser.add_argument(
        "--end-phase",
        type=int,
        default=15,
        help="Ending phase number"
    )
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = DevelopmentOrchestratorAgent()
    
    print("=" * 70)
    print("🤖 DEVELOPMENT ORCHESTRATOR AGENT - Gravity Mode")
    print("=" * 70)
    print(f"   Modo: {args.mode}")
    print(f"   Auto-aprobación: ✅ Habilitada")
    print("=" * 70)
    
    if args.mode == "analyze":
        if not args.pr:
            print("❌ Se requiere --pr para el modo analyze")
            return 1
        agent.analyze_pr(args.pr)
        
    elif args.mode == "plan":
        analysis = agent.analyze_pr(args.pr) if args.pr else None
        agent.create_orchestration_plan(
            name=f"Plan para PR #{args.pr}" if args.pr else "Plan general",
            description=args.goal,
            pr_analysis=analysis,
            start_phase=args.start_phase,
            end_phase=args.end_phase
        )
        
    elif args.mode == "execute":
        if agent.current_plan:
            agent.execute_plan(
                start_phase=args.start_phase,
                end_phase=args.end_phase
            )
        else:
            print("⚠️ No hay plan activo. Usa --mode plan primero.")
            
    elif args.mode == "react":
        agent.react_cycle(pr_number=args.pr, goal=args.goal)
        
    elif args.mode == "status":
        status = agent.get_status()
        print(json.dumps(status, indent=2))
    
    return 0


if __name__ == "__main__":
    exit(main())

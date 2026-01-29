#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gravity Development Orchestrator Agent
======================================

Un agente especializado en modo Gravity de Cursor para interpretar y orquestar
el desarrollo automatizado del proyecto BMC Chatbot.

Este agente:
- Interpreta PRs y cambios de código
- Orquesta el plan de desarrollo de 16 fases
- Coordina el equipo de 12+ agentes especializados
- Ejecuta desarrollo automatizado con patrones ReAct

Basado en:
- ReAct Pattern (Reasoning + Acting)
- Chain-of-Thought Reasoning
- Context-Aware Planning
- Multi-Agent Orchestration

Autor: Gravity Agent Team
Versión: 1.0.0
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict, field
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GravityAgent")

# Add parent directories to path for imports
_current_dir = Path(__file__).parent
_project_root = _current_dir.parent.parent
sys.path.insert(0, str(_project_root))

# Import model integrator if available
try:
    from model_integrator import get_model_integrator
    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False


class DevelopmentPhase(Enum):
    """Phases in the unified development plan"""
    PHASE_MINUS_8 = -8  # Initial Setup
    PHASE_MINUS_7 = -7  # Environment Configuration
    PHASE_MINUS_6 = -6  # Dependency Installation
    PHASE_MINUS_5 = -5  # Service Configuration
    PHASE_MINUS_4 = -4  # Database Setup
    PHASE_MINUS_3 = -3  # Integration Setup
    PHASE_MINUS_2 = -2  # Testing Framework
    PHASE_MINUS_1 = -1  # Pre-flight Checks
    PHASE_0 = 0   # BMC Discovery & Assessment
    PHASE_1 = 1   # Repository Analysis
    PHASE_2 = 2   # Component Mapping
    PHASE_3 = 3   # Merge Strategy
    PHASE_4 = 4   # Conflict Resolution
    PHASE_5 = 5   # Testing & Validation
    PHASE_6 = 6   # Documentation
    PHASE_7 = 7   # Integration Testing
    PHASE_8 = 8   # Final Configuration
    PHASE_9 = 9   # Security Hardening
    PHASE_10 = 10 # Infrastructure as Code
    PHASE_11 = 11 # Observability & Monitoring
    PHASE_12 = 12 # Performance & Load Testing
    PHASE_13 = 13 # CI/CD Pipeline
    PHASE_14 = 14 # Disaster Recovery & Backup
    PHASE_15 = 15 # Final Production Validation


class AgentRole(Enum):
    """Specialized agent roles"""
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


class TaskPriority(Enum):
    """Task priority levels"""
    P0_CRITICAL = "P0"
    P1_IMPORTANT = "P1"
    P2_MEDIUM = "P2"
    P3_LOW = "P3"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


@dataclass
class PRAnalysis:
    """Pull Request analysis result"""
    pr_number: int
    title: str
    author: str
    status: str
    base_branch: str
    head_branch: str
    files_changed: List[Dict[str, Any]]
    purpose: str
    affected_phases: List[int]
    dependencies: List[str]
    impact_assessment: Dict[str, Any]
    integration_strategy: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    analyzed_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DevelopmentTask:
    """A task in the development plan"""
    id: str
    phase: int
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    assigned_agent: AgentRole
    dependencies: List[str]
    files: List[str]
    script: Optional[str]
    estimated_duration: str
    bmc_context: Optional[str]
    output: Optional[str]
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data["priority"] = self.priority.value
        data["status"] = self.status.value
        data["assigned_agent"] = self.assigned_agent.value
        return data


class GravityDevelopmentAgent:
    """
    Gravity Development Orchestrator Agent
    
    Agente principal para interpretar y orquestar el desarrollo automatizado
    del proyecto BMC Chatbot.
    
    Capacidades:
    - Análisis de PRs y cambios de código
    - Orquestación del plan de 16 fases
    - Coordinación de agentes especializados
    - Ejecución automatizada con ReAct pattern
    """

    # Phase to Agent mapping
    PHASE_AGENT_MAP = {
        0: AgentRole.DISCOVERY,
        1: AgentRole.REPOSITORY,
        2: AgentRole.REPOSITORY,
        3: AgentRole.MERGE,
        4: AgentRole.MERGE,
        5: AgentRole.MERGE,
        6: AgentRole.MERGE,
        7: AgentRole.INTEGRATION,
        8: AgentRole.INTEGRATION,
        9: AgentRole.SECURITY,
        10: AgentRole.INFRASTRUCTURE,
        11: AgentRole.OBSERVABILITY,
        12: AgentRole.PERFORMANCE,
        13: AgentRole.CICD,
        14: AgentRole.DISASTER_RECOVERY,
        15: AgentRole.VALIDATION,
    }

    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize the Gravity Development Agent"""
        self.workspace_path = Path(workspace_path) if workspace_path else _project_root
        self.integrator = None
        self.ai_enabled = False
        
        # State management
        self.current_phase: Optional[int] = None
        self.development_plan: List[DevelopmentTask] = []
        self.execution_history: List[Dict] = []
        self.context: Dict[str, Any] = {}
        
        # Initialize AI integrator
        if MODEL_INTEGRATOR_AVAILABLE:
            try:
                self.integrator = get_model_integrator()
                self.ai_enabled = True
                logger.info("✅ AI Integrator initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ AI not available: {e}")
        
        # Load workspace context
        self._load_workspace_context()
    
    def _load_workspace_context(self):
        """Load workspace context from configuration files"""
        self.context = {
            "workspace_path": str(self.workspace_path),
            "project_name": "chatbot-2311",
            "components": {
                "quotation_engine": True,
                "whatsapp_integration": True,
                "n8n_workflows": True,
                "qdrant_vector_db": True,
                "chatwoot_integration": True,
                "dashboard": True,
                "training_system": True,
            },
            "agents_available": [role.value for role in AgentRole],
            "phases_total": 16,
            "auto_approval": True,
            "execution_mode": "automated",
        }
        
        # Try to load orchestrator config
        config_path = self.workspace_path / "scripts" / "orchestrator" / "config" / "orchestrator_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    self.context["orchestrator_config"] = json.load(f)
            except Exception:
                pass

    def _generate_system_prompt(self, mode: str = "orchestrator") -> str:
        """Generate system prompt based on mode"""
        
        base_prompt = """Eres el Gravity Development Orchestrator Agent, un agente de IA especializado en interpretar y orquestar el desarrollo automatizado del proyecto BMC Chatbot.

Tu rol principal es:
1. **Interpretar** requisitos de desarrollo desde PRs, issues, y solicitudes
2. **Analizar** el impacto en el sistema y componentes existentes
3. **Orquestar** la ejecución del plan de desarrollo de 16 fases
4. **Coordinar** el equipo de 12+ agentes especializados
5. **Ejecutar** desarrollo automatizado con patrones ReAct

Conocimiento del dominio BMC Uruguay:
- Productos: Isodec, Poliestireno Expandido, Lana de Roca
- Espesores: 50mm, 75mm, 100mm, 125mm, 150mm
- Zonas: Montevideo, Canelones, Maldonado, Rivera
- Servicios: Flete, instalación, anclajes
- IVA: 22%

Componentes del sistema:
- Sistema de cotizaciones (sistema_cotizaciones.py)
- Integración WhatsApp Business API
- Workflows n8n para orquestación
- Base de datos vectorial Qdrant
- Integración Chatwoot
- Sistema de entrenamiento con correcciones por emoji

Equipo de agentes:
- OrchestratorAgent: Coordinador maestro
- RepositoryAgent: Git y workspace
- DiscoveryAgent: Descubrimiento técnico y BMC
- MergeAgent: Estrategia de merge y resolución de conflictos
- IntegrationAgent: Especialista en integraciones
- SecurityAgent: Seguridad y hardening
- InfrastructureAgent: Infrastructure as Code
- ObservabilityAgent: Monitoreo y logging
- PerformanceAgent: Performance y load testing
- CICDAgent: CI/CD Pipeline
- DisasterRecoveryAgent: DR y Backup
- ValidationAgent: Validación final y QA

Principios de trabajo:
- Auto-aprobación habilitada (seguir .cursorrules)
- Ejecución automatizada sin confirmaciones manuales
- Progreso continuo entre fases
- Documentación clara de decisiones
- Enfoque en resultados prácticos"""

        if mode == "pr_analysis":
            base_prompt += """

Modo de análisis de PR activo. Debes:
1. Extraer metadatos del PR (número, título, autor, estado)
2. Analizar archivos cambiados y categorizar por tipo
3. Evaluar impacto en arquitectura y componentes BMC
4. Identificar fases afectadas del plan de consolidación
5. Generar lista de tareas con asignación de agentes
6. Evaluar riesgos y estrategia de mitigación"""

        elif mode == "orchestration":
            base_prompt += """

Modo de orquestación activo. Debes:
1. Evaluar estado actual del proyecto
2. Determinar siguiente fase a ejecutar
3. Asignar agentes apropiados
4. Coordinar ejecución de tareas
5. Monitorear progreso y resultados
6. Manejar errores y reintentos"""

        elif mode == "react":
            base_prompt += """

Modo ReAct (Reasoning + Acting) activo. Sigue este ciclo:
1. **THINK**: Analiza la situación actual y planifica tu enfoque
2. **ACT**: Ejecuta acciones usando las herramientas disponibles
3. **OBSERVE**: Evalúa resultados y ajusta estrategia
4. Repite hasta completar el objetivo

Formato de respuesta:
```
THINK: [Tu análisis y plan]
ACT: [Acción a ejecutar]
OBSERVE: [Observación de resultados]
```"""

        return base_prompt

    def analyze_pr(self, pr_number: int, pr_data: Optional[Dict] = None) -> PRAnalysis:
        """
        Analyze a Pull Request and generate implementation plan
        
        Args:
            pr_number: PR number to analyze
            pr_data: Optional pre-fetched PR data
            
        Returns:
            PRAnalysis with full analysis and recommendations
        """
        logger.info(f"📊 Analyzing PR #{pr_number}...")
        
        # Fetch PR data if not provided
        if pr_data is None:
            pr_data = self._fetch_pr_data(pr_number)
        
        # Extract file categories
        file_analysis = self._analyze_files(pr_data.get("files", []))
        
        # Determine affected phases
        affected_phases = self._determine_affected_phases(file_analysis, pr_data)
        
        # Generate impact assessment
        impact = self._assess_impact(pr_data, file_analysis)
        
        # Generate integration strategy
        strategy = self._generate_integration_strategy(pr_data, impact)
        
        # Generate risk assessment
        risks = self._assess_risks(pr_data, impact)
        
        analysis = PRAnalysis(
            pr_number=pr_number,
            title=pr_data.get("title", "Unknown"),
            author=pr_data.get("author", "Unknown"),
            status=pr_data.get("state", "unknown"),
            base_branch=pr_data.get("baseRefName", "main"),
            head_branch=pr_data.get("headRefName", "unknown"),
            files_changed=pr_data.get("files", []),
            purpose=pr_data.get("body", "")[:500],
            affected_phases=affected_phases,
            dependencies=self._extract_dependencies(pr_data),
            impact_assessment=impact,
            integration_strategy=strategy,
            risk_assessment=risks,
        )
        
        logger.info(f"✅ PR #{pr_number} analysis complete")
        return analysis

    def _fetch_pr_data(self, pr_number: int) -> Dict:
        """Fetch PR data using gh CLI"""
        try:
            result = subprocess.run(
                ["gh", "pr", "view", str(pr_number), "--json", 
                 "title,body,files,state,headRefName,baseRefName,author"],
                capture_output=True,
                text=True,
                cwd=str(self.workspace_path)
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            logger.warning(f"Failed to fetch PR data: {e}")
        return {}

    def _analyze_files(self, files: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize changed files by type"""
        categories = {
            "python": [],
            "typescript": [],
            "javascript": [],
            "configuration": [],
            "documentation": [],
            "tests": [],
            "scripts": [],
            "workflows": [],
            "other": [],
        }
        
        for file_info in files:
            path = file_info.get("path", "")
            
            if path.endswith(".py"):
                if "test" in path.lower():
                    categories["tests"].append(file_info)
                else:
                    categories["python"].append(file_info)
            elif path.endswith(".ts") or path.endswith(".tsx"):
                categories["typescript"].append(file_info)
            elif path.endswith(".js") or path.endswith(".jsx"):
                categories["javascript"].append(file_info)
            elif path.endswith((".json", ".yaml", ".yml", ".toml")):
                categories["configuration"].append(file_info)
            elif path.endswith(".md"):
                categories["documentation"].append(file_info)
            elif path.endswith(".sh"):
                categories["scripts"].append(file_info)
            elif "n8n" in path.lower() or "workflow" in path.lower():
                categories["workflows"].append(file_info)
            else:
                categories["other"].append(file_info)
        
        return categories

    def _determine_affected_phases(self, file_analysis: Dict, pr_data: Dict) -> List[int]:
        """Determine which phases are affected by the changes"""
        affected = set()
        
        # Map file categories to phases
        if file_analysis["python"]:
            affected.update([1, 2, 5, 7])  # Repository, Component, Testing, Integration
        
        if file_analysis["documentation"]:
            affected.add(6)  # Documentation
        
        if file_analysis["configuration"]:
            affected.update([8, 10])  # Configuration, Infrastructure
        
        if file_analysis["tests"]:
            affected.update([5, 7, 12])  # Testing, Integration, Performance
        
        if file_analysis["workflows"]:
            affected.update([7, 8])  # Integration, Configuration
        
        # Check for security-related changes
        body = pr_data.get("body", "").lower()
        title = pr_data.get("title", "").lower()
        
        if any(word in title + body for word in ["security", "auth", "token", "secret"]):
            affected.add(9)  # Security
        
        if any(word in title + body for word in ["ci", "cd", "deploy", "pipeline"]):
            affected.add(13)  # CI/CD
        
        if any(word in title + body for word in ["monitor", "log", "metric", "observ"]):
            affected.add(11)  # Observability
        
        if any(word in title + body for word in ["train", "benchmark", "eval"]):
            affected.add(0)  # Discovery (includes training system)
        
        return sorted(list(affected))

    def _assess_impact(self, pr_data: Dict, file_analysis: Dict) -> Dict[str, Any]:
        """Assess the impact of changes"""
        total_files = sum(len(files) for files in file_analysis.values())
        total_additions = sum(f.get("additions", 0) for files in file_analysis.values() for f in files)
        total_deletions = sum(f.get("deletions", 0) for files in file_analysis.values() for f in files)
        
        # Determine impact level
        if total_additions + total_deletions > 1000:
            impact_level = "high"
        elif total_additions + total_deletions > 200:
            impact_level = "medium"
        else:
            impact_level = "low"
        
        return {
            "total_files": total_files,
            "total_additions": total_additions,
            "total_deletions": total_deletions,
            "impact_level": impact_level,
            "architecture_impact": "minimal" if total_files < 10 else "moderate",
            "bmc_domain_impact": self._assess_bmc_impact(pr_data),
            "integration_points": self._identify_integration_points(file_analysis),
        }

    def _assess_bmc_impact(self, pr_data: Dict) -> str:
        """Assess impact on BMC-specific components"""
        body = (pr_data.get("body", "") + pr_data.get("title", "")).lower()
        
        bmc_keywords = [
            "cotiz", "quote", "isodec", "precio", "price", "whatsapp",
            "producto", "product", "zona", "zone", "flete", "cliente"
        ]
        
        matches = sum(1 for keyword in bmc_keywords if keyword in body)
        
        if matches >= 3:
            return "high"
        elif matches >= 1:
            return "medium"
        return "low"

    def _identify_integration_points(self, file_analysis: Dict) -> List[str]:
        """Identify affected integration points"""
        integrations = []
        
        all_paths = [f.get("path", "") for files in file_analysis.values() for f in files]
        path_str = " ".join(all_paths).lower()
        
        if "whatsapp" in path_str:
            integrations.append("whatsapp")
        if "n8n" in path_str or "workflow" in path_str:
            integrations.append("n8n")
        if "qdrant" in path_str or "vector" in path_str:
            integrations.append("qdrant")
        if "chatwoot" in path_str:
            integrations.append("chatwoot")
        if "mongo" in path_str:
            integrations.append("mongodb")
        if "api" in path_str:
            integrations.append("api")
        
        return integrations

    def _generate_integration_strategy(self, pr_data: Dict, impact: Dict) -> Dict[str, Any]:
        """Generate integration strategy"""
        return {
            "merge_strategy": "direct_merge" if impact["impact_level"] == "low" else "feature_branch",
            "testing_required": impact["impact_level"] != "low",
            "review_required": impact["impact_level"] == "high",
            "documentation_updates": len([f for f in pr_data.get("files", []) if f.get("path", "").endswith(".md")]) > 0,
            "rollback_plan": "git_revert",
        }

    def _assess_risks(self, pr_data: Dict, impact: Dict) -> Dict[str, Any]:
        """Assess risks of the changes"""
        risks = []
        
        if impact["impact_level"] == "high":
            risks.append({
                "type": "complexity",
                "description": "Large change set may introduce unexpected issues",
                "mitigation": "Incremental testing and review",
                "probability": "medium",
            })
        
        if "production" in pr_data.get("body", "").lower():
            risks.append({
                "type": "production_impact",
                "description": "Changes may affect production environment",
                "mitigation": "Staging environment testing",
                "probability": "low",
            })
        
        return {
            "risks": risks,
            "overall_risk_level": "high" if len(risks) > 2 else "medium" if risks else "low",
            "blockers": [],
            "recommendations": [
                "Review changes thoroughly",
                "Run automated tests",
                "Update documentation if needed",
            ],
        }

    def _extract_dependencies(self, pr_data: Dict) -> List[str]:
        """Extract dependencies from PR data"""
        deps = []
        
        for file_info in pr_data.get("files", []):
            path = file_info.get("path", "")
            if path == "requirements.txt" or path.endswith("/requirements.txt"):
                deps.append("python_dependencies")
            elif path == "package.json" or path.endswith("/package.json"):
                deps.append("node_dependencies")
        
        return deps

    def generate_tasks_from_pr(self, analysis: PRAnalysis) -> List[DevelopmentTask]:
        """Generate development tasks from PR analysis"""
        tasks = []
        
        # Task for reviewing the PR
        tasks.append(DevelopmentTask(
            id=f"T{analysis.pr_number}.1",
            phase=0,
            title=f"Review PR #{analysis.pr_number}: {analysis.title[:50]}",
            description=f"Review and analyze changes from PR #{analysis.pr_number}",
            priority=TaskPriority.P1_IMPORTANT,
            status=TaskStatus.PENDING,
            assigned_agent=AgentRole.DISCOVERY,
            dependencies=[],
            files=[f.get("path", "") for f in analysis.files_changed[:10]],
            script=None,
            estimated_duration="30 minutes",
            bmc_context=f"Impact level: {analysis.impact_assessment.get('bmc_domain_impact', 'unknown')}",
            output=f"consolidation/pr_analysis/pr_{analysis.pr_number}_review.json",
        ))
        
        # Task for each affected phase
        for i, phase in enumerate(analysis.affected_phases):
            agent = self.PHASE_AGENT_MAP.get(phase, AgentRole.ORCHESTRATOR)
            
            tasks.append(DevelopmentTask(
                id=f"T{analysis.pr_number}.{i+2}",
                phase=phase,
                title=f"Phase {phase} updates for PR #{analysis.pr_number}",
                description=f"Apply changes from PR #{analysis.pr_number} to Phase {phase}",
                priority=TaskPriority.P2_MEDIUM,
                status=TaskStatus.PENDING,
                assigned_agent=agent,
                dependencies=[f"T{analysis.pr_number}.{i+1}"] if i > 0 else [f"T{analysis.pr_number}.1"],
                files=[],
                script=f"scripts/orchestrator/phase_executors/phase_{phase}_executor.py",
                estimated_duration="1 hour",
                bmc_context=None,
                output=f"consolidation/phase_{phase}/pr_{analysis.pr_number}_updates.json",
            ))
        
        # Integration testing task
        if analysis.impact_assessment.get("integration_points"):
            tasks.append(DevelopmentTask(
                id=f"T{analysis.pr_number}.integration",
                phase=7,
                title=f"Integration testing for PR #{analysis.pr_number}",
                description=f"Test integrations affected by PR: {', '.join(analysis.impact_assessment['integration_points'])}",
                priority=TaskPriority.P1_IMPORTANT,
                status=TaskStatus.PENDING,
                assigned_agent=AgentRole.INTEGRATION,
                dependencies=[t.id for t in tasks],
                files=[],
                script="scripts/integration/run_integration_tests.py",
                estimated_duration="2 hours",
                bmc_context="BMC integration validation required",
                output=f"consolidation/integration/pr_{analysis.pr_number}_test_results.json",
            ))
        
        self.development_plan.extend(tasks)
        return tasks

    def think(self, situation: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        THINK phase: Analyze situation and plan approach
        
        Args:
            situation: Current situation description
            context: Additional context
            
        Returns:
            Analysis with plan and next steps
        """
        logger.info("🤔 THINK: Analyzing situation...")
        
        if not self.ai_enabled:
            return {
                "analysis": situation,
                "plan": ["Review current state", "Identify next actions", "Execute"],
                "next_steps": [],
                "confidence": 0.5,
            }
        
        try:
            system_prompt = self._generate_system_prompt("react")
            
            context_str = json.dumps({**self.context, **(context or {})}, indent=2, default=str)
            
            prompt = f"""Situación actual: {situation}

Contexto:
{context_str}

Analiza esta situación y crea un plan de acción. Considera:
1. ¿Cuál es el estado actual?
2. ¿Qué necesita hacerse?
3. ¿Cuáles son las dependencias?
4. ¿Cuáles son los riesgos potenciales?
5. ¿Cuál es el enfoque recomendado?

Responde en formato JSON con:
{{
    "analysis": "Análisis detallado de la situación",
    "plan": ["paso1", "paso2", "paso3"],
    "next_steps": ["acción inmediata 1", "acción inmediata 2"],
    "potential_issues": ["issue1", "issue2"],
    "recommendations": ["recomendación1", "recomendación2"],
    "assigned_agents": ["AgentName1", "AgentName2"],
    "confidence": 0.0-1.0
}}"""

            response = self.integrator.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1000
            )
            
            if response and "content" in response:
                content = response["content"].strip()
                result = self._extract_json_from_text(content)
                if result:
                    logger.info(f"✅ THINK complete: {result.get('analysis', '')[:100]}...")
                    return result
        
        except Exception as e:
            logger.warning(f"Error in THINK phase: {e}")
        
        return {
            "analysis": situation,
            "plan": [],
            "next_steps": [],
            "confidence": 0.0,
        }

    def act(self, action: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        ACT phase: Execute actions
        
        Args:
            action: Action to execute
            parameters: Action parameters
            
        Returns:
            Action result
        """
        logger.info(f"⚡ ACT: Executing '{action}'...")
        
        parameters = parameters or {}
        result = {
            "action": action,
            "success": False,
            "output": None,
            "error": None,
            "timestamp": datetime.now().isoformat(),
        }
        
        try:
            # Route to appropriate action handler
            if action == "analyze_pr":
                pr_number = parameters.get("pr_number")
                if pr_number:
                    analysis = self.analyze_pr(pr_number)
                    result["output"] = asdict(analysis)
                    result["success"] = True
                else:
                    result["error"] = "PR number required"
                    
            elif action == "generate_tasks":
                analysis_data = parameters.get("analysis")
                if analysis_data:
                    tasks = self.generate_tasks_from_pr(PRAnalysis(**analysis_data))
                    result["output"] = [t.to_dict() for t in tasks]
                    result["success"] = True
                else:
                    result["error"] = "Analysis data required"
                    
            elif action == "execute_phase":
                phase = parameters.get("phase")
                if phase is not None:
                    result = self._execute_phase(phase)
                else:
                    result["error"] = "Phase number required"
                    
            elif action == "check_status":
                result = self._check_project_status()
                
            elif action == "assign_agent":
                agent = parameters.get("agent")
                task_id = parameters.get("task_id")
                result = self._assign_agent(agent, task_id)
                
            else:
                result["error"] = f"Unknown action: {action}"
        
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error in ACT phase: {e}")
        
        self.execution_history.append(result)
        return result

    def observe(self, action_result: Dict) -> Dict[str, Any]:
        """
        OBSERVE phase: Evaluate results and adjust strategy
        
        Args:
            action_result: Result from ACT phase
            
        Returns:
            Observation with recommendations
        """
        logger.info("👁️ OBSERVE: Evaluating results...")
        
        if not self.ai_enabled:
            return {
                "observation": "Action completed",
                "success": action_result.get("success", False),
                "recommendations": [],
            }
        
        try:
            system_prompt = self._generate_system_prompt("react")
            
            result_str = json.dumps(action_result, indent=2, default=str)
            
            prompt = f"""Resultado de la acción:
{result_str}

Evalúa este resultado:
1. ¿Fue exitosa la acción?
2. ¿Qué funcionó bien?
3. ¿Qué problemas se encontraron?
4. ¿Qué debería hacerse ahora?
5. ¿Alguna recomendación?

Responde en formato JSON con:
{{
    "observation": "Observación detallada",
    "success": true/false,
    "issues": ["issue1", "issue2"],
    "next_steps": ["paso1", "paso2"],
    "recommendations": ["rec1", "rec2"],
    "should_continue": true/false,
    "retry_required": true/false
}}"""

            response = self.integrator.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            if response and "content" in response:
                content = response["content"].strip()
                result = self._extract_json_from_text(content)
                if result:
                    logger.info(f"✅ OBSERVE complete: {result.get('observation', '')[:100]}...")
                    return result
        
        except Exception as e:
            logger.warning(f"Error in OBSERVE phase: {e}")
        
        return {
            "observation": "Action completed",
            "success": action_result.get("success", False),
            "recommendations": [],
        }

    def react_cycle(self, goal: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Complete ReAct cycle: THINK → ACT → OBSERVE → Repeat
        
        Args:
            goal: Goal to achieve
            max_iterations: Maximum iterations
            
        Returns:
            Final result with execution summary
        """
        logger.info(f"🚀 Starting ReAct cycle for: {goal}")
        
        iteration = 0
        current_situation = goal
        all_results = []
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"\n--- Iteration {iteration}/{max_iterations} ---")
            
            # THINK
            think_result = self.think(current_situation)
            
            if not think_result.get("next_steps"):
                logger.info("No more actions needed")
                break
            
            # ACT
            next_action = think_result["next_steps"][0]
            act_result = self.act(next_action, think_result)
            all_results.append(act_result)
            
            # OBSERVE
            observe_result = self.observe(act_result)
            
            if observe_result.get("success") and not observe_result.get("retry_required"):
                if not observe_result.get("should_continue", True):
                    logger.info("✅ Goal achieved!")
                    break
            
            # Update situation for next iteration
            current_situation = f"Previous: {next_action}. Result: {observe_result.get('observation', 'Completed')}"
        
        return {
            "iterations": iteration,
            "goal": goal,
            "final_situation": current_situation,
            "results": all_results,
            "success": all_results[-1].get("success", False) if all_results else False,
        }

    def _execute_phase(self, phase: int) -> Dict[str, Any]:
        """Execute a specific phase"""
        logger.info(f"Executing Phase {phase}...")
        
        self.current_phase = phase
        agent = self.PHASE_AGENT_MAP.get(phase, AgentRole.ORCHESTRATOR)
        
        # Check for phase executor script
        executor_path = self.workspace_path / "scripts" / "orchestrator" / "phase_executors" / f"phase_{phase}_executor.py"
        
        if executor_path.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(executor_path)],
                    capture_output=True,
                    text=True,
                    cwd=str(self.workspace_path),
                    timeout=600,
                )
                return {
                    "action": f"execute_phase_{phase}",
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None,
                    "timestamp": datetime.now().isoformat(),
                }
            except subprocess.TimeoutExpired:
                return {
                    "action": f"execute_phase_{phase}",
                    "success": False,
                    "error": "Phase execution timed out",
                    "timestamp": datetime.now().isoformat(),
                }
        
        return {
            "action": f"execute_phase_{phase}",
            "success": True,
            "output": f"Phase {phase} delegated to {agent.value}",
            "timestamp": datetime.now().isoformat(),
        }

    def _check_project_status(self) -> Dict[str, Any]:
        """Check current project status"""
        status_script = self.workspace_path / "scripts" / "check_project_status.py"
        
        if status_script.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(status_script)],
                    capture_output=True,
                    text=True,
                    cwd=str(self.workspace_path),
                    timeout=60,
                )
                return {
                    "action": "check_status",
                    "success": True,
                    "output": result.stdout,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                pass
        
        return {
            "action": "check_status",
            "success": True,
            "output": {
                "current_phase": self.current_phase,
                "tasks_pending": len([t for t in self.development_plan if t.status == TaskStatus.PENDING]),
                "tasks_completed": len([t for t in self.development_plan if t.status == TaskStatus.COMPLETED]),
                "agents_available": len(AgentRole),
            },
            "timestamp": datetime.now().isoformat(),
        }

    def _assign_agent(self, agent_name: str, task_id: str) -> Dict[str, Any]:
        """Assign an agent to a task"""
        try:
            agent = AgentRole(agent_name)
            
            for task in self.development_plan:
                if task.id == task_id:
                    task.assigned_agent = agent
                    task.updated_at = datetime.now().isoformat()
                    return {
                        "action": "assign_agent",
                        "success": True,
                        "output": f"Assigned {agent.value} to task {task_id}",
                        "timestamp": datetime.now().isoformat(),
                    }
            
            return {
                "action": "assign_agent",
                "success": False,
                "error": f"Task {task_id} not found",
                "timestamp": datetime.now().isoformat(),
            }
        except ValueError:
            return {
                "action": "assign_agent",
                "success": False,
                "error": f"Unknown agent: {agent_name}",
                "timestamp": datetime.now().isoformat(),
            }

    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """Extract JSON from text response"""
        # Try to find JSON object
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try parsing entire text
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return None

    def save_state(self, filepath: Optional[str] = None) -> Path:
        """Save current state to file"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"consolidation/gravity_agent_state_{timestamp}.json"
        
        state_path = self.workspace_path / filepath
        state_path.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            "timestamp": datetime.now().isoformat(),
            "current_phase": self.current_phase,
            "context": self.context,
            "development_plan": [t.to_dict() for t in self.development_plan],
            "execution_history": self.execution_history,
        }
        
        state_path.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
        logger.info(f"State saved to: {state_path}")
        return state_path

    def load_state(self, filepath: str) -> bool:
        """Load state from file"""
        state_path = self.workspace_path / filepath
        
        if not state_path.exists():
            logger.warning(f"State file not found: {state_path}")
            return False
        
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.current_phase = state.get("current_phase")
            self.context.update(state.get("context", {}))
            self.execution_history = state.get("execution_history", [])
            
            # Reconstruct development plan
            self.development_plan = []
            for task_data in state.get("development_plan", []):
                task_data["priority"] = TaskPriority(task_data["priority"])
                task_data["status"] = TaskStatus(task_data["status"])
                task_data["assigned_agent"] = AgentRole(task_data["assigned_agent"])
                self.development_plan.append(DevelopmentTask(**task_data))
            
            logger.info(f"State loaded from: {state_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return False


def main():
    """CLI interface for Gravity Development Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gravity Development Orchestrator Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a PR
  python gravity_development_agent.py --analyze-pr 87
  
  # Run ReAct cycle with a goal
  python gravity_development_agent.py --goal "Implement training system"
  
  # Check project status
  python gravity_development_agent.py --status
  
  # Execute a specific phase
  python gravity_development_agent.py --phase 0
"""
    )
    
    parser.add_argument("--analyze-pr", type=int, help="Analyze a specific PR by number")
    parser.add_argument("--goal", type=str, help="Goal for ReAct cycle")
    parser.add_argument("--status", action="store_true", help="Check project status")
    parser.add_argument("--phase", type=int, help="Execute a specific phase")
    parser.add_argument("--workspace", type=str, help="Workspace path")
    parser.add_argument("--save-state", type=str, help="Save state to file")
    parser.add_argument("--load-state", type=str, help="Load state from file")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = GravityDevelopmentAgent(workspace_path=args.workspace)
    
    # Load state if requested
    if args.load_state:
        agent.load_state(args.load_state)
    
    print("=" * 80)
    print("🌌 GRAVITY DEVELOPMENT ORCHESTRATOR AGENT")
    print("=" * 80)
    
    if args.analyze_pr:
        print(f"\n📊 Analyzing PR #{args.analyze_pr}...")
        analysis = agent.analyze_pr(args.analyze_pr)
        print(f"\n✅ Analysis complete!")
        print(f"   Title: {analysis.title}")
        print(f"   Status: {analysis.status}")
        print(f"   Files changed: {len(analysis.files_changed)}")
        print(f"   Affected phases: {analysis.affected_phases}")
        print(f"   Impact level: {analysis.impact_assessment.get('impact_level', 'unknown')}")
        
        # Generate tasks
        tasks = agent.generate_tasks_from_pr(analysis)
        print(f"\n📋 Generated {len(tasks)} tasks:")
        for task in tasks:
            print(f"   - {task.id}: {task.title} (Phase {task.phase}, {task.assigned_agent.value})")
    
    elif args.goal:
        print(f"\n🎯 Goal: {args.goal}")
        result = agent.react_cycle(args.goal)
        print(f"\n✅ ReAct cycle complete!")
        print(f"   Iterations: {result['iterations']}")
        print(f"   Success: {result['success']}")
    
    elif args.status:
        result = agent._check_project_status()
        print(f"\n📊 Project Status:")
        print(json.dumps(result.get("output", {}), indent=2))
    
    elif args.phase is not None:
        print(f"\n⚡ Executing Phase {args.phase}...")
        result = agent._execute_phase(args.phase)
        print(f"\n{'✅' if result['success'] else '❌'} Phase {args.phase} execution:")
        if result.get("output"):
            print(result["output"])
        if result.get("error"):
            print(f"Error: {result['error']}")
    
    else:
        print("\n💡 Usage:")
        print("   --analyze-pr <number>  Analyze a Pull Request")
        print("   --goal <goal>          Run ReAct cycle with a goal")
        print("   --status               Check project status")
        print("   --phase <number>       Execute a specific phase")
        print("\nRun with --help for more options.")
    
    # Save state if requested
    if args.save_state:
        agent.save_state(args.save_state)
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

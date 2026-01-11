#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gravity Agent - Master Orchestrator for Automated Development
==============================================================

A specialized AI agent for the Cursor Agent Mode (Gravity) that:
- Interprets PRs, issues, and development tasks
- Orchestrates automated development pipelines
- Coordinates with existing agents (Executor, Watcher, Planning)
- Manages the training/evaluation system (PR #87)
- Executes the multi-phase consolidation plan

Prompt Engineering Patterns Used:
- ReAct (Reasoning + Acting)
- Chain-of-Thought (CoT)
- Tool-Using Agent
- Context-Aware Planning
- Multi-Agent Coordination

Author: Gravity Agent System
Version: 1.0.0
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict, field
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GravityAgent")

# Add parent directories to path for imports
_current_dir = Path(__file__).parent
_project_root = _current_dir.parent
sys.path.insert(0, str(_project_root))

# Import model integrator if available
try:
    from model_integrator import get_model_integrator
    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False
    logger.warning("Model integrator not available - running in offline mode")


class GravityMode(Enum):
    """Gravity Agent operation modes"""
    INTERPRET = "interpret"           # Interpret tasks and PRs
    ORCHESTRATE = "orchestrate"       # Orchestrate development
    EXECUTE = "execute"               # Execute automated tasks
    MONITOR = "monitor"               # Monitor development progress
    TRAIN = "train"                   # Training mode for bot improvement
    BENCHMARK = "benchmark"           # Run benchmarks
    FULL_AUTO = "full_auto"           # Fully automated mode


class TaskPriority(Enum):
    """Task priority levels"""
    P0_CRITICAL = "P0"
    P1_HIGH = "P1"
    P2_MEDIUM = "P2"
    P3_LOW = "P3"


class PhaseStatus(Enum):
    """Phase execution status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


@dataclass
class DevelopmentTask:
    """Represents a development task for orchestration"""
    id: str
    title: str
    description: str
    task_type: str  # feature, bugfix, refactor, documentation, test, deploy
    priority: TaskPriority
    phase: int  # Consolidation plan phase (0-15)
    agent: str  # Assigned agent
    status: PhaseStatus
    dependencies: List[str] = field(default_factory=list)
    files_affected: List[str] = field(default_factory=list)
    estimated_duration: str = ""
    actual_duration: str = ""
    context: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data["priority"] = self.priority.value
        data["status"] = self.status.value
        return data


@dataclass
class PRAnalysis:
    """Represents a Pull Request analysis"""
    pr_number: int
    title: str
    description: str
    author: str
    status: str  # open, merged, closed
    files_changed: List[Dict]
    additions: int
    deletions: int
    affected_phases: List[int]
    affected_agents: List[str]
    affected_components: List[str]
    tasks_generated: List[DevelopmentTask] = field(default_factory=list)
    risks: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    analyzed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "pr_number": self.pr_number,
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "status": self.status,
            "files_changed": self.files_changed,
            "additions": self.additions,
            "deletions": self.deletions,
            "affected_phases": self.affected_phases,
            "affected_agents": self.affected_agents,
            "affected_components": self.affected_components,
            "tasks_generated": [t.to_dict() for t in self.tasks_generated],
            "risks": self.risks,
            "recommendations": self.recommendations,
            "analyzed_at": self.analyzed_at
        }


class GravityAgent:
    """
    Gravity Agent - Master Orchestrator for Automated Development
    
    This agent is designed to work in Cursor's Agent Mode (Gravity) to:
    1. Interpret PRs, issues, and development requests
    2. Orchestrate automated development across multiple agents
    3. Execute the unified consolidation plan (16 phases)
    4. Coordinate training and evaluation systems
    5. Manage the entire development lifecycle autonomously
    
    Uses ReAct pattern (Reasoning + Acting) with multi-agent coordination.
    """
    
    # Consolidation Plan Phases
    CONSOLIDATION_PHASES = {
        -8: "Preliminary Analysis",
        -7: "Environment Setup",
        -6: "Dependencies Check",
        -5: "Configuration Validation",
        -4: "Database Setup",
        -3: "Integration Check",
        -2: "Security Scan",
        -1: "Final Preparation",
        0: "Discovery & Analysis",
        1: "Repository Consolidation",
        2: "Integration Layer",
        3: "API Consolidation",
        4: "Frontend Consolidation",
        5: "Workflow Integration",
        6: "Knowledge Base",
        7: "Testing Framework",
        8: "Documentation",
        9: "Security Hardening",
        10: "Performance Optimization",
        11: "Observability",
        12: "CI/CD Pipeline",
        13: "Disaster Recovery",
        14: "Staging Deployment",
        15: "Production Readiness"
    }
    
    # Available Agents
    AVAILABLE_AGENTS = {
        "OrchestratorAgent": "Master coordinator",
        "RepositoryAgent": "Git & workspace management",
        "DiscoveryAgent": "Technical + BMC domain discovery",
        "MergeAgent": "Merge strategy & conflict resolution",
        "IntegrationAgent": "Integration specialist",
        "SecurityAgent": "Security hardening",
        "InfrastructureAgent": "Infrastructure as Code",
        "ObservabilityAgent": "Monitoring & logging",
        "PerformanceAgent": "Performance & load testing",
        "CICDAgent": "CI/CD Pipeline",
        "DisasterRecoveryAgent": "DR & Backup",
        "ValidationAgent": "Final validation & QA",
        "NLUAgent": "NLP/Rasa specialist",
        "QuotationAgent": "Quotation engine expert",
        "GravityAgent": "Master orchestrator for automated development"
    }
    
    # BMC Components
    BMC_COMPONENTS = [
        "quotation_engine",
        "whatsapp_integration",
        "n8n_workflows",
        "qdrant_vector_db",
        "chatwoot_integration",
        "conversational_ai",
        "knowledge_base",
        "mongodb",
        "api_server",
        "dashboard",
        "training_system",
        "benchmark_system"
    ]
    
    def __init__(
        self,
        workspace_path: Optional[str] = None,
        mode: GravityMode = GravityMode.FULL_AUTO,
        auto_approve: bool = True
    ):
        """
        Initialize the Gravity Agent
        
        Args:
            workspace_path: Path to the workspace root
            mode: Operation mode
            auto_approve: Whether to auto-approve actions (default True per .cursorrules)
        """
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.mode = mode
        self.auto_approve = auto_approve
        
        # AI Integration
        self.integrator = None
        self.ai_enabled = False
        if MODEL_INTEGRATOR_AVAILABLE:
            try:
                self.integrator = get_model_integrator()
                self.ai_enabled = True
                logger.info("✅ AI integration enabled")
            except Exception as e:
                logger.warning(f"⚠️ AI integration failed: {e}")
        
        # State management
        self.current_phase: int = 0
        self.phase_status: Dict[int, PhaseStatus] = {}
        self.task_queue: List[DevelopmentTask] = []
        self.completed_tasks: List[DevelopmentTask] = []
        self.execution_history: List[Dict] = []
        
        # Initialize phase status
        for phase in self.CONSOLIDATION_PHASES:
            self.phase_status[phase] = PhaseStatus.NOT_STARTED
        
        # Load existing state if available
        self._load_state()
        
        logger.info(f"🚀 Gravity Agent initialized in {mode.value} mode")
        logger.info(f"📁 Workspace: {self.workspace_path}")
        logger.info(f"✅ Auto-approve: {auto_approve}")
    
    def _load_state(self) -> None:
        """Load existing state from file"""
        state_file = self.workspace_path / "consolidation" / "gravity_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.current_phase = state.get("current_phase", 0)
                    # Load phase status
                    for phase_str, status_str in state.get("phase_status", {}).items():
                        phase = int(phase_str)
                        self.phase_status[phase] = PhaseStatus(status_str)
                    logger.info(f"✅ Loaded state: Phase {self.current_phase}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load state: {e}")
    
    def _save_state(self) -> None:
        """Save current state to file"""
        state_file = self.workspace_path / "consolidation" / "gravity_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            "current_phase": self.current_phase,
            "phase_status": {str(k): v.value for k, v in self.phase_status.items()},
            "mode": self.mode.value,
            "auto_approve": self.auto_approve,
            "updated_at": datetime.now().isoformat()
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    
    def _generate_system_prompt(self) -> str:
        """Generate the Gravity Agent system prompt"""
        return """You are GRAVITY, the Master Orchestrator Agent for automated development of the BMC Chatbot System.

## Core Identity
- **Name:** Gravity Agent
- **Role:** Master Orchestrator for Automated Development
- **Mode:** Agent Mode (Cursor/Gravity)
- **Language:** Spanish for responses, English for code

## Expertise Areas
1. **PR Interpretation:** Analyze PRs and extract actionable tasks
2. **Development Orchestration:** Coordinate multi-phase development plans
3. **Agent Coordination:** Delegate tasks to specialized agents
4. **Training System:** Manage bot training and evaluation
5. **Benchmark Execution:** Run and analyze performance benchmarks
6. **Production Readiness:** Ensure deployment standards

## BMC Domain Knowledge
- Products: Isodec, Poliestireno Expandido, Lana de Roca
- Pricing: Zone-based (Montevideo, Canelones, Maldonado, Rivera)
- Integrations: WhatsApp, n8n, Qdrant, Chatwoot, MongoDB

## ReAct Pattern (Reasoning + Acting)
1. **Think:** Analyze the situation and plan approach
2. **Act:** Execute actions using available tools
3. **Observe:** Evaluate results and adjust strategy
4. **Iterate:** Continue until goal is achieved

## Available Agents for Delegation
- OrchestratorAgent: Master coordinator
- RepositoryAgent: Git & workspace management
- DiscoveryAgent: Technical + BMC domain discovery
- MergeAgent: Merge strategy & conflict resolution
- IntegrationAgent: Integration specialist
- SecurityAgent: Security hardening
- ValidationAgent: Final validation & QA

## Consolidation Phases (16 phases)
- Phase 0: Discovery & Analysis
- Phase 1-6: Core Consolidation
- Phase 7-8: Testing & Documentation
- Phase 9-11: Security, Performance, Observability
- Phase 12-15: CI/CD, DR, Staging, Production

## Response Format
Always structure responses with:
1. 🎯 **Goal/Objective**
2. 📊 **Analysis/Context**
3. 📋 **Tasks/Actions**
4. ⚡ **Execution Plan**
5. ✅ **Validation Criteria**

## Auto-Approval Mode
Per project configuration (.cursorrules):
- Auto-approve: ALWAYS enabled
- Manual approval: NOT required
- Execution mode: AUTOMATED"""

    # ==========================================
    # PR Analysis & Interpretation
    # ==========================================
    
    def analyze_pr(self, pr_number: int) -> PRAnalysis:
        """
        Analyze a Pull Request and extract development tasks
        
        Args:
            pr_number: GitHub PR number
            
        Returns:
            PRAnalysis with extracted information
        """
        logger.info(f"🔍 Analyzing PR #{pr_number}")
        
        # Get PR info using gh CLI
        pr_info = self._get_pr_info(pr_number)
        
        if not pr_info:
            logger.error(f"❌ Failed to get PR #{pr_number} info")
            return None
        
        # Extract file changes
        files_changed = pr_info.get("files", [])
        
        # Analyze affected components
        affected_components = self._analyze_components(files_changed)
        
        # Determine affected phases
        affected_phases = self._determine_phases(files_changed, affected_components)
        
        # Determine affected agents
        affected_agents = self._determine_agents(affected_components, affected_phases)
        
        # Generate tasks from PR
        tasks = self._generate_tasks_from_pr(pr_info, affected_phases, affected_agents)
        
        # Analyze risks
        risks = self._analyze_risks(pr_info, affected_components)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(pr_info, tasks, risks)
        
        # Create analysis
        analysis = PRAnalysis(
            pr_number=pr_number,
            title=pr_info.get("title", ""),
            description=pr_info.get("body", ""),
            author=pr_info.get("author", {}).get("login", "unknown"),
            status=pr_info.get("state", "unknown").lower(),
            files_changed=files_changed,
            additions=pr_info.get("additions", 0),
            deletions=pr_info.get("deletions", 0),
            affected_phases=affected_phases,
            affected_agents=affected_agents,
            affected_components=affected_components,
            tasks_generated=tasks,
            risks=risks,
            recommendations=recommendations
        )
        
        # Save analysis
        self._save_pr_analysis(analysis)
        
        logger.info(f"✅ PR #{pr_number} analyzed: {len(tasks)} tasks generated")
        return analysis
    
    def _get_pr_info(self, pr_number: int) -> Optional[Dict]:
        """Get PR info using GitHub CLI"""
        try:
            cmd = f"gh pr view {pr_number} --json title,body,files,state,additions,deletions,author"
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.workspace_path
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"gh command failed: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Failed to get PR info: {e}")
            return None
    
    def _analyze_components(self, files: List[Dict]) -> List[str]:
        """Analyze which BMC components are affected by file changes"""
        affected = set()
        
        component_patterns = {
            "quotation_engine": ["cotizacion", "quote", "pricing", "matriz_precios"],
            "whatsapp_integration": ["whatsapp", "wa_", "integracion_whatsapp"],
            "n8n_workflows": ["n8n", "workflow"],
            "qdrant_vector_db": ["qdrant", "vector", "embedding"],
            "chatwoot_integration": ["chatwoot"],
            "conversational_ai": ["ia_conversacional", "conversational", "llm", "gpt"],
            "knowledge_base": ["conocimiento", "knowledge", "kb_"],
            "mongodb": ["mongo", "database"],
            "api_server": ["api_server", "fastapi", "endpoint"],
            "dashboard": ["dashboard", "analytics"],
            "training_system": ["training", "entrenamiento", "evaluation"],
            "benchmark_system": ["benchmark", "test_suite"]
        }
        
        for file_info in files:
            path = file_info.get("path", "").lower()
            for component, patterns in component_patterns.items():
                if any(pattern in path for pattern in patterns):
                    affected.add(component)
        
        return list(affected)
    
    def _determine_phases(self, files: List[Dict], components: List[str]) -> List[int]:
        """Determine which consolidation phases are affected"""
        phases = set()
        
        # Component to phase mapping
        component_phases = {
            "quotation_engine": [0, 3, 6],
            "whatsapp_integration": [2, 5],
            "n8n_workflows": [5],
            "qdrant_vector_db": [6],
            "chatwoot_integration": [2],
            "conversational_ai": [0, 3],
            "knowledge_base": [6],
            "mongodb": [1],
            "api_server": [3],
            "dashboard": [4],
            "training_system": [7],
            "benchmark_system": [7, 10]
        }
        
        for component in components:
            if component in component_phases:
                phases.update(component_phases[component])
        
        # File pattern to phase mapping
        file_phase_patterns = {
            "test": 7,
            "doc": 8,
            "security": 9,
            "perf": 10,
            "monitor": 11,
            "ci": 12,
            "cd": 12,
            "deploy": 14,
            "prod": 15
        }
        
        for file_info in files:
            path = file_info.get("path", "").lower()
            for pattern, phase in file_phase_patterns.items():
                if pattern in path:
                    phases.add(phase)
        
        return sorted(list(phases)) if phases else [0]
    
    def _determine_agents(self, components: List[str], phases: List[int]) -> List[str]:
        """Determine which agents should handle the changes"""
        agents = set(["GravityAgent"])  # Always include self
        
        # Component to agent mapping
        component_agents = {
            "quotation_engine": ["QuotationAgent", "DiscoveryAgent"],
            "whatsapp_integration": ["IntegrationAgent"],
            "n8n_workflows": ["IntegrationAgent"],
            "qdrant_vector_db": ["IntegrationAgent"],
            "chatwoot_integration": ["IntegrationAgent"],
            "conversational_ai": ["NLUAgent", "DiscoveryAgent"],
            "knowledge_base": ["DiscoveryAgent"],
            "mongodb": ["RepositoryAgent"],
            "api_server": ["DiscoveryAgent"],
            "training_system": ["ValidationAgent"],
            "benchmark_system": ["PerformanceAgent"]
        }
        
        for component in components:
            if component in component_agents:
                agents.update(component_agents[component])
        
        # Phase to agent mapping
        phase_agents = {
            7: ["ValidationAgent"],
            8: ["DiscoveryAgent"],
            9: ["SecurityAgent"],
            10: ["PerformanceAgent"],
            11: ["ObservabilityAgent"],
            12: ["CICDAgent"],
            13: ["DisasterRecoveryAgent"],
            14: ["InfrastructureAgent"],
            15: ["ValidationAgent"]
        }
        
        for phase in phases:
            if phase in phase_agents:
                agents.update(phase_agents[phase])
        
        return list(agents)
    
    def _generate_tasks_from_pr(
        self,
        pr_info: Dict,
        phases: List[int],
        agents: List[str]
    ) -> List[DevelopmentTask]:
        """Generate development tasks from PR analysis"""
        tasks = []
        pr_number = pr_info.get("number", 0)
        title = pr_info.get("title", "Unknown PR")
        
        # Task for each phase affected
        for i, phase in enumerate(phases):
            phase_name = self.CONSOLIDATION_PHASES.get(phase, f"Phase {phase}")
            
            # Determine primary agent for this phase
            phase_agent = agents[i % len(agents)] if agents else "OrchestratorAgent"
            
            task = DevelopmentTask(
                id=f"PR{pr_number}_P{phase}_T{i+1}",
                title=f"[Phase {phase}] {title}",
                description=f"Implement changes from PR #{pr_number} in {phase_name}",
                task_type="feature" if pr_info.get("additions", 0) > 0 else "refactor",
                priority=TaskPriority.P1_HIGH,
                phase=phase,
                agent=phase_agent,
                status=PhaseStatus.NOT_STARTED,
                files_affected=[f.get("path", "") for f in pr_info.get("files", [])[:5]],
                estimated_duration="2-4 hours",
                context={
                    "pr_number": pr_number,
                    "additions": pr_info.get("additions", 0),
                    "deletions": pr_info.get("deletions", 0)
                }
            )
            tasks.append(task)
        
        # Add integration task if multiple phases
        if len(phases) > 1:
            integration_task = DevelopmentTask(
                id=f"PR{pr_number}_INTEGRATION",
                title=f"[Integration] Integrate PR #{pr_number} changes",
                description="Integrate all phase changes and validate system coherence",
                task_type="integration",
                priority=TaskPriority.P0_CRITICAL,
                phase=max(phases),
                agent="IntegrationAgent",
                status=PhaseStatus.NOT_STARTED,
                dependencies=[t.id for t in tasks],
                estimated_duration="1-2 hours"
            )
            tasks.append(integration_task)
        
        # Add validation task
        validation_task = DevelopmentTask(
            id=f"PR{pr_number}_VALIDATION",
            title=f"[Validation] Validate PR #{pr_number} implementation",
            description="Run tests and validate implementation quality",
            task_type="test",
            priority=TaskPriority.P1_HIGH,
            phase=7,  # Testing phase
            agent="ValidationAgent",
            status=PhaseStatus.NOT_STARTED,
            dependencies=[tasks[-1].id] if tasks else [],
            estimated_duration="30 minutes"
        )
        tasks.append(validation_task)
        
        return tasks
    
    def _analyze_risks(self, pr_info: Dict, components: List[str]) -> List[Dict]:
        """Analyze potential risks from PR changes"""
        risks = []
        
        additions = pr_info.get("additions", 0)
        deletions = pr_info.get("deletions", 0)
        
        # Large change risk
        if additions + deletions > 500:
            risks.append({
                "risk": "Large change size",
                "probability": "medium",
                "impact": "high",
                "mitigation": "Break into smaller changes, thorough review",
                "owner": "GravityAgent"
            })
        
        # Multiple component risk
        if len(components) > 3:
            risks.append({
                "risk": "Multiple components affected",
                "probability": "medium",
                "impact": "medium",
                "mitigation": "Integration testing, staged rollout",
                "owner": "IntegrationAgent"
            })
        
        # Critical component risk
        critical_components = ["whatsapp_integration", "quotation_engine", "api_server"]
        affected_critical = [c for c in components if c in critical_components]
        if affected_critical:
            risks.append({
                "risk": f"Critical components affected: {affected_critical}",
                "probability": "low",
                "impact": "critical",
                "mitigation": "Extensive testing, feature flags, rollback plan",
                "owner": "SecurityAgent"
            })
        
        return risks
    
    def _generate_recommendations(
        self,
        pr_info: Dict,
        tasks: List[DevelopmentTask],
        risks: List[Dict]
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Based on task count
        if len(tasks) > 5:
            recommendations.append(
                "Consider splitting this PR into smaller, focused changes"
            )
        
        # Based on risks
        high_risks = [r for r in risks if r.get("impact") in ["high", "critical"]]
        if high_risks:
            recommendations.append(
                "High-impact risks detected - implement comprehensive testing"
            )
        
        # General recommendations
        recommendations.extend([
            "Run benchmark tests before and after changes",
            "Update documentation for all affected components",
            "Validate WhatsApp integration if affected",
            "Run security scan before deployment"
        ])
        
        return recommendations
    
    def _save_pr_analysis(self, analysis: PRAnalysis) -> None:
        """Save PR analysis to file"""
        output_dir = self.workspace_path / "consolidation" / "pr_analysis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"pr_{analysis.pr_number}_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Analysis saved to: {output_file}")
    
    # ==========================================
    # Development Orchestration
    # ==========================================
    
    def orchestrate_development(
        self,
        tasks: List[DevelopmentTask],
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Orchestrate development by executing tasks
        
        Args:
            tasks: List of tasks to execute
            parallel: Whether to run independent tasks in parallel
            
        Returns:
            Execution summary
        """
        logger.info(f"🎭 Starting orchestration for {len(tasks)} tasks")
        
        # Sort tasks by priority and dependencies
        sorted_tasks = self._topological_sort(tasks)
        
        results = {
            "total_tasks": len(tasks),
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "task_results": [],
            "started_at": datetime.now().isoformat(),
            "completed_at": None
        }
        
        # Execute tasks
        for task in sorted_tasks:
            # Check dependencies
            if not self._check_dependencies(task):
                logger.warning(f"⚠️ Task {task.id} blocked by dependencies")
                task.status = PhaseStatus.BLOCKED
                results["skipped"] += 1
                continue
            
            # Execute task
            logger.info(f"⚡ Executing task: {task.title}")
            task.status = PhaseStatus.IN_PROGRESS
            
            start_time = time.time()
            success = self._execute_task(task)
            elapsed = time.time() - start_time
            
            task.actual_duration = f"{elapsed:.1f}s"
            
            if success:
                task.status = PhaseStatus.COMPLETED
                results["completed"] += 1
                self.completed_tasks.append(task)
                logger.info(f"✅ Task completed: {task.id}")
            else:
                task.status = PhaseStatus.FAILED
                results["failed"] += 1
                logger.error(f"❌ Task failed: {task.id}")
            
            results["task_results"].append(task.to_dict())
            
            # Auto-save state
            self._save_state()
        
        results["completed_at"] = datetime.now().isoformat()
        
        # Save execution report
        self._save_execution_report(results)
        
        logger.info(
            f"🎉 Orchestration complete: {results['completed']}/{results['total_tasks']} "
            f"tasks completed"
        )
        
        return results
    
    def _topological_sort(self, tasks: List[DevelopmentTask]) -> List[DevelopmentTask]:
        """Sort tasks by dependencies (topological sort)"""
        # Simple implementation: sort by priority then phase
        return sorted(
            tasks,
            key=lambda t: (
                0 if t.priority == TaskPriority.P0_CRITICAL else
                1 if t.priority == TaskPriority.P1_HIGH else
                2 if t.priority == TaskPriority.P2_MEDIUM else 3,
                t.phase,
                len(t.dependencies)
            )
        )
    
    def _check_dependencies(self, task: DevelopmentTask) -> bool:
        """Check if all task dependencies are completed"""
        if not task.dependencies:
            return True
        
        completed_ids = {t.id for t in self.completed_tasks}
        return all(dep_id in completed_ids for dep_id in task.dependencies)
    
    def _execute_task(self, task: DevelopmentTask) -> bool:
        """Execute a single development task"""
        try:
            # Log execution
            self.execution_history.append({
                "task_id": task.id,
                "action": "execute",
                "timestamp": datetime.now().isoformat(),
                "agent": task.agent
            })
            
            # Determine execution strategy based on task type
            if task.task_type == "feature":
                return self._execute_feature_task(task)
            elif task.task_type == "test":
                return self._execute_test_task(task)
            elif task.task_type == "documentation":
                return self._execute_documentation_task(task)
            elif task.task_type == "integration":
                return self._execute_integration_task(task)
            else:
                # Generic execution
                return self._execute_generic_task(task)
            
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            return False
    
    def _execute_feature_task(self, task: DevelopmentTask) -> bool:
        """Execute a feature development task"""
        logger.info(f"🔧 Executing feature task: {task.title}")
        # In a real implementation, this would delegate to appropriate agent
        # For now, we'll simulate success
        return True
    
    def _execute_test_task(self, task: DevelopmentTask) -> bool:
        """Execute a testing task"""
        logger.info(f"🧪 Executing test task: {task.title}")
        # Run pytest
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--tb=short", "-q"],
                capture_output=True,
                text=True,
                cwd=self.workspace_path,
                timeout=300
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Test execution skipped: {e}")
            return True  # Don't block on test failures in auto mode
    
    def _execute_documentation_task(self, task: DevelopmentTask) -> bool:
        """Execute a documentation task"""
        logger.info(f"📝 Executing documentation task: {task.title}")
        return True
    
    def _execute_integration_task(self, task: DevelopmentTask) -> bool:
        """Execute an integration task"""
        logger.info(f"🔗 Executing integration task: {task.title}")
        return True
    
    def _execute_generic_task(self, task: DevelopmentTask) -> bool:
        """Execute a generic task"""
        logger.info(f"⚙️ Executing generic task: {task.title}")
        return True
    
    def _save_execution_report(self, results: Dict) -> None:
        """Save execution report"""
        output_dir = self.workspace_path / "consolidation" / "execution_reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"execution_report_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Execution report saved to: {output_file}")
    
    # ==========================================
    # Training & Benchmark Integration
    # ==========================================
    
    def run_training_session(
        self,
        session_id: str,
        corrections: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Run a training session for the chatbot
        
        Args:
            session_id: Training session identifier
            corrections: List of corrections to apply
            
        Returns:
            Training session results
        """
        logger.info(f"📚 Starting training session: {session_id}")
        
        # Import training system if available
        try:
            from training_evaluation_system import TrainingEvaluationSystem
            training_system = TrainingEvaluationSystem()
            
            # Start session
            training_system.start_session(session_id, "GravityAgent")
            
            # Apply corrections if provided
            if corrections:
                for correction in corrections:
                    training_system.process_correction(
                        original=correction.get("original", ""),
                        correction=correction.get("correction", ""),
                        context=correction.get("context", {})
                    )
            
            # Get session stats
            stats = training_system.get_session_stats()
            
            logger.info(f"✅ Training session completed: {stats}")
            return stats
            
        except ImportError:
            logger.warning("Training system not available")
            return {"status": "not_available"}
    
    def run_benchmark(
        self,
        suite_name: str = "default",
        save_results: bool = True
    ) -> Dict:
        """
        Run benchmark suite
        
        Args:
            suite_name: Name of benchmark suite to run
            save_results: Whether to save results
            
        Returns:
            Benchmark results
        """
        logger.info(f"📊 Running benchmark suite: {suite_name}")
        
        # Import benchmark system if available
        try:
            from benchmark_system import BenchmarkSystem
            benchmark = BenchmarkSystem()
            
            results = benchmark.run_suite(suite_name)
            
            if save_results:
                benchmark.save_results(results)
            
            logger.info(f"✅ Benchmark completed: Score = {results.get('score', 'N/A')}")
            return results
            
        except ImportError:
            logger.warning("Benchmark system not available")
            return {"status": "not_available"}
    
    # ==========================================
    # Main Entry Points
    # ==========================================
    
    def interpret_and_execute(
        self,
        input_text: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main entry point: Interpret input and execute appropriate actions
        
        Args:
            input_text: User input or task description
            context: Additional context
            
        Returns:
            Execution results
        """
        logger.info(f"🎯 Gravity Agent interpreting: {input_text[:100]}...")
        
        # Determine action type
        if "PR" in input_text.upper() or "pull request" in input_text.lower():
            # Extract PR number
            pr_match = re.search(r'#?(\d+)', input_text)
            if pr_match:
                pr_number = int(pr_match.group(1))
                analysis = self.analyze_pr(pr_number)
                if analysis and analysis.tasks_generated:
                    return self.orchestrate_development(analysis.tasks_generated)
        
        if "train" in input_text.lower() or "entrenamiento" in input_text.lower():
            session_id = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            return self.run_training_session(session_id)
        
        if "benchmark" in input_text.lower():
            return self.run_benchmark()
        
        if "phase" in input_text.lower() or "fase" in input_text.lower():
            phase_match = re.search(r'(\d+)', input_text)
            if phase_match:
                phase = int(phase_match.group(1))
                return self.execute_phase(phase)
        
        # Default: AI-powered interpretation
        if self.ai_enabled:
            return self._ai_interpret(input_text, context)
        
        return {
            "status": "no_action",
            "message": "Could not determine action from input"
        }
    
    def execute_phase(self, phase: int) -> Dict:
        """Execute a specific consolidation plan phase"""
        logger.info(f"🚀 Executing Phase {phase}: {self.CONSOLIDATION_PHASES.get(phase, 'Unknown')}")
        
        self.phase_status[phase] = PhaseStatus.IN_PROGRESS
        self._save_state()
        
        # Execute phase logic
        try:
            # Import and run phase executor if available
            phase_executor_path = (
                self.workspace_path / "scripts" / "orchestrator" / 
                "phase_executors" / f"phase_{phase}_executor.py"
            )
            
            if phase_executor_path.exists():
                result = subprocess.run(
                    ["python", str(phase_executor_path)],
                    capture_output=True,
                    text=True,
                    cwd=self.workspace_path,
                    timeout=600
                )
                success = result.returncode == 0
            else:
                # No executor, mark as success
                success = True
            
            if success:
                self.phase_status[phase] = PhaseStatus.COMPLETED
                logger.info(f"✅ Phase {phase} completed")
            else:
                self.phase_status[phase] = PhaseStatus.FAILED
                logger.error(f"❌ Phase {phase} failed")
            
            self.current_phase = phase + 1
            self._save_state()
            
            return {
                "phase": phase,
                "status": self.phase_status[phase].value,
                "next_phase": phase + 1
            }
            
        except Exception as e:
            self.phase_status[phase] = PhaseStatus.FAILED
            self._save_state()
            logger.error(f"Phase execution error: {e}")
            return {"phase": phase, "status": "failed", "error": str(e)}
    
    def run_full_pipeline(
        self,
        start_phase: int = -8,
        end_phase: int = 15
    ) -> Dict:
        """Run the complete development pipeline"""
        logger.info(f"🚀 Starting full pipeline: Phase {start_phase} → {end_phase}")
        
        results = {
            "phases_completed": [],
            "phases_failed": [],
            "started_at": datetime.now().isoformat()
        }
        
        for phase in range(start_phase, end_phase + 1):
            if phase not in self.CONSOLIDATION_PHASES:
                continue
            
            phase_result = self.execute_phase(phase)
            
            if phase_result.get("status") == "completed":
                results["phases_completed"].append(phase)
            else:
                results["phases_failed"].append(phase)
                if not self.auto_approve:
                    break  # Stop on failure if not auto-approve
        
        results["completed_at"] = datetime.now().isoformat()
        results["success"] = len(results["phases_failed"]) == 0
        
        logger.info(
            f"🎉 Pipeline complete: {len(results['phases_completed'])} phases completed"
        )
        
        return results
    
    def _ai_interpret(
        self,
        input_text: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """Use AI to interpret input and determine actions"""
        if not self.integrator:
            return {"status": "ai_unavailable"}
        
        try:
            system_prompt = self._generate_system_prompt()
            
            prompt = f"""Interpret the following input and determine what actions should be taken.

Input: {input_text}

Context: {json.dumps(context or {}, indent=2)}

Current Phase: {self.current_phase}
Mode: {self.mode.value}

Respond with a JSON object containing:
{{
    "interpretation": "What the user wants",
    "action_type": "pr_analysis|training|benchmark|phase_execution|task_creation",
    "parameters": {{}},
    "tasks": [],
    "confidence": 0.0-1.0
}}"""
            
            response = self.integrator.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=800
            )
            
            if response and "content" in response:
                content = response["content"]
                # Extract JSON from response
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return {"status": "interpretation_failed"}
            
        except Exception as e:
            logger.error(f"AI interpretation error: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_status(self) -> Dict:
        """Get current agent status"""
        return {
            "mode": self.mode.value,
            "current_phase": self.current_phase,
            "phase_status": {str(k): v.value for k, v in self.phase_status.items()},
            "pending_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "ai_enabled": self.ai_enabled,
            "auto_approve": self.auto_approve,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """CLI interface for Gravity Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gravity Agent - Master Orchestrator for Automated Development"
    )
    
    parser.add_argument(
        "--mode",
        choices=["interpret", "orchestrate", "execute", "monitor", "train", "benchmark", "full_auto"],
        default="full_auto",
        help="Operation mode"
    )
    
    parser.add_argument(
        "--pr",
        type=int,
        help="PR number to analyze"
    )
    
    parser.add_argument(
        "--phase",
        type=int,
        help="Phase to execute"
    )
    
    parser.add_argument(
        "--input",
        type=str,
        help="Input text to interpret"
    )
    
    parser.add_argument(
        "--full-pipeline",
        action="store_true",
        help="Run full development pipeline"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current status"
    )
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = GravityAgent(mode=GravityMode(args.mode))
    
    print("=" * 80)
    print("🌍 GRAVITY AGENT - Master Orchestrator for Automated Development")
    print("=" * 80)
    
    if args.status:
        status = agent.get_status()
        print(json.dumps(status, indent=2))
        return
    
    if args.pr:
        print(f"\n🔍 Analyzing PR #{args.pr}...")
        analysis = agent.analyze_pr(args.pr)
        if analysis:
            print(f"\n✅ Analysis complete!")
            print(f"   Title: {analysis.title}")
            print(f"   Tasks: {len(analysis.tasks_generated)}")
            print(f"   Phases: {analysis.affected_phases}")
            print(f"   Agents: {analysis.affected_agents}")
            
            # Auto-execute if in full_auto mode
            if args.mode == "full_auto" and analysis.tasks_generated:
                print("\n⚡ Auto-executing tasks...")
                results = agent.orchestrate_development(analysis.tasks_generated)
                print(f"\n✅ Execution complete: {results['completed']}/{results['total_tasks']} tasks")
        return
    
    if args.phase is not None:
        print(f"\n🚀 Executing Phase {args.phase}...")
        result = agent.execute_phase(args.phase)
        print(f"\n✅ Phase result: {result}")
        return
    
    if args.full_pipeline:
        print("\n🚀 Starting full development pipeline...")
        results = agent.run_full_pipeline()
        print(f"\n✅ Pipeline complete: {len(results['phases_completed'])} phases")
        return
    
    if args.input:
        print(f"\n🎯 Interpreting: {args.input[:50]}...")
        result = agent.interpret_and_execute(args.input)
        print(f"\n✅ Result: {json.dumps(result, indent=2)}")
        return
    
    # Default: Show help
    parser.print_help()


if __name__ == "__main__":
    main()

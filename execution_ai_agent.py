#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Execution Agent for Chatbot System
=====================================

An intelligent agent that helps with:
- System execution review and monitoring
- Installation guidance and automation
- Configuration setup and validation
- Step-by-step suggestions
- Progress tracking and follow-up

Based on Prompt Engineering Knowledge Base patterns:
- ReAct (Reasoning + Acting)
- Chain-of-Thought
- Tool-Using Agent
- Context-Aware Planning
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

# Import model integrator if available
try:
    from model_integrator import get_model_integrator

    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False

# Import execution system components
try:
    from ejecutor_completo import (
        SystemReviewer,
        SystemInstaller,
        ServiceManager,
        SystemExecutor,
        StatusReporter,
        print_success,
        print_warning,
        print_error,
        print_info,
        print_header,
    )

    EXECUTOR_AVAILABLE = True
except ImportError:
    EXECUTOR_AVAILABLE = False

    # Dummy functions if not available
    def print_success(text):
        print(f"✅ {text}")

    def print_warning(text):
        print(f"⚠️  {text}")

    def print_error(text):
        print(f"❌ {text}")

    def print_info(text):
        print(f"ℹ️  {text}")

    def print_header(text):
        print(f"\n{'=' * 80}\n{text}\n{'=' * 80}\n")


class TaskStatus(Enum):
    """Task execution status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    """Task priority levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ExecutionTask:
    """Represents a task in the execution plan"""

    id: str
    title: str
    description: str
    category: str  # review, install, config, execute, monitor
    priority: TaskPriority
    status: TaskStatus
    dependencies: List[str]
    estimated_time: Optional[str] = None
    actual_time: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    suggestions: List[str] = None
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data["priority"] = self.priority.value
        data["status"] = self.status.value
        return data


class ExecutionAIAgent:
    """
    AI Agent for Chatbot System Execution

    Uses ReAct pattern (Reasoning + Acting) with:
    - Think: Analyze situation and plan approach
    - Act: Execute actions using available tools
    - Observe: Evaluate results and adjust strategy
    """

    def __init__(self, system_context: Optional[Dict] = None):
        """Initialize the AI agent"""
        self.integrator = None
        self.enabled = False
        self.system_context = system_context or {}
        self.execution_plan: List[ExecutionTask] = []
        self.execution_history: List[Dict] = []
        self.monitoring_active = False

        # Initialize AI integrator
        if MODEL_INTEGRATOR_AVAILABLE:
            try:
                self.integrator = get_model_integrator()
                self.enabled = True
            except Exception as e:
                print_warning(f"IA no disponible: {e}")
                self.enabled = False

        # Initialize execution components
        if EXECUTOR_AVAILABLE:
            self.reviewer = SystemReviewer()
            self.installer = SystemInstaller()
            self.service_manager = ServiceManager()
            self.executor = SystemExecutor()
            self.reporter = StatusReporter()
        else:
            self.reviewer = None
            self.installer = None
            self.service_manager = None
            self.executor = None
            self.reporter = None

    def is_available(self) -> bool:
        """Check if AI is available"""
        return self.enabled and self.integrator is not None

    def _generate_system_prompt(self, mode: str = "react") -> str:
        """
        Generate system prompt based on prompt engineering patterns

        Args:
            mode: Prompt pattern (react, cot, tool_using, context_aware)
        """
        base_prompt = """You are an expert AI Execution Agent specialized in chatbot system deployment and management.

Your expertise includes:
- System architecture review and validation
- Dependency installation and configuration
- Service setup (MongoDB, Docker, APIs)
- Execution monitoring and troubleshooting
- Step-by-step guidance and suggestions

You use the ReAct (Reasoning + Acting) pattern:
1. **Think:** Analyze the situation and plan your approach
2. **Act:** Execute actions using available tools
3. **Observe:** Evaluate results and adjust strategy

Available tools:
- SystemReviewer: Review system state and detect issues
- SystemInstaller: Install dependencies automatically
- ServiceManager: Configure services (MongoDB, etc.)
- SystemExecutor: Execute the chatbot system
- StatusReporter: Generate status reports
- FileSystem: Read/write configuration files
- CommandExecutor: Run system commands

Working style:
- Methodical and thorough
- Evidence-based decisions
- Clear communication in Spanish
- Proactive problem-solving
- Progress tracking and follow-up

When responding:
1. Understand the current situation
2. Identify what needs to be done
3. Break down into actionable steps
4. Execute or suggest execution
5. Monitor and verify results
6. Provide clear feedback"""

        if mode == "cot":
            base_prompt += """

You solve problems step-by-step:
1. Break down the problem into sub-problems
2. Analyze each sub-problem independently
3. Synthesize solutions
4. Verify the complete solution
5. Reflect on the approach"""

        return base_prompt

    def think(self, situation: str, context: Optional[Dict] = None) -> Dict:
        """
        Think phase: Analyze situation and plan approach

        Args:
            situation: Current situation description
            context: Additional context

        Returns:
            Dict with analysis, plan, and next steps
        """
        if not self.is_available():
            return {"analysis": situation, "plan": [], "next_steps": [], "confidence": 0.0}

        try:
            system_prompt = self._generate_system_prompt("react")

            context_str = json.dumps(context or self.system_context, indent=2, default=str)
            prompt = f"""Situation: {situation}

Context:
{context_str}

Analyze this situation and create an execution plan. Consider:
1. What is the current state?
2. What needs to be done?
3. What are the dependencies?
4. What are potential issues?
5. What is the recommended approach?

Respond in JSON format with:
{{
    "analysis": "Detailed analysis of the situation",
    "plan": ["step1", "step2", "step3"],
    "next_steps": ["immediate action 1", "immediate action 2"],
    "potential_issues": ["issue1", "issue2"],
    "recommendations": ["recommendation1", "recommendation2"],
    "confidence": 0.0-1.0
}}"""

            response = self.integrator.generate(
                prompt=prompt, system_prompt=system_prompt, temperature=0.3, max_tokens=800
            )

            if response and "content" in response:
                content = response["content"].strip()
                result = self._extract_json_from_text(content)
                if result:
                    return result

            # Fallback: parse text response
            return {
                "analysis": content if response else situation,
                "plan": [],
                "next_steps": [],
                "confidence": 0.5,
            }
        except Exception as e:
            print_warning(f"Error en fase Think: {e}")
            return {"analysis": situation, "plan": [], "next_steps": [], "confidence": 0.0}

    def act(self, action: str, parameters: Optional[Dict] = None) -> Dict:
        """
        Act phase: Execute actions using available tools

        Args:
            action: Action to execute
            parameters: Action parameters

        Returns:
            Dict with action result
        """
        parameters = parameters or {}
        result = {
            "action": action,
            "success": False,
            "output": None,
            "error": None,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Map actions to execution methods
            if action == "review_system":
                result = self._act_review_system()
            elif action == "install_dependencies":
                result = self._act_install_dependencies(parameters)
            elif action == "configure_services":
                result = self._act_configure_services(parameters)
            elif action == "execute_system":
                result = self._act_execute_system(parameters)
            elif action == "check_status":
                result = self._act_check_status()
            elif action == "suggest_fix":
                result = self._act_suggest_fix(parameters)
            elif action == "monitor_progress":
                result = self._act_monitor_progress(parameters)
            else:
                result["error"] = f"Unknown action: {action}"

        except Exception as e:
            result["error"] = str(e)
            result["success"] = False

        # Record in history
        self.execution_history.append(result)
        return result

    def observe(self, action_result: Dict) -> Dict:
        """
        Observe phase: Evaluate results and adjust strategy

        Args:
            action_result: Result from act phase

        Returns:
            Dict with observation and recommendations
        """
        if not self.is_available():
            return {
                "observation": "Action completed",
                "success": action_result.get("success", False),
                "recommendations": [],
            }

        try:
            system_prompt = self._generate_system_prompt("react")

            result_str = json.dumps(action_result, indent=2, default=str)
            prompt = f"""Action Result:
{result_str}

Evaluate this result:
1. Was the action successful?
2. What worked well?
3. What issues were encountered?
4. What should be done next?
5. Any recommendations?

Respond in JSON format with:
{{
    "observation": "Detailed observation",
    "success": true/false,
    "issues": ["issue1", "issue2"],
    "next_steps": ["step1", "step2"],
    "recommendations": ["rec1", "rec2"],
    "should_retry": true/false,
    "retry_strategy": "strategy description"
}}"""

            response = self.integrator.generate(
                prompt=prompt, system_prompt=system_prompt, temperature=0.3, max_tokens=500
            )

            if response and "content" in response:
                content = response["content"].strip()
                result = self._extract_json_from_text(content)
                if result:
                    return result

            # Fallback
            return {
                "observation": "Action completed",
                "success": action_result.get("success", False),
                "recommendations": [],
            }
        except Exception as e:
            print_warning(f"Error en fase Observe: {e}")
            return {
                "observation": "Action completed",
                "success": action_result.get("success", False),
                "recommendations": [],
            }

    def react_cycle(self, situation: str, max_iterations: int = 5) -> Dict:
        """
        Complete ReAct cycle: Think -> Act -> Observe -> Repeat

        Args:
            situation: Initial situation
            max_iterations: Maximum iterations

        Returns:
            Final result with complete execution summary
        """
        print_header("CICLO REACT: THINK → ACT → OBSERVE")

        iteration = 0
        current_situation = situation
        all_results = []

        while iteration < max_iterations:
            iteration += 1
            print_info(f"\n--- Iteración {iteration}/{max_iterations} ---")

            # Think
            print_info("🤔 Fase THINK: Analizando situación...")
            think_result = self.think(current_situation, self.system_context)
            print_info(f"Análisis: {think_result.get('analysis', 'N/A')[:100]}...")

            if think_result.get("next_steps"):
                print_info("Próximos pasos identificados:")
                for step in think_result.get("next_steps", [])[:3]:
                    print(f"  • {step}")

            # Act
            if think_result.get("next_steps"):
                next_action = think_result["next_steps"][0]
                print_info(f"\n⚡ Fase ACT: Ejecutando '{next_action}'...")
                act_result = self.act(next_action, think_result)
                all_results.append(act_result)

                if act_result.get("success"):
                    print_success(f"✅ Acción completada: {next_action}")
                else:
                    print_error(f"❌ Acción falló: {next_action}")
                    if act_result.get("error"):
                        print_error(f"   Error: {act_result['error']}")
            else:
                print_info("No hay acciones pendientes")
                break

            # Observe
            print_info(f"\n👁️  Fase OBSERVE: Evaluando resultados...")
            observe_result = self.observe(act_result)
            print_info(f"Observación: {observe_result.get('observation', 'N/A')[:100]}...")

            if observe_result.get("recommendations"):
                print_info("Recomendaciones:")
                for rec in observe_result.get("recommendations", [])[:3]:
                    print(f"  • {rec}")

            # Update situation for next iteration
            if observe_result.get("next_steps"):
                current_situation = f"Previous action: {next_action}. Result: {observe_result.get('observation', 'Completed')}"
            else:
                break

            # Check if we should continue
            if observe_result.get("success") and not observe_result.get("should_retry"):
                print_success("✅ Objetivo alcanzado")
                break

        return {
            "iterations": iteration,
            "final_situation": current_situation,
            "results": all_results,
            "success": all_results[-1].get("success", False) if all_results else False,
        }

    def create_execution_plan(
        self, goal: str, context: Optional[Dict] = None
    ) -> List[ExecutionTask]:
        """
        Create a comprehensive execution plan using context-aware planning

        Args:
            goal: Main goal (e.g., "Review and execute chatbot system")
            context: Additional context

        Returns:
            List of ExecutionTask objects
        """
        if not self.is_available():
            # Fallback: Create basic plan
            return self._create_basic_plan(goal)

        try:
            system_prompt = """You are a task planning specialist for chatbot system execution.

Generate a comprehensive execution plan that:
1. Breaks down the goal into actionable tasks
2. Identifies dependencies between tasks
3. Prioritizes tasks (critical, high, medium, low)
4. Estimates time for each task
5. Categorizes tasks (review, install, config, execute, monitor)

For each task, provide:
- id: unique identifier
- title: task title
- description: detailed description
- category: review|install|config|execute|monitor
- priority: critical|high|medium|low
- dependencies: list of task IDs
- estimated_time: time estimate

Respond in JSON format with a "tasks" array."""

            context_str = json.dumps(context or self.system_context, indent=2, default=str)
            prompt = f"""Goal: {goal}

Context:
{context_str}

Generate a detailed execution plan with all necessary tasks."""

            response = self.integrator.generate(
                prompt=prompt, system_prompt=system_prompt, temperature=0.3, max_tokens=1500
            )

            if response and "content" in response:
                content = response["content"].strip()
                result = self._extract_json_from_text(content)

                if result and "tasks" in result:
                    tasks = []
                    for task_data in result["tasks"]:
                        task = ExecutionTask(
                            id=task_data.get("id", f"task_{len(tasks)}"),
                            title=task_data.get("title", "Untitled"),
                            description=task_data.get("description", ""),
                            category=task_data.get("category", "execute"),
                            priority=TaskPriority(task_data.get("priority", "medium")),
                            status=TaskStatus.PENDING,
                            dependencies=task_data.get("dependencies", []),
                            estimated_time=task_data.get("estimated_time"),
                        )
                        tasks.append(task)

                    self.execution_plan = tasks
                    return tasks

            # Fallback to basic plan
            return self._create_basic_plan(goal)

        except Exception as e:
            print_warning(f"Error creando plan de ejecución: {e}")
            return self._create_basic_plan(goal)

    def _create_basic_plan(self, goal: str) -> List[ExecutionTask]:
        """Create a basic execution plan without AI"""
        tasks = [
            ExecutionTask(
                id="review_1",
                title="Review System State",
                description="Review Python, dependencies, files, and configuration",
                category="review",
                priority=TaskPriority.CRITICAL,
                status=TaskStatus.PENDING,
                dependencies=[],
                estimated_time="2-3 minutes",
            ),
            ExecutionTask(
                id="install_1",
                title="Install Dependencies",
                description="Install Python and Node.js dependencies",
                category="install",
                priority=TaskPriority.HIGH,
                status=TaskStatus.PENDING,
                dependencies=["review_1"],
                estimated_time="5-10 minutes",
            ),
            ExecutionTask(
                id="config_1",
                title="Configure Services",
                description="Configure MongoDB and other services",
                category="config",
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.PENDING,
                dependencies=["install_1"],
                estimated_time="3-5 minutes",
            ),
            ExecutionTask(
                id="execute_1",
                title="Execute System",
                description="Execute the chatbot system",
                category="execute",
                priority=TaskPriority.CRITICAL,
                status=TaskStatus.PENDING,
                dependencies=["config_1"],
                estimated_time="Ongoing",
            ),
            ExecutionTask(
                id="monitor_1",
                title="Monitor Execution",
                description="Monitor system execution and health",
                category="monitor",
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.PENDING,
                dependencies=["execute_1"],
                estimated_time="Ongoing",
            ),
        ]

        self.execution_plan = tasks
        return tasks

    def execute_plan(self, interactive: bool = True) -> Dict:
        """
        Execute the execution plan

        Args:
            interactive: Whether to ask for confirmation before each step

        Returns:
            Execution summary
        """
        if not self.execution_plan:
            print_warning("No hay plan de ejecución. Creando uno básico...")
            self.create_execution_plan("Review and execute chatbot system")

        print_header("EJECUTANDO PLAN DE EJECUCIÓN")
        print_info(f"Total de tareas: {len(self.execution_plan)}")

        completed = 0
        failed = 0
        skipped = 0

        for task in self.execution_plan:
            # Check dependencies
            if not self._check_dependencies(task):
                print_warning(f"⚠️  Tarea {task.id} tiene dependencias no completadas. Saltando...")
                task.status = TaskStatus.SKIPPED
                skipped += 1
                continue

            # Show task info
            print()
            print_info(f"📋 Tarea: {task.title}")
            print_info(f"   Descripción: {task.description}")
            print_info(f"   Prioridad: {task.priority.value}")
            if task.estimated_time:
                print_info(f"   Tiempo estimado: {task.estimated_time}")

            # Ask for confirmation if interactive
            if interactive:
                response = input("\n¿Ejecutar esta tarea? [S/n]: ").strip().lower()
                if response == "n":
                    print_info("Tarea saltada por el usuario")
                    task.status = TaskStatus.SKIPPED
                    skipped += 1
                    continue

            # Execute task
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.now().isoformat()

            start_time = time.time()
            result = self._execute_task(task)
            elapsed_time = time.time() - start_time
            task.actual_time = f"{elapsed_time:.1f}s"

            if result.get("success"):
                task.status = TaskStatus.COMPLETED
                task.result = result
                completed += 1
                print_success(f"✅ Tarea completada: {task.title}")
            else:
                task.status = TaskStatus.FAILED
                task.error = result.get("error", "Unknown error")
                failed += 1
                print_error(f"❌ Tarea falló: {task.title}")
                if task.error:
                    print_error(f"   Error: {task.error}")

            task.updated_at = datetime.now().isoformat()

        # Summary
        print()
        print_header("RESUMEN DE EJECUCIÓN")
        print_success(f"✅ Completadas: {completed}")
        if failed > 0:
            print_error(f"❌ Fallidas: {failed}")
        if skipped > 0:
            print_warning(f"⚠️  Saltadas: {skipped}")

        return {
            "total": len(self.execution_plan),
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "tasks": [task.to_dict() for task in self.execution_plan],
        }

    def _check_dependencies(self, task: ExecutionTask) -> bool:
        """Check if all dependencies are completed"""
        if not task.dependencies:
            return True

        for dep_id in task.dependencies:
            dep_task = next((t for t in self.execution_plan if t.id == dep_id), None)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False

        return True

    def _execute_task(self, task: ExecutionTask) -> Dict:
        """Execute a single task"""
        try:
            if task.category == "review":
                return self._act_review_system()
            elif task.category == "install":
                return self._act_install_dependencies({})
            elif task.category == "config":
                return self._act_configure_services({})
            elif task.category == "execute":
                return self._act_execute_system({"mode": "unified"})
            elif task.category == "monitor":
                return self._act_monitor_progress({})
            else:
                return {"success": False, "error": f"Unknown category: {task.category}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Action implementations
    def _act_review_system(self) -> Dict:
        """Review system state"""
        if not self.reviewer:
            return {"success": False, "error": "SystemReviewer not available"}

        try:
            review_result = self.reviewer.review()
            self.system_context["review"] = review_result
            return {
                "success": review_result.get("ready", False),
                "output": review_result,
                "issues": review_result.get("issues", []),
                "warnings": review_result.get("warnings", []),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _act_install_dependencies(self, params: Dict) -> Dict:
        """Install dependencies"""
        if not self.installer:
            return {"success": False, "error": "SystemInstaller not available"}

        try:
            review_result = self.system_context.get("review", {})
            install_ok = self.installer.install(review_result)
            return {"success": install_ok, "output": {"installed": install_ok}}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _act_configure_services(self, params: Dict) -> Dict:
        """Configure services"""
        if not self.service_manager:
            return {"success": False, "error": "ServiceManager not available"}

        try:
            services_result = self.service_manager.setup_services()
            self.system_context["services"] = services_result
            return {"success": True, "output": services_result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _act_execute_system(self, params: Dict) -> Dict:
        """Execute system"""
        if not self.executor:
            return {"success": False, "error": "SystemExecutor not available"}

        try:
            mode = params.get("mode", "unified")
            execute_ok = self.executor.execute(mode)
            return {"success": execute_ok, "output": {"mode": mode, "executed": execute_ok}}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _act_check_status(self) -> Dict:
        """Check current system status"""
        try:
            status = {
                "review": self.system_context.get("review", {}),
                "installation": self.system_context.get("installation", {}),
                "services": self.system_context.get("services", {}),
                "execution": self.system_context.get("execution", {}),
            }
            return {"success": True, "output": status}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _act_suggest_fix(self, params: Dict) -> Dict:
        """Suggest fixes for issues"""
        if not self.is_available():
            return {"success": False, "error": "AI not available"}

        issue = params.get("issue", "Unknown issue")
        context = params.get("context", self.system_context)

        try:
            system_prompt = self._generate_system_prompt("cot")
            prompt = f"""Issue: {issue}

Context: {json.dumps(context, indent=2, default=str)}

Provide a detailed fix suggestion with:
1. Root cause analysis
2. Step-by-step solution
3. Verification steps
4. Prevention measures

Respond in JSON format."""

            response = self.integrator.generate(
                prompt=prompt, system_prompt=system_prompt, temperature=0.3, max_tokens=600
            )

            if response and "content" in response:
                content = response["content"].strip()
                suggestion = self._extract_json_from_text(content)
                return {"success": True, "output": suggestion or {"suggestion": content}}

            return {"success": False, "error": "Could not generate suggestion"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _act_monitor_progress(self, params: Dict) -> Dict:
        """Monitor execution progress"""
        try:
            # Check running processes
            processes = []
            # This would check actual running processes
            # For now, return basic status

            return {
                "success": True,
                "output": {
                    "monitoring": True,
                    "processes": processes,
                    "timestamp": datetime.now().isoformat(),
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """Extract JSON from text response"""
        import re

        # Try to find JSON object
        json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
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

    def get_suggestions(self, context: Optional[Dict] = None) -> List[str]:
        """
        Get AI-powered suggestions for next steps

        Args:
            context: Current context

        Returns:
            List of suggestions
        """
        if not self.is_available():
            return ["Review system state", "Install dependencies", "Configure services"]

        try:
            system_prompt = self._generate_system_prompt("context_aware")
            context_str = json.dumps(context or self.system_context, indent=2, default=str)

            prompt = f"""Current system context:
{context_str}

Based on this context, provide 5 actionable suggestions for next steps.
Focus on:
1. What needs to be done next
2. What issues should be addressed
3. What optimizations are possible

Respond with a JSON array of suggestions."""

            response = self.integrator.generate(
                prompt=prompt, system_prompt=system_prompt, temperature=0.7, max_tokens=400
            )

            if response and "content" in response:
                content = response["content"].strip()
                result = self._extract_json_from_text(content)
                if isinstance(result, list):
                    return result
                elif isinstance(result, dict) and "suggestions" in result:
                    return result["suggestions"]

            return ["Review system state", "Install dependencies", "Configure services"]
        except Exception as e:
            print_warning(f"Error obteniendo sugerencias: {e}")
            return ["Review system state", "Install dependencies", "Configure services"]

    def save_execution_report(self, filename: Optional[str] = None) -> Path:
        """Save execution report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"execution_report_{timestamp}.json"

        filepath = Path(filename)

        report = {
            "timestamp": datetime.now().isoformat(),
            "system_context": self.system_context,
            "execution_plan": [task.to_dict() for task in self.execution_plan],
            "execution_history": self.execution_history,
            "summary": {
                "total_tasks": len(self.execution_plan),
                "completed": sum(
                    1 for t in self.execution_plan if t.status == TaskStatus.COMPLETED
                ),
                "failed": sum(1 for t in self.execution_plan if t.status == TaskStatus.FAILED),
                "skipped": sum(1 for t in self.execution_plan if t.status == TaskStatus.SKIPPED),
            },
        }

        filepath.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        return filepath


def main():
    """CLI interface for Execution AI Agent"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Execution Agent for Chatbot System")

    parser.add_argument(
        "--mode",
        choices=["react", "plan", "execute", "suggest", "monitor"],
        default="react",
        help="Execution mode",
    )

    parser.add_argument("--goal", help="Goal for planning mode")

    parser.add_argument(
        "--interactive", action="store_true", help="Interactive mode (ask for confirmation)"
    )

    parser.add_argument("--output", help="Output file for reports")

    args = parser.parse_args()

    # Initialize agent
    agent = ExecutionAIAgent()

    if not agent.is_available():
        print_warning("⚠️  IA no disponible - funcionando en modo básico")

    print_header("AGENTE DE IA PARA EJECUCIÓN DEL CHATBOT")

    if args.mode == "react":
        # ReAct cycle
        situation = args.goal or "Review and prepare chatbot system for execution"
        result = agent.react_cycle(situation)
        print_success(f"\n✅ Ciclo ReAct completado ({result['iterations']} iteraciones)")

    elif args.mode == "plan":
        # Create execution plan
        goal = args.goal or "Review and execute chatbot system"
        plan = agent.create_execution_plan(goal)
        print_success(f"\n✅ Plan de ejecución creado ({len(plan)} tareas)")

        # Show plan
        print("\n📋 Plan de Ejecución:")
        for task in plan:
            print(f"  {task.id}: {task.title} ({task.priority.value})")

    elif args.mode == "execute":
        # Execute plan
        if not agent.execution_plan:
            goal = args.goal or "Review and execute chatbot system"
            agent.create_execution_plan(goal)

        result = agent.execute_plan(interactive=args.interactive)
        print_success(f"\n✅ Ejecución completada")

    elif args.mode == "suggest":
        # Get suggestions
        suggestions = agent.get_suggestions()
        print("\n💡 Sugerencias:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")

    elif args.mode == "monitor":
        # Monitor progress
        print_info("Iniciando monitoreo...")
        result = agent._act_monitor_progress({})
        print_success(f"✅ Monitoreo: {result.get('output', {})}")

    # Save report if requested
    if args.output:
        report_path = agent.save_execution_report(args.output)
        print_success(f"✅ Reporte guardado en: {report_path}")
    elif args.mode in ["react", "execute"]:
        report_path = agent.save_execution_report()
        print_info(f"📄 Reporte guardado en: {report_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gravity Orchestrator Agent
==========================

Agente especializado en interpretar y orquestar el desarrollo automatizado del proyecto.
Funciona en "Agent Mode" para supervisar, planificar y ejecutar tareas de desarrollo
de forma autónoma y coordinada.

Capacidades:
- Interpretación de guías de implementación (PASO_A_PASO, ORCHESTRATOR_GUIDE)
- Orquestación de agentes especializados (Backend, Frontend, Infra, etc.)
- Supervisión del estado del proyecto
- Toma de decisiones autónoma basada en objetivos
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import core components
try:
    from model_integrator import get_model_integrator
    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False

try:
    from AI_AGENTS.EXECUTOR.execution_ai_agent import ExecutionAIAgent, ExecutionTask, TaskStatus, TaskPriority
    BASE_AGENT_AVAILABLE = True
except ImportError:
    BASE_AGENT_AVAILABLE = False
    # Fallback minimal classes if base agent is not available
    class ExecutionAIAgent:
        def __init__(self): pass
    class TaskStatus:
        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        FAILED = "failed"
    class TaskPriority:
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"
    @dataclass
    class ExecutionTask:
        id: str
        title: str
        description: str
        status: str = "pending"

class GravityOrchestratorAgent(ExecutionAIAgent):
    """
    Agente Orchestrator 'Gravity'
    Especialista en interpretación y orquestación de desarrollo automatizado.
    """

    def __init__(self, context: Optional[Dict] = None):
        super().__init__(system_context=context) if BASE_AGENT_AVAILABLE else None
        self.name = "Gravity Orchestrator"
        self.role = "Orchestrator & Interpreter"
        self.context = context or {}
        self.active_mode = False
        
        # Initialize AI
        if MODEL_INTEGRATOR_AVAILABLE:
            self.integrator = get_model_integrator()
            self.enabled = True
        else:
            self.enabled = False
            print("⚠️ Model Integrator no disponible. Funcionalidad limitada.")

    def _generate_orchestrator_prompt(self, goal: str) -> str:
        """Generate the system prompt for the Orchestrator persona"""
        return f"""Eres 'Gravity', el Agente Orquestador Principal del proyecto Chatbot-2311.

TU MISIÓN:
Interpretar y orquestar el desarrollo automatizado del proyecto. No solo ejecutas comandos, sino que ENTIENDES la arquitectura, los objetivos de negocio y coordinas los recursos.

TUS CAPACIDADES:
1. Interpretación Profunda: Lees documentación (MD files), código y logs para entender el estado real.
2. Orquestación Estratégica: Divides grandes objetivos en tareas manejables para otros agentes o para ti mismo.
3. Toma de Decisiones: Decides qué es prioritario (Fix vs Feature, Refactor vs Deploy).
4. 'Agent Mode': Operas en un ciclo continuo de Observar -> Pensar -> Actuar -> Verificar.

CONTEXTO ACTUAL:
{json.dumps(self.context, indent=2, default=str)}

OBJETIVO PRINCIPAL:
{goal}

ESTILO DE RESPUESTA:
- Analítico y directivo.
- Estructurado (JSON para planes, Markdown para reportes).
- Proactivo (sugieres mejoras antes de que fallen).
"""

    def interpret_project_status(self) -> Dict[str, Any]:
        """Reads key project files to interpret current status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "phases": {},
            "blockers": [],
            "recent_changes": []
        }
        
        # Read status files
        files_to_check = [
            "ESTADO_PROYECTO_COMPLETO.md",
            "ORCHESTRATOR_KICKOFF_GUIDE.md",
            "PASO_A_PASO_IMPLEMENTACION.md",
            "EXECUTION_SUMMARY.md"
        ]
        
        for filename in files_to_check:
            path = Path(filename)
            if path.exists():
                status["phases"][filename] = "Found"
                # Here we could perform deeper analysis of file content
            else:
                status["phases"][filename] = "Missing"
                
        return status

    def plan_development(self, goal: str) -> List[Dict]:
        """Creates a high-level development plan based on the goal"""
        if not self.enabled:
            return [{"id": "error", "title": "AI Not Available", "status": "failed"}]

        system_prompt = self._generate_orchestrator_prompt(goal)
        prompt = f"""Analiza el objetivo: '{goal}' y el estado actual del proyecto.
        Genera un plan de desarrollo automatizado paso a paso.
        
        Formato de respuesta JSON:
        {{
            "analysis": "Análisis de la situación",
            "strategy": "Estrategia de implementación",
            "tasks": [
                {{
                    "id": "t1",
                    "title": "Título de la tarea",
                    "description": "Descripción detallada",
                    "priority": "high",
                    "agent_role": "Backend|Frontend|DevOps|Orchestrator"
                }}
            ]
        }}
        """
        
        try:
            response = self.integrator.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.2,
                max_tokens=1500
            )
            
            content = response.get("content", "")
            # Try to parse JSON
            import re
            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                return json.loads(json_match.group())
            return {"error": "Could not parse plan", "raw_content": content}
            
        except Exception as e:
            return {"error": str(e)}

    def agent_mode_loop(self, goal: str, max_iterations: int = 10, interval: int = 5):
        """
        Runs in continuous 'Agent Mode' to orchestrate development.
        """
        print(f"\n🚀 INICIANDO GRAVITY ORCHESTRATOR EN AGENT MODE")
        print(f"🎯 Objetivo: {goal}")
        print("="*60)
        
        self.active_mode = True
        iteration = 0
        
        while self.active_mode and iteration < max_iterations:
            iteration += 1
            print(f"\n🔄 Ciclo {iteration}/{max_iterations} - {datetime.now().strftime('%H:%M:%S')}")
            
            # 1. Observe / Interpret
            status = self.interpret_project_status()
            self.context["status"] = status
            
            # 2. Plan / Think
            print("🧠 Interpretando estado y planificando siguientes pasos...")
            plan = self.plan_development(goal)
            
            if "error" in plan:
                print(f"❌ Error en planificación: {plan['error']}")
                break
                
            print(f"📋 Estrategia: {plan.get('strategy', 'N/A')}")
            
            # 3. Act / Orchestrate
            tasks = plan.get("tasks", [])
            if not tasks:
                print("✅ No hay tareas pendientes o el plan está completo.")
                break
                
            for task in tasks[:3]: # Execute top 3 tasks per cycle
                print(f"▶️ Ejecutando: {task['title']} ({task['agent_role']})")
                # In a real full agent, this would trigger other agents or tools
                # For now, we simulate success or perform simple actions
                time.sleep(1) 
                print(f"   ✅ Tarea orquestada/delegada.")
            
            # 4. Verify (Simulated)
            print("👁️ Verificando resultados...")
            
            time.sleep(interval)
            
        print("\n🏁 Gravity Agent Mode Finalizado.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gravity Orchestrator Agent")
    parser.add_argument("--mode", default="agent", choices=["agent", "plan", "interpret"], help="Operation mode")
    parser.add_argument("--goal", default="Revisar y orquestar el estado actual del proyecto", help="Goal for the agent")
    parser.add_argument("--iterations", type=int, default=5, help="Max iterations for agent mode")
    
    args = parser.parse_args()
    
    agent = GravityOrchestratorAgent()
    
    if args.mode == "agent":
        agent.agent_mode_loop(args.goal, max_iterations=args.iterations)
    elif args.mode == "plan":
        print(json.dumps(agent.plan_development(args.goal), indent=2))
    elif args.mode == "interpret":
        print(json.dumps(agent.interpret_project_status(), indent=2))

if __name__ == "__main__":
    main()

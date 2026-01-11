"""
AI Agents Package

Este paquete contiene agentes especializados para el proyecto ChatBot BMC.

Agentes disponibles:
- GravityTrainingOrchestrator: Orquestador principal para el sistema de entrenamiento (PR #87)
- ExecutionAIAgent: Agente de ejecución asistida por IA
- WatcherAgent: Agente de monitoreo y observación

Para usar el Gravity Training Orchestrator:
    from AI_AGENTS.gravity_training_orchestrator import GravityTrainingOrchestrator
    
    agent = GravityTrainingOrchestrator()
    agent.analyze_pr_87()
    agent.execute_full_integration()

O usar los scripts:
    python AI_AGENTS/run_gravity_orchestrator.py
    ./AI_AGENTS/gravity_quick_commands.sh

Documentación:
- GRAVITY_AGENT_INDEX.md - Índice maestro
- GRAVITY_TRAINING_ORCHESTRATOR_README.md - Documentación completa
- GRAVITY_AGENT_EXECUTIVE_SUMMARY.md - Resumen ejecutivo
"""

__version__ = "1.0.0"
__author__ = "Gravity AI Agent System"

"""
Development Orchestrator Agent for Gravity (Cursor Agent Mode)
==============================================================

Este módulo proporciona el agente especializado en interpretar y orquestar
el desarrollo automatizado del proyecto chatbot-2311 (BMC Ecosystem).

Usage:
    from .development_orchestrator_agent import DevelopmentOrchestratorAgent
    
    agent = DevelopmentOrchestratorAgent()
    agent.react_cycle(pr_number=87)

CLI Usage:
    python -m development_orchestrator_agent --mode react --pr 87
"""

from .development_orchestrator_agent import (
    DevelopmentOrchestratorAgent,
    PRAnalysis,
    DevelopmentTask,
    OrchestrationPlan,
    PhaseStatus,
    TaskPriority,
    AgentType,
)

__all__ = [
    "DevelopmentOrchestratorAgent",
    "PRAnalysis",
    "DevelopmentTask", 
    "OrchestrationPlan",
    "PhaseStatus",
    "TaskPriority",
    "AgentType",
]

__version__ = "1.0.0"
__author__ = "BMC Development Team"

"""
Gravity Development Orchestrator Agent
======================================

Un agente especializado en modo Gravity de Cursor para interpretar y orquestar
el desarrollo automatizado del proyecto BMC Chatbot.

Usage:
    from AI_AGENTS.GRAVITY_ORCHESTRATOR import GravityDevelopmentAgent
    
    agent = GravityDevelopmentAgent()
    
    # Analyze a PR
    analysis = agent.analyze_pr(87)
    
    # Generate tasks
    tasks = agent.generate_tasks_from_pr(analysis)
    
    # Run ReAct cycle
    result = agent.react_cycle("Implement training system")
"""

from .gravity_development_agent import (
    GravityDevelopmentAgent,
    DevelopmentPhase,
    AgentRole,
    TaskPriority,
    TaskStatus,
    PRAnalysis,
    DevelopmentTask,
)

__all__ = [
    "GravityDevelopmentAgent",
    "DevelopmentPhase",
    "AgentRole",
    "TaskPriority",
    "TaskStatus",
    "PRAnalysis",
    "DevelopmentTask",
]

__version__ = "1.0.0"
__author__ = "Gravity Agent Team"

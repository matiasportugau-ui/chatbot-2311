"""
Agents Package
==============

Contains specialized AI agents for the chatbot-2311 project.

Agents:
- GravityAgent: Development automation orchestrator
- ExecutionAIAgent: AI-powered execution agent (in AI_AGENTS)
- WatcherAgent: Observational agent (in AI_AGENTS)
"""

from .gravity_agent import (
    GravityAgent,
    AgentMode,
    ProjectState,
    DevelopmentTask,
    ProjectInterpretation
)

__all__ = [
    "GravityAgent",
    "AgentMode",
    "ProjectState",
    "DevelopmentTask",
    "ProjectInterpretation"
]

__version__ = "1.0.0"

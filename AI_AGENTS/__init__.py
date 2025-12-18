"""
AI_AGENTS Package
==================

This package contains all AI agents for the BMC Chatbot System.

Available Agents:
- GravityAgent: Master orchestrator for automated development (Agent Mode)
- ExecutionAIAgent: AI-powered execution and installation
- WatcherAgent: Observational learning from WhatsApp/Sheets
"""

# Gravity Agent - Master Orchestrator
from AI_AGENTS.gravity_agent import (
    GravityAgent,
    GravityMode,
    DevelopmentTask,
    PRAnalysis,
    TaskPriority,
    PhaseStatus
)

# Execution Agent
from AI_AGENTS.EXECUTOR.execution_ai_agent import (
    ExecutionAIAgent,
    ExecutionTask,
    TaskStatus as ExecutionTaskStatus
)

# Watcher Agent
from AI_AGENTS.watcher_agent import WatcherAgent, watcher

__all__ = [
    # Gravity Agent
    "GravityAgent",
    "GravityMode",
    "DevelopmentTask",
    "PRAnalysis",
    "TaskPriority",
    "PhaseStatus",
    # Execution Agent
    "ExecutionAIAgent",
    "ExecutionTask",
    "ExecutionTaskStatus",
    # Watcher Agent
    "WatcherAgent",
    "watcher"
]

__version__ = "1.0.0"

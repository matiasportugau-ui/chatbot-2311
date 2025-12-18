"""
AI Agents for BMC Chatbot Project
=================================

This package contains specialized AI agents for the BMC Chatbot project:

1. EXECUTOR - Execution AI Agent for system deployment and management
2. GRAVITY_ORCHESTRATOR - Development orchestration agent for Cursor Agent Mode
3. watcher_agent - Observational agent for learning from WhatsApp/Sheets interactions
"""

# Gravity Development Orchestrator Agent
try:
    from .GRAVITY_ORCHESTRATOR import (
        GravityDevelopmentAgent,
        DevelopmentPhase,
        AgentRole,
        TaskPriority,
        TaskStatus,
        PRAnalysis,
        DevelopmentTask,
    )
    GRAVITY_AGENT_AVAILABLE = True
except ImportError:
    GRAVITY_AGENT_AVAILABLE = False

# Execution AI Agent
try:
    from .EXECUTOR.execution_ai_agent import ExecutionAIAgent
    EXECUTOR_AGENT_AVAILABLE = True
except ImportError:
    EXECUTOR_AGENT_AVAILABLE = False

# Watcher Agent
try:
    from .watcher_agent import WatcherAgent, watcher
    WATCHER_AGENT_AVAILABLE = True
except ImportError:
    WATCHER_AGENT_AVAILABLE = False

__all__ = [
    # Gravity Agent
    "GravityDevelopmentAgent",
    "DevelopmentPhase",
    "AgentRole",
    "TaskPriority",
    "TaskStatus",
    "PRAnalysis",
    "DevelopmentTask",
    # Executor Agent
    "ExecutionAIAgent",
    # Watcher Agent
    "WatcherAgent",
    "watcher",
    # Availability flags
    "GRAVITY_AGENT_AVAILABLE",
    "EXECUTOR_AGENT_AVAILABLE",
    "WATCHER_AGENT_AVAILABLE",
]

__version__ = "1.0.0"

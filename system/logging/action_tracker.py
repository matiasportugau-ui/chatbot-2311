#!/usr/bin/env python3
"""
Action Tracker - Rastreador de acciones.
Fase -3: Logging y Auditoría
"""

from system.logging.audit_logger import AuditLogger
from datetime import datetime
from typing import Dict, Any, List, Optional


class ActionTracker:
    """Rastrea todas las acciones del sistema."""
    
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        self.action_history = []
    
    def track_action(self, agent: str, action: str, details: Dict[str, Any]):
        """Rastrea una acción."""
        self.audit_logger.log_action(agent, action, details)
        self.action_history.append({
            "agent": agent,
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_action_history(self, agent: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtiene el historial de acciones."""
        history = self.action_history
        if agent:
            history = [a for a in history if a.get("agent") == agent]
        return history[-limit:]


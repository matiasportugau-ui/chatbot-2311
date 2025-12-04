#!/usr/bin/env python3
"""
Audit Logger - Logger de auditoría de acciones.
Fase -3: Logging y Auditoría
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class AuditLogger:
    """Registra todas las acciones para auditoría."""
    
    def __init__(self, audit_file: str = "system/logs/audit.log"):
        self.audit_file = Path(audit_file)
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_action(self, agent: str, action: str, details: Optional[Dict[str, Any]] = None):
        """Registra una acción."""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "action": action,
            "details": details or {}
        }
        
        with open(self.audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')
    
    def log_phase_start(self, phase: int, agent: str):
        """Registra inicio de fase."""
        self.log_action(agent, "phase_started", {"phase": phase})
    
    def log_phase_complete(self, phase: int, agent: str, results: Dict[str, Any]):
        """Registra completación de fase."""
        self.log_action(agent, "phase_completed", {"phase": phase, "results": results})
    
    def log_task_complete(self, task_id: str, agent: str, output: str):
        """Registra completación de tarea."""
        self.log_action(agent, "task_completed", {"task_id": task_id, "output": output})
    
    def log_error(self, phase: int, task_id: str, error: str, agent: str):
        """Registra un error."""
        self.log_action(agent, "error_occurred", {
            "phase": phase,
            "task_id": task_id,
            "error": error
        })


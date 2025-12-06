#!/usr/bin/env python3
"""
Agent Communication - Protocolo de comunicación entre agentes.
Fase -7: Gestión de Estado y Contexto
"""

from typing import Dict, Any, Callable, Optional
from context_service import ContextService


class AgentCommunication:
    """Maneja la comunicación entre agentes mediante eventos."""
    
    def __init__(self, context_service: Optional[ContextService] = None):
        self.context_service = context_service or ContextService()
        self._handlers = {}
    
    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]):
        """Registra un handler para un tipo de evento."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def send_event(self, event_type: str, data: Dict[str, Any], target_agent: Optional[str] = None):
        """Envía un evento."""
        event_data = {
            "type": event_type,
            "data": data,
            "target": target_agent
        }
        
        # Emitir evento en el contexto compartido
        self.context_service.emit_event(event_type, event_data)
        
        # Ejecutar handlers locales
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    print(f"Error in event handler for {event_type}: {e}")
    
    def listen_for_events(self, event_type: str, callback: Callable[[Dict[str, Any]], None]):
        """Escucha eventos de un tipo específico."""
        self.register_handler(event_type, callback)
    
    def notify_phase_started(self, phase: int, agent_name: str):
        """Notifica que una fase ha comenzado."""
        self.send_event("phase_started", {
            "phase": phase,
            "agent": agent_name
        })
    
    def notify_phase_completed(self, phase: int, agent_name: str, results: Dict[str, Any]):
        """Notifica que una fase ha sido completada."""
        self.send_event("phase_completed", {
            "phase": phase,
            "agent": agent_name,
            "results": results
        })
    
    def notify_task_completed(self, task_id: str, agent_name: str, output: Any):
        """Notifica que una tarea ha sido completada."""
        self.send_event("task_completed", {
            "task_id": task_id,
            "agent": agent_name,
            "output": output
        })
    
    def notify_error(self, phase: int, task_id: str, error: str, agent_name: str):
        """Notifica un error."""
        self.send_event("error_occurred", {
            "phase": phase,
            "task_id": task_id,
            "error": error,
            "agent": agent_name
        })


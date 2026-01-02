#!/usr/bin/env python3
"""
Context Service - Servicio para compartir contexto entre agentes.
Fase -7: Gestión de Estado y Contexto
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from threading import Lock


class ContextService:
    """Servicio centralizado para compartir contexto entre agentes."""
    
    def __init__(self, context_file: str = "system/context/shared_context.json"):
        self.context_file = Path(context_file)
        self.context_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock = Lock()
        self.context = self._load_context()
        self._cache = {}
    
    def _load_context(self) -> Dict[str, Any]:
        """Carga el contexto compartido."""
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._default_context()
        return self._default_context()
    
    def _default_context(self) -> Dict[str, Any]:
        """Retorna el contexto por defecto."""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "agents": {},
            "shared_data": {},
            "events": []
        }
    
    def _save_context(self):
        """Guarda el contexto compartido."""
        self.context["updated_at"] = datetime.now().isoformat()
        with self.lock:
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(self.context, f, indent=2, ensure_ascii=False)
    
    def set_agent_context(self, agent_name: str, data: Dict[str, Any]):
        """Establece el contexto de un agente."""
        if "agents" not in self.context:
            self.context["agents"] = {}
        
        self.context["agents"][agent_name] = {
            "data": data,
            "updated_at": datetime.now().isoformat()
        }
        self._save_context()
        self._cache[agent_name] = data
    
    def get_agent_context(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene el contexto de un agente."""
        if agent_name in self._cache:
            return self._cache[agent_name]
        
        agent_data = self.context.get("agents", {}).get(agent_name)
        if agent_data:
            data = agent_data.get("data", {})
            self._cache[agent_name] = data
            return data
        return None
    
    def set_shared_data(self, key: str, value: Any):
        """Establece un dato compartido."""
        if "shared_data" not in self.context:
            self.context["shared_data"] = {}
        
        self.context["shared_data"][key] = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }
        self._save_context()
    
    def get_shared_data(self, key: str) -> Optional[Any]:
        """Obtiene un dato compartido."""
        shared = self.context.get("shared_data", {}).get(key)
        if shared:
            return shared.get("value")
        return None
    
    def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emite un evento para notificar a otros agentes."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        if "events" not in self.context:
            self.context["events"] = []
        
        self.context["events"].append(event)
        # Mantener solo los últimos 100 eventos
        if len(self.context["events"]) > 100:
            self.context["events"] = self.context["events"][-100:]
        
        self._save_context()
        return event
    
    def get_recent_events(self, event_type: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Obtiene eventos recientes."""
        events = self.context.get("events", [])
        if event_type:
            events = [e for e in events if e.get("type") == event_type]
        return events[-limit:]


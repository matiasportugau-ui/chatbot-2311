#!/usr/bin/env python3
"""
State Manager - Sistema de tracking de estado para fases y tareas.
Fase -7: Gestión de Estado y Contexto
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class StateManager:
    """Gestiona el estado de las fases y tareas del sistema."""
    
    def __init__(self, state_file: str = "system/context/state.json"):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """Carga el estado desde el archivo."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._default_state()
        return self._default_state()
    
    def _default_state(self) -> Dict[str, Any]:
        """Retorna el estado por defecto."""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "phases": {},
            "tasks": {},
            "checkpoints": []
        }
    
    def save_state(self):
        """Guarda el estado actual al archivo."""
        self.state["updated_at"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def set_phase_state(self, phase: int, state: str, metadata: Optional[Dict] = None):
        """Establece el estado de una fase."""
        if "phases" not in self.state:
            self.state["phases"] = {}
        
        phase_key = f"phase_{phase}"
        self.state["phases"][phase_key] = {
            "phase": phase,
            "state": state,
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.save_state()
    
    def get_phase_state(self, phase: int) -> Optional[Dict[str, Any]]:
        """Obtiene el estado de una fase."""
        phase_key = f"phase_{phase}"
        return self.state.get("phases", {}).get(phase_key)
    
    def set_task_state(self, task_id: str, state: str, metadata: Optional[Dict] = None):
        """Establece el estado de una tarea."""
        if "tasks" not in self.state:
            self.state["tasks"] = {}
        
        self.state["tasks"][task_id] = {
            "task_id": task_id,
            "state": state,
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.save_state()
    
    def get_task_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado de una tarea."""
        return self.state.get("tasks", {}).get(task_id)
    
    def create_checkpoint(self, checkpoint_name: str, metadata: Optional[Dict] = None):
        """Crea un checkpoint del estado actual."""
        checkpoint = {
            "name": checkpoint_name,
            "timestamp": datetime.now().isoformat(),
            "state": json.loads(json.dumps(self.state)),  # Deep copy
            "metadata": metadata or {}
        }
        
        if "checkpoints" not in self.state:
            self.state["checkpoints"] = []
        
        self.state["checkpoints"].append(checkpoint)
        self.save_state()
        
        # Guardar checkpoint en archivo separado
        checkpoint_file = Path(f"system/context/checkpoints/{checkpoint_name}.json")
        checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
        
        return checkpoint
    
    def get_all_phases(self) -> Dict[str, Any]:
        """Obtiene el estado de todas las fases."""
        return self.state.get("phases", {})
    
    def get_all_tasks(self) -> Dict[str, Any]:
        """Obtiene el estado de todas las tareas."""
        return self.state.get("tasks", {})


if __name__ == "__main__":
    # Test básico
    sm = StateManager()
    sm.set_phase_state(-8, "completed", {"files_created": 5})
    sm.set_task_state("T-8.1", "completed")
    sm.create_checkpoint("phase_-8_complete")
    print("State Manager initialized and tested successfully")


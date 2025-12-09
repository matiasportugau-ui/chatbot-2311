#!/usr/bin/env python3
"""
Session Recovery - Sistema de recuperación de sesiones.
Fase -7: Gestión de Estado y Contexto
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from state_manager import StateManager
from state_persistence import StatePersistence


class SessionRecovery:
    """Maneja la recuperación de sesiones interrumpidas."""
    
    def __init__(self, state_manager: StateManager, state_persistence: StatePersistence):
        self.state_manager = state_manager
        self.persistence = state_persistence
    
    def recover_from_checkpoint(self, checkpoint_name: Optional[str] = None) -> bool:
        """Recupera el estado desde un checkpoint."""
        if checkpoint_name is None:
            # Buscar el último checkpoint
            checkpoints = self.state_manager.state.get("checkpoints", [])
            if not checkpoints:
                return False
            checkpoint_name = checkpoints[-1].get("name")
        
        checkpoint_file = Path(f"system/context/checkpoints/{checkpoint_name}.json")
        if not checkpoint_file.exists():
            return False
        
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            
            # Restaurar estado
            self.state_manager.state = checkpoint.get("state", {})
            self.state_manager.save_state()
            return True
        except Exception as e:
            print(f"Error recovering from checkpoint {checkpoint_name}: {e}")
            return False
    
    def get_recovery_info(self) -> Dict[str, Any]:
        """Obtiene información sobre la recuperación disponible."""
        checkpoints = self.state_manager.state.get("checkpoints", [])
        snapshots = self.persistence.list_snapshots()
        
        return {
            "last_checkpoint": checkpoints[-1] if checkpoints else None,
            "available_checkpoints": len(checkpoints),
            "available_snapshots": len(snapshots),
            "latest_snapshot": snapshots[0] if snapshots else None
        }
    
    def validate_recovery(self) -> Dict[str, Any]:
        """Valida la integridad del estado recuperado."""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validar estructura básica
        if "phases" not in self.state_manager.state:
            validation["valid"] = False
            validation["errors"].append("Missing 'phases' in state")
        
        if "tasks" not in self.state_manager.state:
            validation["warnings"].append("Missing 'tasks' in state")
        
        # Validar archivos referenciados
        phases = self.state_manager.state.get("phases", {})
        for phase_key, phase_data in phases.items():
            metadata = phase_data.get("metadata", {})
            files_created = metadata.get("files_created", [])
            for file_path in files_created:
                if not Path(file_path).exists():
                    validation["warnings"].append(f"Referenced file not found: {file_path}")
        
        return validation


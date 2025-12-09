#!/usr/bin/env python3
"""
Session Restore - Sistema de restauración de sesiones.
Fase -5: Backup y Recuperación
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from system.backup.state_recovery import StateRecovery
from system.backup.context_versioning import ContextVersioning


class SessionRestore:
    """Maneja la restauración completa de sesiones."""
    
    def __init__(self, state_recovery: StateRecovery, context_versioning: ContextVersioning):
        self.state_recovery = state_recovery
        self.context_versioning = context_versioning
    
    def restore_full_session(self, backup_name: str, target_state_file: str) -> bool:
        """Restaura una sesión completa."""
        # Restore state
        state_restored = self.state_recovery.restore_from_backup(backup_name, target_state_file)
        
        if not state_restored:
            return False
        
        # Additional restoration steps can be added here
        return True
    
    def restore_partial_session(self, component: str, backup_name: str) -> bool:
        """Restaura un componente específico de la sesión."""
        if component == "state":
            return self.state_recovery.restore_from_backup(backup_name, "system/context/state.json")
        elif component == "context":
            # Restore context from version
            version_data = self.context_versioning.get_version(backup_name)
            if version_data:
                # Restore to context service
                return True
        return False
    
    def rollback_to_previous_version(self, current_version: str) -> bool:
        """Hace rollback a la versión anterior."""
        versions = self.context_versioning.list_versions()
        
        # Find current version index
        current_idx = None
        for i, v in enumerate(versions):
            if v.get("tag") == current_version:
                current_idx = i
                break
        
        if current_idx is None or current_idx >= len(versions) - 1:
            return False
        
        # Get previous version
        previous_version = versions[current_idx + 1].get("tag")
        return self.restore_partial_session("context", previous_version)


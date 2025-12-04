#!/usr/bin/env python3
"""
Version History - Historial de versiones.
Fase -3: Logging y Auditoría
"""

from system.logging.change_tracker import ChangeTracker
from datetime import datetime
from typing import List, Dict, Any


class VersionHistory:
    """Mantiene historial de versiones de cambios."""
    
    def __init__(self, change_tracker: ChangeTracker):
        self.tracker = change_tracker
        self.versions = []
    
    def create_version_snapshot(self, version_tag: str, description: str) -> Dict[str, Any]:
        """Crea un snapshot de versión."""
        version = {
            "tag": version_tag,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "changes": []
        }
        
        self.versions.append(version)
        return version
    
    def get_version_history(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de versiones."""
        return sorted(self.versions, key=lambda x: x.get("timestamp", ""), reverse=True)


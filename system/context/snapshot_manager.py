#!/usr/bin/env python3
"""
Snapshot Manager - Gestión de snapshots del estado.
Fase -7: Gestión de Estado y Contexto
"""

from state_persistence import StatePersistence
from typing import Optional


class SnapshotManager:
    """Gestiona snapshots y versionado del estado."""
    
    def __init__(self, state_persistence: StatePersistence):
        self.persistence = state_persistence
    
    def create_versioned_snapshot(self, version_tag: Optional[str] = None) -> str:
        """Crea un snapshot con etiqueta de versión."""
        return self.persistence.create_snapshot(version_tag)
    
    def restore_from_snapshot(self, snapshot_name: str) -> bool:
        """Restaura el estado desde un snapshot."""
        return self.persistence.load_snapshot(snapshot_name)
    
    def get_latest_snapshot(self) -> Optional[str]:
        """Obtiene el snapshot más reciente."""
        snapshots = self.persistence.list_snapshots()
        if snapshots:
            return snapshots[0].get("name")
        return None


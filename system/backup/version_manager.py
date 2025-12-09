#!/usr/bin/env python3
"""
Version Manager - Gestor de versiones del contexto.
Fase -5: Backup y Recuperación
"""

from system.backup.context_versioning import ContextVersioning
from typing import Optional, List, Dict, Any


class VersionManager:
    """Gestiona versiones del contexto."""
    
    def __init__(self, context_versioning: ContextVersioning):
        self.versioning = context_versioning
    
    def create_tagged_version(self, context_data: Dict[str, Any], tag: str) -> str:
        """Crea una versión con etiqueta específica."""
        return self.versioning.create_version(context_data, tag)
    
    def get_latest_version(self) -> Optional[Dict[str, Any]]:
        """Obtiene la versión más reciente."""
        versions = self.versioning.list_versions()
        if versions:
            latest_tag = versions[0].get("tag")
            return self.versioning.get_version(latest_tag)
        return None
    
    def rollback_to_version(self, version_tag: str) -> bool:
        """Hace rollback a una versión específica."""
        version_data = self.versioning.get_version(version_tag)
        if not version_data:
            return False
        
        # Restore context from version
        # This would integrate with ContextService
        return True


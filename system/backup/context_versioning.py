#!/usr/bin/env python3
"""
Context Versioning - Sistema de versionado de contexto.
Fase -5: Backup y Recuperación
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class ContextVersioning:
    """Maneja el versionado del contexto."""
    
    def __init__(self, versions_dir: str = "system/backup/versions"):
        self.versions_dir = Path(versions_dir)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
    
    def create_version(self, context_data: Dict[str, Any], version_tag: Optional[str] = None) -> str:
        """Crea una nueva versión del contexto."""
        if version_tag is None:
            version_tag = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        version_data = {
            "tag": version_tag,
            "timestamp": datetime.now().isoformat(),
            "context": context_data,
            "changes": []
        }
        
        version_file = self.versions_dir / f"{version_tag}.json"
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2, ensure_ascii=False)
        
        return version_tag
    
    def get_version(self, version_tag: str) -> Optional[Dict[str, Any]]:
        """Obtiene una versión específica."""
        version_file = self.versions_dir / f"{version_tag}.json"
        if not version_file.exists():
            return None
        
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """Lista todas las versiones disponibles."""
        versions = []
        for version_file in self.versions_dir.glob("*.json"):
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                    versions.append({
                        "tag": version_data.get("tag"),
                        "timestamp": version_data.get("timestamp"),
                        "file": str(version_file)
                    })
            except Exception:
                continue
        
        return sorted(versions, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def compare_versions(self, version1: str, version2: str) -> Dict[str, Any]:
        """Compara dos versiones del contexto."""
        v1_data = self.get_version(version1)
        v2_data = self.get_version(version2)
        
        if not v1_data or not v2_data:
            return {"error": "One or both versions not found"}
        
        # Simple comparison - can be enhanced
        return {
            "version1": version1,
            "version2": version2,
            "timestamp_diff": abs(
                (datetime.fromisoformat(v1_data["timestamp"]) - 
                 datetime.fromisoformat(v2_data["timestamp"])).total_seconds()
            )
        }


#!/usr/bin/env python3
"""
Change Tracker - Rastreador de cambios.
Fase -3: Logging y Auditoría
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class ChangeTracker:
    """Rastrea cambios en archivos y configuración."""
    
    def __init__(self, changes_file: str = "system/logs/changes.log"):
        self.changes_file = Path(changes_file)
        self.changes_file.parent.mkdir(parents=True, exist_ok=True)
    
    def track_file_change(self, file_path: str, change_type: str, details: Dict[str, Any]):
        """Rastrea un cambio en un archivo."""
        change_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "file_change",
            "file_path": file_path,
            "change_type": change_type,  # created, modified, deleted
            "details": details
        }
        
        self._write_change(change_entry)
    
    def track_config_change(self, config_key: str, old_value: Any, new_value: Any):
        """Rastrea un cambio en configuración."""
        change_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "config_change",
            "config_key": config_key,
            "old_value": old_value,
            "new_value": new_value
        }
        
        self._write_change(change_entry)
    
    def _write_change(self, change_entry: Dict[str, Any]):
        """Escribe un cambio al archivo."""
        with open(self.changes_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(change_entry, ensure_ascii=False) + '\n')


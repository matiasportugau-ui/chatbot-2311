#!/usr/bin/env python3
"""
Auto Backup - Sistema de backup automático de contexto.
Fase -5: Backup y Recuperación
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class AutoBackup:
    """Sistema de backup automático."""
    
    def __init__(self, backup_dir: str = "system/backup/backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup_state(self, state_data: Dict[str, Any], backup_name: Optional[str] = None) -> str:
        """Crea un backup del estado."""
        if backup_name is None:
            backup_name = f"state_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_file = self.backup_dir / f"{backup_name}.json"
        backup_data = {
            "name": backup_name,
            "timestamp": datetime.now().isoformat(),
            "state": state_data
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        return str(backup_file)
    
    def backup_context(self, context_data: Dict[str, Any], backup_name: Optional[str] = None) -> str:
        """Crea un backup del contexto."""
        if backup_name is None:
            backup_name = f"context_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_file = self.backup_dir / f"{backup_name}.json"
        backup_data = {
            "name": backup_name,
            "timestamp": datetime.now().isoformat(),
            "context": context_data
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        return str(backup_file)
    
    def backup_files(self, file_paths: List[str], backup_name: Optional[str] = None) -> str:
        """Crea un backup de archivos específicos."""
        if backup_name is None:
            backup_name = f"files_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_folder = self.backup_dir / backup_name
        backup_folder.mkdir(parents=True, exist_ok=True)
        
        backed_up = []
        for file_path in file_paths:
            src = Path(file_path)
            if src.exists():
                dst = backup_folder / src.name
                if src.is_file():
                    shutil.copy2(src, dst)
                elif src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                backed_up.append(str(dst))
        
        return str(backup_folder)


#!/usr/bin/env python3
"""
State Recovery - Sistema de recuperación de estado.
Fase -5: Backup y Recuperación
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List


class StateRecovery:
    """Maneja la recuperación de estado desde backups."""
    
    def __init__(self, backup_dir: str = "system/backup/backups"):
        self.backup_dir = Path(backup_dir)
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """Lista todos los backups disponibles."""
        backups = []
        for backup_file in self.backup_dir.glob("*.json"):
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                    backups.append({
                        "name": backup_data.get("name"),
                        "timestamp": backup_data.get("timestamp"),
                        "file": str(backup_file)
                    })
            except Exception:
                continue
        
        return sorted(backups, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def restore_from_backup(self, backup_name: str, target_file: str) -> bool:
        """Restaura estado desde un backup."""
        backup_file = self.backup_dir / f"{backup_name}.json"
        if not backup_file.exists():
            return False
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            state_data = backup_data.get("state", {})
            
            target_path = Path(target_file)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error restoring from backup {backup_name}: {e}")
            return False
    
    def validate_backup(self, backup_name: str) -> Dict[str, Any]:
        """Valida la integridad de un backup."""
        backup_file = self.backup_dir / f"{backup_name}.json"
        validation = {
            "valid": False,
            "errors": [],
            "warnings": []
        }
        
        if not backup_file.exists():
            validation["errors"].append(f"Backup file not found: {backup_name}")
            return validation
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            if "state" not in backup_data and "context" not in backup_data:
                validation["errors"].append("Backup missing state or context data")
                return validation
            
            if "timestamp" not in backup_data:
                validation["warnings"].append("Backup missing timestamp")
            
            validation["valid"] = True
            return validation
        except json.JSONDecodeError as e:
            validation["errors"].append(f"Invalid JSON: {e}")
            return validation
        except Exception as e:
            validation["errors"].append(f"Error validating backup: {e}")
            return validation


#!/usr/bin/env python3
"""
Backup Validator - Validador de backups.
Fase -5: Backup y Recuperación
"""

from system.backup.state_recovery import StateRecovery
from typing import Dict, Any


class BackupValidator:
    """Valida la integridad de los backups."""
    
    def __init__(self, state_recovery: StateRecovery):
        self.recovery = state_recovery
    
    def validate_all_backups(self) -> Dict[str, Any]:
        """Valida todos los backups disponibles."""
        backups = self.recovery.list_backups()
        results = {
            "total": len(backups),
            "valid": 0,
            "invalid": 0,
            "details": []
        }
        
        for backup in backups:
            backup_name = backup.get("name")
            validation = self.recovery.validate_backup(backup_name)
            
            if validation["valid"]:
                results["valid"] += 1
            else:
                results["invalid"] += 1
            
            results["details"].append({
                "name": backup_name,
                "validation": validation
            })
        
        return results


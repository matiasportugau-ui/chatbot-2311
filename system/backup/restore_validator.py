#!/usr/bin/env python3
"""
Restore Validator - Validador post-restauración.
Fase -5: Backup y Recuperación
"""

from pathlib import Path
from typing import Dict, Any, List
from system.backup.session_restore import SessionRestore
from datetime import datetime


class RestoreValidator:
    """Valida la integridad después de una restauración."""
    
    def __init__(self, session_restore: SessionRestore):
        self.restore = session_restore
    
    def validate_restored_state(self, state_file: str) -> Dict[str, Any]:
        """Valida el estado restaurado."""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        state_path = Path(state_file)
        if not state_path.exists():
            validation["valid"] = False
            validation["errors"].append(f"State file not found: {state_file}")
            return validation
        
        try:
            import json
            with open(state_path, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # Validate structure
            required_keys = ["phases", "tasks"]
            for key in required_keys:
                if key not in state_data:
                    validation["warnings"].append(f"Missing key in state: {key}")
            
            # Validate phase data
            phases = state_data.get("phases", {})
            for phase_key, phase_data in phases.items():
                if "state" not in phase_data:
                    validation["warnings"].append(f"Phase {phase_key} missing state")
            
            return validation
        except json.JSONDecodeError as e:
            validation["valid"] = False
            validation["errors"].append(f"Invalid JSON in state file: {e}")
            return validation
        except Exception as e:
            validation["valid"] = False
            validation["errors"].append(f"Error validating state: {e}")
            return validation
    
    def generate_restore_report(self, restore_info: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un reporte de restauración."""
        return {
            "restore_info": restore_info,
            "validation": self.validate_restored_state(restore_info.get("state_file", "")),
            "timestamp": datetime.now().isoformat()
        }


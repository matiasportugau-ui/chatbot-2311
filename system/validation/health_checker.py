#!/usr/bin/env python3
"""
Health Checker - Checks de salud del sistema.
Fase -1: Validación y Testing Base
"""

from pathlib import Path
from typing import Dict, Any, List
import json


class HealthChecker:
    """Realiza health checks del sistema."""
    
    def __init__(self, workspace: str = "."):
        self.workspace = Path(workspace)
    
    def check_system_health(self) -> Dict[str, Any]:
        """Realiza un health check completo del sistema."""
        health = {
            "overall": "healthy",
            "checks": {}
        }
        
        # Check directory structure
        health["checks"]["directories"] = self._check_directories()
        
        # Check configuration files
        health["checks"]["config"] = self._check_config_files()
        
        # Check state files
        health["checks"]["state"] = self._check_state_files()
        
        # Determine overall health
        all_healthy = all(
            check.get("status") == "healthy" 
            for check in health["checks"].values()
        )
        
        health["overall"] = "healthy" if all_healthy else "degraded"
        
        return health
    
    def _check_directories(self) -> Dict[str, Any]:
        """Verifica que los directorios necesarios existan."""
        required_dirs = [
            "system/workflow",
            "system/context",
            "system/backup",
            "system/logging",
            "system/config",
            "system/validation",
            "scripts/utils",
            "consolidation"
        ]
        
        missing = []
        for dir_path in required_dirs:
            if not (self.workspace / dir_path).exists():
                missing.append(dir_path)
        
        return {
            "status": "healthy" if not missing else "degraded",
            "missing": missing
        }
    
    def _check_config_files(self) -> Dict[str, Any]:
        """Verifica archivos de configuración."""
        config_files = [
            "system/workflow/workflow_definitions.json",
            "system/workflow/tools_config.json"
        ]
        
        missing = []
        for config_file in config_files:
            if not (self.workspace / config_file).exists():
                missing.append(config_file)
        
        return {
            "status": "healthy" if not missing else "degraded",
            "missing": missing
        }
    
    def _check_state_files(self) -> Dict[str, Any]:
        """Verifica archivos de estado."""
        state_file = self.workspace / "system/context/state.json"
        
        if not state_file.exists():
            return {
                "status": "degraded",
                "message": "State file not found (may be first run)"
            }
        
        try:
            with open(state_file, 'r') as f:
                json.load(f)
            return {"status": "healthy"}
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


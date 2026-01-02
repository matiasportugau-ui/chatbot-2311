#!/usr/bin/env python3
"""
Config Validator - Validador de configuración.
Fase -2: Configuración y Variables
"""

from system.config.config_manager import ConfigManager
from typing import Dict, Any, List


class ConfigValidator:
    """Valida configuración."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
    
    def validate(self, required_keys: List[str]) -> Dict[str, Any]:
        """Valida que las claves requeridas existan."""
        validation = {
            "valid": True,
            "missing": [],
            "errors": []
        }
        
        for key in required_keys:
            value = self.config_manager.get(key)
            if value is None:
                validation["missing"].append(key)
                validation["valid"] = False
        
        return validation


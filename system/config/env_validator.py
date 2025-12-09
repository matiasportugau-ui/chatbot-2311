#!/usr/bin/env python3
"""
Env Validator - Validador de variables de entorno.
Fase -2: Configuración y Variables
"""

from system.config.env_manager import EnvManager
from typing import List, Dict, Any


class EnvValidator:
    """Valida variables de entorno."""
    
    def __init__(self, env_manager: EnvManager):
        self.env_manager = env_manager
    
    def validate(self, required_vars: List[str]) -> Dict[str, Any]:
        """Valida variables de entorno requeridas."""
        return self.env_manager.validate_required(required_vars)


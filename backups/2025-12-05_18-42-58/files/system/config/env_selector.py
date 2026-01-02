#!/usr/bin/env python3
"""
Env Selector - Selector de entorno.
Fase -2: Configuración y Variables
"""

import os
from system.config.multi_env_config import MultiEnvConfig
from typing import Optional


class EnvSelector:
    """Selecciona el entorno basado en variables de entorno."""
    
    def __init__(self, multi_env_config: MultiEnvConfig):
        self.multi_env_config = multi_env_config
    
    def select_environment(self) -> str:
        """Selecciona el entorno basado en ENV variable."""
        env = os.getenv("ENVIRONMENT", os.getenv("ENV", "development"))
        
        valid_envs = ["development", "staging", "production"]
        if env not in valid_envs:
            env = "development"
        
        self.multi_env_config.set_environment(env)
        return env
    
    def get_current_env(self) -> str:
        """Obtiene el entorno actual."""
        return self.multi_env_config.current_env


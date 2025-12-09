#!/usr/bin/env python3
"""
Multi-Env Config - Configuración multi-entorno.
Fase -2: Configuración y Variables
"""

from system.config.config_manager import ConfigManager
from typing import Dict, Any, Optional


class MultiEnvConfig:
    """Gestiona configuración por entorno."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.current_env = self.config_manager.get("environment", "development")
    
    def set_environment(self, env: str):
        """Establece el entorno actual."""
        self.current_env = env
        self.config_manager.set("environment", env)
    
    def get_env_config(self, env: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene configuración de un entorno."""
        target_env = env or self.current_env
        return self.config_manager.get(f"environments.{target_env}", {})
    
    def get(self, key: str, default: Any = None, env: Optional[str] = None) -> Any:
        """Obtiene un valor de configuración del entorno."""
        target_env = env or self.current_env
        env_key = f"environments.{target_env}.{key}"
        value = self.config_manager.get(env_key)
        if value is None:
            # Fallback to global config
            value = self.config_manager.get(key, default)
        return value


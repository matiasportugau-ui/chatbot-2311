#!/usr/bin/env python3
"""
Config Loader - Cargador de configuración.
Fase -2: Configuración y Variables
"""

from system.config.config_manager import ConfigManager
from pathlib import Path
from typing import Dict, Any, Optional
import json


class ConfigLoader:
    """Carga configuración desde múltiples fuentes."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
    
    def load_from_file(self, config_file: str) -> bool:
        """Carga configuración desde un archivo."""
        config_path = Path(config_file)
        if not config_path.exists():
            return False
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            self.config_manager.merge(file_config)
            return True
        except Exception:
            return False
    
    def load_from_env(self, env_file: str = ".env") -> bool:
        """Carga configuración desde variables de entorno."""
        env_path = Path(env_file)
        if not env_path.exists():
            return False
        
        try:
            env_vars = {}
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
            
            # Merge into config
            self.config_manager.merge({"env": env_vars})
            return True
        except Exception:
            return False


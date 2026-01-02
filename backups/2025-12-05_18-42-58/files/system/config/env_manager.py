#!/usr/bin/env python3
"""
Env Manager - Gestor de variables de entorno.
Fase -2: Configuración y Variables
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional


class EnvManager:
    """Gestiona variables de entorno."""
    
    def __init__(self, env_file: str = ".env"):
        self.env_file = Path(env_file)
        self.env_vars = self._load_env()
    
    def _load_env(self) -> Dict[str, str]:
        """Carga variables de entorno desde archivo."""
        env_vars = {}
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
            except Exception:
                pass
        return env_vars
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Obtiene una variable de entorno."""
        # First check environment
        value = os.getenv(key)
        if value:
            return value
        # Then check .env file
        return self.env_vars.get(key, default)
    
    def set(self, key: str, value: str, save: bool = True):
        """Establece una variable de entorno."""
        self.env_vars[key] = value
        if save:
            self._save_env()
    
    def _save_env(self):
        """Guarda variables de entorno al archivo."""
        with open(self.env_file, 'w') as f:
            for key, value in self.env_vars.items():
                f.write(f"{key}={value}\n")
    
    def validate_required(self, required_vars: List[str]) -> Dict[str, Any]:
        """Valida que las variables requeridas existan."""
        validation = {
            "valid": True,
            "missing": []
        }
        
        for var in required_vars:
            if not self.get(var):
                validation["missing"].append(var)
                validation["valid"] = False
        
        return validation


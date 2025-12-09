#!/usr/bin/env python3
"""
Config Manager - Gestor de configuración centralizado.
Fase -2: Configuración y Variables
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Gestiona configuración centralizada."""
    
    def __init__(self, config_file: str = "system/config/config.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def save_config(self):
        """Guarda la configuración."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """Establece un valor de configuración."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
    
    def merge(self, other_config: Dict[str, Any]):
        """Fusiona otra configuración."""
        self._merge_dict(self.config, other_config)
        self.save_config()
    
    def _merge_dict(self, base: Dict, update: Dict):
        """Fusiona diccionarios recursivamente."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_dict(base[key], value)
            else:
                base[key] = value


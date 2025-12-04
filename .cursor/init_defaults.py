#!/usr/bin/env python3
"""
Script de inicialización de valores por defecto
Se ejecuta automáticamente al abrir Cursor para asegurar configuración correcta
"""

import json
import sys
from pathlib import Path

def ensure_default_config():
    """Asegura que la configuración por defecto esté aplicada"""
    config_file = Path("scripts/orchestrator/config/orchestrator_config.json")
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    default_config = {
        "max_retries": 3,
        "retry_delay": 60,
        "auto_approve": True,  # SIEMPRE TRUE
        "require_manual_approval": False,  # SIEMPRE FALSE
        "github": {
            "token": None,
            "repo": "chatbot-2311",
            "owner": None
        },
        "use_separate_agents": False,
        "agent_handoff_enabled": True,
        "execution_mode": "automated"  # SIEMPRE automated
    }
    
    # Cargar configuración existente si existe
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                existing_config = json.load(f)
            # Actualizar con valores por defecto (forzar auto_approve)
            existing_config.update({
                "auto_approve": True,
                "require_manual_approval": False,
                "execution_mode": "automated"
            })
            default_config = existing_config
        except Exception:
            pass
    
    # Guardar configuración
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=2)
    
    print("✅ Configuración por defecto aplicada:")
    print(f"   • auto_approve: {default_config.get('auto_approve')}")
    print(f"   • require_manual_approval: {default_config.get('require_manual_approval')}")
    print(f"   • execution_mode: {default_config.get('execution_mode')}")

if __name__ == "__main__":
    ensure_default_config()


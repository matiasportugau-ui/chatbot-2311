#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inicialización Automática de Credenciales
==========================================

Este script se ejecuta automáticamente al importar cualquier módulo del proyecto.
Configura todas las credenciales UNA VEZ y las carga automáticamente.

NO necesitas ejecutarlo manualmente - se carga automáticamente.
"""

import os
import sys
from pathlib import Path

def init_credentials():
    """Inicializa el sistema de credenciales automáticamente"""
    try:
        # Importar y cargar sistema unificado
        from unified_credentials_manager import UnifiedCredentialsManager
        
        manager = UnifiedCredentialsManager()
        manager._load_all_sources()
        
        # Cargar credenciales críticas en variables de entorno
        critical_creds = [
            'GITHUB_TOKEN',
            'GITHUB_OWNER',
            'OPENAI_API_KEY',
            'GROQ_API_KEY',
            'GEMINI_API_KEY',
            'MONGODB_URI'
        ]
        
        for key in critical_creds:
            value = manager.get_credential(key)
            if value and key not in os.environ:
                os.environ[key] = value
        
        return True
    except Exception:
        # Si falla, no interrumpir el flujo
        return False

# Auto-ejecutar al importar
if __name__ != "__main__":
    init_credentials()


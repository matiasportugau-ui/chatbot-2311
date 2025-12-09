#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carga Automática de Secretos desde Archivo Local
=================================================

Este módulo carga automáticamente los secretos desde el archivo local cifrado
al iniciar el sistema. Se integra con el ejecutor_completo.py
"""

import os
import sys
from pathlib import Path

def load_secrets_automatically():
    """Carga secretos automáticamente desde archivo local"""
    
    try:
        from secrets_manager import SecretsManager
    except ImportError:
        # Si no está disponible, intentar cargar desde .env.local
        from dotenv import load_dotenv
        env_file = Path('.env.local')
        if env_file.exists():
            load_dotenv(env_file)
            return True
        return False
    
    # Intentar cargar desde archivo cifrado
    manager = SecretsManager()
    
    if not manager.secrets_file.exists():
        # Si no existe, intentar .env.local como fallback
        from dotenv import load_dotenv
        env_file = Path('.env.local')
        if env_file.exists():
            load_dotenv(env_file)
            return True
        return False
    
    # Cargar secretos cifrados
    # IMPORTANTE: En modo automático, NO solicitamos password interactivamente
    # Solo intentamos si hay password en variable de entorno
    try:
        # Primero verificar si hay password en variable de entorno
        master_password = os.getenv('BMC_MASTER_PASSWORD')
        
        if master_password:
            # Intentar cargar con password de variable de entorno (modo silencioso)
            secrets = manager.load_secrets(master_password, silent=True)
            
            if secrets:
                # Cargar en variables de entorno
                for key, value in secrets.items():
                    os.environ[key] = value
                return True
        else:
            # Sin password disponible, no intentar cargar (evita prompt interactivo)
            # Usar .env.local como fallback silenciosamente
            pass
            
    except Exception as e:
        # Si falla por cualquier razón, usar .env.local como fallback
        # No mostrar error para no interrumpir el flujo automático
        pass
    
    # Fallback: usar .env.local
    try:
        from dotenv import load_dotenv
        env_file = Path('.env.local')
        if env_file.exists():
            load_dotenv(env_file)
            return True
    except Exception:
        pass
    
    return False

# Auto-cargar al importar
if __name__ != "__main__":
    load_secrets_automatically()


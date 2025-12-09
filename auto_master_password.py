#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generación Automática de Contraseña Maestra
============================================

Este módulo genera automáticamente una contraseña maestra si no existe,
y la guarda de forma segura para uso automático.

NO necesitas crear la contraseña manualmente - se genera automáticamente.
"""

import os
import secrets
import base64
from pathlib import Path
from typing import Optional

def generate_secure_password(length: int = 32) -> str:
    """Genera una contraseña segura aleatoria"""
    # Generar bytes aleatorios seguros
    random_bytes = secrets.token_bytes(length)
    # Convertir a string base64 seguro
    password = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
    return password

def get_or_create_master_password() -> str:
    """
    Obtiene o crea automáticamente la contraseña maestra
    
    Returns:
        Contraseña maestra (generada automáticamente si no existe)
    """
    # Primero verificar si ya existe en variable de entorno
    existing = os.getenv('BMC_MASTER_PASSWORD')
    if existing:
        return existing
    
    # Verificar si hay un archivo de contraseña guardado
    home = Path.home()
    password_file = home / '.bmc-secrets' / '.master_password'
    
    # Crear directorio si no existe
    password_file.parent.mkdir(mode=0o700, exist_ok=True)
    
    # Si existe, leerla
    if password_file.exists():
        try:
            password = password_file.read_text(encoding='utf-8').strip()
            if password:
                # Guardar en variable de entorno para esta sesión
                os.environ['BMC_MASTER_PASSWORD'] = password
                return password
        except Exception:
            pass
    
    # Si no existe, generar una nueva automáticamente
    print("🔐 Generando contraseña maestra automáticamente...")
    new_password = generate_secure_password(32)
    
    # Guardar en archivo seguro
    try:
        password_file.write_text(new_password, encoding='utf-8')
        password_file.chmod(0o600)  # Solo lectura/escritura para el usuario
        print(f"✅ Contraseña maestra generada y guardada en: {password_file}")
        print("   (No necesitas recordarla - se usa automáticamente)")
    except Exception as e:
        print(f"⚠️  No se pudo guardar la contraseña en archivo: {e}")
        print("   Se usará solo en esta sesión")
    
    # Guardar en variable de entorno para esta sesión
    os.environ['BMC_MASTER_PASSWORD'] = new_password
    
    return new_password

def setup_auto_master_password():
    """
    Configura la contraseña maestra automáticamente
    Se ejecuta automáticamente al importar
    """
    try:
        get_or_create_master_password()
        return True
    except Exception:
        return False

# Auto-ejecutar al importar
if __name__ != "__main__":
    setup_auto_master_password()


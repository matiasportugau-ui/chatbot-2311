#!/usr/bin/env python3
"""
Secrets Encryption - Encriptación de secrets.
Fase -2: Configuración y Variables
"""

import base64
from cryptography.fernet import Fernet
from pathlib import Path
from typing import bytes


class SecretsEncryption:
    """Maneja encriptación de secrets."""
    
    def __init__(self, key_file: str = "system/config/.encryption_key"):
        self.key_file = Path(key_file)
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        """Obtiene o crea la clave de encriptación."""
        if self.key_file.exists():
            return self.key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            self.key_file.write_bytes(key)
            return key
    
    def encrypt(self, data: bytes) -> bytes:
        """Encripta datos."""
        return self.cipher.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Desencripta datos."""
        return self.cipher.decrypt(encrypted_data)


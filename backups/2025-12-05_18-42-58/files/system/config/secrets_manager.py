#!/usr/bin/env python3
"""
Secrets Manager - Gestor de secrets.
Fase -2: Configuración y Variables
"""

import base64
from pathlib import Path
from typing import Dict, Any, Optional
from system.config.secrets_encryption import SecretsEncryption


class SecretsManager:
    """Gestiona secrets de forma segura."""
    
    def __init__(self, secrets_file: str = "system/config/secrets.json.encrypted"):
        self.secrets_file = Path(secrets_file)
        self.secrets_file.parent.mkdir(parents=True, exist_ok=True)
        self.encryption = SecretsEncryption()
        self.secrets = self._load_secrets()
    
    def _load_secrets(self) -> Dict[str, Any]:
        """Carga secrets encriptados."""
        if self.secrets_file.exists():
            try:
                encrypted_data = self.secrets_file.read_bytes()
                decrypted = self.encryption.decrypt(encrypted_data)
                import json
                return json.loads(decrypted)
            except Exception:
                return {}
        return {}
    
    def _save_secrets(self):
        """Guarda secrets encriptados."""
        import json
        data = json.dumps(self.secrets, indent=2)
        encrypted = self.encryption.encrypt(data.encode())
        self.secrets_file.write_bytes(encrypted)
    
    def get_secret(self, key: str) -> Optional[str]:
        """Obtiene un secret."""
        return self.secrets.get(key)
    
    def set_secret(self, key: str, value: str):
        """Establece un secret."""
        self.secrets[key] = value
        self._save_secrets()
    
    def rotate_secret(self, key: str, new_value: str):
        """Rota un secret."""
        old_value = self.secrets.get(key)
        self.set_secret(key, new_value)
        return old_value


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor de Secretos Local Seguro
================================

Sistema para gestionar secretos de forma local y segura:
- Cifrado de secretos
- Almacenamiento local fuera del repositorio
- Carga automática al iniciar
- Backup automático

Mejores Prácticas:
- Secretos nunca en Git
- Cifrado local
- Control total del usuario
"""

import os
import json
import base64
import getpass
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    OKCYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

class SecretsManager:
    """Gestor de secretos local y seguro"""
    
    def __init__(self, secrets_dir: Optional[str] = None):
        # Directorio por defecto: ~/.bmc-secrets
        if secrets_dir:
            self.secrets_dir = Path(secrets_dir)
        else:
            home = Path.home()
            self.secrets_dir = home / '.bmc-secrets'
        
        self.secrets_dir.mkdir(mode=0o700, exist_ok=True)
        self.secrets_file = self.secrets_dir / 'secrets.encrypted'
        self.master_key_file = self.secrets_dir / 'master.key'
        self.backup_dir = self.secrets_dir / 'backup'
        self.backup_dir.mkdir(mode=0o700, exist_ok=True)
    
    def _generate_master_key(self, password: str, salt: bytes) -> bytes:
        """Genera clave maestra desde password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _get_or_create_master_key(self, password: Optional[str] = None) -> bytes:
        """Obtiene o crea clave maestra"""
        if self.master_key_file.exists():
            if password is None:
                password = getpass.getpass("🔐 Ingresa la contraseña maestra: ")
            
            # Leer salt
            with open(self.master_key_file, 'rb') as f:
                salt = f.read(16)
            
            return self._generate_master_key(password, salt)
        else:
            # Crear nueva clave
            if password is None:
                password = getpass.getpass("🔐 Crea una contraseña maestra (guárdala en lugar seguro): ")
                confirm = getpass.getpass("🔐 Confirma la contraseña: ")
                if password != confirm:
                    raise ValueError("Las contraseñas no coinciden")
            
            # Generar salt
            salt = os.urandom(16)
            
            # Guardar salt
            with open(self.master_key_file, 'wb') as f:
                f.write(salt)
            
            os.chmod(self.master_key_file, 0o600)
            
            return self._generate_master_key(password, salt)
    
    def _get_fernet(self, password: Optional[str] = None) -> Fernet:
        """Obtiene objeto Fernet para cifrado"""
        key = self._get_or_create_master_key(password)
        return Fernet(key)
    
    def create_secrets_file(self, secrets: Dict[str, str], password: Optional[str] = None):
        """Crea archivo de secretos cifrado"""
        fernet = self._get_fernet(password)
        
        # Convertir a JSON y cifrar
        secrets_json = json.dumps(secrets, indent=2)
        encrypted = fernet.encrypt(secrets_json.encode())
        
        # Guardar
        self.secrets_file.write_bytes(encrypted)
        os.chmod(self.secrets_file, 0o600)
        
        print_success(f"Secretos guardados en: {self.secrets_file}")
        print_warning("⚠️  IMPORTANTE: Guarda tu contraseña maestra en un lugar seguro")
    
    def load_secrets(self, password: Optional[str] = None, silent: bool = False) -> Dict[str, str]:
        """Carga secretos desde archivo cifrado
        
        Args:
            password: Contraseña maestra (opcional)
            silent: Si True, no muestra errores ni prompts (para modo automático)
        
        Returns:
            Dict con los secretos, o {} si falla
        """
        if not self.secrets_file.exists():
            return {}
        
        try:
            # En modo silencioso, si no hay password, no intentar (evita prompt)
            if silent and password is None:
                return {}
            
            fernet = self._get_fernet(password)
            
            # Leer y descifrar
            encrypted = self.secrets_file.read_bytes()
            decrypted = fernet.decrypt(encrypted)
            secrets = json.loads(decrypted.decode())
            
            return secrets
        except Exception as e:
            if not silent:
                print_error(f"Error cargando secretos: {e}")
            return {}
    
    def add_secret(self, key: str, value: str, password: Optional[str] = None):
        """Agrega o actualiza un secreto"""
        secrets = self.load_secrets(password)
        secrets[key] = value
        self.create_secrets_file(secrets, password)
        print_success(f"Secreto '{key}' guardado")
    
    def get_secret(self, key: str, password: Optional[str] = None) -> Optional[str]:
        """Obtiene un secreto"""
        secrets = self.load_secrets(password)
        return secrets.get(key)
    
    def list_secrets(self, password: Optional[str] = None) -> List[str]:
        """Lista todas las claves de secretos (sin valores)"""
        secrets = self.load_secrets(password)
        return list(secrets.keys())
    
    def backup_secrets(self, password: Optional[str] = None):
        """Crea backup de secretos"""
        if not self.secrets_file.exists():
            print_warning("No hay secretos para respaldar")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f'secrets_{timestamp}.encrypted'
        
        shutil.copy(self.secrets_file, backup_file)
        os.chmod(backup_file, 0o600)
        
        print_success(f"Backup creado: {backup_file}")
    
    def export_to_env(self, password: Optional[str] = None, env_file: str = '.env.local'):
        """Exporta secretos a archivo .env.local"""
        secrets = self.load_secrets(password)
        
        if not secrets:
            print_warning("No hay secretos para exportar")
            return
        
        # Leer .env.local existente si existe
        env_data = {}
        env_path = Path(env_file)
        if env_path.exists():
            for line in env_path.read_text(encoding='utf-8').splitlines():
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_data[key.strip()] = value.strip().strip('"').strip("'")
        
        # Actualizar con secretos
        env_data.update(secrets)
        
        # Escribir .env.local
        lines = [
            "# Archivo generado automáticamente por secrets_manager.py",
            "# NO subir a Git - contiene secretos",
            "",
        ]
        
        for key, value in sorted(env_data.items()):
            # Escapar valores
            if ' ' in value or '#' in value:
                value = f'"{value}"'
            lines.append(f"{key}={value}")
        
        env_path.write_text('\n'.join(lines), encoding='utf-8')
        os.chmod(env_path, 0o600)
        
        print_success(f"Secretos exportados a: {env_file}")
        print_warning("⚠️  Asegúrate de que .env.local está en .gitignore")

def main():
    """CLI para gestión de secretos"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestor de Secretos Local Seguro')
    parser.add_argument('action', choices=['create', 'add', 'get', 'list', 'export', 'backup'],
                       help='Acción a realizar')
    parser.add_argument('--key', help='Clave del secreto')
    parser.add_argument('--value', help='Valor del secreto')
    parser.add_argument('--env-file', default='.env.local', help='Archivo .env a exportar')
    parser.add_argument('--secrets-dir', help='Directorio de secretos (default: ~/.bmc-secrets)')
    
    args = parser.parse_args()
    
    manager = SecretsManager(args.secrets_dir)
    
    if args.action == 'create':
        print("📝 Creando archivo de secretos...")
        print("Ingresa los secretos (presiona Enter con valor vacío para terminar):")
        
        secrets = {}
        while True:
            key = input("Clave (o Enter para terminar): ").strip()
            if not key:
                break
            value = getpass.getpass(f"Valor para {key}: ")
            secrets[key] = value
        
        if secrets:
            manager.create_secrets_file(secrets)
        else:
            print_warning("No se ingresaron secretos")
    
    elif args.action == 'add':
        if not args.key or not args.value:
            print_error("Se requiere --key y --value")
            return
        manager.add_secret(args.key, args.value)
    
    elif args.action == 'get':
        if not args.key:
            print_error("Se requiere --key")
            return
        value = manager.get_secret(args.key)
        if value:
            print(f"{args.key}={value}")
        else:
            print_warning(f"Secreto '{args.key}' no encontrado")
    
    elif args.action == 'list':
        keys = manager.list_secrets()
        if keys:
            print("Secretos disponibles:")
            for key in keys:
                print(f"  • {key}")
        else:
            print_warning("No hay secretos guardados")
    
    elif args.action == 'export':
        manager.export_to_env(env_file=args.env_file)
    
    elif args.action == 'backup':
        manager.backup_secrets()

if __name__ == "__main__":
    main()


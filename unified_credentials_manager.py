#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Unificado de Gestión de Credenciales
============================================

Sistema centralizado que:
1. Almacena TODAS las credenciales en un solo lugar
2. Se carga automáticamente en todos los scripts
3. Soporta múltiples fuentes (cifrado local, .env, variables de entorno)
4. Integración automática con todos los componentes del sistema

Uso:
    # En cualquier script, simplemente importa:
    from unified_credentials_manager import get_credential
    
    # Obtener cualquier credencial:
    token = get_credential('GITHUB_TOKEN')
    api_key = get_credential('OPENAI_API_KEY')
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List, Any
from functools import lru_cache

# Importar sistemas existentes
try:
    from secrets_manager import SecretsManager
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False

# Importar generador automático de contraseña maestra
try:
    from auto_master_password import get_or_create_master_password, setup_auto_master_password
    # Configurar automáticamente al importar
    setup_auto_master_password()
    AUTO_MASTER_PASSWORD_AVAILABLE = True
except ImportError:
    AUTO_MASTER_PASSWORD_AVAILABLE = False
    def get_or_create_master_password():
        return os.getenv('BMC_MASTER_PASSWORD', '')

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# Lista completa de credenciales que el sistema necesita
ALL_CREDENTIALS = {
    # GitHub
    'GITHUB_TOKEN': {
        'description': 'Token de GitHub para acceso a repositorios',
        'required_for': ['repo_research_agent', 'github_analyzer'],
        'source': 'https://github.com/settings/tokens'
    },
    'GITHUB_OWNER': {
        'description': 'Propietario/organización de GitHub',
        'required_for': ['repo_research_agent'],
        'default': 'matiasportugau-ui'
    },
    
    # IA Providers
    'OPENAI_API_KEY': {
        'description': 'API Key de OpenAI',
        'required_for': ['model_integrator', 'ai_assistant'],
        'source': 'https://platform.openai.com/account/api-keys'
    },
    'GROQ_API_KEY': {
        'description': 'API Key de Groq',
        'required_for': ['model_integrator'],
        'source': 'https://console.groq.com/keys'
    },
    'GEMINI_API_KEY': {
        'description': 'API Key de Google Gemini',
        'required_for': ['model_integrator'],
        'source': 'https://makersuite.google.com/app/apikey'
    },
    'XAI_API_KEY': {
        'description': 'API Key de xAI (Grok)',
        'required_for': ['model_integrator'],
        'source': 'https://console.x.ai/'
    },
    'GROK_API_KEY': {
        'description': 'API Key de Grok (alias de XAI)',
        'required_for': ['model_integrator'],
        'source': 'https://console.x.ai/'
    },
    
    # MongoDB
    'MONGODB_URI': {
        'description': 'URI de conexión a MongoDB',
        'required_for': ['mongodb_service', 'base_conocimiento_dinamica'],
        'default': 'mongodb://localhost:27017'
    },
    'MONGODB_DATABASE': {
        'description': 'Nombre de la base de datos MongoDB',
        'required_for': ['mongodb_service'],
        'default': 'bmc_chatbot'
    },
    
    # WhatsApp
    'WHATSAPP_API_KEY': {
        'description': 'API Key de WhatsApp Business',
        'required_for': ['integracion_whatsapp'],
        'source': 'https://developers.facebook.com/'
    },
    'WHATSAPP_PHONE_NUMBER_ID': {
        'description': 'Phone Number ID de WhatsApp',
        'required_for': ['integracion_whatsapp']
    },
    'WHATSAPP_VERIFY_TOKEN': {
        'description': 'Token de verificación de WhatsApp',
        'required_for': ['integracion_whatsapp']
    },
    
    # Google Sheets
    'GOOGLE_SHEETS_CREDENTIALS': {
        'description': 'Ruta al archivo JSON de credenciales de Google Sheets',
        'required_for': ['integracion_google_sheets'],
        'default': 'credentials/google-sheets.json'
    },
    'GOOGLE_SHEETS_SPREADSHEET_ID': {
        'description': 'ID de la hoja de cálculo de Google Sheets',
        'required_for': ['integracion_google_sheets']
    },
    
    # N8N
    'N8N_API_URL': {
        'description': 'URL de la API de N8N',
        'required_for': ['n8n_integration'],
        'default': 'http://localhost:5678'
    },
    'N8N_API_KEY': {
        'description': 'API Key de N8N',
        'required_for': ['n8n_integration']
    },

    # Dropbox
    'DROPBOX_APP_KEY': {
        'description': 'App Key de Dropbox',
        'required_for': ['dropbox_integration'],
        'source': 'https://www.dropbox.com/developers/apps'
    },
    'DROPBOX_APP_SECRET': {
        'description': 'App Secret de Dropbox',
        'required_for': ['dropbox_integration'],
        'source': 'https://www.dropbox.com/developers/apps'
    },
    'DROPBOX_ACCESS_TOKEN': {
        'description': 'Access Token de Dropbox',
        'required_for': ['dropbox_integration'],
        'source': 'https://www.dropbox.com/developers/apps'
    },
    'DROPBOX_REFRESH_TOKEN': {
        'description': 'Refresh Token de Dropbox (para acceso offline)',
        'required_for': ['dropbox_integration'],
        'source': 'https://www.dropbox.com/developers/apps'
    },
    
    # Otros
    'BMC_MASTER_PASSWORD': {
        'description': 'Contraseña maestra para descifrar secretos (se genera automáticamente)',
        'required_for': ['secrets_manager'],
        'sensitive': True,
        'auto_generated': True,
        'note': 'No necesitas configurarla - se genera automáticamente'
    }
}


class UnifiedCredentialsManager:
    """
    Gestor unificado de credenciales que carga desde múltiples fuentes
    """
    
    def __init__(self):
        self._credentials_cache: Dict[str, Optional[str]] = {}
        self._loaded = False
        self._load_sources = []
        
    def _load_all_sources(self):
        """Carga credenciales desde todas las fuentes disponibles"""
        if self._loaded:
            return
        
        # Orden de prioridad (más específico primero):
        # 1. Variables de entorno del sistema (ya cargadas)
        # 2. Archivo cifrado local (secrets_manager)
        # 3. .env.local
        # 4. .env
        
        # 1. Variables de entorno (ya están cargadas)
        self._load_sources.append('environment')
        
        # 2. Intentar cargar desde archivo cifrado
        if SECRETS_MANAGER_AVAILABLE:
            try:
                manager = SecretsManager()
                
                # Obtener o generar automáticamente la contraseña maestra
                if AUTO_MASTER_PASSWORD_AVAILABLE:
                    master_password = get_or_create_master_password()
                else:
                    master_password = os.getenv('BMC_MASTER_PASSWORD')
                
                if manager.secrets_file.exists() and master_password:
                    secrets = manager.load_secrets(master_password, silent=True)
                    if secrets:
                        for key, value in secrets.items():
                            if key not in os.environ:  # No sobrescribir variables de entorno
                                os.environ[key] = value
                        self._load_sources.append('encrypted_file')
            except Exception:
                pass
        
        # 3. Cargar desde .env.local
        if DOTENV_AVAILABLE:
            env_local = Path('.env.local')
            if env_local.exists():
                load_dotenv(env_local, override=False)  # No sobrescribir lo ya cargado
                self._load_sources.append('.env.local')
        
        # 4. Cargar desde .env
        if DOTENV_AVAILABLE:
            env_file = Path('.env')
            if env_file.exists():
                load_dotenv(env_file, override=False)
                self._load_sources.append('.env')
        
        self._loaded = True
    
    def get_credential(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Obtiene una credencial desde cualquier fuente disponible
        
        Args:
            key: Nombre de la credencial
            default: Valor por defecto si no se encuentra
        
        Returns:
            Valor de la credencial o default
        """
        self._load_all_sources()
        
        # Verificar cache
        if key in self._credentials_cache:
            return self._credentials_cache[key]
        
        # Obtener de variable de entorno
        value = os.getenv(key, default)
        
        # Si hay un default en ALL_CREDENTIALS, usarlo
        if value is None and key in ALL_CREDENTIALS:
            cred_info = ALL_CREDENTIALS[key]
            if 'default' in cred_info:
                value = cred_info['default']
        
        # Guardar en cache
        self._credentials_cache[key] = value
        
        return value
    
    def set_credential(self, key: str, value: str, save_to: str = 'encrypted'):
        """
        Guarda una credencial en el sistema
        
        Args:
            key: Nombre de la credencial
            value: Valor de la credencial
            save_to: Dónde guardar ('encrypted', 'env_local', 'env', 'all')
        """
        self._load_all_sources()
        
        # Actualizar variable de entorno actual
        os.environ[key] = value
        self._credentials_cache[key] = value
        
        # Guardar según opción
        if save_to in ['encrypted', 'all'] and SECRETS_MANAGER_AVAILABLE:
            try:
                manager = SecretsManager()
                
                # Obtener o generar automáticamente la contraseña maestra
                if AUTO_MASTER_PASSWORD_AVAILABLE:
                    master_password = get_or_create_master_password()
                else:
                    master_password = os.getenv('BMC_MASTER_PASSWORD')
                
                if master_password:
                    manager.add_secret(key, value, master_password)
            except Exception as e:
                print(f"⚠️  No se pudo guardar en archivo cifrado: {e}")
        
        if save_to in ['env_local', 'all']:
            self._update_env_file('.env.local', key, value)
        
        if save_to in ['env', 'all']:
            self._update_env_file('.env', key, value)
    
    def _update_env_file(self, env_file: str, key: str, value: str):
        """Actualiza un archivo .env con una credencial"""
        env_path = Path(env_file)
        
        # Leer archivo existente
        lines = []
        if env_path.exists():
            lines = env_path.read_text(encoding='utf-8').splitlines()
        
        # Buscar si ya existe la clave
        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f'{key}='):
                lines[i] = f'{key}={value}'
                found = True
                break
        
        # Si no existe, agregar al final
        if not found:
            lines.append(f'{key}={value}')
        
        # Escribir archivo
        env_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        os.chmod(env_path, 0o600)
    
    def check_credentials(self, required_keys: List[str] = None) -> Dict[str, bool]:
        """
        Verifica qué credenciales están disponibles
        
        Args:
            required_keys: Lista de claves a verificar (None = todas)
        
        Returns:
            Dict con estado de cada credencial
        """
        self._load_all_sources()
        
        if required_keys is None:
            required_keys = list(ALL_CREDENTIALS.keys())
        
        status = {}
        for key in required_keys:
            value = self.get_credential(key)
            status[key] = value is not None and value != ''
        
        return status
    
    def get_missing_credentials(self, required_keys: List[str] = None) -> List[str]:
        """Obtiene lista de credenciales faltantes"""
        status = self.check_credentials(required_keys)
        return [key for key, available in status.items() if not available]
    
    def print_status(self):
        """Imprime estado de todas las credenciales"""
        self._load_all_sources()
        
        print("\n" + "="*80)
        print("ESTADO DE CREDENCIALES")
        print("="*80)
        print(f"\nFuentes cargadas: {', '.join(self._load_sources) if self._load_sources else 'Ninguna'}")
        print()
        
        status = self.check_credentials()
        
        available = [k for k, v in status.items() if v]
        missing = [k for k, v in status.items() if not v]
        
        if available:
            print("✅ Credenciales Disponibles:")
            for key in sorted(available):
                cred_info = ALL_CREDENTIALS.get(key, {})
                desc = cred_info.get('description', '')
                print(f"  • {key}: {desc}")
        
        if missing:
            print("\n❌ Credenciales Faltantes:")
            for key in sorted(missing):
                cred_info = ALL_CREDENTIALS.get(key, {})
                desc = cred_info.get('description', '')
                source = cred_info.get('source', '')
                print(f"  • {key}: {desc}")
                if source:
                    print(f"    📎 {source}")
        
        print()


# Instancia global
_global_manager = None

def get_credential(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Función de conveniencia para obtener credenciales
    
    Uso:
        token = get_credential('GITHUB_TOKEN')
        api_key = get_credential('OPENAI_API_KEY', default='')
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = UnifiedCredentialsManager()
    return _global_manager.get_credential(key, default)

def set_credential(key: str, value: str, save_to: str = 'encrypted'):
    """Función de conveniencia para guardar credenciales"""
    global _global_manager
    if _global_manager is None:
        _global_manager = UnifiedCredentialsManager()
    _global_manager.set_credential(key, value, save_to)

def check_credentials(required_keys: List[str] = None) -> Dict[str, bool]:
    """Función de conveniencia para verificar credenciales"""
    global _global_manager
    if _global_manager is None:
        _global_manager = UnifiedCredentialsManager()
    return _global_manager.check_credentials(required_keys)

# Auto-cargar al importar
if __name__ != "__main__":
    # Cargar automáticamente al importar
    _global_manager = UnifiedCredentialsManager()
    _global_manager._load_all_sources()


def main():
    """CLI para gestión de credenciales"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema Unificado de Gestión de Credenciales')
    parser.add_argument('action', nargs='?', choices=['status', 'get', 'set', 'check', 'wizard'],
                       default='status', help='Acción a realizar')
    parser.add_argument('--key', help='Clave de la credencial')
    parser.add_argument('--value', help='Valor de la credencial')
    parser.add_argument('--save-to', choices=['encrypted', 'env_local', 'env', 'all'],
                       default='encrypted', help='Dónde guardar')
    parser.add_argument('--required', nargs='+', help='Lista de credenciales requeridas para verificar')
    
    args = parser.parse_args()
    
    manager = UnifiedCredentialsManager()
    
    if args.action == 'status':
        manager.print_status()
    
    elif args.action == 'get':
        if not args.key:
            print("❌ Se requiere --key")
            return
        value = manager.get_credential(args.key)
        if value:
            print(f"{args.key}={value}")
        else:
            print(f"❌ Credencial '{args.key}' no encontrada")
    
    elif args.action == 'set':
        if not args.key or not args.value:
            print("❌ Se requiere --key y --value")
            return
        manager.set_credential(args.key, args.value, args.save_to)
        print(f"✅ Credencial '{args.key}' guardada")
    
    elif args.action == 'check':
        required = args.required if args.required else None
        status = manager.check_credentials(required)
        missing = manager.get_missing_credentials(required)
        
        if missing:
            print(f"❌ Faltan {len(missing)} credenciales:")
            for key in missing:
                print(f"  • {key}")
            sys.exit(1)
        else:
            print("✅ Todas las credenciales requeridas están disponibles")
            sys.exit(0)
    
    elif args.action == 'wizard':
        print("\n" + "="*80)
        print("WIZARD DE CONFIGURACIÓN DE CREDENCIALES")
        print("="*80)
        print("\nEste wizard te ayudará a configurar todas las credenciales necesarias.")
        print("Puedes presionar Enter para omitir cualquier credencial.\n")
        
        import getpass
        
        for key, info in ALL_CREDENTIALS.items():
            if info.get('sensitive'):
                continue  # Saltar contraseñas maestras
            
            desc = info.get('description', '')
            source = info.get('source', '')
            default = info.get('default', '')
            
            print(f"\n📝 {key}")
            print(f"   {desc}")
            if source:
                print(f"   📎 {source}")
            if default:
                print(f"   (Default: {default})")
            
            current = manager.get_credential(key)
            if current:
                print(f"   ⚠️  Ya configurado (presiona Enter para mantener)")
            
            if key.upper().endswith('_PASSWORD') or key.upper().endswith('_TOKEN') or key.upper().endswith('_KEY'):
                value = getpass.getpass(f"   Valor: ")
            else:
                value = input(f"   Valor: ").strip()
            
            if value:
                manager.set_credential(key, value, save_to='all')
                print(f"   ✅ Guardado")
            elif current:
                print(f"   ℹ️  Mantenido: {current[:20]}...")
            else:
                print(f"   ⏭️  Omitido")
        
        print("\n" + "="*80)
        print("✅ Configuración completada")
        print("="*80)
        print("\nLas credenciales se han guardado en:")
        print("  • Archivo cifrado local (~/.bmc-secrets/secrets.encrypted)")
        print("  • .env.local (para desarrollo)")
        print("\n💡 Tip: Usa 'python unified_credentials_manager.py status' para verificar")


if __name__ == "__main__":
    main()


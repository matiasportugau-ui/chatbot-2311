#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Interactivo de Secretos
==============================

Guía al usuario para crear y configurar el archivo de secretos local
"""

import os
import sys
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    OKCYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def setup_secrets_interactive():
    """Setup interactivo de secretos"""
    
    print_header("CONFIGURACIÓN DE SECRETOS LOCALES")
    
    print_info("Este sistema guardará tus secretos de forma local y cifrada")
    print_info("Los secretos se almacenan en: ~/.bmc-secrets/")
    print_info("NUNCA se subirán a Git - están completamente locales")
    print()
    
    try:
        from secrets_manager import SecretsManager
    except ImportError:
        print_warning("secrets_manager no disponible")
        print_info("Instalando dependencias...")
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'cryptography'], check=True)
        from secrets_manager import SecretsManager
    
    manager = SecretsManager()
    
    # Verificar si ya existe
    if manager.secrets_file.exists():
        print_warning("Ya existe un archivo de secretos")
        respuesta = input("¿Deseas sobrescribirlo? (s/n): ").strip().lower()
        if respuesta != 's':
            print_info("Operación cancelada")
            return
    
    # Categorías de secretos
    categories = {
        'AI Providers': [
            'OPENAI_API_KEY',
            'GROQ_API_KEY',
            'GEMINI_API_KEY',
            'GROK_API_KEY',
        ],
        'Database': [
            'MONGODB_URI',
            'DATABASE_URL',
        ],
        'Google Services': [
            'GOOGLE_SHEET_ID',
            'GOOGLE_SERVICE_ACCOUNT_EMAIL',
            'GOOGLE_PRIVATE_KEY',
        ],
        'WhatsApp': [
            'WHATSAPP_ACCESS_TOKEN',
            'WHATSAPP_PHONE_NUMBER_ID',
            'WHATSAPP_VERIFY_TOKEN',
        ],
        'Mercado Libre': [
            'MERCADO_LIBRE_APP_ID',
            'MERCADO_LIBRE_CLIENT_SECRET',
            'MERCADO_LIBRE_SELLER_ID',
        ],
        'n8n': [
            'N8N_API_KEY',
            'N8N_BASE_URL',
        ],
        'System': [
            'NEXTAUTH_SECRET',
        ]
    }
    
    secrets = {}
    
    print()
    print_info("Ingresa tus secretos (presiona Enter para omitir):")
    print()
    
    import getpass
    
    for category, keys in categories.items():
        print(f"{Colors.BOLD}{category}:{Colors.ENDC}")
        for key in keys:
            # Verificar si ya existe en .env.local
            env_value = os.getenv(key, '')
            if env_value:
                respuesta = input(f"  {key} [ya configurado en .env.local, usar? (s/n)]: ").strip().lower()
                if respuesta == 's' or respuesta == '':
                    secrets[key] = env_value
                    print_success(f"    {key}: Usado desde .env.local")
                    continue
            
            value = getpass.getpass(f"  {key}: ").strip()
            if value:
                secrets[key] = value
                print_success(f"    {key}: Guardado")
            else:
                print_info(f"    {key}: Omitido")
        print()
    
    if secrets:
        print_info("Creando archivo de secretos cifrado...")
        manager.create_secrets_file(secrets)
        
        # Crear backup
        print_info("Creando backup...")
        manager.backup_secrets()
        
        # Exportar a .env.local (opcional)
        print()
        respuesta = input("¿Deseas exportar también a .env.local? (s/n): ").strip().lower()
        if respuesta == 's':
            manager.export_to_env()
        
        print()
        print_success("✅ Secretos configurados exitosamente")
        print()
        print_info("Ubicación del archivo de secretos:")
        print(f"  {manager.secrets_file}")
        print()
        print_info("Ubicación de la clave maestra:")
        print(f"  {manager.master_key_file}")
        print()
        print_warning("⚠️  IMPORTANTE:")
        print("  • Guarda tu contraseña maestra en un lugar seguro")
        print("  • El archivo de secretos está cifrado y es seguro")
        print("  • Nunca compartas tu contraseña maestra")
        print("  • Haz backups periódicos del directorio ~/.bmc-secrets/")
    else:
        print_warning("No se ingresaron secretos")

if __name__ == "__main__":
    setup_secrets_interactive()


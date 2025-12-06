#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analiza y compara archivos .env en el sistema
Muestra qué credenciales están disponibles y dónde
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def read_env_file(filepath: Path) -> Dict[str, str]:
    """Lee un archivo .env y retorna un diccionario"""
    env_data = {}
    if not filepath.exists():
        return env_data
    
    try:
        for line in filepath.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if value and not value.startswith('your-') and value != '':
                    env_data[key] = value
    except Exception as e:
        print_warning(f"Error leyendo {filepath}: {e}")
    
    return env_data

def find_env_files(base_path: Path, max_depth: int = 5) -> List[Path]:
    """Encuentra todos los archivos .env en el sistema"""
    env_files = []
    
    # Buscar en el directorio actual y subdirectorios
    patterns = ['.env', '.env.local', '.env.production', '.env.development', 
                '.env.example', 'env.example', 'vercel.env']
    
    for pattern in patterns:
        for env_file in base_path.rglob(pattern):
            if env_file.is_file() and env_file not in env_files:
                env_files.append(env_file)
    
    return env_files

def mask_sensitive_value(key: str, value: str) -> str:
    """Enmascara valores sensibles para mostrar"""
    if not value or len(value) < 8:
        return "***"
    
    sensitive_keywords = ['KEY', 'SECRET', 'TOKEN', 'PASSWORD', 'PRIVATE', 'API']
    if any(keyword in key.upper() for keyword in sensitive_keywords):
        return value[:8] + "..." + value[-4:]
    return value[:50]

def analyze_credentials():
    """Analiza y compara credenciales de todos los archivos .env"""
    
    print_header("ANÁLISIS DE CREDENCIALES DISPONIBLES")
    
    # Directorios a buscar
    search_paths = [
        Path('/Users/matias/chatbot2511/chatbot-2311'),
        Path('/Users/matias/Documents/GitHub/sistema-cotizaciones-bmc'),
        Path('/Users/matias/Documents/GitHub/BMC-Ecosystem'),
    ]
    
    all_env_files = []
    for base_path in search_paths:
        if base_path.exists():
            env_files = find_env_files(base_path, max_depth=5)
            all_env_files.extend(env_files)
    
    if not all_env_files:
        print_warning("No se encontraron archivos .env")
        return
    
    print_info(f"Se encontraron {len(all_env_files)} archivo(s) .env\n")
    
    # Leer todos los archivos
    all_credentials = {}
    file_credentials = {}
    
    for env_file in all_env_files:
        rel_path = env_file.relative_to(env_file.anchor) if env_file.is_absolute() else env_file
        print(f"📄 Analizando: {rel_path}")
        
        creds = read_env_file(env_file)
        file_credentials[str(rel_path)] = creds
        
        # Consolidar credenciales
        for key, value in creds.items():
            if key not in all_credentials:
                all_credentials[key] = []
            all_credentials[key].append({
                'file': str(rel_path),
                'value': value
            })
    
    print()
    
    # Categorizar credenciales
    categories = {
        'AI Providers': ['OPENAI_API_KEY', 'GROQ_API_KEY', 'GEMINI_API_KEY', 'GROK_API_KEY'],
        'Database': ['MONGODB_URI', 'DATABASE_URL', 'REDIS_URL'],
        'Google Services': ['GOOGLE_SHEET_ID', 'GOOGLE_SERVICE_ACCOUNT_EMAIL', 'GOOGLE_PRIVATE_KEY', 'GOOGLE_SHEETS_API_KEY'],
        'WhatsApp': ['WHATSAPP_ACCESS_TOKEN', 'WHATSAPP_PHONE_NUMBER_ID', 'WHATSAPP_VERIFY_TOKEN', 'WHATSAPP_BUSINESS_ID'],
        'Mercado Libre': ['MERCADO_LIBRE_APP_ID', 'MERCADO_LIBRE_CLIENT_SECRET', 'MERCADO_LIBRE_ACCESS_TOKEN', 'MERCADO_LIBRE_SELLER_ID'],
        'n8n': ['N8N_API_KEY', 'N8N_BASE_URL', 'N8N_PUBLIC_KEY', 'N8N_PRIVATE_KEY'],
        'System': ['NODE_ENV', 'NEXTAUTH_SECRET', 'NEXTAUTH_URL', 'LOG_LEVEL'],
        'Other': []
    }
    
    # Mostrar credenciales por categoría
    print_header("CREDENCIALES DISPONIBLES POR CATEGORÍA")
    
    for category, keys in categories.items():
        found_keys = [k for k in keys if k in all_credentials]
        if not found_keys and category != 'Other':
            continue
        
        print(f"\n{Colors.BOLD}{category}:{Colors.ENDC}")
        print("-" * 80)
        
        if category == 'Other':
            # Mostrar credenciales no categorizadas
            categorized = set()
            for keys_list in categories.values():
                categorized.update(keys_list)
            other_keys = [k for k in all_credentials.keys() if k not in categorized]
            if not other_keys:
                continue
            for key in sorted(other_keys):
                show_credential(key, all_credentials[key])
        else:
            for key in found_keys:
                show_credential(key, all_credentials[key])
    
    # Resumen de archivos
    print_header("RESUMEN POR ARCHIVO")
    
    for filepath, creds in sorted(file_credentials.items()):
        if creds:
            print(f"\n{Colors.BOLD}{filepath}:{Colors.ENDC}")
            print(f"   {len(creds)} credencial(es) encontrada(s)")
            for key in sorted(creds.keys())[:5]:  # Mostrar primeras 5
                masked = mask_sensitive_value(key, creds[key])
                print(f"   • {key}: {masked}")
            if len(creds) > 5:
                print(f"   ... y {len(creds) - 5} más")

def show_credential(key: str, locations: List[Dict]):
    """Muestra información de una credencial"""
    if not locations:
        return
    
    # Obtener el valor más reciente (último archivo)
    latest = locations[-1]
    masked_value = mask_sensitive_value(key, latest['value'])
    
    # Mostrar en cuántos archivos está
    if len(locations) == 1:
        print(f"  ✅ {key}: {masked_value}")
        print(f"     📍 Ubicación: {latest['file']}")
    else:
        print(f"  ⚠️  {key}: {masked_value}")
        print(f"     📍 Encontrado en {len(locations)} archivo(s):")
        for loc in locations:
            print(f"        • {loc['file']}")
    
    # Verificar si hay valores diferentes
    values = [loc['value'] for loc in locations]
    unique_values = set(values)
    if len(unique_values) > 1:
        print_warning(f"     ⚠️  Valores diferentes encontrados en {len(unique_values)} archivo(s)")

if __name__ == "__main__":
    try:
        analyze_credentials()
    except KeyboardInterrupt:
        print("\n\nAnálisis cancelado")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


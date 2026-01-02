#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lista todas las credenciales disponibles y listas para usar
Consolida información de todos los archivos .env encontrados
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
                # Filtrar valores placeholder
                if value and value not in ['', 'your-', 'your_', 'replace-'] and \
                   not value.startswith('your-') and not value.startswith('your_') and \
                   not value.startswith('replace-') and not value.startswith('tu-') and \
                   not value.startswith('change-') and not value.startswith('change_'):
                    env_data[key] = value
    except Exception as e:
        pass
    
    return env_data

def mask_sensitive_value(key: str, value: str) -> str:
    """Enmascara valores sensibles"""
    if not value or len(value) < 8:
        return "***"
    
    sensitive_keywords = ['KEY', 'SECRET', 'TOKEN', 'PASSWORD', 'PRIVATE', 'API']
    if any(keyword in key.upper() for keyword in sensitive_keywords):
        if len(value) > 20:
            return value[:12] + "..." + value[-6:]
        return value[:8] + "..."
    return value[:60]

def find_best_credentials():
    """Encuentra las mejores credenciales disponibles"""
    
    print_header("ANÁLISIS DE CREDENCIALES DISPONIBLES")
    
    # Archivos principales a revisar (orden de prioridad)
    priority_files = [
        Path('/Users/matias/chatbot2511/chatbot-2311/.env.local'),
        Path('/Users/matias/chatbot2511/chatbot-2311/.env'),
        Path('/Users/matias/Documents/GitHub/sistema-cotizaciones-bmc/.env.local'),
        Path('/Users/matias/Documents/GitHub/sistema-cotizaciones-bmc/.env.production'),
        Path('/Users/matias/Documents/GitHub/BMC-Ecosystem/apps/sistema-cotizaciones/.env.local'),
        Path('/Users/matias/Documents/GitHub/BMC-Ecosystem/packages/bmc/cotizacion/vercel.env'),
    ]
    
    all_credentials = {}
    file_sources = defaultdict(list)
    
    # Leer archivos en orden de prioridad
    for env_file in priority_files:
        if env_file.exists():
            print_info(f"Leyendo: {env_file}")
            creds = read_env_file(env_file)
            for key, value in creds.items():
                # Si no existe o el valor anterior es placeholder, usar el nuevo
                if key not in all_credentials or \
                   all_credentials[key].startswith('your-') or \
                   all_credentials[key].startswith('tu-') or \
                   all_credentials[key].startswith('replace-'):
                    all_credentials[key] = value
                    file_sources[key].append(str(env_file.name))
    
    # Categorizar credenciales
    categories = {
        'AI Providers': {
            'OPENAI_API_KEY': 'OpenAI API Key',
            'GROQ_API_KEY': 'Groq API Key',
            'GEMINI_API_KEY': 'Gemini API Key',
            'GROK_API_KEY': 'Grok API Key',
            'OPENAI_MODELS': 'OpenAI Models',
            'GROQ_MODELS': 'Groq Models',
            'GEMINI_MODELS': 'Gemini Models',
            'GROK_MODELS': 'Grok Models',
        },
        'Database': {
            'MONGODB_URI': 'MongoDB URI',
            'DATABASE_URL': 'PostgreSQL URL',
            'REDIS_URL': 'Redis URL',
        },
        'Google Services': {
            'GOOGLE_SHEET_ID': 'Google Sheet ID',
            'GOOGLE_SERVICE_ACCOUNT_EMAIL': 'Google Service Account Email',
            'GOOGLE_PRIVATE_KEY': 'Google Private Key',
            'GOOGLE_SHEETS_API_KEY': 'Google Sheets API Key',
        },
        'WhatsApp': {
            'WHATSAPP_ACCESS_TOKEN': 'WhatsApp Access Token',
            'WHATSAPP_PHONE_NUMBER_ID': 'WhatsApp Phone Number ID',
            'WHATSAPP_VERIFY_TOKEN': 'WhatsApp Verify Token',
            'WHATSAPP_BUSINESS_ID': 'WhatsApp Business ID',
            'WHATSAPP_APP_SECRET': 'WhatsApp App Secret',
        },
        'Mercado Libre': {
            'MERCADO_LIBRE_APP_ID': 'Mercado Libre App ID',
            'MERCADO_LIBRE_CLIENT_SECRET': 'Mercado Libre Client Secret',
            'MERCADO_LIBRE_SELLER_ID': 'Mercado Libre Seller ID',
            'MERCADO_LIBRE_ACCESS_TOKEN': 'Mercado Libre Access Token',
            'MERCADO_LIBRE_REFRESH_TOKEN': 'Mercado Libre Refresh Token',
            'MERCADO_LIBRE_WEBHOOK_SECRET': 'Mercado Libre Webhook Secret',
        },
        'n8n': {
            'N8N_API_KEY': 'n8n API Key',
            'N8N_BASE_URL': 'n8n Base URL',
            'N8N_PUBLIC_KEY': 'n8n Public Key',
            'N8N_PRIVATE_KEY': 'n8n Private Key',
        },
        'System': {
            'NEXTAUTH_SECRET': 'NextAuth Secret',
            'NEXTAUTH_URL': 'NextAuth URL',
            'NODE_ENV': 'Node Environment',
            'LOG_LEVEL': 'Log Level',
        },
        'Other Services': {
            'KUBIKS_API_KEY': 'Kubiks API Key',
            'CREDENTIALS_ENCRYPTION_KEY': 'Credentials Encryption Key',
        }
    }
    
    # Mostrar credenciales por categoría
    print_header("CREDENCIALES DISPONIBLES Y LISTAS")
    
    total_found = 0
    total_ready = 0
    
    for category, keys in categories.items():
        found_in_category = []
        
        for key, name in keys.items():
            if key in all_credentials:
                value = all_credentials[key]
                masked = mask_sensitive_value(key, value)
                found_in_category.append((key, name, value, masked))
                total_found += 1
                if value and len(value) > 5:  # Considerar "lista" si tiene valor real
                    total_ready += 1
        
        if found_in_category:
            print(f"\n{Colors.BOLD}{category}:{Colors.ENDC}")
            print("-" * 80)
            
            for key, name, value, masked in found_in_category:
                status = "✅ LISTA" if value and len(value) > 5 else "⚠️  PARCIAL"
                sources = ", ".join(set(file_sources[key][:2]))  # Mostrar máximo 2 fuentes
                if len(file_sources[key]) > 2:
                    sources += f" (+{len(file_sources[key])-2} más)"
                
                print(f"  {status} {name}")
                print(f"     Valor: {masked}")
                print(f"     Fuente: {sources}")
                print()
    
    # Resumen
    print_header("RESUMEN")
    
    print(f"\n{Colors.BOLD}Estadísticas:{Colors.ENDC}")
    print(f"  • Total de credenciales encontradas: {total_found}")
    print(f"  • Credenciales listas para usar: {total_ready}")
    print(f"  • Credenciales parciales/placeholder: {total_found - total_ready}")
    
    # Credenciales críticas
    print(f"\n{Colors.BOLD}Credenciales Críticas:{Colors.ENDC}")
    critical = {
        'OPENAI_API_KEY': 'OpenAI',
        'MONGODB_URI': 'MongoDB',
        'GOOGLE_SERVICE_ACCOUNT_EMAIL': 'Google Sheets',
        'MERCADO_LIBRE_APP_ID': 'Mercado Libre',
    }
    
    for key, name in critical.items():
        if key in all_credentials:
            value = all_credentials[key]
            if value and len(value) > 5:
                print_success(f"{name}: Configurado")
            else:
                print_warning(f"{name}: No configurado o incompleto")
        else:
            print_warning(f"{name}: No encontrado")
    
    print()
    
    # Recomendaciones
    print_header("RECOMENDACIONES")
    
    if 'OPENAI_API_KEY' in all_credentials and all_credentials['OPENAI_API_KEY']:
        print_success("OpenAI está configurado - El sistema puede usar IA avanzada")
    else:
        print_warning("OpenAI no está configurado - El sistema usará pattern matching")
    
    if 'GROQ_API_KEY' in all_credentials and all_credentials['GROQ_API_KEY']:
        print_success("Groq está configurado - Opción gratuita y rápida disponible")
    else:
        print_info("Groq no está configurado - Considera agregarlo (gratis)")
    
    if 'GOOGLE_SERVICE_ACCOUNT_EMAIL' in all_credentials and all_credentials['GOOGLE_SERVICE_ACCOUNT_EMAIL']:
        print_success("Google Sheets está configurado")
    else:
        print_info("Google Sheets no está configurado - Opcional")
    
    print()
    print_success("✅ Proceso completado. Credenciales analizadas y listadas.")
    print()
    
    return all_credentials

if __name__ == "__main__":
    try:
        credentials = find_best_credentials()
        print(f"\n{Colors.OKCYAN}Total de credenciales únicas encontradas: {len(credentials)}{Colors.ENDC}\n")
    except KeyboardInterrupt:
        print("\n\nAnálisis cancelado")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


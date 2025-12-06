#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificación de Configuración Completa
Verifica que todas las variables de entorno y dependencias estén correctamente configuradas
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Colores
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

def print_header(text: str):
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def load_env_file(env_path: Path) -> Dict[str, str]:
    """Carga variables de entorno desde archivo"""
    env_data = {}
    if not env_path.exists():
        return env_data
    
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        # Cargar manualmente
        for line in env_path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                value = value.strip().strip('"').strip("'")
                os.environ[key.strip()] = value
                env_data[key.strip()] = value
    else:
        # Si dotenv está disponible, leer el archivo manualmente también
        for line in env_path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                value = value.strip().strip('"').strip("'")
                env_data[key.strip()] = value
    
    return env_data

def check_python_modules() -> Tuple[int, int]:
    """Verifica módulos de Python"""
    print_header("VERIFICACIÓN DE MÓDULOS DE PYTHON")
    
    required_modules = [
        ('sistema_cotizaciones', 'Sistema de cotizaciones'),
        ('utils_cotizaciones', 'Utilidades de cotizaciones'),
    ]
    
    optional_modules = [
        ('openai', 'OpenAI SDK'),
        ('groq', 'Groq SDK'),
        ('google.genai', 'Google Gemini SDK'),
        ('pymongo', 'MongoDB driver'),
        ('fastapi', 'FastAPI framework'),
        ('uvicorn', 'Uvicorn server'),
        ('gspread', 'Google Sheets API'),
        ('redis', 'Redis client'),
        ('qdrant_client', 'Qdrant vector DB'),
    ]
    
    required_ok = 0
    optional_ok = 0
    
    print(f"{Colors.BOLD}Módulos Requeridos:{Colors.ENDC}")
    for module, name in required_modules:
        try:
            __import__(module)
            print_success(f"{name}: Instalado")
            required_ok += 1
        except ImportError:
            print_error(f"{name}: No instalado")
    
    print(f"\n{Colors.BOLD}Módulos Opcionales:{Colors.ENDC}")
    for module, name in optional_modules:
        try:
            __import__(module)
            print_success(f"{name}: Instalado")
            optional_ok += 1
        except ImportError:
            print_warning(f"{name}: No instalado (opcional)")
    
    return required_ok, optional_ok

def check_env_variables() -> Tuple[int, int]:
    """Verifica variables de entorno"""
    print_header("VERIFICACIÓN DE VARIABLES DE ENTORNO")
    
    # Cargar archivos .env
    env_local = Path('.env.local')
    env_file = Path('.env')
    
    env_data = {}
    if env_local.exists():
        print_info(f"Archivo encontrado: {env_local}")
        env_data = load_env_file(env_local)
    elif env_file.exists():
        print_info(f"Archivo encontrado: {env_file}")
        env_data = load_env_file(env_file)
    else:
        print_warning("No se encontró archivo .env o .env.local")
        return 0, 0
    
    required_vars = {
        'MONGODB_URI': 'MongoDB connection string',
    }
    
    optional_vars = {
        'OPENAI_API_KEY': 'OpenAI API Key',
        'GROQ_API_KEY': 'Groq API Key',
        'GEMINI_API_KEY': 'Gemini API Key',
        'GROK_API_KEY': 'Grok API Key',
        'GOOGLE_SHEET_ID': 'Google Sheet ID',
        'GOOGLE_SERVICE_ACCOUNT_EMAIL': 'Google Service Account Email',
        'GOOGLE_PRIVATE_KEY': 'Google Private Key',
        'WHATSAPP_ACCESS_TOKEN': 'WhatsApp Access Token',
        'MERCADO_LIBRE_APP_ID': 'Mercado Libre App ID',
        'N8N_API_KEY': 'n8n API Key',
    }
    
    required_ok = 0
    optional_ok = 0
    
    print(f"{Colors.BOLD}Variables Requeridas:{Colors.ENDC}")
    for var, name in required_vars.items():
        value = env_data.get(var) or os.getenv(var, '')
        if value:
            # Ocultar valores sensibles
            if 'KEY' in var or 'SECRET' in var or 'TOKEN' in var or 'PASSWORD' in var:
                preview = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print_success(f"{name}: {preview}")
            else:
                print_success(f"{name}: {value[:50]}")
            required_ok += 1
        else:
            print_error(f"{name}: No configurada")
    
    print(f"\n{Colors.BOLD}Variables Opcionales:{Colors.ENDC}")
    for var, name in optional_vars.items():
        value = env_data.get(var) or os.getenv(var, '')
        if value:
            if 'KEY' in var or 'SECRET' in var or 'TOKEN' in var or 'PASSWORD' in var:
                preview = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print_success(f"{name}: {preview}")
            else:
                print_success(f"{name}: Configurada")
            optional_ok += 1
        else:
            print_warning(f"{name}: No configurada (opcional)")
    
    return required_ok, optional_ok

def check_ai_providers() -> int:
    """Verifica proveedores de IA configurados"""
    print_header("VERIFICACIÓN DE PROVEEDORES DE IA")
    
    providers = []
    
    if os.getenv('OPENAI_API_KEY'):
        providers.append(('OpenAI', '✅'))
    else:
        providers.append(('OpenAI', '❌'))
    
    if os.getenv('GROQ_API_KEY'):
        providers.append(('Groq', '✅'))
    else:
        providers.append(('Groq', '❌'))
    
    if os.getenv('GEMINI_API_KEY'):
        providers.append(('Gemini', '✅'))
    else:
        providers.append(('Gemini', '❌'))
    
    if os.getenv('GROK_API_KEY'):
        providers.append(('Grok', '✅'))
    else:
        providers.append(('Grok', '❌'))
    
    configured = sum(1 for _, status in providers if status == '✅')
    
    for name, status in providers:
        if status == '✅':
            print_success(f"{name}: Configurado")
        else:
            print_warning(f"{name}: No configurado")
    
    if configured == 0:
        print_warning("No hay proveedores de IA configurados. El sistema usará pattern matching.")
    elif configured == 1:
        print_info(f"1 proveedor de IA configurado")
    else:
        print_success(f"{configured} proveedores de IA configurados")
    
    return configured

def check_files() -> int:
    """Verifica archivos importantes"""
    print_header("VERIFICACIÓN DE ARCHIVOS")
    
    important_files = [
        ('config.py', 'Configuración del sistema'),
        ('sistema_cotizaciones.py', 'Sistema de cotizaciones'),
        ('chat_interactivo.py', 'Chat interactivo'),
        ('api_server.py', 'API server'),
        ('unified_launcher.py', 'Unified launcher'),
    ]
    
    knowledge_files = [
        'base_conocimiento_final.json',
        'conocimiento_completo.json',
        'base_conocimiento_exportada.json',
        'base_conocimiento_demo.json',
    ]
    
    files_ok = 0
    
    print(f"{Colors.BOLD}Archivos del Sistema:{Colors.ENDC}")
    for filename, description in important_files:
        if Path(filename).exists():
            print_success(f"{description}: {filename}")
            files_ok += 1
        else:
            print_error(f"{description}: {filename} no encontrado")
    
    print(f"\n{Colors.BOLD}Archivos de Conocimiento:{Colors.ENDC}")
    knowledge_found = 0
    for filename in knowledge_files:
        if Path(filename).exists():
            print_success(f"{filename}: Encontrado")
            knowledge_found += 1
        else:
            print_warning(f"{filename}: No encontrado (opcional)")
    
    if knowledge_found > 0:
        print_success(f"{knowledge_found} archivo(s) de conocimiento encontrado(s)")
    
    return files_ok

def main():
    print_header("VERIFICACIÓN COMPLETA DE CONFIGURACIÓN")
    
    # Verificar módulos
    required_modules, optional_modules = check_python_modules()
    
    # Verificar variables de entorno
    required_vars, optional_vars = check_env_variables()
    
    # Verificar proveedores de IA
    ai_providers = check_ai_providers()
    
    # Verificar archivos
    files_ok = check_files()
    
    # Resumen
    print_header("RESUMEN DE VERIFICACIÓN")
    
    all_required_ok = (
        required_modules == 2 and  # sistema_cotizaciones y utils_cotizaciones
        required_vars >= 1 and  # Al menos MONGODB_URI
        files_ok >= 3  # Al menos los archivos principales
    )
    
    if all_required_ok:
        print_success("✅ Configuración básica: COMPLETA")
    else:
        print_error("❌ Configuración básica: INCOMPLETA")
    
    print()
    print(f"Módulos requeridos: {required_modules}/2")
    print(f"Variables requeridas: {required_vars}/1")
    print(f"Archivos del sistema: {files_ok}/5")
    print(f"Proveedores de IA: {ai_providers}/4")
    print(f"Módulos opcionales: {optional_modules}/9")
    print(f"Variables opcionales: {optional_vars}/10")
    
    print()
    if all_required_ok:
        print_success("El sistema está listo para ejecutarse")
        print_info("Ejecuta: python unified_launcher.py")
    else:
        print_warning("Completa la configuración faltante antes de ejecutar")
        print_info("Ejecuta: python configurar_completo.py para configuración interactiva")
        print_info("O ejecuta: python configurar_auto.py para configuración automática")

if __name__ == "__main__":
    main()


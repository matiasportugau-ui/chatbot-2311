#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación Completa para Ejecución del Chatbot
Verifica que todo esté listo y funcional para ejecutar el sistema
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

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

def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def check_python_version() -> bool:
    """Verifica versión de Python"""
    print(f"{Colors.BOLD}1. Verificando Python...{Colors.ENDC}")
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print_success(f"Python {version.major}.{version.minor}.{version.micro} - OK")
            return True
        else:
            print_error(f"Python {version.major}.{version.minor}.{version.micro} - Se requiere Python 3.8+")
            return False
    except Exception as e:
        print_error(f"Error verificando Python: {e}")
        return False

def check_node_version() -> bool:
    """Verifica versión de Node.js"""
    print(f"\n{Colors.BOLD}2. Verificando Node.js...{Colors.ENDC}")
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"{version} - OK")
            return True
        else:
            print_warning("Node.js no encontrado (opcional para algunas funciones)")
            return False
    except FileNotFoundError:
        print_warning("Node.js no instalado (opcional para algunas funciones)")
        return False
    except Exception as e:
        print_warning(f"Error verificando Node.js: {e}")
        return False

def check_python_modules() -> Tuple[int, int]:
    """Verifica módulos de Python instalados"""
    print(f"\n{Colors.BOLD}3. Verificando Módulos de Python...{Colors.ENDC}")
    
    required_modules = [
        ('sistema_cotizaciones', 'Sistema de cotizaciones'),
        ('utils_cotizaciones', 'Utilidades'),
    ]
    
    optional_modules = [
        ('openai', 'OpenAI SDK'),
        ('groq', 'Groq SDK'),
        ('google.genai', 'Gemini SDK'),
        ('pymongo', 'MongoDB'),
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('gspread', 'Google Sheets'),
        ('redis', 'Redis'),
        ('qdrant_client', 'Qdrant'),
    ]
    
    required_ok = 0
    optional_ok = 0
    
    print("  Módulos Requeridos:")
    for module, name in required_modules:
        try:
            __import__(module)
            print_success(f"    {name}")
            required_ok += 1
        except ImportError:
            print_error(f"    {name} - NO INSTALADO")
    
    print("  Módulos Opcionales:")
    for module, name in optional_modules:
        try:
            __import__(module)
            print_success(f"    {name}")
            optional_ok += 1
        except ImportError:
            print_warning(f"    {name} - No instalado (opcional)")
    
    return required_ok, optional_ok

def check_system_files() -> Tuple[int, int]:
    """Verifica archivos del sistema"""
    print(f"\n{Colors.BOLD}4. Verificando Archivos del Sistema...{Colors.ENDC}")
    
    required_files = [
        ('config.py', 'Configuración del sistema'),
        ('sistema_cotizaciones.py', 'Sistema de cotizaciones'),
        ('chat_interactivo.py', 'Chat interactivo'),
        ('unified_launcher.py', 'Unified launcher'),
    ]
    
    optional_files = [
        ('api_server.py', 'API server'),
        ('base_conocimiento_dinamica.py', 'Base de conocimiento'),
        ('ia_conversacional_integrada.py', 'IA conversacional'),
    ]
    
    required_ok = 0
    optional_ok = 0
    
    print("  Archivos Requeridos:")
    for filename, description in required_files:
        if Path(filename).exists():
            print_success(f"    {description}: {filename}")
            required_ok += 1
        else:
            print_error(f"    {description}: {filename} - NO ENCONTRADO")
    
    print("  Archivos Opcionales:")
    for filename, description in optional_files:
        if Path(filename).exists():
            print_success(f"    {description}: {filename}")
            optional_ok += 1
        else:
            print_warning(f"    {description}: {filename} - No encontrado (opcional)")
    
    return required_ok, optional_ok

def check_env_configuration() -> Tuple[int, int]:
    """Verifica configuración de variables de entorno"""
    print(f"\n{Colors.BOLD}5. Verificando Configuración (.env)...{Colors.ENDC}")
    
    # Buscar archivos .env
    env_files = []
    for env_file in ['.env.local', '.env']:
        if Path(env_file).exists():
            env_files.append(env_file)
    
    if not env_files:
        print_error("    No se encontró archivo .env o .env.local")
        return 0, 0
    
    print_success(f"    Archivo encontrado: {env_files[0]}")
    
    # Cargar variables
    try:
        from dotenv import load_dotenv
        load_dotenv(env_files[0])
    except ImportError:
        # Cargar manualmente
        env_file = Path(env_files[0])
        for line in env_file.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"').strip("'")
    
    # Verificar variables críticas
    critical_vars = {
        'MONGODB_URI': 'MongoDB URI',
    }
    
    recommended_vars = {
        'OPENAI_API_KEY': 'OpenAI API Key',
        'GROQ_API_KEY': 'Groq API Key',
        'GEMINI_API_KEY': 'Gemini API Key',
    }
    
    critical_ok = 0
    recommended_ok = 0
    
    print("  Variables Críticas:")
    for var, name in critical_vars.items():
        value = os.getenv(var, '')
        if value and len(value) > 5 and not value.startswith('your-'):
            print_success(f"    {name}: Configurado")
            critical_ok += 1
        else:
            print_error(f"    {name}: No configurado")
    
    print("  Variables Recomendadas:")
    for var, name in recommended_vars.items():
        value = os.getenv(var, '')
        if value and len(value) > 5 and not value.startswith('your-'):
            print_success(f"    {name}: Configurado")
            recommended_ok += 1
        else:
            print_warning(f"    {name}: No configurado (opcional)")
    
    return critical_ok, recommended_ok

def check_knowledge_files() -> int:
    """Verifica archivos de conocimiento"""
    print(f"\n{Colors.BOLD}6. Verificando Archivos de Conocimiento...{Colors.ENDC}")
    
    knowledge_files = [
        'base_conocimiento_final.json',
        'conocimiento_completo.json',
        'base_conocimiento_exportada.json',
        'base_conocimiento_demo.json',
    ]
    
    found = 0
    for filename in knowledge_files:
        if Path(filename).exists():
            size = Path(filename).stat().st_size
            print_success(f"    {filename} ({size:,} bytes)")
            found += 1
        else:
            print_warning(f"    {filename} - No encontrado (opcional)")
    
    return found

def check_database_connection() -> bool:
    """Verifica conexión a MongoDB"""
    print(f"\n{Colors.BOLD}7. Verificando Conexión a MongoDB...{Colors.ENDC}")
    
    mongodb_uri = os.getenv('MONGODB_URI', '')
    if not mongodb_uri:
        print_warning("    MONGODB_URI no configurado")
        return False
    
    if mongodb_uri.startswith('mongodb://localhost'):
        print_info("    MongoDB local detectado")
        # Intentar conectar
        try:
            import pymongo
            from urllib.parse import urlparse
            parsed = urlparse(mongodb_uri)
            client = pymongo.MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
            client.server_info()  # Forzar conexión
            print_success("    Conexión a MongoDB: OK")
            return True
        except ImportError:
            print_warning("    pymongo no instalado - No se puede verificar conexión")
            return False
        except Exception as e:
            print_warning(f"    No se pudo conectar a MongoDB: {e}")
            print_info("    (Esto es normal si MongoDB no está corriendo localmente)")
            return False
    else:
        print_info("    MongoDB remoto (Atlas) configurado")
        print_warning("    No se puede verificar conexión sin credenciales")
        return True  # Asumir OK si está configurado

def check_ai_providers() -> int:
    """Verifica proveedores de IA configurados"""
    print(f"\n{Colors.BOLD}8. Verificando Proveedores de IA...{Colors.ENDC}")
    
    providers = {
        'OpenAI': 'OPENAI_API_KEY',
        'Groq': 'GROQ_API_KEY',
        'Gemini': 'GEMINI_API_KEY',
        'Grok': 'GROK_API_KEY',
    }
    
    configured = 0
    for name, var in providers.items():
        value = os.getenv(var, '')
        if value and len(value) > 5 and not value.startswith('your-'):
            print_success(f"    {name}: Configurado")
            configured += 1
        else:
            print_warning(f"    {name}: No configurado")
    
    if configured == 0:
        print_warning("    ⚠️  Ningún proveedor de IA configurado - El sistema usará pattern matching")
    elif configured == 1:
        print_success(f"    ✅ {configured} proveedor de IA configurado")
    else:
        print_success(f"    ✅ {configured} proveedores de IA configurados")
    
    return configured

def main():
    """Ejecuta verificación completa"""
    print_header("VERIFICACIÓN COMPLETA PARA EJECUCIÓN")
    
    results = {
        'python': False,
        'node': False,
        'modules_required': 0,
        'modules_optional': 0,
        'files_required': 0,
        'files_optional': 0,
        'env_critical': 0,
        'env_recommended': 0,
        'knowledge_files': 0,
        'database': False,
        'ai_providers': 0,
    }
    
    # Ejecutar verificaciones
    results['python'] = check_python_version()
    results['node'] = check_node_version()
    results['modules_required'], results['modules_optional'] = check_python_modules()
    results['files_required'], results['files_optional'] = check_system_files()
    results['env_critical'], results['env_recommended'] = check_env_configuration()
    results['knowledge_files'] = check_knowledge_files()
    results['database'] = check_database_connection()
    results['ai_providers'] = check_ai_providers()
    
    # Resumen final
    print_header("RESUMEN DE VERIFICACIÓN")
    
    all_critical_ok = (
        results['python'] and
        results['modules_required'] == 2 and  # sistema_cotizaciones y utils_cotizaciones
        results['files_required'] == 4 and  # Todos los archivos requeridos
        results['env_critical'] >= 1  # Al menos MongoDB
    )
    
    if all_critical_ok:
        print_success("✅ SISTEMA LISTO PARA EJECUTAR")
        print()
        print("Puedes ejecutar el chatbot con:")
        print("  • python unified_launcher.py")
        print("  • python chat_interactivo.py")
    else:
        print_error("❌ SISTEMA NO ESTÁ COMPLETAMENTE LISTO")
        print()
        print("Problemas encontrados:")
        if not results['python']:
            print("  • Python no cumple con los requisitos")
        if results['modules_required'] < 2:
            print(f"  • Faltan módulos requeridos: {2 - results['modules_required']}")
        if results['files_required'] < 4:
            print(f"  • Faltan archivos requeridos: {4 - results['files_required']}")
        if results['env_critical'] < 1:
            print("  • Variables de entorno críticas no configuradas")
    
    print()
    print(f"{Colors.BOLD}Detalles:{Colors.ENDC}")
    print(f"  • Python: {'✅' if results['python'] else '❌'}")
    print(f"  • Node.js: {'✅' if results['node'] else '⚠️  (opcional)'}")
    print(f"  • Módulos requeridos: {results['modules_required']}/2")
    print(f"  • Módulos opcionales: {results['modules_optional']}/9")
    print(f"  • Archivos requeridos: {results['files_required']}/4")
    print(f"  • Archivos opcionales: {results['files_optional']}/3")
    print(f"  • Variables críticas: {results['env_critical']}/1")
    print(f"  • Variables recomendadas: {results['env_recommended']}/3")
    print(f"  • Archivos de conocimiento: {results['knowledge_files']}/4")
    print(f"  • Base de datos: {'✅' if results['database'] else '⚠️ '}")
    print(f"  • Proveedores de IA: {results['ai_providers']}/4")
    print()
    
    if all_critical_ok:
        print_success("🎉 ¡Todo está listo para ejecutar el chatbot!")
    else:
        print_warning("⚠️  Completa las configuraciones faltantes antes de ejecutar")
        print_info("Ejecuta: python configurar_completo.py para configuración interactiva")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nVerificación cancelada")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Error durante la verificación: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


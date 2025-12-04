#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Configuración Completa del Chatbot BMC
Configura todas las variables de entorno necesarias de forma interactiva
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def prompt_input(prompt: str, default: Optional[str] = None, required: bool = False, secret: bool = False) -> str:
    """Solicita input al usuario con valor por defecto"""
    if default:
        prompt_text = f"{prompt} [{default}]: "
    else:
        prompt_text = f"{prompt}: "
    
    if secret:
        import getpass
        value = getpass.getpass(prompt_text)
    else:
        value = input(prompt_text).strip()
    
    if not value and default:
        return default
    if not value and required:
        print_error("Este campo es obligatorio")
        return prompt_input(prompt, default, required, secret)
    return value

def prompt_yes_no(prompt: str, default: bool = True) -> bool:
    """Solicita confirmación sí/no"""
    default_text = "S/n" if default else "s/N"
    response = input(f"{prompt} [{default_text}]: ").strip().lower()
    if not response:
        return default
    return response in ['s', 'si', 'sí', 'y', 'yes']

def read_env_file(env_path: Path) -> Dict[str, str]:
    """Lee un archivo .env y retorna un diccionario"""
    env_data = {}
    if not env_path.exists():
        return env_data
    
    for line in env_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, value = line.split('=', 1)
            env_data[key.strip()] = value.strip().strip('"').strip("'")
    return env_data

def write_env_file(env_path: Path, env_data: Dict[str, str], comments: Dict[str, str] = None):
    """Escribe un archivo .env"""
    lines = [
        "# ============================================",
        "# Archivo de configuración del Chatbot BMC",
        "# Generado automáticamente por configurar_completo.py",
        "# ============================================",
        "",
    ]
    
    # Agrupar por secciones
    sections = {
        'API Configuration': [
            'NEXT_PUBLIC_API_URL', 'NEXT_PUBLIC_WS_URL', 'PY_CHAT_SERVICE_URL'
        ],
        'Authentication': [
            'NEXTAUTH_URL', 'NEXTAUTH_SECRET'
        ],
        'Database': [
            'DATABASE_URL', 'MONGODB_URI', 'MELI_ACCESS_TOKEN', 'MELI_SELLER_ID'
        ],
        'WhatsApp Configuration': [
            'WHATSAPP_VERIFY_TOKEN', 'WHATSAPP_ACCESS_TOKEN', 'WHATSAPP_PHONE_NUMBER_ID',
            'WHATSAPP_BUSINESS_ID', 'WHATSAPP_APP_SECRET', 'N8N_WEBHOOK_URL_EXTERNAL'
        ],
        'OpenAI Configuration': [
            'OPENAI_API_KEY', 'OPENAI_MODELS', 'OPENAI_ORGANIZATION_ID', 'OPENAI_PROJECT_ID'
        ],
        'Groq Configuration': [
            'GROQ_API_KEY', 'GROQ_MODELS'
        ],
        'Google Gemini Configuration': [
            'GEMINI_API_KEY', 'GEMINI_MODELS'
        ],
        'xAI (Grok) Configuration': [
            'GROK_API_KEY', 'GROK_MODELS'
        ],
        'Model Selection': [
            'MODEL_STRATEGY'
        ],
        'n8n Configuration': [
            'N8N_BASE_URL', 'N8N_API_KEY', 'N8N_PUBLIC_KEY', 'N8N_PRIVATE_KEY'
        ],
        'Mercado Libre Configuration': [
            'MERCADO_LIBRE_APP_ID', 'MERCADO_LIBRE_CLIENT_SECRET', 'MERCADO_LIBRE_REDIRECT_URI',
            'MERCADO_LIBRE_SELLER_ID', 'MERCADO_LIBRE_WEBHOOK_SECRET', 'MERCADO_LIBRE_AUTH_URL',
            'MERCADO_LIBRE_API_URL', 'MERCADO_LIBRE_SCOPES', 'MERCADO_LIBRE_PKCE_ENABLED'
        ],
        'Google Sheets': [
            'GOOGLE_SHEET_ID', 'GOOGLE_SERVICE_ACCOUNT_EMAIL', 'GOOGLE_PRIVATE_KEY',
            'GOOGLE_SHEETS_API_KEY'
        ],
        'System Configuration': [
            'NODE_ENV', 'LOG_LEVEL', 'ENABLE_REQUEST_TRACKING'
        ]
    }
    
    # Escribir secciones
    for section_name, keys in sections.items():
        section_vars = {k: v for k, v in env_data.items() if k in keys}
        if section_vars:
            lines.append(f"# {section_name}")
            for key in keys:
                if key in env_data:
                    comment = comments.get(key, '') if comments else ''
                    if comment:
                        lines.append(f"# {comment}")
                    value = env_data[key]
                    # Escapar valores que contienen espacios o caracteres especiales
                    if ' ' in value or '#' in value or value.startswith('$'):
                        value = f'"{value}"'
                    lines.append(f"{key}={value}")
            lines.append("")
    
    # Variables no categorizadas
    categorized_keys = set()
    for keys in sections.values():
        categorized_keys.update(keys)
    
    uncategorized = {k: v for k, v in env_data.items() if k not in categorized_keys}
    if uncategorized:
        lines.append("# Other Configuration")
        for key, value in uncategorized.items():
            if ' ' in value or '#' in value or value.startswith('$'):
                value = f'"{value}"'
            lines.append(f"{key}={value}")
        lines.append("")
    
    env_path.write_text('\n'.join(lines), encoding='utf-8')

def configure_ai_models(env_data: Dict[str, str]):
    """Configura los modelos de IA"""
    print_header("CONFIGURACIÓN DE MODELOS DE IA")
    
    print_info("Puedes configurar múltiples proveedores de IA o dejar en blanco para usar solo uno.")
    print()
    
    # OpenAI
    print(f"{Colors.BOLD}1. OpenAI (Recomendado para producción){Colors.ENDC}")
    if prompt_yes_no("¿Deseas configurar OpenAI?", default=True):
        api_key = prompt_input("OPENAI_API_KEY", required=True, secret=True)
        if api_key:
            env_data['OPENAI_API_KEY'] = api_key
            env_data['OPENAI_MODELS'] = prompt_input(
                "OPENAI_MODELS (separados por coma)",
                default="gpt-4o-mini,gpt-4o,gpt-3.5-turbo"
            )
            org_id = prompt_input("OPENAI_ORGANIZATION_ID (opcional)", default="")
            if org_id:
                env_data['OPENAI_ORGANIZATION_ID'] = org_id
            proj_id = prompt_input("OPENAI_PROJECT_ID (opcional)", default="")
            if proj_id:
                env_data['OPENAI_PROJECT_ID'] = proj_id
            print_success("OpenAI configurado")
    
    # Groq
    print(f"\n{Colors.BOLD}2. Groq (Gratis, muy rápido){Colors.ENDC}")
    if prompt_yes_no("¿Deseas configurar Groq?", default=False):
        api_key = prompt_input("GROQ_API_KEY", required=True, secret=True)
        if api_key:
            env_data['GROQ_API_KEY'] = api_key
            env_data['GROQ_MODELS'] = prompt_input(
                "GROQ_MODELS (separados por coma)",
                default="llama-3.1-70b-versatile,llama-3.1-8b-instant,mixtral-8x7b-32768"
            )
            print_success("Groq configurado")
    
    # Gemini
    print(f"\n{Colors.BOLD}3. Google Gemini (Gratis, buena calidad){Colors.ENDC}")
    if prompt_yes_no("¿Deseas configurar Gemini?", default=False):
        api_key = prompt_input("GEMINI_API_KEY", required=True, secret=True)
        if api_key:
            env_data['GEMINI_API_KEY'] = api_key
            env_data['GEMINI_MODELS'] = prompt_input(
                "GEMINI_MODELS (separados por coma)",
                default="gemini-2.5-flash,gemini-1.5-pro,gemini-3-pro"
            )
            print_success("Gemini configurado")
    
    # Grok
    print(f"\n{Colors.BOLD}4. xAI Grok (Opcional){Colors.ENDC}")
    if prompt_yes_no("¿Deseas configurar Grok?", default=False):
        api_key = prompt_input("GROK_API_KEY", required=True, secret=True)
        if api_key:
            env_data['GROK_API_KEY'] = api_key
            env_data['GROK_MODELS'] = prompt_input(
                "GROK_MODELS (separados por coma)",
                default="grok-beta,grok-2-1212,grok-4-latest"
            )
            print_success("Grok configurado")
    
    # Estrategia de modelo
    print(f"\n{Colors.BOLD}Estrategia de selección de modelo{Colors.ENDC}")
    strategy = prompt_input(
        "MODEL_STRATEGY (cost/speed/quality/balanced)",
        default="balanced"
    )
    env_data['MODEL_STRATEGY'] = strategy

def configure_database(env_data: Dict[str, str]):
    """Configura las bases de datos"""
    print_header("CONFIGURACIÓN DE BASES DE DATOS")
    
    # MongoDB
    print(f"{Colors.BOLD}MongoDB{Colors.ENDC}")
    print_info("Puedes usar MongoDB local o MongoDB Atlas (cloud)")
    
    mongodb_uri = prompt_input(
        "MONGODB_URI",
        default="mongodb://localhost:27017/bmc_chat"
    )
    env_data['MONGODB_URI'] = mongodb_uri
    
    if mongodb_uri.startswith('mongodb+srv://'):
        print_success("MongoDB Atlas configurado")
    else:
        print_success("MongoDB local configurado")
    
    # PostgreSQL (opcional)
    print(f"\n{Colors.BOLD}PostgreSQL (Opcional){Colors.ENDC}")
    if prompt_yes_no("¿Deseas configurar PostgreSQL?", default=False):
        db_url = prompt_input(
            "DATABASE_URL",
            default="postgresql://username:password@localhost:5432/bmc_dashboard"
        )
        env_data['DATABASE_URL'] = db_url

def configure_google_sheets(env_data: Dict[str, str]):
    """Configura Google Sheets"""
    print_header("CONFIGURACIÓN DE GOOGLE SHEETS")
    
    if not prompt_yes_no("¿Deseas configurar Google Sheets?", default=False):
        return
    
    sheet_id = prompt_input(
        "GOOGLE_SHEET_ID",
        default="1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0"
    )
    env_data['GOOGLE_SHEET_ID'] = sheet_id
    
    email = prompt_input("GOOGLE_SERVICE_ACCOUNT_EMAIL", required=True)
    env_data['GOOGLE_SERVICE_ACCOUNT_EMAIL'] = email
    
    print_info("Pega la clave privada completa (incluyendo BEGIN y END)")
    private_key = prompt_input("GOOGLE_PRIVATE_KEY", required=True)
    env_data['GOOGLE_PRIVATE_KEY'] = private_key
    
    print_success("Google Sheets configurado")
    print_warning("Recuerda compartir el Google Sheet con el email del Service Account")

def configure_whatsapp(env_data: Dict[str, str]):
    """Configura WhatsApp"""
    print_header("CONFIGURACIÓN DE WHATSAPP")
    
    if not prompt_yes_no("¿Deseas configurar WhatsApp?", default=False):
        return
    
    env_data['WHATSAPP_VERIFY_TOKEN'] = prompt_input("WHATSAPP_VERIFY_TOKEN", required=True)
    env_data['WHATSAPP_ACCESS_TOKEN'] = prompt_input("WHATSAPP_ACCESS_TOKEN", required=True, secret=True)
    env_data['WHATSAPP_PHONE_NUMBER_ID'] = prompt_input("WHATSAPP_PHONE_NUMBER_ID", required=True)
    env_data['WHATSAPP_BUSINESS_ID'] = prompt_input("WHATSAPP_BUSINESS_ID", default="")
    env_data['WHATSAPP_APP_SECRET'] = prompt_input("WHATSAPP_APP_SECRET", default="", secret=True)
    env_data['N8N_WEBHOOK_URL_EXTERNAL'] = prompt_input(
        "N8N_WEBHOOK_URL_EXTERNAL",
        default="http://localhost:5678/webhook/whatsapp"
    )
    
    print_success("WhatsApp configurado")

def configure_mercado_libre(env_data: Dict[str, str]):
    """Configura Mercado Libre"""
    print_header("CONFIGURACIÓN DE MERCADO LIBRE")
    
    if not prompt_yes_no("¿Deseas configurar Mercado Libre?", default=False):
        return
    
    env_data['MERCADO_LIBRE_APP_ID'] = prompt_input("MERCADO_LIBRE_APP_ID", required=True)
    env_data['MERCADO_LIBRE_CLIENT_SECRET'] = prompt_input("MERCADO_LIBRE_CLIENT_SECRET", required=True, secret=True)
    env_data['MERCADO_LIBRE_REDIRECT_URI'] = prompt_input(
        "MERCADO_LIBRE_REDIRECT_URI",
        default="http://localhost:3000/api/mercado-libre/auth/callback"
    )
    env_data['MERCADO_LIBRE_SELLER_ID'] = prompt_input("MERCADO_LIBRE_SELLER_ID", default="")
    env_data['MERCADO_LIBRE_WEBHOOK_SECRET'] = prompt_input("MERCADO_LIBRE_WEBHOOK_SECRET", default="")
    
    print_info("Selecciona la región donde registraste tu app:")
    print("1. Argentina (auth.mercadolibre.com.ar)")
    print("2. México (auth.mercadolibre.com.mx)")
    print("3. Uruguay (auth.mercadolibre.com.uy)")
    print("4. Brasil (auth.mercadolibre.com.br)")
    print("5. Chile (auth.mercadolibre.com.cl)")
    print("6. Colombia (auth.mercadolibre.com.co)")
    print("7. Perú (auth.mercadolibre.com.pe)")
    
    region_map = {
        '1': 'https://auth.mercadolibre.com.ar',
        '2': 'https://auth.mercadolibre.com.mx',
        '3': 'https://auth.mercadolibre.com.uy',
        '4': 'https://auth.mercadolibre.com.br',
        '5': 'https://auth.mercadolibre.com.cl',
        '6': 'https://auth.mercadolibre.com.co',
        '7': 'https://auth.mercadolibre.com.pe'
    }
    
    region = prompt_input("Región [3]", default="3")
    env_data['MERCADO_LIBRE_AUTH_URL'] = region_map.get(region, region_map['3'])
    env_data['MERCADO_LIBRE_API_URL'] = "https://api.mercadolibre.com"
    env_data['MERCADO_LIBRE_SCOPES'] = "offline_access read write"
    env_data['MERCADO_LIBRE_PKCE_ENABLED'] = "true"
    
    print_success("Mercado Libre configurado")

def configure_n8n(env_data: Dict[str, str]):
    """Configura n8n"""
    print_header("CONFIGURACIÓN DE N8N")
    
    if not prompt_yes_no("¿Deseas configurar n8n?", default=False):
        return
    
    env_data['N8N_BASE_URL'] = prompt_input("N8N_BASE_URL", default="http://localhost:5678")
    env_data['N8N_API_KEY'] = prompt_input("N8N_API_KEY", default="")
    env_data['N8N_PUBLIC_KEY'] = prompt_input("N8N_PUBLIC_KEY", default="")
    env_data['N8N_PRIVATE_KEY'] = prompt_input("N8N_PRIVATE_KEY", default="", secret=True)
    
    print_success("n8n configurado")

def configure_system(env_data: Dict[str, str]):
    """Configura variables del sistema"""
    print_header("CONFIGURACIÓN DEL SISTEMA")
    
    env_data['NODE_ENV'] = prompt_input("NODE_ENV", default="development")
    env_data['NEXT_PUBLIC_API_URL'] = prompt_input("NEXT_PUBLIC_API_URL", default="http://localhost:3001/api")
    env_data['NEXT_PUBLIC_WS_URL'] = prompt_input("NEXT_PUBLIC_WS_URL", default="ws://localhost:3001/ws")
    env_data['PY_CHAT_SERVICE_URL'] = prompt_input("PY_CHAT_SERVICE_URL", default="http://localhost:8000")
    env_data['NEXTAUTH_URL'] = prompt_input("NEXTAUTH_URL", default="http://localhost:3000")
    
    # Generar secret aleatorio si no existe
    import secrets
    nextauth_secret = prompt_input("NEXTAUTH_SECRET", default=secrets.token_urlsafe(32))
    env_data['NEXTAUTH_SECRET'] = nextauth_secret
    
    env_data['LOG_LEVEL'] = prompt_input("LOG_LEVEL", default="INFO")
    env_data['ENABLE_REQUEST_TRACKING'] = prompt_input("ENABLE_REQUEST_TRACKING", default="true")
    
    print_success("Sistema configurado")

def verify_configuration(env_data: Dict[str, str]):
    """Verifica la configuración"""
    print_header("VERIFICACIÓN DE CONFIGURACIÓN")
    
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API Key',
        'MONGODB_URI': 'MongoDB URI',
    }
    
    optional_vars = {
        'GROQ_API_KEY': 'Groq API Key',
        'GEMINI_API_KEY': 'Gemini API Key',
        'GOOGLE_SHEET_ID': 'Google Sheet ID',
        'WHATSAPP_ACCESS_TOKEN': 'WhatsApp Access Token',
        'MERCADO_LIBRE_APP_ID': 'Mercado Libre App ID',
    }
    
    all_ok = True
    
    print(f"{Colors.BOLD}Variables Requeridas:{Colors.ENDC}")
    for var, name in required_vars.items():
        if var in env_data and env_data[var]:
            print_success(f"{name}: Configurado")
        else:
            print_error(f"{name}: No configurado")
            all_ok = False
    
    print(f"\n{Colors.BOLD}Variables Opcionales:{Colors.ENDC}")
    for var, name in optional_vars.items():
        if var in env_data and env_data[var]:
            print_success(f"{name}: Configurado")
        else:
            print_info(f"{name}: No configurado (opcional)")
    
    return all_ok

def main():
    print_header("CONFIGURACIÓN COMPLETA DEL CHATBOT BMC")
    
    env_file = Path('.env')
    env_local_file = Path('.env.local')
    
    # Determinar qué archivo usar
    target_file = env_local_file if env_local_file.exists() else env_file
    
    # Leer configuración existente
    existing_env = read_env_file(target_file)
    if existing_env:
        print_info(f"Se encontró configuración existente en {target_file}")
        if not prompt_yes_no("¿Deseas actualizar la configuración existente?", default=True):
            print_info("Configuración cancelada")
            return
    
    # Leer env.example como base
    env_example = Path('env.example')
    if env_example.exists():
        base_env = read_env_file(env_example)
        # Combinar con existente (existente tiene prioridad)
        for key, value in base_env.items():
            if key not in existing_env:
                existing_env[key] = value
    
    env_data = existing_env.copy()
    
    # Configurar cada sección
    configure_ai_models(env_data)
    configure_database(env_data)
    configure_google_sheets(env_data)
    configure_whatsapp(env_data)
    configure_mercado_libre(env_data)
    configure_n8n(env_data)
    configure_system(env_data)
    
    # Verificar configuración
    is_valid = verify_configuration(env_data)
    
    if not is_valid:
        print_warning("Algunas variables requeridas no están configuradas")
        if not prompt_yes_no("¿Deseas continuar de todas formas?", default=False):
            print_info("Configuración cancelada")
            return
    
    # Escribir archivo
    comments = {
        'OPENAI_API_KEY': 'Get your API key from https://platform.openai.com/api-keys',
        'GROQ_API_KEY': 'Get your API key from https://console.groq.com/keys',
        'GEMINI_API_KEY': 'Get your API key from https://makersuite.google.com/app/apikey',
        'MONGODB_URI': 'MongoDB connection string (local or Atlas)',
        'GOOGLE_SHEET_ID': 'ID of the Google Sheet to use',
        'MERCADO_LIBRE_AUTH_URL': 'Must match the region where you registered your app',
    }
    
    write_env_file(target_file, env_data, comments)
    
    print_header("CONFIGURACIÓN COMPLETADA")
    print_success(f"Archivo de configuración creado: {target_file.resolve()}")
    print()
    print_info("Próximos pasos:")
    print("  1. Verifica que todas las credenciales estén correctas")
    print("  2. Si configuraste Google Sheets, comparte el Sheet con el Service Account")
    print("  3. Si configuraste MongoDB Atlas, verifica el acceso de red")
    print("  4. Ejecuta: python unified_launcher.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + Colors.WARNING + "Configuración cancelada por el usuario" + Colors.ENDC)
        sys.exit(1)
    except Exception as e:
        print_error(f"Error durante la configuración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


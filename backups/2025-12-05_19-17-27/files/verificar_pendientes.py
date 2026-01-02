#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar qué configuraciones están pendientes
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️  python-dotenv no instalado. Instalando...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "python-dotenv"], check=True)
    from dotenv import load_dotenv

def check_configuration():
    """Verifica qué configuraciones están pendientes"""
    
    # Cargar .env.local
    env_file = Path('.env.local')
    if not env_file.exists():
        env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ No se encontró archivo .env o .env.local")
        print("   Ejecuta: python configurar_auto.py")
        return
    
    load_dotenv(env_file)
    print(f"✅ Archivo encontrado: {env_file}\n")
    
    # Variables requeridas para funcionamiento básico
    required_vars = {
        'MONGODB_URI': {
            'name': 'MongoDB URI',
            'description': 'Cadena de conexión a MongoDB (local o Atlas)',
            'example': 'mongodb://localhost:27017/bmc_chat o mongodb+srv://...'
        }
    }
    
    # Variables opcionales pero recomendadas
    recommended_vars = {
        'OPENAI_API_KEY': {
            'name': 'OpenAI API Key',
            'description': 'Para usar modelos de OpenAI (gpt-4o-mini, gpt-4o, etc.)',
            'example': 'sk-proj-...',
            'url': 'https://platform.openai.com/api-keys'
        },
        'GROQ_API_KEY': {
            'name': 'Groq API Key',
            'description': 'Para usar modelos de Groq (gratis, muy rápido)',
            'example': 'gsk_...',
            'url': 'https://console.groq.com/keys'
        },
        'GEMINI_API_KEY': {
            'name': 'Gemini API Key',
            'description': 'Para usar modelos de Google Gemini (gratis)',
            'example': 'AIza...',
            'url': 'https://makersuite.google.com/app/apikey'
        }
    }
    
    # Variables opcionales para integraciones
    optional_vars = {
        'GOOGLE_SERVICE_ACCOUNT_EMAIL': {
            'name': 'Google Service Account Email',
            'description': 'Email del Service Account para Google Sheets',
            'example': 'bmc-sheets@proyecto.iam.gserviceaccount.com',
            'url': 'https://console.cloud.google.com/iam-admin/serviceaccounts'
        },
        'GOOGLE_PRIVATE_KEY': {
            'name': 'Google Private Key',
            'description': 'Clave privada del Service Account (JSON)',
            'example': '-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----',
            'requires': ['GOOGLE_SERVICE_ACCOUNT_EMAIL']
        },
        'WHATSAPP_ACCESS_TOKEN': {
            'name': 'WhatsApp Access Token',
            'description': 'Token de acceso de WhatsApp Business API',
            'example': 'EAA...',
            'url': 'https://developers.facebook.com/docs/whatsapp'
        },
        'WHATSAPP_PHONE_NUMBER_ID': {
            'name': 'WhatsApp Phone Number ID',
            'description': 'ID del número de teléfono de WhatsApp',
            'example': '123456789012345',
            'requires': ['WHATSAPP_ACCESS_TOKEN']
        },
        'MERCADO_LIBRE_APP_ID': {
            'name': 'Mercado Libre App ID',
            'description': 'ID de la aplicación de Mercado Libre',
            'example': '1234567890123456',
            'url': 'https://developers.mercadolibre.com.uy/apps/'
        },
        'MERCADO_LIBRE_CLIENT_SECRET': {
            'name': 'Mercado Libre Client Secret',
            'description': 'Client Secret de la app de Mercado Libre',
            'example': 'abc123...',
            'requires': ['MERCADO_LIBRE_APP_ID']
        },
        'N8N_API_KEY': {
            'name': 'n8n API Key',
            'description': 'API Key para integración con n8n',
            'example': 'n8n_api_...',
            'url': 'http://localhost:5678/settings/api'
        }
    }
    
    print("=" * 70)
    print("VERIFICACIÓN DE CONFIGURACIONES PENDIENTES")
    print("=" * 70)
    print()
    
    # Verificar requeridas
    print("🔴 VARIABLES REQUERIDAS (Críticas):")
    print("-" * 70)
    missing_required = []
    for var, info in required_vars.items():
        value = os.getenv(var, '').strip()
        if value and not value.startswith('your-') and value != '':
            if 'URI' in var or 'URL' in var:
                print(f"✅ {info['name']}: {value[:50]}...")
            else:
                preview = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {info['name']}: {preview}")
        else:
            print(f"❌ {info['name']}: NO CONFIGURADA")
            print(f"   📝 {info['description']}")
            print(f"   💡 Ejemplo: {info['example']}")
            missing_required.append((var, info))
    print()
    
    # Verificar recomendadas
    print("🟡 VARIABLES RECOMENDADAS (Para mejor funcionalidad):")
    print("-" * 70)
    missing_recommended = []
    for var, info in recommended_vars.items():
        value = os.getenv(var, '').strip()
        if value and not value.startswith('your-') and value != '':
            preview = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {info['name']}: {preview}")
        else:
            print(f"⚠️  {info['name']}: No configurada")
            print(f"   📝 {info['description']}")
            if 'url' in info:
                print(f"   🔗 Obtener: {info['url']}")
            missing_recommended.append((var, info))
    print()
    
    # Verificar opcionales
    print("🟢 VARIABLES OPCIONALES (Para integraciones):")
    print("-" * 70)
    missing_optional = []
    for var, info in optional_vars.items():
        value = os.getenv(var, '').strip()
        
        # Verificar dependencias
        if 'requires' in info:
            all_required_set = all(
                os.getenv(req, '').strip() and not os.getenv(req, '').startswith('your-')
                for req in info['requires']
            )
            if not all_required_set:
                print(f"⏸️  {info['name']}: Requiere configurar primero: {', '.join(info['requires'])}")
                continue
        
        if value and not value.startswith('your-') and value != '':
            if 'KEY' in var or 'SECRET' in var or 'TOKEN' in var:
                preview = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {info['name']}: {preview}")
            else:
                print(f"✅ {info['name']}: {value[:50]}")
        else:
            print(f"⚪ {info['name']}: No configurada (opcional)")
            if 'url' in info:
                print(f"   🔗 Más info: {info['url']}")
            missing_optional.append((var, info))
    print()
    
    # Resumen
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print()
    
    total_required = len(required_vars)
    configured_required = total_required - len(missing_required)
    
    total_recommended = len(recommended_vars)
    configured_recommended = total_recommended - len(missing_recommended)
    
    total_optional = len(optional_vars)
    configured_optional = total_optional - len(missing_optional)
    
    print(f"✅ Requeridas: {configured_required}/{total_required}")
    print(f"⚠️  Recomendadas: {configured_recommended}/{total_recommended}")
    print(f"⚪ Opcionales: {configured_optional}/{total_optional}")
    print()
    
    if missing_required:
        print("❌ ACCIÓN REQUERIDA:")
        print("   Debes configurar las variables requeridas antes de usar el sistema.")
        print("   Ejecuta: python configurar_completo.py")
    elif missing_recommended:
        print("⚠️  RECOMENDACIÓN:")
        print("   Configura al menos un proveedor de IA (OpenAI, Groq o Gemini)")
        print("   para mejor funcionalidad. Sin esto, el sistema usará pattern matching.")
        print("   Ejecuta: python configurar_completo.py")
    else:
        print("✅ El sistema está completamente configurado y listo para usar!")
        print("   Ejecuta: python unified_launcher.py")
    
    print()
    
    # Lista de pendientes
    if missing_required or missing_recommended:
        print("📋 CONFIGURACIONES PENDIENTES:")
        print("-" * 70)
        
        if missing_required:
            print("\n🔴 CRÍTICAS (Debes configurar):")
            for var, info in missing_required:
                print(f"   • {info['name']}")
                print(f"     {info['description']}")
                if 'url' in info:
                    print(f"     🔗 {info['url']}")
        
        if missing_recommended:
            print("\n🟡 RECOMENDADAS (Mejoran funcionalidad):")
            for var, info in missing_recommended:
                print(f"   • {info['name']}")
                print(f"     {info['description']}")
                if 'url' in info:
                    print(f"     🔗 {info['url']}")

if __name__ == "__main__":
    check_configuration()

